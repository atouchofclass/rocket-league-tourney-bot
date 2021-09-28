'''
    Rocket League Tourney Bot v1.0.4 (2021.09.27.0)
    A simple Discord bot for notifying users about upcoming Rocket League tournaments
    Copyright (c) 2021 atouchofclass
'''

import os
import sys
from datetime import datetime, timedelta
import json
import discord
from discord.ext import tasks

from data.tourney_times import tourney_notify_times_season_4, reaction_notify_times_season_4
from models.active_tourney_notification import ActiveTourneyNotification
from data.ranks import emoji_ranks, rank_emojis

channel = None

active_notification = None
past_notification_times_today = []

info_msg_text = "**Rocket League Tourney Bot v1.0.4** by atouchofclass" \
    + "\nHow it works:" \
    + "\n• __35 minutes__ before a scheduled tournament, the bot will send a message asking members to react with the rank they are interested in playing." \
    + "\n• __15 minutes__ before a scheduled 2nd chance tournament, the bot will send a message asking members to react with the rank they are interested in playing." \
    + "\n• __10 minutes__ before a scheduled tournament, the bot will create teams of players if there are enough reactions." \
    + " The server will be notified if someone needs a teammate. If someone would like to join a team, they should message the other players in the <#general> channel."

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(config['channel_id'])

    tourney_notify_times = tourney_notify_times_season_4
    reaction_notify_times = reaction_notify_times_season_4

    time_tracker.start(channel, tourney_notify_times, reaction_notify_times)

# Bot controller
@client.event
async def on_message(message):
    global active_notification
    msg_content = message.content
    reply = False

    if msg_content == '!info':
        msg = info_msg_text
        reply = True

    if reply:
        try:
            await message.channel.send(msg)
        except discord.errors.Forbidden:
            pass

# Bot loop
@tasks.loop(seconds=15)
async def time_tracker(channel, tourney_notify_times, reaction_notify_times):
    global active_notification
    global past_notification_times_today

    cur_time_hhmm = (datetime.now() + timedelta(hours=config['utc_time_correction'])).strftime('%H:%M')

    # check time to make tourney notification
    if cur_time_hhmm in tourney_notify_times and cur_time_hhmm not in past_notification_times_today:
        active_notification = ActiveTourneyNotification(tourney_notify_times[cur_time_hhmm]['party_size'])
        
        # time to notify channel
        print('[%s] Tourney notification' % cur_time_hhmm)
        past_notification_times_today.append(cur_time_hhmm)

        # send tourney notification
        msg = await channel.send(tourney_announcement_text(tourney_notify_times[cur_time_hhmm]))
        active_notification.message_id = msg.id
        
        for rank in rank_emojis:
            await msg.add_reaction(rank_emojis[rank]['emoji'])

        # cache_msg = discord.utils.get(client.cached_messages, id=msg.id)
        # print(cache_msg.reactions)

    # check time to make reactions / tourney teams notification
    if cur_time_hhmm in reaction_notify_times and cur_time_hhmm not in past_notification_times_today:
        # time to notify channel
        print('[%s] Reactions notification' % cur_time_hhmm)
        past_notification_times_today.append(cur_time_hhmm)
        active_notification.accepting_registrations = False

        # tests
        # active_notification.test_fill_registrants()
        # active_notification.test_add_reg()

        active_notification.create_teams()

        if active_notification.there_are_registrations():
            # send reactions notification
            msg = await channel.send(reactions_annoucement_text(reaction_notify_times[cur_time_hhmm]))
            if active_notification.there_are_leftover_registrants():
                await channel.send(leftover_registrants_announcement_text())
        else:
            # delete tourney notification message if there are no registrations
            msg = await channel.fetch_message(active_notification.message_id)
            await msg.delete()

    # check time to clear daily notification times
    if cur_time_hhmm == '00:15':
        print('[%s] Clear daily notification times' % cur_time_hhmm)
        past_notification_times_today = []

@client.event
async def on_reaction_add(reaction, user):
    # ignore reaction made by bot user
    if user.bot: return

    # ignore if not accepting registrations
    if not active_notification.accepting_registrations: return

    # check if reaction is attached the original notification message by the tourney bot
    if reaction.message.id == active_notification.message_id:
        try:
            reaction_emoji_name = str(reaction).split(':')[1]
            if reaction_emoji_name not in emoji_ranks: return
        except IndexError:
            # ignore extraneous emojis
            return
        
        send_to_channel = client.get_channel(config['channel_id'])

        # add player to registrations
        user_name = user.nick if user.nick is not None else user.name
        active_notification.add_player(user_id=user.id, user_name=user_name, reaction_emoji=reaction_emoji_name)
        # print(active_notification.registrations)

        # send message to channel
        msg = ":white_check_mark: **%s** is interested in playing the **%s** tournament!" % (user_name, emoji_ranks[reaction_emoji_name]['label'])
        await send_to_channel.send(msg)

