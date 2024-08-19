# bxtctl

Commandline tool for bxt package management

## repo packages

- python-cmd2
- python-prettytable
- python-pyjwt
- python-requests
- python-requests-toolbelt

### custom package

- python-pwinput

## Development

```bash
sudo pacman -S poetry
git clone https://github.com/fhdk/bxtctl.git
cd bxtctl
poetry install
poetry run bxtctl
```

## Command overview

As the project is WIP the following is subject to change.

This issue https://github.com/fhdk/bxtctl/issues/2 is intended to gather feedback on how the CLI commands.

## Workspace 
A tree structure will be created in the designated workspace.

The structure will macth the permissions for the user accessing the service.

The interactive shell is not default launched - to enter the shell use the `-i/--interactive` argument.

A few arguments has been added to main entry to 

- set a workspace
- get the current workspace (can be used to instruct chrootbuild where to store the output)
- commit current workspace - optionally only a specific repo e.g. `unstable/core/x86_64`
- debug loggin argument
- interactive shell

### Help command

```
Documented commands (use 'help -v' for verbose/'help <topic>' for details):
===========================================================================
commit     copy     login    ls_workspace  remove  shortcuts
compare    help     ls_path  move          set     workspace
configure  history  ls_repo  quit          shell 
```

### list configured shortcuts command
Several of the commands has shortcuts configured. To list the available shortcuts

```
shortcuts
```

### Configure command

The `configure` command is run at first start to create a basic configuration file.

It will query for the http endpoint of the bxt API and the username and the password needed to retrieve an access token.

At any point the `configure` command can be used to change the service endpoint and the username.

### Login command

The `login` command can be used to change the username and retrieve a new access token based on the username and a
provide password.

The password is never stored on the system and there will be no characters echoed to screen.

### workspace command

The workspace is where you keep the packages you build. A default workspace `$HOME/bxt-workspace` is created at first
run.
```
Usage: workspace [-h] [-w WORKSPACE]

Get or set workspace

optional arguments:
  -h, --help            show this help message and exit
  -w, --workspace WORKSPACE
                        Full path to workspace
```
### list workspace content
List content of the current workspace
```
Usage: ls_workspace [-h] [-l]

List workspace content

optional arguments:
  -h, --help  show this help message and exit
  -l, --long  use long list
```
### list content of arbitrary path
List content of any system paths
```
Usage: ls_path [-h] [-l] [path]

List path content

positional arguments:
  path        Path to list content

optional arguments:
  -h, --help  show this help message and exit
  -l, --long  use long list
```

## Remote BXT Repository commands

The command will only list locations the user has permissions to access

### List repo contents command

```
Usage: ls_repo [-h] location

List content of remote bxt repository

positional arguments:
  location    {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}
```

### Compare command

```
Usage: compare [-h] [-l [LOCATION [...]]] [-p [PACKAGE]]

Compare repo package across branches and architectures

optional arguments:
  -h, --help            show this help message and exit
  -l, --location [LOCATION [...]]
                        {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'}
  -p, --package [PACKAGE]
                        Package(s) to compare (multiple -p can be passed)
```

### Commit command

```
Usage: commit [-h] [-p PACKAGE [...]] location

Commit package(s) to repository

positional arguments:
  location              {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'}

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        package name(s) (multiple files can be passed)
```

### Copy command

```
Usage: copy [-h] [-p PACKAGE [...]]

Copy package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        'pkgname {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'} {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'}'
```

### Move command
```
Usage: move [-h] [-p PACKAGE [...]]

Move package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        Package move from repo to repo: 'pkgname {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'} {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'}'
```

### Remove command
```
Usage: remove [-h] [-p PACKAGE [...]]

Delete package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        Package remove from repo: 'pkgname {'unstable'}/{'extra', 'core', 'multilib'}/{'x86_64'}'
```
