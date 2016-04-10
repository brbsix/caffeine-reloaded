#!/bin/bash
#
# Build Debian package


cleanup(){
    info "Removing $TEMP_DIRECTORY"
    rm -rf "$TEMP_DIRECTORY"
}


error(){
    echo "$PROGRAM:ERROR: $*" >&2
    exit 1
}


finish(){
    info "TEMP_DIRECTORY=$TEMP_DIRECTORY"
}


info(){
    echo "$PROGRAM:INFO: $*"
}


warning(){
    echo "$PROGRAM:WARNING: $*" >&2
}


PROGRAM=${0##*/}

APPLICATION=caffeine-reloaded
SCRIPT_DIRECTORY=$(readlink -m "$(dirname "$0")")
VERSION=$(< "$SCRIPT_DIRECTORY/VERSION")

if (( $# == 1 )) && [[ $1 =~ ^(-d|--dev(elopment)?)$ ]]; then
    trap finish EXIT
elif (( $# == 0 )); then
    trap cleanup EXIT
else
    cat <<-EOF
	Usage: $PROGRAM [-d|--development]
	Build a Debian package.

	  -d, --development      DO NOT remove build files after build

	Build details:

	  APPLICATION=$APPLICATION
	  VERSION=$VERSION

	  SCRIPT_DIRECTORY=$SCRIPT_DIRECTORY

	EOF
    exit 0
fi

TEMP_DIRECTORY=$(mktemp --directory --tmpdir caffeine.XXXXXX)

[[ -d $TEMP_DIRECTORY ]] || {
    error "Failed to create temp directory"
}

# enter the script directory (necessary to update changelog)
cd "$SCRIPT_DIRECTORY" || {
    error "Failed to cd into $SCRIPT_DIRECTORY"
}

# copy entire repo into temp directory
# cp -aR "$SCRIPT_DIRECTORY" "$TEMP_DIRECTORY"
rsync -aC --exclude='.*' --exclude='__pycache__' --exclude='*.deb' "$SCRIPT_DIRECTORY" "$TEMP_DIRECTORY"

BUILD_DIRECTORY=${TEMP_DIRECTORY}/${SCRIPT_DIRECTORY##*/}

# enter the build directory
cd "$BUILD_DIRECTORY" || {
    error "Failed to cd into $BUILD_DIRECTORY"
}

# perform build
debuild -b -uc -us

EC=$?

# warn upon debuild failure
if (( EC != 0 )); then
    error "debuild returned a nonzero exit code [$EC]"
fi

# enter the temp directory containing .deb and logs
cd "$TEMP_DIRECTORY" || {
    error "Failed to cd into $TEMP_DIRECTORY"
}

# move .deb into the root directory
mv ./*.deb "$SCRIPT_DIRECTORY" || {
    error "Failed to move .deb into $SCRIPT_DIRECTORY"
}
