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

### Help command

```
Documented commands (use 'help -v' for verbose/'help <topic>' for details):
===========================================================================
commit     copy     login    ls_workspace  remove  shortcuts
compare    help     ls_path  move          set     workspace
configure  history  ls_repo  quit          shell 
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

## Repository commands
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
Compare repo package across branches and architectures

optional arguments:
  -h, --help            show this help message and exit
  -l, --location [LOCATION [...]]
                        {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}
  -p, --package [PACKAGE]
                        Package(s) to compare (multiple -p can be passed)
```

### Commit command

```
Usage: commit [-h] location [package]

Commit package(s) to repository

positional arguments:
  location    {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}
  package     package name(s) (multiple files can be passed)

optional arguments:
  -h, --help  show this help message and exit
```

### Copy command

```
Usage: copy [-h] [-p PACKAGE [...]]

Copy package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        'pkgname {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'} {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}'
```

### Remove command
```
Usage: remove [-h] [-p PACKAGE [...]]

Delete package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        Package remove from repo: 'pkgname {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}'
```

### Move command
```
Usage: move [-h] [-p PACKAGE [...]]

Move package(s) inside bxt storage

optional arguments:
  -h, --help            show this help message and exit
  -p, --package PACKAGE [...]
                        Package move from repo to repo: 'pkgname {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'} {'unstable'}/{'extra', 'multilib', 'core'}/{'x86_64'}'
```