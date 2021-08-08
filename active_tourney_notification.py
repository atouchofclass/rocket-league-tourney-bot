from player import Player

class ActiveTourneyNotification:

    emoji_ranks = {
        'Bronze1_rank_icon': 'bronze',
        'Silver1_rank_icon': 'silver'
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
