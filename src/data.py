from typing import List

from src import dicts

SECOND_MAP_BANS = 0
FIRST_MAP_BANS = 1
MAP_PICK = 2
FIRST_HERO_BANS = 3
SECOND_HERO_BANS = 4
FIRST_HERO_PICKS = 5
FIRST_PICK = 6
SECOND_HERO_PICKS = 7
LAST_PICK = 8
FIN = 9


class Team:
    """The team data is stored here.
    Contains bans, picks, captain name"""

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

    def __init__(self, team_first: Team = None, team_second: Team = None, stage_num: int = 0, mb_num: int = 2,
                 tm_num: int = 5):
        self.stage_num = stage_num
        self.team_first = team_first
        self.team_second = team_second
        self.num_map_bans = mb_num if mb_num in range(0, 8) else 2
        self.num_team_members = tm_num if tm_num in range(1, 6) else 5
        # init stages
        # map bans are alternating
        self.SECOND_MAP_BANS = [*range(0, mb_num * 2, 2)]
        self.FIRST_MAP_BANS = [*range(1, mb_num * 2, 2)]
        # map pick comes after map bans
        self.MAP_PICK = self.num_map_bans * 2
        # 2 bans each after map pick
        self.FIRST_HERO_BANS = [*range(self.MAP_PICK + 1, self.MAP_PICK + 5, 2)]
        self.SECOND_HERO_BANS = [*range(self.MAP_PICK + 2, self.MAP_PICK + 6, 2)]
        # first pick comes after last ban. basis for all other picks
        self.FIRST_PICK = self.SECOND_HERO_BANS[-1] + 1
        if self.num_team_members == 5:
            self.FIRST_HERO_PICKS = [self.FIRST_PICK, self.FIRST_PICK + 3, self.FIRST_PICK + 4, self.FIRST_PICK + 9,
                                     self.FIRST_PICK + 10]
            self.SECOND_HERO_PICKS = [self.FIRST_PICK + 1, self.FIRST_PICK + 2, self.FIRST_PICK + 7,
                                      self.FIRST_PICK + 8, self.FIRST_PICK + 11]
            self.SECOND_HERO_BANS = self.SECOND_HERO_BANS + [self.FIRST_PICK + 5]
            self.FIRST_HERO_BANS = self.FIRST_HERO_BANS + [self.FIRST_PICK + 6]
            self.LAST_PICK = self.SECOND_HERO_PICKS[-1]
        elif self.num_team_members == 4:
            pass
        elif self.num_team_members == 3:
            self.FIRST_HERO_PICKS = [self.FIRST_PICK, self.FIRST_PICK + 5, self.FIRST_PICK + 6]
            self.SECOND_HERO_PICKS = [self.FIRST_PICK + 1, self.FIRST_PICK + 2, self.FIRST_PICK + 7]
            self.SECOND_HERO_BANS = self.SECOND_HERO_BANS + [self.FIRST_PICK + 3]
            self.FIRST_HERO_BANS = self.FIRST_HERO_BANS + [self.FIRST_PICK + 4]
            self.LAST_PICK = self.SECOND_HERO_PICKS[-1]
        elif self.num_team_members == 2:
            pass
        elif self.num_team_members == 1:
            self.FIRST_HERO_PICKS = self.FIRST_PICK
            self.SECOND_HERO_PICKS = self.LAST_PICK = self.FIRST_PICK + 1
        # init teams if empty
        if team_first is None:
            self.team_first = Team("", [], "", [], [])
        if team_second is None:
            self.team_second = Team("", [], "", [], [])

    def stage(self) -> int:
        """This will return the stage that is currently happening.
        :returns: the Stage constant corresponding to the current draft stage"""
        if self.stage_num in self.FIRST_HERO_PICKS:
            return FIRST_PICK if self.stage_num == self.FIRST_PICK else FIRST_HERO_PICKS
        elif self.stage_num in self.SECOND_HERO_PICKS:
            return LAST_PICK if self.stage_num == self.LAST_PICK else SECOND_HERO_PICKS
        elif self.stage_num in self.FIRST_HERO_BANS:
            return FIRST_HERO_BANS
        elif self.stage_num in self.SECOND_HERO_BANS:
            return SECOND_HERO_BANS
        elif self.stage_num == self.MAP_PICK:
            return MAP_PICK
        elif self.stage_num in self.FIRST_MAP_BANS:
            return FIRST_MAP_BANS
        elif self.stage_num in self.SECOND_MAP_BANS:
            return SECOND_MAP_BANS
        else:
            return FIN

    def turn(self) -> int:
        """Return which teams turn it is.
        :returns: 0 for first team; 1 for second team"""
        if self.stage() in [FIRST_MAP_BANS, FIRST_HERO_BANS, FIRST_HERO_PICKS]:
            return 0
        elif self.stage() in [SECOND_MAP_BANS, SECOND_HERO_BANS, SECOND_HERO_PICKS, MAP_PICK]:
            return 1

    def lock(self, picks: List[str]) -> None:
        """lock in the pick or ban into the current draft
        :param picks: the tuple with bans or picks"""
        print(f"stage: {self.stage_num}")
        # ban maps
        if self.stage() == SECOND_MAP_BANS:
            self.team_second.map_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.stage() == FIRST_MAP_BANS:
            self.team_first.map_bans.append((picks[0]))
            self.stage_num += 1
            return
        # pick map
        elif self.stage() == MAP_PICK:
            self.team_second.map_pick = picks[0]
            self.stage_num += 1
            return
        # ban heroes
        elif self.stage() == FIRST_HERO_BANS:
            self.team_first.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        elif self.stage() == SECOND_HERO_BANS:
            self.team_second.hero_bans.append(picks[0])
            self.stage_num += 1
            return
        # pick heroes
        elif self.stage() == FIRST_HERO_PICKS:
            if self.stage() == FIRST_PICK:
                self.team_first.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_first.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return
        elif self.stage() == SECOND_HERO_PICKS:
            if self.stage() == LAST_PICK:
                self.team_second.hero_picks.append(picks[0])
                self.stage_num += 1
            else:
                self.team_second.hero_picks.extend(picks)
                self.stage_num += len(picks)
            return

    def status(self) -> str:
        return dicts.draft_status[self.stage()].format(
            self.team_first.captain if self.turn() else self.team_second.captain)
