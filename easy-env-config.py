#!/bin/python
import sys
import unittest
import shutil
import os
import re
from enum import Enum
from argparse import Namespace, ArgumentParser, FileType
# TODO: i need to change how the escaping works for comments and {}
# as it doesnt allow you to type a { after a \
r"""config:documentation

./easyenv -p to print instead of write changes, print target path followed by content
# is for a comment
you can use a backslacsh to escape the pound \#
set_shells(bash, fish, nu)
alias(la,ls -a)
abbr(la,ls -a) creates an abbreviation and falls back to aliases if abbreviations don't exist
set_env(d,frog) sets environment variable
set_motion_mode(vi) parameter can be vi, emacs or normal, not supported by nushell
add_path(path)

to reference env variable in an expression use {VAR_NAME} escape \{ \} if you want to use them

compile_path(shell, path)
"""

CURRENT_VERSION = 'v1.1'


def parse_args(args) -> Namespace:
    parser = ArgumentParser(
        prog='easy-env-config',
        description='this is a simple program for setting up environment variables and alises/abbrevations for users who frequently switch shells or are trying out a new shell')

    parser.add_argument('-v', '--version', action='store_true',
                        help='prints the current version to the screen')
    parser.add_argument('-t', '--run_test',
                        action='store_true', help="runs programs tests")
    parser.add_argument('-p', '--print',
                        action='store_true', help="prints the resulting config on a per shell bases without writing to disk")
    parser.add_argument('file', nargs='?', type=FileType('r'),
                        help='config file')
    return parser.parse_args(args)


def read_file(path) -> str:
    with open(path, 'r') as file:
        lines = file.readlines()
    return lines


def empty(collection):
    return len(collection) == 0


class MotionMode(Enum):
    VI = "vi"
    EMACS = "emacs"
    NORMAL = "normal"


class Shell:
    def __init__(self):
        self.env_variables = {}
        self.config_path = "~/.easy_env_bash"
        self.aliases = {}
        self.abbrs = dict()
        self.motion_mode = MotionMode.NORMAL
        self.paths_to_add = []

    @property
    def shell_name(self):
        return "bash"

    @property
    def updated(self) -> bool:

        fields_to_check = [self.aliases, self.abbrs,
                           self.env_variables, self.paths_to_add]

        return any(not empty(attr) for attr in fields_to_check)

    def reformat_env_variables(self, line: str):
        pattern = r'(?<!\\){([^}]*)}'

        # Use re.sub with a function to substitute the matched content
        result = re.sub(
            pattern, lambda match: self._env_variable_format(match), line)

        # replace escaped curlies
        result = result.replace(r'\{', '{').replace(r'\}', '}')
        return result

    def _env_variable_format(self, match):
        return self.env_variable_format(match.group(1))

    def env_variable_format(self, variable):
        return f'${variable}'

    def add_abbr(self, key, val):
        self.add_alias(key, val)

    def add_path(self, path: str):
        path = self.reformat_env_variables(path)
        self.paths_to_add.append(path)

    def add_alias(self, key, val):
        val = self.reformat_env_variables(val)
        self.aliases[key] = val

    @property
    def emacs_motion_str(self):
        return "set -o emacs"

    @property
    def vi_motion_str(self):
        return "set -o vi"

    @property
    def motion_mode_str(self):
        if self.motion_mode == MotionMode.VI:
            return self.vi_motion_str
        elif self.motion_mode == MotionMode.EMACS:
            return self.emacs_motion_str
        else:
            return ""

    def supports_abbreviations(self):
        return False

    def set_environment_variable(self, key, val):
        val = self.reformat_env_variables(val)
        self.env_variables[key] = val

    def aliases_string(self) -> str:
        out = ""
        for key, val in self.aliases.items():
            out += f'{self.alias_to_string(key, val)}\n'
        return out.removesuffix('\n')

    def alias_to_string(self, key, value):
        if self.alias_needs_quotes(value):
            value = f'"{value}"'
        return f'alias {key}={value}'

    def alias_needs_quotes(self, val: str):
        has_problematic_char = any(c in val for c in ['|', '>', '&'])
        return has_problematic_char and "'" not in val

    def add_paths_string(self):
        out = ""
        for path in self.paths_to_add:
            out += f'{self.add_paths_to_string(path)}\n'
        return out.removesuffix("\n")

    def add_paths_to_string(self, path):
        return f'export PATH="$PATH:{path}"'

    def abbrs_string(self) -> str:
        out = ''
        for key, val in self.abbrs.items():

            if self.alias_needs_quotes(key):
                key = f"'{key}'"

            if self.alias_needs_quotes(val):
                val = f"'{val}'"

            out += f"abbr {key} {val}\n"

        out = out.removesuffix('\n')
        return out

    def env_variable_string(self):
        out = ""
        for key, val in self.env_variables.items():
            if len(val.split(' ')) > 1:
                val = f'"{val}"'
            out += f'export {key}={val}\n'

        return out.removesuffix('\n')

    def comment_string(self, input):
        return f'#{input}'

    def __str__(self):
        out = ""
        motion_mode = self.motion_mode_str
        if len(motion_mode) > 0:
            out += motion_mode
            out += '\n\n'
        if len(self.env_variables) > 0:
            out += self.comment_string("environment variables\n")
            out += self.env_variable_string()
            out += '\n\n'
        if len(self.paths_to_add) > 0:
            out += self.comment_string("update path\n")
            out += self.add_paths_string()
            out += '\n\n'
        if len(self.aliases) > 0:
            out += self.comment_string("aliases\n")
            out += self.aliases_string()
            out += '\n\n'
        if len(self.abbrs) > 0:
            out += self.comment_string("abbreviations\n")
            out += self.abbrs_string()
        return out


