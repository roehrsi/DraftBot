import json
import regex



def isin(arg1, arg2: str) -> list:
    if arg2 == "maps" or "heroes":
        with open("draft.json", "r") as res:
            jfile = json.load(res)
            entries = jfile[arg2]
            match = []
            arg1 = [arg1]
            print(f"entries: {entries}")
            print(f"arg1: {arg1}")
            for arg in arg1:
                fuzz = len(arg)//4
                print(f"fuzz: {fuzz}")
                pattern = "(?b)({0}){{e<={1}}}".format(arg, fuzz)
                for entry in entries:
                    if regex.search(pattern, entry, regex.IGNORECASE):
                        match.append(entry)
            print(f"match: {match}")
            return match
