# bxtctl

Commandline tool for bxt package management

## Development

```bash
sudo pacman -S poetry
git clone https://github.com/fhdk/bxtctl.git
cd bxtctl
poetry install
poetry run bxtctl
```
```bash
(default@bxt) $ help

Documented commands (use 'help -v' for verbose/'help <topic>' for details):
===========================================================================
alias    configure  history  macro         run_script  shortcuts
commit   edit       list     quit          set         sync     
compare  help       login    run_pyscript  shell    
```
```
(default@bxt) $ help compare
Usage: compare [-h] [-b [{testing, unstable, stable} [...]]] [-a [{aarch64, x86_64} [...]]] [-p [PACKAGE [...]]] {core}

Compare repo package across branches and architecures

positional arguments:
  {core}                Target Repository

optional arguments:
  -h, --help            show this help message and exit
  -b, --branch [{testing, unstable, stable} [...]]
                        Branches to compare
  -a, --arch [{aarch64, x86_64} [...]]
                        Architecures to compare
  -p, --package [PACKAGE [...]]
                        Packages to compare

```
```
(default@bxt) $ help list
Usage: list [-h] {core} {testing, unstable, stable} {aarch64, x86_64}

List content of repo branch architecture

positional arguments:
  {core}                Target Repository
  {testing, unstable, stable}
                        Target Branch
  {aarch64, x86_64}     Target Artitecture

optional arguments:
  -h, --help            show this help message and exit

```
```
(default@bxt) $ help commit
Usage: commit [-h] package pkgfile sigfile {core} {testing, unstable, stable} {aarch64, x86_64}

Commit package to repository

positional arguments:
  package               Path to package file
  pkgfile               Path to package file
  sigfile               Path to signature file
  {core}                Target Repository
  {testing, unstable, stable}
                        Target Branch
  {aarch64, x86_64}     Target Architecture

optional arguments:
  -h, --help            show this help message and exit

```