NO_DRAFT = "No draft is currently happening here... But you can change that!\n" \
           "Please start a draft first, by typing ``!draft``.\n"
NO_MATCH = "I couldn't find a {0} with that name. :(\n" \
           "Maybe try again with a more precise name."
GREETING = "Welcome to the draft, {0} \n " \
           "If you want to draft a map, type ``!draft tournament`` to start the coin flip and draft a map.\n " \
           "Otherwise use ``!draft quick [map]`` to skip map draft and pick a map directly, then do the coin flip.\n " \
           "If you want to restart the draft, simply call this base command again to reset all parameters."
REDUNDANT_PICK = "This {0} is already picked. Try something different.",
ILLEGAL_PICK = "You cannot pick a banned {0}."
DRAFT_RESET = "The draft has been reset and deleted."

help_embed = {
    "title": "Hey there!",
    "description": "*honk honk* This is DraftBot. "
                   "He can help you draft the team of your dream in Heroes of the Storm! "
                   "Take a minute to read the command doc below to get started.",
    "color": 0xff8040,
    "author": {"name":"DraftBot"},
    "url": "https://github.com/roehrsi/DraftBot",
    "fields": [
        {"name": "!draft",
         "value": "To start a draft, the **!draft** command will begin a fresh draft for you. "
                  "Use either the **!draft tournament [@Opponent]** command if you want to start with "
                  "flipping a coin for the first pick and drafting a map, "
                  "or **!draft quick [map] [@Opponent]** if you want to pick a map directly "
                  "and move on to the hero draft. "
                  "Only you and your tagged opponent can influence the draft, "
                  "so you are safe from griefers and run-downers ;). "
                  "Nobody can stop you from tagging yourself though...",
         "inline": False},
        {"name": "!ban",
         "value": "The **!ban** command is your one stop shop for banning maps and heroes. "
                  "It takes one argument - the map or hero name - and adds that to the draft."
                  "DraftBot can handle some spelling error and shorthands, "
                  "but try not to be too obscure with your inputs",
         "inline": False},
        {"name": "!pick",
         "value": "The **!pick** command works just like **!ban** for map and hero picks."
                  "For the double pick phases, the **!pick** command also takes two "
                  "arguments.",
         "inline": False},
        {"name": "!draft help",
         "value": "Use the **!draft help** command to display this information.",
         "inline": False},
        {"name": "drafting order",
         "value": "Order adheres to HotS tournament draft standard with **A** as coin toss winner: \n"
                  "Map Bans: **B A B A**\n"
                  "Map Pick: **B**\n"
                  "Hero Bans: **A B A B**\n"
                  "Hero Picks: **A BB AA**\n"
                  "Hero Bans: **B A**\n"
                  "Hero Picks: **BB AA B**",
         "inline": False},

    ],
    "footer": {"text": "GL HF!"}
}
