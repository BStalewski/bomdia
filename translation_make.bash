#!/usr/bin/env bash

if [ $# != "1" ]; then
    echo "Wrong usage. Use: $0 <lang>"
    exit 1
fi

LANG=$1

I18N_DIR="i18n"
PROJECT_NAME="Bomdia"
TEMPLATE_FILE="$I18N_DIR/$PROJECT_NAME.pot"
PO_FILE="$I18N_DIR/$LANG/LC_MESSAGES/$PROJECT_NAME.po"

# Create translation template
xgettext --language=Python --keyword=_ "--output=$TEMPLATE_FILE" `find . -name "*.py"`
sed -i 's/CHARSET/utf-8/' $TEMPLATE_FILE

# Update translations
if [ -f $PO_FILE ]; then
    msgmerge -q $PO_FILE $TEMPLATE_FILE --output-file=$PO_FILE
else
    msginit "--input=$TEMPLATE_FILE" "--output-file=$PO_FILE" "--locale=$LANG"
fi