class Zsh(Shell):
    def __init__(self):
        super().__init__()
        self.config_path = "~/.easy_env_zsh"

    @property
    def emacs_motion_str(self):
        return "bindkey -e"

    @property
    def vi_motion_str(self):
        return "bindkey -v"

    @property
    def shell_name(self):
        return "zsh"

    def add_paths_to_string(self, path):
        if ' ' in path:
            path = f'"{path}"'
        return f'path+={path}'


class Nu(Shell):

    def alias_to_string(self, key, value):
        problematic_chars = ['|', "&", '>', '<']

        for problem_char in problematic_chars:
            if problem_char in value:
                out = f'def {key} [...args] '
                out += '{'
                out += value
                out += ' ...$args}'
                return out
        return f'alias {key} = {value}'

    @property
    def motion_mode_str(self):
        print("setting motion mode is not supported in nushell do to how it handles global configuration")
        return ""

    def env_variable_format(self, variable):
        return f'$env.{variable}'

    def __init__(self):
        super().__init__()
        self.config_path = "~/.config/nushell/easy_env.nu"

    @property
    def shell_name(self):
        return "nu"

    def env_variable_string(self):
        out = ""
        for key, val in self.env_variables.items():
            line = f'$env.{key} = '
            if not val.startswith('"') and not val.startswith("'"):
                line += '"'
            line += val
            if not val.endswith('"') and not val.endswith("'"):
                line += '"'
            out += f'{line}\n'
        return out.removesuffix('\n')

    def add_paths_to_string(self, path):
        return f'$env.path ++= [{path}]'


# TODO for fish writing a alias i can use an equals sign or not but either way if the values have more then one string then I need to use an quotes
class Fish(Shell):
    def __init__(self):
        super().__init__()
        self.config_path = "~/.config/fish/easy_env.fish"

    @property
    def shell_name(self):
        return "fish"

    @property
    def emacs_motion_str(self):
        return "fish_default_key_bindings"

    @property
    def vi_motion_str(self):
        return "fish_vi_key_bindings"

    def add_abbr(self, key, val):
        val = self.reformat_env_variables(val)
        self.abbrs[key.strip()] = val.strip()

    def add_paths_to_string(self, path):
        if ' ' in path:
            path = f'"{path}"'
        return f'fish_add_path {path}'

    def supports_abbreviations(self):
        return True

    def alias_to_string(self, key, val):
        val = self.reformat_env_variables(val)
        if self.alias_needs_quotes(val):
            val = f'"{val}"'
        return f'alias {key} {val}'

    def env_variable_string(self):
        out = ""
        for key, val in self.env_variables.items():
            out += f'set -gx {key} {val}\n'
        return out.removesuffix('\n')


