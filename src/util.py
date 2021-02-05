import json
import re


def isin(kind: str, arg1, arg2=None) -> list:
    if kind == "maps" or "heroes":
        with open("draft.json", "r") as res:
            jfile = json.load(res)
            entries = jfile[kind]

            if arg2:
                args = [arg1, arg2]
            else:
                args = [arg1]

            print(f"args: {args}")

            match = []
            for arg in args:
                print(f"arg: {arg}")
                # fuzz = len(arg) // 4
                # pattern = "(?b)({0}){{e<={1}}}".format(arg, fuzz)
                pattern = r"{0}".format(arg)
                for entry in entries:
                    if re.search(pattern, entry, re.IGNORECASE):
                        match.append(entry)
            print(f"match: {match}")
            return match
