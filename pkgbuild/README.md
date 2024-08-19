## Test packages
To avoid having binary test files in the repo, those can be created using the PKGBUILD.

Do not use real packages as those may interfere with normal operation.

## Create test packages
The PKGBUILD creates 3 dummy pacakges with no content.

    makepkg -cC

## Sign the test packages
bxt service requires a signature for all uploads.

Sign the files with your key (assuming you create an env variable with that name).

    gpg --detach-sign -u $GPGKEY a-dummy1-0-0-any.pkg.tar.zst
    gpg --detach-sign -u $GPGKEY a-dummy2-0-0-any.pkg.tar.zst

## Using the test packages
Place the dummy packages in the repo folder

    /.../pkgbuild $  cp *.pkg.tar.zst.* ../repo
    /.../pkgbuild $  cd ..
    /.../bxtctl $  ls ./repo
    a-dummy1-0-0-any.pkg.tar.zst  a-dummy1-0-0-any.pkg.tar.zst.sig  a-dummy2-0-0-any.pkg.tar.zst  a-dummy2-0-0-any.pkg.tar.zst.sig

## From v.0.4
A tree structure will be created in the designated workspace.

The structure will macth the permissions for the user accessing the service.

The interactive shell is not default launched - to enter the shell use the `-i/--interactive` argument.

A few arguments has been added to main entry to 

- set a workspace
- get the current workspace (can be used to instruct chrootbuild where to store the output)
- commit current workspace - optionally only a specific repo e.g. `unstable/core/x86_64`
- debug loggin argument
- interactive shell

The scratchpads folder contains scripts which use the files to

- upload
- copy
- move
- delete
