import json
import regex


def isin(kind: str, arg1, arg2=None) -> list:
    if kind == "map" or "hero":
        with open("draft.json", "r") as res:
            jfile = json.load(res)
            entries = jfile[kind]

        if arg2:
            args = "".join(arg1, arg2) if kind == "map" else (arg1, arg2)
        else:
            args = [arg1]

        print(f"args: {args}")
        match=[]
        result = []
        for arg in args:
            fuzz = len(arg) // 4
            pattern = r"({0}){{e<={1}}}".format(arg, fuzz)
            # pattern = r"{0}".format(arg)
            match.extend([entry for entry in entries if regex.search(pattern, entry, regex.BESTMATCH | regex.IGNORECASE)])
            print(f"match: {match}")
            print(len(match))
        if len(match) > len(args):
            for arg in args:
                result.extend([m for m in match if regex.search(arg, m, regex.BESTMATCH | regex.IGNORECASE)])
        else:
            result = match
        print(f"final match: {result}")
        return result
