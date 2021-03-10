SECOND_MAP_BANS = 0
FIRST_MAP_BANS = 1
MAP_PICK = 2
FIRST_HERO_BANS = 3
SECOND_HERO_BANS = 4
FIRST_HERO_PICKS = 5
SECOND_HERO_PICKS = 6


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
    """The Draft instance that will be used to keep track of the active draft"""

    def __init__(self, team_first=None, team_second=None, stage_num=0, mb_num: int = 2, tm_num: int = 5):
        self.stage_num = 0
        self.team_first = team_first
        self.team_second = team_second
        self.num_map_bans = mb_num if mb_num in range(0, 8) else 2
        self.num_team_members = tm_num if tm_num in range(1, 6) else 5
        # init stages
        self.SECOND_MAP_BANS = [*range(0, mb_num * 2, 2)]
        self.FIRST_MAP_BANS = [*range(1, mb_num * 2, 2)]
        self.MAP_PICK = self.num_map_bans * 2
        self.FIRST_HERO_BANS = [*range(self.MAP_PICK, self.MAP_PICK + 4, 2)]
        self.SECOND_HERO_BANS = [*range(self.MAP_PICK + 1, self.MAP_PICK + 5, 2)]
        self.FIRST_PICK = self.SECOND_HERO_BANS + 1
        if self.num_team_members == 5:
            self.FIRST_HERO_PICKS = [self.FIRST_PICK, self.FIRST_PICK + 3, self.FIRST_PICK + 4, self.FIRST_PICK + 9,
                                     self.FIRST_PICK + 10]
            self.SECOND_HERO_PICKS = [self.FIRST_PICK + 1, self.FIRST_PICK + 2, self.FIRST_PICK + 7,
                                      self.FIRST_PICK + 8, self.FIRST_PICK + 11]
            self.SECOND_HERO_BANS = self.SECOND_HERO_BANS + [self.FIRST_PICK + 5]
            self.FIRST_HERO_BANS = self.FIRST_HERO_BANS + [self.FIRST_PICK + 6]
        elif self.num_team_members == 4:
            pass
        elif self.num_team_members == 3:
            self.FIRST_HERO_PICKS = [self.FIRST_PICK, self.FIRST_PICK + 5, self.FIRST_PICK + 6]
            self.SECOND_HERO_PICKS = [self.FIRST_PICK + 1, self.FIRST_PICK + 2, self.FIRST_PICK + 7]
            self.SECOND_HERO_BANS = self.SECOND_HERO_BANS + [self.FIRST_PICK + 3]
            self.FIRST_HERO_BANS = self.FIRST_HERO_BANS + [self.FIRST_PICK + 4]
        elif self.num_team_members == 2:
            pass
        elif self.num_team_members == 1:
            self.FIRST_HERO_PICKS = self.FIRST_PICK
            self.SECOND_HERO_PICKS = self.FIRST_PICK + 1

        # init teams
        if team_first is None:
            self.team_first = Team("", [], "", [], [])
        if team_second is None:
            self.team_second = Team("", [], "", [], [])

    def set_num_map_bans(self, num: int):
        self.num_map_bans = num

    def set_num_team_members(self, num: int):
        self.num_team_members = num

    def turn(self) -> int:
        """This will return the stage that is currently happening."""
        if self.stage_num in self.FIRST_HERO_PICKS:
            return FIRST_HERO_PICKS
        elif self.stage_num in self.SECOND_HERO_PICKS:
            return SECOND_HERO_PICKS
        elif self.stage_num in self.FIRST_HERO_BANS:
            return FIRST_HERO_BANS
        elif self.stage_num in self.SECOND_HERO_BANS:
            return SECOND_HERO_BANS
        elif self.stage_num in self.MAP_PICK:
            return MAP_PICK
        elif self.stage_num in self.FIRST_MAP_BANS:
            return FIRST_MAP_BANS
        elif self.stage_num in self.SECOND_MAP_BANS:
            return SECOND_MAP_BANS

    def lock(self, picks):
        """lock in the pick or ban into the current draft"""
        print(f"stage: {self.stage_num}")
        # ban maps
        if self.turn() == SECOND_MAP_BANS:
            self.team_second.map_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.turn() == FIRST_MAP_BANS:
            self.team_first.map_bans.append((picks[0]))
            self.stage_num += 1
            return
        # pick map
        elif self.turn() == MAP_PICK:
            self.team_second.map_pick = picks[0]
            self.stage_num += 1
            return
        # ban heroes
        elif self.turn() == FIRST_HERO_BANS:
            self.team_first.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.turn() == SECOND_HERO_BANS:
            self.team_second.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        # pick heroes
        elif self.turn() == FIRST_HERO_PICKS:
            if self.stage_num in self.FIRST_PICK:
                self.team_first.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_first.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return
        elif self.turn() == SECOND_HERO_PICKS:
            if self.stage_num in self.SECOND_HERO_PICKS[-1]:
                self.team_second.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_second.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return
