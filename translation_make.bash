#!/usr/bin/env bash

xgettext --language=Python --keyword=_ --output=po/bomdia.pot `find . -name "*.py"`
