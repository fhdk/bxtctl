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
alias    configure  history  macro         run_script  shortcuts
commit   edit       list     quit          set         sync     
compare  help       login    run_pyscript  shell    
```

### Configure command

The `configure` command is run at first start to create a basic configuration file.

It will query for the http endpoint of the bxt API and the username and the password needed to retrieve an access token.

At any point the `configure` command can be used to change the service endpoint and the username.

### Login command

The `login` command can be used to change the username and retrieve a new access token based on the username and a provide password.

The password is never stored on the system and there will be no characters echoed to screen.

### Set workspace command

The workspace is where you keep the packages you build. A default workspace `$HOME/bxt-workspace` is created at first run. 
Use the `set_workspace` command to change the default.

```
set_workspace /path/to/new/workspace
```

### Compare command

```
Usage: compare [-h] [-b [{testing, unstable, stable} [...]]] [-r [{core, extra, multilib} [...]]] [-a [{aarch64, x86_64} [...]]] [-p [PACKAGE]]

Compare repo package across branches and architectures

optional arguments:
  -h, --help            show this help message and exit
  -b, --branch [{testing, unstable, stable} [...]]
                        Branches to compare
  -r, --repo [{core, extra, multilib} [...]]
                        Repositories to compare
  -a, --arch [{aarch64, x86_64} [...]]
                        Architecures to compare
  -p, --package [PACKAGE]
                        Package(s) to compare (multiple -p can be passed)
```

### List command

```
Usage: list [-h] {testing, unstable, stable} {core, extra, multilib} {aarch64, x86_64}

List content of repo branch architecture

positional arguments:
  {testing, unstable, stable}
                        Target Branch
  {core, extra, multilib}
                        Target Repository
  {aarch64, x86_64}     Target Artitecture

optional arguments:
  -h, --help            show this help message and exit
```

### Commit command

```
Usage: commit [-h] {testing, unstable, stable} {extra, multilib, core} {aarch64, x86_64} [package]

Commit package(s) to repository

positional arguments:
  {testing, unstable, stable}
                        Target Branch
  {extra, multilib, core}
                        Target Repository
  {aarch64, x86_64}     Target Architecture
  package               package filename (multiple packages can be passed)

optional arguments:
  -h, --help            show this help message and exit
```
