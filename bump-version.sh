#!/bin/bash
#
# Bump package version


error(){
    echo "$PROGRAM:ERROR: $*" >&2
    exit 1
}


info(){
    echo "$PROGRAM:INFO: $*"
}


PROGRAM=${0##*/}

SCRIPT_DIRECTORY=$(readlink -m "$(dirname "$0")")

FILES=(caffeine-screensaver
       share/man/man1/caffeine.1
       share/man/man1/caffeine-indicator.1
       share/man/man1/caffeine-screensaver.1
       README.rst
       VERSION)

# enter the script directory
cd "$SCRIPT_DIRECTORY" || {
    error "Failed to cd into $SCRIPT_DIRECTORY"
}

# determine the package's current version
CURRENT_VERSION=$(< VERSION)

info "Package's current version number is '$CURRENT_VERSION'"

# prompt user for new version
read -ei "$CURRENT_VERSION" -p 'Please enter new version number: ' NEW_VERSION

# ensure user has entered new version
[[ -n $NEW_VERSION ]] || {
    error "Failed to set new version"
}

# update version strings
for file in "${FILES[@]}"; do
    sed -i "s/${CURRENT_VERSION//./\\.}/$NEW_VERSION/g" "$file" || {
        error "Failed to update version string in '$file'"
    }
done

# update changelog
dch --controlmaint --distribution "$(lsb_release -cs)" --newversion "$NEW_VERSION" --urgency low || {
    error "debchange experienced an unknown error"
}
