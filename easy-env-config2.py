#!/bin/python


class Shell:
    def __init__(self):
        self.env_variables = {}
        self.paths = set()
        self.aliases = {}
    def add_abbr(self,key,val):
        self.add_alias(key,val)
    def add_alias(self,key,val):
        self.aliases[key]=val
        




class Nu(Shell):
    pass
#TODO for fish writing a alais i can use an equals sign or not but either way if the values have more then one string then I need to use an quotes
class Fish(Shell):
    def __init__(self):
        self.abbrs = {}
        super().__init__()
    def add_abbr(self,key,val):
        self.abbrs[key]=val
class Bash(Shell):
    pass

SHELLS = {'nu':Nu,'fish':Fish, 'bash':Bash, 'zsh':Shell}
#all methods that are publicly availbe for the user to use must exist as a method with the same name in this class for now
#TODO: probably won't actually do but it might be a good idea to map strings to decople the user interface and the code
class ShellWriter:
    def __init__(self):
        self.shells = {}
        self.current_shells = {}

        self.in_place = False
        self.ignored_shells = set()
        #map, that maps shells to map that contains enviorment variables
        super().__init__()
    def auto_detect_shells(self) -> [str]:
        pass
    def add_shells(self, shells:[str]):
        for shell in shells:
            self._add_shell(shell)
    def _add_shell(self, shell:str):
        if shell not in SHELLS.keys():
            print(f'{shell} is not a supported shell, the supported shells are: {SHELLS.keys()}')
            exit(-1)
        if shell not in self.shells:
            self.shells[shell] = SHELLS[shell]()

        self.current_shells[shell] = self.shells[shell]
    def remove_shells(self,shells:[str]):
        for shell in shells:
            self._remove_shell(shell)
    def _remove_shell(self,shell):
        self.current_shells.pop(shell)
    def ignore_shells(self,shells:[str]):
        for shell in shells:
            self.ignore_shell(shell)
    def ignore_shell(self,shell):
        self._remove_shell(shell)
        self.ignored_shells.add(shell)
    def un_ignore_shell(self, shell):
        self.ignored_shells.remove(shell)
    def alias(self,operands:[str]):
        pass
    def abbr(self,operands:[str]):
        if len(operands)<2:
            print('no')
            exit(-1)
        variable = operands[0]
        if variable.startswith('$'):
            variable = variable[1:]
        rest = ''
        for s in operands[1:]:
            rest += s
        for shell in self.current_shells:
            shell.abbrs[variable]=rest
    

    def add_path(self, path):#TODO iterate current_shells, add to path, verify path exists first
        for _,val in self.current_shells:
            val.paths.add(val)
    def exec(self, line:str):
        if '#' in line:
            line = line[:line.index('#')]
        line = line.strip()
        if line == '':
            return
        split = line.split(' ')
        if len(split)==0:
            print('you did something wrong split has length 0')
            exit(-1)
        command = split[0].lower()
        if len(split) > 1:
          operands = split[1:]
          getattr(self,command)(operands)#creates coupling between there code and my methods
        else:
            getattr(self,command)()

