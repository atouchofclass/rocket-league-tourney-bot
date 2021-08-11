'''
    Rocket League Tourney Bot v0.0.1 (2021.08.02.0)
    A simple Discord bot for notifying users about upcoming Rocket League tournaments
    Copyright (c) 2021 atouchofclass
'''

from datetime import datetime
import discord
from discord.ext import tasks

from tourney_times import tourney_notify_times_weekday, reaction_notify_times_weekday, \
    tourney_notify_times_weekend, reaction_notify_times_weekend
from active_tourney_notification import ActiveTourneyNotification
from ranks import emoji_ranks, rank_emojis

channel_id = 874839079995445278
client_user_id = 871218479435489281
time_test = {'00:14': '6:00 PM EST', '23:52': '9:00 PM EST', '23:52': '12:00 AM EST'}
channel = None

active_notification = None

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(channel_id)

    tourney_notify_times = tourney_notify_times_weekday if is_weekday() else tourney_notify_times_weekend
    reaction_notify_times = reaction_notify_times_weekday if is_weekday() else reaction_notify_times_weekend

    # client.loop.create_task(time_tracker(channel, tourney_notify_times, reaction_notify_times))
    time_tracker.start(channel, tourney_notify_times, reaction_notify_times)

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

# @client.event
@tasks.loop(seconds=10)
async def time_tracker(send_to_channel, tourney_notify_times, reaction_notify_times):
    global active_notification
    past_notification_times_today = []
    notify = True
    notify_2 = True

    # while True:
    cur_time_hhmm = datetime.now().strftime('%H:%M')

    # check time to make tourney notification
    if (notify and cur_time_hhmm == '22:49') or cur_time_hhmm in tourney_notify_times and cur_time_hhmm not in past_notification_times_today:
        print('here2')
        active_notification = ActiveTourneyNotification()
        
        # time to notify channel
        print('[%s] Tourney notification' % cur_time_hhmm)
        past_notification_times_today.append(cur_time_hhmm)
        notify = False

        # msg = await send_to_channel.send('There is an upcoming tournament at **%s**' % (tourney_times[cur_time_hhmm]))
        # print(tourney_notify_times['23:30'])
        msg = await send_to_channel.send(tourney_announcement_text(tourney_notify_times['23:30'])) # cur_time_hhmm
        active_notification.message_id = msg.id
        await msg.add_reaction('<:Bronze1_rank_icon:853469916614885397>')
        await msg.add_reaction('<:Silver1_rank_icon:853469917219258418>')
        await msg.add_reaction('<:Gold1_rank_icon:853469917432381450>')
        await msg.add_reaction('<:Platinum1_rank_icon:853469917385588766>')
        await msg.add_reaction('<:Diamond1_rank_icon:853469917189767191>')
        await msg.add_reaction('<:Champion1_rank_icon:853469916928671781>')
        await msg.add_reaction('<:Grand_champion1_rank_icon:853469917197893702>')
        await msg.add_reaction('<:Supersonic_Legend_rank_icon:853469921589198879>')

        # cache_msg = discord.utils.get(client.cached_messages, id=msg.id)
        # print(cache_msg.reactions)

    # check time to make reactions / tourney teams notification
    if (notify_2 and cur_time_hhmm == '22:29') or cur_time_hhmm in reaction_notify_times and cur_time_hhmm not in past_notification_times_today:
        # time to notify channel
        print('[%s] Reactions notification' % cur_time_hhmm)
        past_notification_times_today.append(cur_time_hhmm)
        active_notification.accepting_registrations = False

        notify_2 = False

        # active_notification.test_fill_registrants()
        # active_notification.test_add_reg()
        active_notification.create_teams()

        msg = await send_to_channel.send(reactions_annoucement_text(reaction_notify_times['23:55'])) # cur_time_hhmm
        if active_notification.there_are_leftover_registrants():
            await send_to_channel.send(leftover_registrants_announcement_text())

    # check time to clear daily notification times
    if cur_time_hhmm == '22:28':
        print('[%s] Clear daily data and update tourney times' % cur_time_hhmm)
        past_notification_times_today = []
        tourney_notify_times = tourney_notify_times_weekday if is_weekday() else tourney_notify_times_weekend
        reaction_notify_times = reaction_notify_times_weekday if is_weekday() else reaction_notify_times_weekend

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
        
        send_to_channel = client.get_channel(channel_id)

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
    if event.user_id == client_user_id: return

    # ignore if not accepting registrations
    if not active_notification.accepting_registrations: return

    # ignore extraneous emojis
    if event.emoji.name not in emoji_ranks: return
    
    # check if reaction is attached the original notification message by the tourney bot 
    if event.message_id == active_notification.message_id:
        send_to_channel = client.get_channel(channel_id)

        # remove player from registrations
        removed_player = active_notification.remove_player(user_id=event.user_id, reaction_emoji=event.emoji.name)

        # send message to channel
        msg = ":no_entry_sign: **%s** is no longer interested in playing the **%s** tournament." % (removed_player.user_name, emoji_ranks[event.emoji.name]['label'])
        await send_to_channel.send(msg)

def is_weekday():
    return datetime.now().weekday() < 4

# Generate tourney announcement text
def tourney_announcement_text(tourney_time_obj):
    return ":bell: __**Announcement!**__ :bell:" \
        + "\nThere is an upcoming tournament" + (' **(2nd Chance)**' if tourney_time_obj['second_chance'] else '') + " at **%s**." % (tourney_time_obj['time_label']) \
        + "\nIf you would like to participate, react with the tournament rank you are interested in playing." \
        + "\nReactions will close 5 minutes before tournaments begin."

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
            msg += "\n:warning: **%s** is looking for teammates for the **%s** tournament!" % \
                (active_notification.leftover_registrants[rank][0].user_name,
                rank_emojis[rank]['label'])

    return msg

def mention(user_id):
    return '<@!%s>' % (user_id)

def load_api_token(filename):
    with open('api_token.txt', 'r') as f:
        return f.readlines()[0].strip()

# Entry
api_token = load_api_token('api_token.txt')
print('datetime.now(): ' + datetime.now().strftime('%H:%M'))

client.run(api_token)