@client.event
async def on_raw_reaction_remove(event):
    # ignore reaction made by bot user
    if event.user_id == config['client_user_id']: return

    # ignore if not accepting registrations
    if not active_notification.accepting_registrations: return

    # ignore extraneous emojis
    if event.emoji.name not in emoji_ranks: return
    
    # check if reaction is attached the original notification message by the tourney bot 
    if event.message_id == active_notification.message_id:
        send_to_channel = client.get_channel(config['channel_id'])

        # remove player from registrations
        removed_player = active_notification.remove_player(user_id=event.user_id, reaction_emoji=event.emoji.name)

        # send message to channel
        msg = ":no_entry_sign: **%s** is no longer interested in playing the **%s** tournament." % (removed_player.user_name, emoji_ranks[event.emoji.name]['label'])
        await send_to_channel.send(msg)

# Generate tourney announcement text
def tourney_announcement_text(tourney_time_obj):
    return ":bell: __**Announcement!**__ :bell:" \
        + "\nThere is an upcoming **%s** tournament at **%s**." % (tourney_time_obj['tourney_name'], tourney_time_obj['time_label']) \
        + "\nIf you would like to participate, react with the tournament rank you are interested in playing." \
        + "\nReactions will close 10 minutes before tournaments begin. If there are no reactions by that time, this message will self-destruct."

# Generate reactions / teams announcement text
def reactions_annoucement_text(reactions_time_obj):
    msg = ":bell: __**Announcement!**__ :bell:" \
        + "\nThere are 5 minutes left before the tournament at **%s**." % (reactions_time_obj['time_label'])
    
    if active_notification.teams_count() > 0:
        msg += "\nThe teams have been formed as follows:"
        for rank in active_notification.teams:
            if len(active_notification.teams[rank]) == 0: continue
            msg += "\n%s **%s**:" % (rank_emojis[rank]['emoji'], rank_emojis[rank]['label'])
            for t in range(len(active_notification.teams[rank])):
                msg += "\n\t• %s" % (', '.join(map(lambda p: mention(p.user_id), active_notification.teams[rank][t])))
    
    return msg

# Generate leftover registrants announcement text
def leftover_registrants_announcement_text():
    msg = '@everyone'

    for rank in active_notification.leftover_registrants:
        if len(active_notification.leftover_registrants[rank]) == 2:
            msg += "\n:warning: **%s** and **%s** are looking for a teammate for the **%s** tournament!" % \
                (active_notification.leftover_registrants[rank][0].user_name,
                active_notification.leftover_registrants[rank][1].user_name,
                rank_emojis[rank]['label'])
        if len(active_notification.leftover_registrants[rank]) == 1:
            msg += "\n:warning: **%s** is looking for teammate(s) for the **%s** tournament!" % \
                (active_notification.leftover_registrants[rank][0].user_name,
                rank_emojis[rank]['label'])
    
    msg += "\n:information_source: Please use the %s channel and voice channels to communicate with potential teammates." % (channel(config['alt_text_channel_id']))

    return msg

def is_weekday():
    return datetime.now().weekday() < 4

def mention(user_id):
    return '<@!%s>' % (user_id)

def channel(channel_id):
    return '<#%s>' % (channel_id)

def load_api_token():
    with open('api_token.txt', 'r') as f:
        return f.readlines()[0].strip()

def load_config():
    with open('config.json', 'r') as f:
        config_data = json.load(f)
        if 'utc_time_correction' not in config_data:
            config_data['utc_time_correction'] = 0
        return config_data

# Entry
config = load_config()
if 'alt_text_channel_id' in config:
    info_msg_text = info_msg_text.replace('<#general>', '<#%s>' % config['alt_text_channel_id'])
else:
    config['alt_text_channel_id'] = '#general'

if len(sys.argv) > 1 and sys.argv[1] == '--use-token-from-env-var':
    api_token = os.getenv('DISCORD_API_TOKEN_TOURNEY_BOT')
else:
    api_token = load_api_token()

print('datetime.now():', datetime.now().strftime('%H:%M'), ', utc_time_correction:', config['utc_time_correction'])

client.run(api_token)
