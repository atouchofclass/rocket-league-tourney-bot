'''
    Rocket League Tourney Bot v0.0.1 (2021.08.02.0)
    A simple Discord bot for notifying users about upcoming Rocket League tournaments
    Copyright (c) 2021 atouchofclass
'''

import asyncio
from datetime import datetime
import discord

from tourney_times import tourney_times_weekday, tourney_times_weekend

channel_id = 871224692177006602
tourney_times_test = {'00:14': '6:00 PM EST', '23:52': '9:00 PM EST', '23:52': '12:00 AM EST'}
channel = None

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    # tourney_times = tourney_times_weekday if is_weekday() else tourney_times_weekend
    tourney_times = tourney_times_test

    client.loop.create_task(time_tracker(channel, tourney_times))

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
async def time_tracker(send_to_channel, tourney_times):
    past_notification_times_today = []

    while True:
        cur_time_hhmm = datetime.now().strftime('%H:%M')

        # check time to make tourney notification
        if cur_time_hhmm in tourney_times and cur_time_hhmm not in past_notification_times_today:
            # time to notify channel
            print('[Tourney notification for %s]' % cur_time_hhmm)
            past_notification_times_today.append(cur_time_hhmm)

            # msg = await send_to_channel.send('There is an upcoming tournament at **%s**' % (tourney_times[cur_time_hhmm]))
            msg = await send_to_channel.send(tourney_announcement_text(tourney_times[cur_time_hhmm]))
            await msg.add_reaction('<:Bronze1_rank_icon:853469916614885397>')
            await msg.add_reaction('<:Silver1_rank_icon:853469917219258418>')
            await msg.add_reaction('<:Gold1_rank_icon:853469917432381450>')
            await msg.add_reaction('<:Platinum1_rank_icon:853469917385588766>')
            await msg.add_reaction('<:Diamond1_rank_icon:853469917189767191>')
            await msg.add_reaction('<:Champion1_rank_icon:853469916928671781>')
            await msg.add_reaction('<:Grand_champion1_rank_icon:853469917197893702>')
            await msg.add_reaction('<:Supersonic_Legend_rank_icon:853469921589198879>')

        # check time to clear daily notification times
        if cur_time_hhmm == '00:00':
            past_notification_times_today = []
            tourney_times = tourney_times_weekday if is_weekday() else tourney_times_weekend

        await asyncio.sleep(10)

def is_weekday():
    return datetime.now().weekday() < 4

def tourney_announcement_text(time_string):
    return '**Announcement!** :robot:' \
        + "\nThere is an upcoming tournament at **%s**." % (time_string) \
        + "\nIf you would like to participate, react with the tournament rank you are interested in playing."

def load_api_token(filename):
    with open('api_token.txt', 'r') as f:
        return f.readlines()[0].strip()

# Entry
api_token = load_api_token('api_token.txt')
print('datetime.now(): ' + datetime.now().strftime('%H:%M'))

client.run(api_token)
