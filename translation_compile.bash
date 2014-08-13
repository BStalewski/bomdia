#!/usr/bin/env bash

I18N_DIR="i18n"
PROJECT_NAME="Bomdia"

if [ $# != "1" ]; then
    echo "Wrong usage. Use: $0 <lang>"
    exit 1
fi

LANG=$1
MESSAGES_DIR="$I18N_DIR/$LANG/LC_MESSAGES"

msgfmt "$MESSAGES_DIR/$PROJECT_NAME.po" --output-file "$MESSAGES_DIR/$PROJECT_NAME.mo"
