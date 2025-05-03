#!/bin/python
import sys
import json as json_parser
import argparse
import unittest
from argparse import Namespace, ArgumentParser

# I can't lru cache because of seen
rec(current,seen):
  if(current in seen):
    exception('collision')
  total = 0
  for var in get_vars(current):
    total = max(total,1+rec(var,seen.append(seen))
  return total

sort vars by rec(var,{})

# TODO: it might be a good idea when parsing a json string to ignore white space that occurs in the json to avoid needing to wrap in quotes
def parse_args(args) -> Namespace:
    parser = ArgumentParser(
        prog='easy-env-config',
        description='this is a simple program for setting up enviorment varaibles and alises/abbrevations for users who frequently swtich shells or are trying out a new shell')

    parser.add_argument('-v', '--version', action='store_true', help='prints the current version to the screen')
    parser.add_argument('-t', '--run_test', action='store_true', help="runs programs tests")
    parser.add_argument('-j', '--raw_json', action='store_true',
                        help='makes easy-env-config take raw json text instead of a file')
    parser.add_argument('json', nargs='?',
                        help='if the -j flag is set then a raw json string is expected otherwise a path to a json file is expected')
    return parser.parse_args(args)


def read_file(path) -> str:
    with open('path', 'r') as file:
        return file.read()


def _get_json_string(args: Namespace):
    if args.raw_json:
        json_string = args.json
    else:
        json_string = read_file(args.json)
    return json_string


def get_json(args: Namespace):
    # TODO: strip any comments from the string to support json comments
    return json_parser.loads(_get_json_string(args))


class SortingGraphNode:
    def __init__(self, key: str, vals=None):
        if vals is None:
            vals = []
        self.vals = vals
        self.key = key


class SortingGraph:
    def __init__(self):
        self.keys = {}
        self.vals = {}

    def add_entry(self, key, val):
        pass


def sort_aliases(aliases_map):
    pass


def sort_enviorment_variables(var_map):
    pass


# TODO: figure out how to break apart sub commands in alieses or don't support until v2 things that could spearete a command, | & > ; ' ' or always wrap in quotes, this needs to be done for handling aliases that depend on each other

class Shell:
    def __init__(self):
        self.env_variables = {}
        self.path = None
        self.aliases = {}

    def add_abbr(self, key, val):
        self.add_alias(key, val)

    def add_alias(self, key, val):
        self.aliases[key] = val

    def aliases_string(self) -> str:
        pass

    def __str__(self):
        pass


class Nu(Shell):
    pass


# TODO for fish writing a alais i can use an equals sign or not but either way if the values have more then one string then I need to use an quotes
class Fish(Shell):
    def __init__(self):
        self.abbrs = {}
        super().__init__()

    def add_abbr(self, key, val):
        self.abbrs[key.trim()] = val.trim()

    def abbr_string(self) -> str:
        out = ''
        for key, val in self.abbrs:
            out += f"abbr {key} '{val}'\n"
        return out


SHELLS = {'nu': Nu(), 'fish': Fish(), 'bash': Shell(), 'zsh': Shell()}


def add_path(self, path):  # TODO iterate current_shells, add to path, verify path exists first
    for _, val in self.current_shells:
        val.paths.add(val)


def process_multi_shell(json):
    shells: [Shell] = [SHELLS[shell] for shell in json['shells']]
    for key, val in json['aliases']:
        for shell in shells:
            shell.add_alias(key, val)


def process_shell(json):
    pass


def process_json(json):
    if 'multi_shells' in json_map:
        multi_shells = json_map['multi_shells']
        for multi_shell in multi_shells:
            process_multi_shell(multi_shell)
    for key, val in SHELLS:
        if key in json_map:
            process_shell(val)


class TestRunner(unittest.TestCase):
    def test_read_json1(self):
        test_args = parse_args(['-j', '{}'])
        json = get_json(test_args)
        self.assertEqual(json, {})

    def test_read_json2(self):
        test_args = parse_args(['-j', '{"Hello":"there","json":"is scary","Especially":"when","writing":"test"}'])
        json = get_json(test_args)
        self.assertEqual(json, {"Hello": "there", "json": "is scary", "Especially": "when", "writing": "test"})


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])  # argv[0] is the program itself, even if run directly as an executable
    display_version = args.version
    run_test = args.run_test
    if display_version:
        print('v0.0')
        exit(0)
    if run_test:
        base_name = sys.argv[0]
        unittest.main(argv=[
            base_name])  # needs basename, but if I don't explictly pass argv it will try to parse all args passed to program
        # runnig the test automatically exits the program
    json_map = get_json(args)
    process_json(json_map)
