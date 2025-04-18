# BxtCtl (WIP)

Commandline tool for bxt package management

## Development and Testing
Required packages

### repo packages

- python-cmd2
- python-prettytable
- python-pyjwt
- python-requests
- python-requests-toolbelt

```bash
sudo pacman -Syu python-cmd python-prettytable python-pyjwt python-requests python-requests-toolbelt
```

```bash
sudo pacman -S poetry
git clone https://github.com/fhdk/bxtctl.git
cd bxtctl
poetry install
poetry run bxtctl
```

## Command overview

As the project is WIP the following is subject to change.

This issue https://github.com/fhdk/bxtctl/issues/2 is intended to gather feedback on how the CLI commands could be used,
and any thoughts and ideas to improve or extend the functionality.

If you discover a bug (likely you will) please create a new issue.

## Workspace
A tree structure will be created in the designated workspace.

The structure will match the permissions for the user accessing the service.

## Overall design is
Ideas and thoughts
- ~/.config/bxtctl/config.json
- workspace ~/bxt-workspace
- the workspace is populated with a folder structure matching the user's permission on bxt
- this is perhaps overkill, I am more in favor of having a single copy e.g., and all commits are done to unstable
- the tests I have been doing have been using testing branch, so I could easily see what my actions achieved.
- I am totally open to suggestions and feedback on how you see yourself use the client

## Basic scripting
What I have now are a few basic commandline actions (these will only work if the shell has been launched and configured)

```bash
poetry run bxtctl --help
Usage: Execute action and return to prompt. [-h] [-getws] [-setws SETWS]
                                            [-commit [{*, stable/extra/x86_64, stable/extra/aarch64, stable/core/x86_64, stable/core/aarch64, stable/multilib/x86_64, stable/multilib/aarch64, unstable/extra/x86_64, unstable/extra/aarch64, unstable/core/x86_64, unstable/core/aarch64, unstable/multilib/x86_64, unstable/multilib/aarch64, testing/extra/x86_64, testing/extra/aarch64, testing/core/x86_64, testing/core/aarch64, testing/multilib/x86_64, testing/multilib/aarch64}]]

optional arguments:
  -h, --help            show this help message and exit
  -getws                Get active workspace
  -setws SETWS          Set active workspace. The full path to the workspace
  -commit [{*, stable/extra/x86_64, stable/extra/aarch64, stable/core/x86_64, stable/core/aarch64, stable/multilib/x86_64, stable/multilib/aarch64, unstable/extra/x86_64, unstable/extra/aarch64, unstable/core/x86_64, unstable/core/aarch64, unstable/multilib/x86_64, unstable/multilib/aarch64, testing/extra/x86_64, testing/extra/aarch64, testing/core/x86_64, testing/core/aarch64, testing/multilib/x86_64, testing/multilib/aarch64}]
                        Commit active workspace or specified repo
```

- -getws is intended as outside tools to retrieve the workspace for pointing chrootbuild PKGDEST to the bxt workspace. the root of the workspace is returned
- -setws is somewhat similar, I thought it might be useful for scripting if one could both read and write the workspace location.
- -commit is intended to commit what is in the workspace; usually this will be new packages; it is thought to be everything or a single repo

## The shell is bxtctl without arguments

You will get a prompt indicating who you are and the server you are connected to.

```shell
(bxtctl@bxt.staging.manjaro.org) $ 
```

Inside the shell has advanced functionality

```shell
(bxtctl@bxt.staging.manjaro.org) $ help
Documented commands (use 'help -v' for verbose/'help <topic>' for details):
===========================================================================
compare    delete_pkg  list_path       login        quit       upload_pkg
configure  help        list_repo       move_pkg     set        workspace 
copy_pkg   history     list_workspace  permissions  shortcuts
```

It is these functions I need some input on how we imagine them used; that is your purpose; I am the coder; 
I not likely to be the enduser, so I would love your feedback on every aspect - 
that includes what the commands are called, what would come natural to you as enduser.

As you have seen, the webui is highly versatile, and it is next to impossible to make the client as versatile.

As an example, the commit endpoint - which can do all commit transactions - I have split this into

```text
upload_pkg
copy_pkg
remove_pkg
move_pkg
```

And idea for Upload

```text
upload_pkg -p pkg -p pkg -p pkg -repo unstable/extra/aarch64
```

An idea for removal

```text
remove_pkg -p pkg -p pkg -p pkg -repo unstable/extra/aarch64
```

The copy and move are more challenging

```text
copy_pkg -p pkg -from unstable/extra/aarch64 -to testing/extra/aarch64
move_pkg -p pkg -from unstable/extra/aarch64 -to testing/extra/aarch64
```

Some commands will also make more sense than others.

Inside bxtctl (shell) the above-mentioned commands also have shortcuts assigned

```shell
(bxtctl@bxt.staging.manjaro.org) $ shortcuts
Shortcuts for other commands:
?: help
cfg: configure
cmp: compare
cpp: copy_pkg
exit: quit
lsp: list_path
lsr: list_repo
lsw: list_workspace
mvp: move_pkg
rmp: delete_pkg
upp: upload_pkg
ws: workspace
```

See your permissions

```shell
(bxtctl@bxt.staging.manjaro.org) $ permissions
---------- PERMISSIONS ----------
bxt user      : bxtctl
Branches      : stable, testing, unstable
Repositories  : core, extra, multilib
Architectures : aarch64, x86_64
```

