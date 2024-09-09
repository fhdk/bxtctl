
## Test packages
To avoid having binary test files in the repo, those can be created using the PKGBUILD.

Do not use real packages as those may interfere with normal operation.

## Create test packages
Use the script `recreate_packages.sh` to update versions.

    bash recreate_packages.sh

### Script function
- Remove old packages from test repo
- build new packages
- sign new packages
- copy packages to test repo
- cleanup repo root

## Workspace

After an initial run the workspace will be populated with a tree structure macthing the users permissions.

The only scratchpad that uses the full filename is the upload scratchpad, 
so remember to update the script to use the updated filename

- upload
- copy
- move
- delete
