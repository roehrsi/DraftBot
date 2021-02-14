import json
import regex


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

            result = []
            match = []
            for arg in args:
                fuzz = len(arg) // 4
                pattern = r"({0}){{e<={1}}}".format(arg, fuzz)
                # pattern = r"{0}".format(arg)
                for entry in entries:
                    if regex.search(pattern, entry, regex.BESTMATCH | regex.IGNORECASE):
                        match.append(entry)
                        print(f"match: {entry}")
                print(len(match))
                if len(match) > 1:
                    for m in match:
                        if regex.search(arg, m, regex.BESTMATCH | regex.IGNORECASE):
                            result.append(m)
                else:
                    result = match

        print(f"final match: {result}")
        return result
