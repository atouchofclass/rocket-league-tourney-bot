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
        self.leftover_registrants = {
            'bronze': [],
            'silver': [],
            'gold': [],
            'platinum': [],
            'diamond': [],
            'champion': [],
            'grand_champion': [],
            'ssl': []
        }
        self.have_teams = set()
        self.message_id = ''
        self.accepting_registrations = True

    # Add a player to the ranked registration list
    def add_player(self, reaction_emoji, user_id, user_name):
        if reaction_emoji in emoji_ranks:
            player = Player(user_id, user_name)
            self.registrations[emoji_ranks[reaction_emoji]['id']].append(player)

    # Remove a player from the ranked registration list and return it
    def remove_player(self, user_id, reaction_emoji):
        if reaction_emoji in emoji_ranks:
            for player in self.registrations[emoji_ranks[reaction_emoji]['id']]:
                if player.user_id == user_id:
                    removed_player = player
                    self.registrations[emoji_ranks[reaction_emoji]['id']].remove(player)
                    return removed_player

    # Create teams from registrations
    def create_teams(self):
        # take first multiple of 3 & shuffle players per team
        for rank in reversed(list(self.registrations.keys())):
            # filter by players who do not yet have a team
            filtered_registrations = list(filter(lambda player: player.user_id not in self.have_teams, self.registrations[rank]))
            reg_count = len(filtered_registrations)

            # Make random teams out of multiple of 3 players per rank
            if reg_count >= 3:
                top_multiple_of_3 = reg_count - (reg_count % 3)
                current_rank_players = filtered_registrations[:top_multiple_of_3]
                for player in current_rank_players:
                    self.have_teams.add(player.user_id)
                random.shuffle(current_rank_players)
                while len(current_rank_players) > 0:
                    self.teams[rank].append([current_rank_players.pop(), current_rank_players.pop(), current_rank_players.pop()])

        # identify leftover players & add to leftover registrants
        for rank in self.registrations:
            reg_count = len(self.registrations[rank])

            if reg_count == 1:
                if not self.registrations[rank][0].user_id in self.have_teams:
                    self.leftover_registrants[rank].append(self.registrations[rank][0])
            elif reg_count == 2:
                if not self.registrations[rank][0].user_id in self.have_teams:
                    self.leftover_registrants[rank].append(self.registrations[rank][0])
                if not self.registrations[rank][1].user_id in self.have_teams:
                    self.leftover_registrants[rank].append(self.registrations[rank][1])
            elif reg_count >= 3:
                len_mod_3 = reg_count % 3

                if len_mod_3 == 2:
                    if not self.registrations[rank][reg_count - 2].user_id in self.have_teams:
                        self.leftover_registrants[rank].append(self.registrations[rank][reg_count - 2])
                    if not self.registrations[rank][reg_count - 1].user_id in self.have_teams:
                        self.leftover_registrants[rank].append(self.registrations[rank][reg_count - 1])
                elif len_mod_3 == 1:
                    if not self.registrations[rank][reg_count - 1].user_id in self.have_teams:
                        self.leftover_registrants[rank].append(self.registrations[rank][reg_count - 1])

    def teams_count(self):
        teams_count = 0
        for rank in self.teams:
            teams_count += len(self.teams[rank])
        return teams_count

    def there_are_leftover_registrants(self):
        for rank in self.leftover_registrants:
            if len(self.leftover_registrants[rank]) > 0: return True

    def test_fill_registrations(self):
        self.registrations['bronze'].append('Player A')
        self.registrations['bronze'].append('Player B')
        self.registrations['bronze'].append('Player C')
        self.registrations['bronze'].append('Player D')

        self.registrations['silver'].append('Player A')
        self.registrations['silver'].append('Player D')

        self.registrations['gold'].append('Player B')
        self.registrations['gold'].append('Player A')
        self.registrations['gold'].append('Player D')
        self.registrations['gold'].append('Player E')
        self.registrations['gold'].append('Player F')
        self.registrations['gold'].append('Player G')
        self.registrations['gold'].append('Player I') # should not be in a team

        self.registrations['diamond'].append('Player E')
        self.registrations['diamond'].append('Player G')
        self.registrations['diamond'].append('Player H')

    def test_add_reg(self):
        self.registrations['bronze'].append(Player(user_id=0, user_name='TestPlayerA'))
        self.registrations['ssl'].append(Player(user_id=1, user_name='TestPlayerB'))
