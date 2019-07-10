#!/bin/bash


die() {
    printf 'FATAL: %s\n' "$*" >&2
    exit 1
}

set -x

# Get path to parts depot
if [[ -n "$PUP_CUSTOM_DIR" ]] ; then
    DIRPATH="$PUP_CUSTOM_DIR/r10k/postrun_parts"
else
    # Fall back to execution path
    DIRPATH="$( dirname "$0" )/postrun_parts"
fi

# Ensure run-parts is installed
RP=$(which run-parts)
if [[ -z "$RP" ]] ; then
    die "run-parts not found"
fi

# run-parts on debian 16.x works differently than on CentOS 7
# ... have to give regex to select files to run
$RP --verbose --regex='^[0-9]' "$DIRPATH"