class ShellSet:
    def __init__(self, current_shells={"nu", "bash", "fish", "zsh"}):
        self.all_shells = {"nu": Nu(), "fish": Fish(),
                           "bash": Shell(), "zsh": Zsh(), }
        self.current_shells = self._get_shells(current_shells)
        self.set_targets(current_shells)

    def __iter__(self):
        return (val for val in self.all_shells.values() if val.updated)

    def add_alias(self, key, value):
        for shell in self.current_shells:
            shell.add_alias(key, value)

    def add_abbr(self, key, value):
        for shell in self.current_shells:
            shell.add_abbr(key, value)

    def set_env_variable(self, key, value):
        for shell in self.current_shells:
            shell.set_environment_variable(key, value)

    def add_path(self, path):
        for shell in self.current_shells:
            shell.add_path(path)

    def set_targets(self, shells):
        self.current_shells = self._get_shells(shells)

    def set_compile_path(self, shell, path):
        self.all_shells[shell].config_path = path

    def set_motion_mode(self, mode):
        for shell in self.current_shells:
            shell.motion_mode = MotionMode(mode)

    def _get_shells(self, shells_as_strings):
        out: set = set()
        for shell in shells_as_strings:
            out.add(self.all_shells[shell])
        return out


def _get_params(command: str) -> tuple:
    start = command.find('(')
    end = command.rfind(')')

    # Ensure both parentheses are found and properly ordered
    if start == -1 or end == -1 or start > end:
        return tuple()

    # Get the substring inside the parentheses
    params_str = command[start + 1:end].strip()

    # Return tuple of parameters, empty string check avoids ['']
    if not params_str:
        return tuple()

    # Split by commas and strip whitespace
    params = tuple(param.strip() for param in params_str.split(','))
    return params


def source(paths, parent_dir=".."):
    to_add = []
    for path in paths:
        expanded_path = os.path.expanduser(path)
        if os.path.isabs(expanded_path):
            abs_path = expanded_path
        else:
            abs_path = os.path.join(parent_dir, path)
        new_lines = read_file(abs_path)
        new_lines = filter_lines_and_handle_sourcing(new_lines, parent_dir)
        to_add.extend(new_lines)
    return to_add


def _execute(command: str, shell_set: ShellSet):
    params = _get_params(command)
    try:
        if command.startswith("alias"):
            shell_set.add_alias(*params)
        elif command.startswith("abbr"):
            shell_set.add_abbr(*params)
        elif command.startswith("set_env"):
            shell_set.set_env_variable(*params)
        elif command.startswith("add_path"):
            shell_set.add_path(*params)
        elif command.startswith("set_shells"):
            shell_set.set_targets([*params])
        elif command.startswith("compile_path"):
            shell_set.set_compile_path(*params)
        elif command.startswith("set_motion_mode"):
            shell_set.set_motion_mode(*params)
        elif command.startswith("source"):
            shell_set.source([*params])
        else:
            print(f'unknown command: {command}')
            exit(1)
    except Exception:
        print(f"command:{command}, invalid parameters: {params}")


shell_to_command = {
    "bash": "bash",
    "zsh": "zsh",
    "fish": "fish",
    "nu": "nu",
    # "cmd": "cmd.exe",
    # "powershell": "powershell.exe",
    # "pwsh": "pwsh",
}


def auto_detect_shells():
    out = []
    for name, command in shell_to_command.items():
        if shutil.which(command):
            out.append(name)
    return out


def process_config(lines, shell_set):
    for line in lines:
        _execute(line, shell_set)


