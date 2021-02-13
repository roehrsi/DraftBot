SECOND_MAP_BANS = [0, 2]
FIRST_MAP_BANS = [1, 3]
SECOND_MAP_PICK = 4
FIRST_HERO_BANS = [5, 7, 15]
SECOND_HERO_BANS = [6, 8, 14]
FIRST_HERO_PICKS = [9, 12, 13, 18, 19]
SECOND_HERO_PICKS = [10, 11, 16, 17, 20]


class Team:
    def __init__(self, captain="", map_bans=None, map_pick="-", hero_bans=None, hero_picks=None):
        self.captain = captain
        self.map_bans = map_bans
        self.map_pick = map_pick
        self.hero_bans = hero_bans
        self.hero_picks = hero_picks
        if map_bans is None:
            self.map_bans = []
        if hero_bans is None:
            self.hero_bans = []
        if hero_picks is None:
            self.hero_picks = []

    def __repr__(self):
        s = ("Map Bans: \n"
             "``` " + ", ".join(self.map_bans) + "```" +
             "**Map Pick**: \n"
             "``` " + self.map_pick + "```" +
             "**Hero Bans**: \n"
             "``` " + "\n ".join(self.hero_bans) + "```" +
             "**Hero Picks**: \n" +
             "``` " + "\n ".join(self.hero_picks) + "```")
        return s


class Draft:
    def __init__(self, team_first=None, team_second=None, stage_num=0):
        self.stage_num = stage_num
        self.team_first = team_first
        self.team_second = team_second
        if team_first is None:
            self.team_first = Team("", [], "", [], [])
        if team_second is None:
            self.team_second = Team("", [], "", [], [])

    def lock(self, picks):
        print(f"stage: {self.stage_num}")
        # ban maps
        if self.stage_num in SECOND_MAP_BANS:
            self.team_second.map_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.stage_num in FIRST_MAP_BANS:
            self.team_first.map_bans.append((picks[0]))
            self.stage_num += 1
            return
        # pick map
        elif self.stage_num == SECOND_MAP_PICK:
            self.team_second.map_pick = picks[0]
            self.stage_num += 1
            return
        # ban heroes
        elif self.stage_num in FIRST_HERO_BANS:
            self.team_first.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.stage_num in SECOND_HERO_BANS:
            self.team_second.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        # pick heroes
        elif self.stage_num in FIRST_HERO_PICKS:
            for pick in picks:
                self.team_first.hero_picks.append(pick)
                self.stage_num += 1
            return
        elif self.stage_num in SECOND_HERO_PICKS:
            for pick in picks:
                self.team_second.hero_picks.append(pick)
                self.stage_num += 1
            return
