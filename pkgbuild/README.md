
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

After an initial run the workspace will be populated with a tree structure macthing the users permissions

Copy the text packages to one of those folders to test commit/upload

The scratchpads folder contains scripts which use the files to

- upload
- copy
- move
- delete
