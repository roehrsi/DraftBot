SECOND_MAP_BANS = [0, 2]
FIRST_MAP_BANS = [1, 3]
SECOND_MAP_PICK = [4]
FIRST_HERO_BANS = [5, 7, 15]
SECOND_HERO_BANS = [6, 8, 14]
FIRST_HERO_PICKS = [9, 12, 13, 18, 19]
SECOND_HERO_PICKS = [10, 11, 16, 17, 20]
FIRST_PICK = [9]
LAST_PICK = [20]


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

    def turn(self) -> int:
        """This will return the Team that is currently expected to ban or pick.
        Returns 1 for the first pick team and 0 for the map pick team"""
        if self.stage_num in (FIRST_HERO_PICKS + FIRST_HERO_BANS + FIRST_MAP_BANS):
            return 1
        else:
            return 0

    def lock(self, picks):
        """lock in the pick or ban into the current draft"""
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
        elif self.stage_num in SECOND_MAP_PICK:
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
            if self.stage_num in FIRST_PICK:
                self.team_first.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_first.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return
        elif self.stage_num in SECOND_HERO_PICKS:
            if self.stage_num in LAST_PICK:
                self.team_second.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_second.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return
