'''
    Rocket League Tourney Bot v0.0.1 (2021.08.02.0)
    A simple Discord bot for notifying users about upcoming Rocket League tournaments
    Copyright (c) 2021 atouchofclass
'''

import asyncio
from datetime import datetime
import discord

from tourney_times import tourney_notify_times_weekday, reaction_notify_times_weekday, \
    tourney_notify_times_weekend, reaction_notify_times_weekend
from active_tourney_notification import ActiveTourneyNotification
from ranks import emoji_ranks

channel_id = 871224692177006602
time_test = {'00:14': '6:00 PM EST', '23:52': '9:00 PM EST', '23:52': '12:00 AM EST'}
channel = None

active_notification = ActiveTourneyNotification()

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    # TODO change to weekend
    tourney_notify_times = tourney_notify_times_weekday if is_weekday() else tourney_notify_times_weekend
    reaction_notify_times = reaction_notify_times_weekday if is_weekday() else tourney_notify_times_weekend

    client.loop.create_task(time_tracker(channel, tourney_notify_times, reaction_notify_times))

# Bot controller
@client.event
async def on_message(message):
    msg_content = message.content
    reply = False

    if msg_content == '!hello':
        msg = "Hello, {0.author.mention}!".format(message)
        reply = True

    elif msg_content == '!help':
        pass

    if reply: await message.channel.send(msg)

@client.event
async def time_tracker(send_to_channel, tourney_notify_times, reaction_notify_times):
    past_notification_times_today = []
    active_notification_local = active_notification

    while True:
        cur_time_hhmm = datetime.now().strftime('%H:%M')

        # check time to make tourney notification
        if cur_time_hhmm[:2] == '17' or cur_time_hhmm in tourney_notify_times and cur_time_hhmm not in past_notification_times_today:
            # time to notify channel
            print('[Tourney notification for %s]' % cur_time_hhmm)
            past_notification_times_today.append(cur_time_hhmm)

            # msg = await send_to_channel.send('There is an upcoming tournament at **%s**' % (tourney_times[cur_time_hhmm]))
            # print(tourney_notify_times['23:30'])
            msg = await send_to_channel.send(tourney_announcement_text(tourney_notify_times['23:30'])) # cur_time_hhmm
            active_notification_local.message_id = msg.id
            await msg.add_reaction('<:Bronze1_rank_icon:853469916614885397>')
            await msg.add_reaction('<:Silver1_rank_icon:853469917219258418>')
            # await msg.add_reaction('<:Gold1_rank_icon:853469917432381450>')
            # await msg.add_reaction('<:Platinum1_rank_icon:853469917385588766>')
            # await msg.add_reaction('<:Diamond1_rank_icon:853469917189767191>')
            # await msg.add_reaction('<:Champion1_rank_icon:853469916928671781>')
            # await msg.add_reaction('<:Grand_champion1_rank_icon:853469917197893702>')
            # await msg.add_reaction('<:Supersonic_Legend_rank_icon:853469921589198879>')

            cache_msg = discord.utils.get(client.cached_messages, id=msg.id)
            # print(cache_msg.reactions)

        # check time to make reactions / tourney teams notification
        if cur_time_hhmm[:2] == '16' or cur_time_hhmm in reaction_notify_times and cur_time_hhmm not in past_notification_times_today:
            # time to notify channel
            print('[Reactions notification for %s]' % cur_time_hhmm)
            past_notification_times_today.append(cur_time_hhmm)

        # check time to clear daily notification times
        if cur_time_hhmm == '00:15':
            past_notification_times_today = []
            tourney_times = tourney_times_weekday if is_weekday() else tourney_times_weekend

        await asyncio.sleep(10)

@client.event
async def on_reaction_add(reaction, user):
    # ignore reaction made by bot user
    if user.bot: return

    # check if reaction is attached the original notification message by the tourney bot 
    reaction_emoji_name = str(reaction).split(':')[1]
    if reaction.message.id == active_notification.message_id:
        send_to_channel = client.get_channel(channel_id)

        # add player to registrations
        active_notification.add_player(user_id=user.id, user_name=user.name, reaction_emoji=reaction_emoji_name)
        print(active_notification.registrations)

        # send message to channel
        msg = ":white_check_mark: **%s** is interested in playing the **%s** tournament!" % (user.name, emoji_ranks[reaction_emoji_name].capitalize())
        await send_to_channel.send(msg)

@client.event
async def on_raw_reaction_remove(event):
    # TODO ignore bot's user id

    # check if reaction is attached the original notification message by the tourney bot 
    if event.message_id == active_notification.message_id:
        send_to_channel = client.get_channel(channel_id)

        # remove player from registrations
        active_notification.remove_player(user_id=event.user_id, reaction_emoji=event.emoji.name)
        print(active_notification.registrations)

        # send message to channel
        user = await client.fetch_user(event.user_id)
        msg = ":no_entry_sign: **%s** is no longer interested in playing the **%s** tournament." % (user.name, emoji_ranks[event.emoji.name].capitalize())
        await send_to_channel.send(msg)

def is_weekday():
    return datetime.now().weekday() < 4

def tourney_announcement_text(tourney_time_obj):
    return ":bell: **Announcement!** :bell:" \
        + "\nThere is an upcoming tournament" + (' **(2nd Chance)**' if tourney_time_obj['second_chance'] else '') + " at **%s**." % (tourney_time_obj['time_label']) \
        + "\nIf you would like to participate, react with the tournament rank you are interested in playing." \
        + "\nReactions will close 5 minutes before tournaments begin."

def reactions_annoucement_text(reactions_time_obj):
    return ":bell: **Announcement!** :bell:" \
        + "\nThere are 5 minutes before the tournament at **%s**." % (reactions_time_obj['time_label']) \
        + "\nThe teams have been formed as follows:" \
        + "\n"

def load_api_token(filename):
    with open('api_token.txt', 'r') as f:
        return f.readlines()[0].strip()

# Entry
api_token = load_api_token('api_token.txt')
print('datetime.now(): ' + datetime.now().strftime('%H:%M'))

client.run(api_token)