def print_shell_set(shell_set: ShellSet):
    toPrint = ""
    for shell in shell_set:
        toPrint += f'{shell.shell_name}:{shell.config_path}\n'
        toPrint += f'{shell}\n\n'
    print(toPrint.rstrip())


def write_shell_set(shell_set: ShellSet):
    for shell in shell_set:
        config_path = os.path.expanduser(shell.config_path)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        if os.path.exists(config_path) and os.path.isdir(config_path):
            print(f'cannot overrde directory{config_path}')
            exit(1)
        with open(config_path, 'w') as file:
            file.write(str(shell))


def remove_comments(s):
    match = re.search(r'(?<!\\)#', s)
    if match:
        return s[:match.start()]
    else:
        return s


def filter_lines_and_handle_sourcing(lines, parent_dir=".."):
    out = []
    for line in lines:
        line = remove_comments(line)
        line = line.strip()
        line = re.sub(r'\\#', '#', line)
        if line.startswith("source"):
            params = _get_params(line)
            out.extend(source([*params], parent_dir))
        elif line != '':
            out.append(line)
    return out


class TestRunner(unittest.TestCase):
    def test_add_abbr_fish1(self):
        shell = Fish()
        shell.add_abbr("ls", "eza")
        self.assertEqual(shell.abbrs_string(), "abbr ls eza")

    def test_add_abbr_fish2(self):
        shell = Fish()
        shell.add_abbr("ls", "eza")
        shell.add_abbr("sl", "eza")
        shell.add_abbr("sh0", "shutdown now")
        shell.add_abbr("lg", "eza|rg")
        expected = "abbr ls eza\nabbr sl eza\nabbr sh0 shutdown now\nabbr lg 'eza|rg'"
        self.assertEqual(shell.abbrs_string(), expected)

    def test_set_env_fish(self):
        shell = Fish()
        shell.set_environment_variable("dog", "cat")
        shell.set_environment_variable("pig", "cow thing")
        expected = "set -gx dog cat\nset -gx pig cow thing"
        self.assertEqual(shell.env_variable_string(), expected)

    def test_set_env_nu(self):
        shell = Nu()
        shell.set_environment_variable("dog", "cat")
        shell.set_environment_variable("pig", "cow thing")
        expected = '$env.dog = "cat"\n$env.pig = "cow thing"'
        self.assertEqual(shell.env_variable_string(), expected)

    def test_set_env_bash(self):
        # TODO: duplicate code
        shell = Shell()
        shell.set_environment_variable("dog", "cat")
        shell.set_environment_variable("pig", "cow thing")
        expected = 'export dog=cat\nexport pig="cow thing"'
        self.assertEqual(shell.env_variable_string(), expected)

    def test_bash_alias(self):
        shell = Shell()
        shell.add_alias("l", "ls")
        shell.add_alias("la", "ls -a | echo")
        expected = 'alias l=ls\nalias la="ls -a | echo"'
        self.assertEqual(shell.aliases_string(), expected)

    def test_fish_alias(self):
        shell = Fish()
        shell.add_alias("l", "ls")
        shell.add_alias("la", "ls -a | echo")
        expected = 'alias l ls\nalias la "ls -a | echo"'
        self.assertEqual(shell.aliases_string(), expected)

    def test_fish_add_path(self):
        shell = Fish()
        shell.add_path("~/.cargo/bin")
        shell.add_path("~/.nix-profile/bin")
        expected = "fish_add_path ~/.cargo/bin\nfish_add_path ~/.nix-profile/bin"
        self.assertEqual(shell.add_paths_string(), expected)

    def test_zsh_add_path(self):
        shell = Zsh()
        shell.add_path("~/.cargo/bin")
        shell.add_path("~/.nix-profile/bin")
        expected = "path+=~/.cargo/bin\npath+=~/.nix-profile/bin"
        self.assertEqual(shell.add_paths_string(), expected)

    def test_bash_add_path(self):
        shell = Shell()
        p1 = "~/.cargo/bin"
        p2 = "~/.nix-profile/bin"
        shell.add_path(p1)
        shell.add_path(p2)
        expected = f'export PATH="$PATH:{p1}"\nexport PATH="$PATH:{p2}"'
        self.assertEqual(shell.add_paths_string(), expected)

    def test_execute_add_alias(self):
        shells = {'nu', 'fish', 'bash'}
        shell_set = ShellSet(current_shells=shells)
        command = "alias(la,ls -a)"
        _execute(command, shell_set)
        self.assertEqual(len(shell_set.current_shells), 3)
        for shell in shell_set.current_shells:
            self.assertEqual(shell.aliases['la'], 'ls -a')

    def test_execute_add_abbr(self):
        shells = {'nu', 'fish', 'bash'}
        shell_set = ShellSet(current_shells=shells)
        command = "abbr(la,ls -a)"
        _execute(command, shell_set)
        self.assertEqual(len(shell_set.current_shells), 3)
        for shell in shell_set.current_shells:
            if isinstance(shell, Fish):
                self.assertEqual(shell.abbrs['la'], 'ls -a')
            else:
                self.assertEqual(shell.aliases['la'], 'ls -a')

    def test_execute_add_path(self):
        shells = {'nu', 'fish', 'bash'}
        shell_set = ShellSet(current_shells=shells)
        c1 = "add_path(~/.cargo/bin)"
        c2 = "add_path(~/.nix-profile/bin)"
        _execute(c1, shell_set)
        _execute(c2, shell_set)
        self.assertEqual(len(shell_set.current_shells), 3)
        for shell in shell_set.current_shells:
            self.assertEqual(shell.paths_to_add, [
                             "~/.cargo/bin", "~/.nix-profile/bin"])

    def test_execute_set_shells(self):
        shells = {'fish', 'zsh'}
        shell_set = ShellSet(shells)

        def has_shell_type(type):
            current_shells = shell_set.current_shells
            return any(isinstance(shell, type) for shell in current_shells)
        assert has_shell_type(Fish)
        assert has_shell_type(Zsh)
        self.assertEqual(len(shell_set.current_shells), 2)

        command = "set_shells(nu, bash)"
        _execute(command, shell_set)
        assert has_shell_type(Nu)
        self.assertEqual(len(shell_set.current_shells), 2)

    def test_set_shell_config_path(self):
        shells = {"fish", "nu"}
        shell_set = ShellSet(shells)
        fish_path = "/cool/path/fish.fish"
        nu_path = "~/hi.nu"
        shell_set.set_compile_path("fish", fish_path)
        shell_set.set_compile_path("nu", nu_path)
        self.assertEqual(shell_set.all_shells["fish"].config_path, fish_path)
        self.assertEqual(shell_set.all_shells["nu"].config_path, nu_path)

    def test_filter_lines(self):
        original = ["hello()", "bye", "# byte", "h#llo", "c\\#llo", ]
        expected = ["hello()", "bye", "h", "c#llo"]

        self.assertEqual(filter_lines_and_handle_sourcing(original), expected)


if __name__ == '__main__':
    # argv[0] is the program itself, even if run directly as an executable
    args = parse_args(sys.argv[1:])
    display_version = args.version
    run_test = args.run_test
    if display_version:
        print(CURRENT_VERSION)
        exit(0)
    elif run_test:
        base_name = sys.argv[0]
        unittest.main(argv=[
            base_name])  # needs basename, but if I don't explicitly pass argv it will try to parse all args passed to program
        # running the test automatically exits the program
    else:
        shells = auto_detect_shells()
        shell_set = ShellSet(shells)
        default_config_path = os.path.expanduser(
            "~/.config/easy_env/easy.conf")

        if args.file is None:
            path = default_config_path
            unfiltered_lines = read_file(default_config_path)
        else:
            path = os.path.abspath(args.file.name)
            unfiltered_lines = args.file.readlines()
        parent_dir = os.path.dirname(path)
        lines = filter_lines_and_handle_sourcing(unfiltered_lines, parent_dir)
        process_config(lines, shell_set)
        if args.print:
            print_shell_set(shell_set)
        else:
            write_shell_set(shell_set)
