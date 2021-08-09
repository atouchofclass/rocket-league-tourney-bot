import random

from ranks import emoji_ranks
from player import Player

class ActiveTourneyNotification:

    def __init__(self):
        self.registrations = {
            'bronze': [],
            'silver': [],
            'gold': [],
            'platinum': [],
            'diamond': [],
            'champion': [],
            'grand_champion': [],
            'ssl': []
        }
        self.teams = {
            'bronze': [],
            'silver': [],
            'gold': [],
            'platinum': [],
            'diamond': [],
            'champion': [],
            'grand_champion': [],
            'ssl': []
        }
        self.message_id = ''

    # Add a player to the ranked registration list
    def add_player(self, reaction_emoji, user_id, user_name):
        if reaction_emoji in emoji_ranks:
            player = Player(user_id, user_name)
            self.registrations[emoji_ranks[reaction_emoji]].append(player)

    # Remove a player from the ranked registration list
    def remove_player(self, user_id, reaction_emoji):
        if reaction_emoji in emoji_ranks:
            for player in self.registrations[emoji_ranks[reaction_emoji]]:
                if player.user_id == user_id:
                    self.registrations[emoji_ranks[reaction_emoji]].remove(player)
                    return

    # Create teams from registrations
    def create_teams(self):
        # take first multiple of 3 & shuffle players per team
        for rank in self.registrations:
            if len(self.registrations[rank]) >= 3:
                top_multiple_of_3 = len(self.registrations[rank]) - (len(self.registrations[rank]) % 3)
                current_rank_players = self.registrations[rank][:top_multiple_of_3]
                random.shuffle(current_rank_players)
                while len(current_rank_players) > 0:
                    self.teams[rank].append([current_rank_players.pop(), current_rank_players.pop(), current_rank_players.pop()])
