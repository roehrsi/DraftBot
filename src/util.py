import json
import regex
from math import ceil


def isin(arg1: list, arg2: str) -> str:
    if arg2 == "maps" or "heroes":
        with open("draft.json", "r") as res:
            jfile = json.load(res)
            entries = jfile[arg2]
            match = []
            arg1 = [arg1]
            print(f"entries: {entries}")
            print(f"arg1: {arg1}")
            for arg in arg1:
                pattern = "({0}){{e<={1}}}".format(arg, ceil(len(arg) / 4))
                for entry in entries:
                    if regex.search(pattern, entry, regex.IGNORECASE):
                        match.append(entry)
            print(f"match: {match}")
            return match[0]
