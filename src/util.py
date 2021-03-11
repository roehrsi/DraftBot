import json
import regex


def isin(kind: str, arg1: str, arg2: str = None) -> list:
    """Searches for the given arguments in either hero or map pool (depends on 'kind') and returns one unique name for
    each argument.
    Utilizes fuzzy regex for arguments of sufficient length, so typos are sometimes overlooked.
    Don't expect AI miracles here...
    The pool of maps and heroes works with aliases, so some common alternative spellings or shorthands are accepted.
    [~~If the Number of confirmed entries does not equal the arguments given, returns empty.~~ disabled].
    Otherwise return a list of confirmed entries."""

    if kind == "map" or "hero":
        with open("draft.json", "r") as res:
            jfile = json.load(res)
            pool = jfile[kind]
        if arg2:
            args = str.lower("".join(arg1, arg2)) if kind == "map" else (str.lower(arg1), str.lower(arg2))
        else:
            args = [str.lower(arg1)]

        print(f"args: {args}")
        match = []
        # iterate over aliases for pool elements and try to regex match to arguments
        for arg in args:
            # pattern fuzz depends on argument length. floordiv 4 seems like a good baseline for this...
            fuzz = len(arg) // 4
            pattern = r"({0}){{e<={1}}}".format(arg, fuzz)
            for entry in pool:
                for alias in entry["alias"]:
                    # add entry, if any aliases match the argument
                    if regex.search(pattern, alias, regex.IGNORECASE):
                        match.append(entry["name"]) if isinstance(entry["name"], str) else match.extend(entry["name"])
                        break
        # assert at most 2 results.
        print(f"final match: {match}")
        if len(match) > len(args):
            if match[:2] == ["Cho", "Gall"]:
                return match[:2]
            else:
                result = [m for m in match if str.lower(m) in args]
                print(f"result: {result}")
                return result

        else:
            return match
