# easy_env_config


## about
Easy Env Config is a Python-based tool designed to simplify the management of environment variables and shell aliases. The tool takes a JSON configuration as input and generates shell-specific scripts to set the corresponding environment variables and aliases. It aims to support multiple shell environments, including:

    Bash

    Zsh

    Fish

    NuShell


The project is written entirely in a single Python file (plus a README and a sample configuration), which includes both the core functionality and unit tests. Keeping all the code in one file is intended as a challenge for the developer and it is highly advised to never do anything like this.

On the plus side it means that running the program is just running one script.
Use easy_env_config.py -h to see all the available flags 

You will need to source the generated files from your config files for your shell.


#config:documentation
you can pass a path to a config file using ./easy-env-config.py <filePath>
if it is not specified then easy-env will look at this default config path  "~/.config/easy_env/easy.conf"
./easy-env-config.py -p to print instead of write changes, print target path followed by content

# is syntax for a comment and \# is how you type a literal pound
set_shells(bash, fish, nu) → sets the shells to change, every shell on your device should be autodetected beforehand
alias(la,ls -a) → defines an alias
abbr(la,ls -a) creates an abbreviation and falls back to aliases if abbreviations don't exist
set_env(d,frog) -> sets environment variable
add_path(path) -> add a path to the PATH environment variable
set_motion_mode(vi) parameter can be vi, emacs or normal, not supported by nushell
compile_path(shell, path)# config syntax
