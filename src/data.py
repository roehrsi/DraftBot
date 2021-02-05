class Team:
    def __init__(self, captain="", map_bans=None, map_pick=None, hero_bans=None, hero_picks=None):
        self.captain = captain
        self.map_bans = map_bans
        self.map_pick = map_pick
        self.hero_bans = hero_bans
        self.hero_picks = hero_picks


class Draft:
    def __init__(self, team_first=None, team_second=None, stage_num=0):
        self.stage_num = stage_num
        self.teamFirst = team_first
        self.teamSecond = team_second
        self.second_map_bans = [0, 2]
        self.first_map_bans = [1, 3]
        self.second_map_pick = 4
        self.first_hero_bans = [5, 7, 15]
        self.second_hero_bans = [6, 8, 14]
        self.first_hero_picks = [9, 12, 13, 18, 19]
        self.second_hero_picks = [10, 11, 16, 17, 20]
