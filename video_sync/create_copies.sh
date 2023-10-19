#!/bin/bash
# Copyright 2023, Metropolis Technologies, Inc.
# USAGE: ./create_copies.sh <directory_of_files> <desired_prefix>
# Will create copies of files inside directory with a specified prefix
DEFAULT_DIR="/home/aim/nvme_data/AB_TESTING_VIDEOS"
DEFAULT_PREFIX="copy_"
INPUT_DIR=${1-"${DEFAULT_DIR}"}
COPY_PREFIX=${2-"${DEFAULT_PREFIX}"}

NOT_COPY=()
COPY=()
for entry in "$INPUT_DIR"/*
do
    if [ ! -d $entry ] && [ -f $entry ]; then
        CURRENT_FILE=${entry#"${INPUT_DIR}/"}
        if [[ $CURRENT_FILE == $COPY_PREFIX* ]]; then
            COPY+=($CURRENT_FILE)
        else
            NOT_COPY+=($CURRENT_FILE)
        fi
        ALL_FILES+=($CURRENT_FILE)
    fi
done
NOT_COPIED=()
COPIED=()
for file in "${NOT_COPY[@]}"
do
    COPY_VERSION="${COPY_PREFIX}${file}"
    if [[ ${COPY[*]} =~ (^|[[:space:]])"${COPY_VERSION}"($|[[:space:]]) ]]; then
        #echo "Not copying: $file"
        NOT_COPIED+=$file
    else
        #echo "Creating copy for $file"
        cp -r "$INPUT_DIR/$file" "$INPUT_DIR/$COPY_VERSION"
        HASH_ORIG=$(md5sum "$INPUT_DIR/$file" | cut -d ' ' -f 1)
        HASH_COPIED=$(md5sum "$INPUT_DIR/$COPY_VERSION" | cut -d ' ' -f 1)
        if [ "$HASH_ORIG" = "$HASH_COPIED" ]; then
            COPIED+=("$INPUT_DIR/$COPY_VERSION")
        fi
    fi
done
if [ ${#COPIED[@]} -eq 0 ]; then
    echo "No files copied."
else

    printf "\nCopied Files:\n"
    printf '+ %s\n' "${COPIED[@]}"
fi