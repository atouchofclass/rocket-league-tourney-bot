from player import Player

class ActiveTourneyNotification:

    emoji_ranks = {
        'Bronze1_rank_icon': 'bronze',
        'Silver1_rank_icon': 'silver',
        'Gold1_rank_icon': 'gold',
        'Platinum1_rank_icon': 'platinum',
        'Diamond1_rank_icon': 'diamond',
        'Champion1_rank_icon': 'champion',
        'Grand_champion1_rank_icon': 'grand_champion',
        'Supersonic_Legend_rank_icon': 'ssl'
    }
    ranks = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'champion', 'grand_champion', 'ssl']

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
        if reaction_emoji in self.emoji_ranks:
            player = Player(user_id, user_name)
            self.registrations[self.emoji_ranks[reaction_emoji]].append(player)

    # Remove a player from the ranked registration list
    def remove_player(self, user_id, reaction_emoji):
        if reaction_emoji in self.emoji_ranks:
            for player in self.registrations[self.emoji_ranks[reaction_emoji]]:
                if player.user_id == user_id:
                    self.registrations[self.emoji_ranks[reaction_emoji]].remove(player)
                    return

    # Create teams
    def create_teams(self):
        # take first multiple of 3 & shuffle players per team
        pass
