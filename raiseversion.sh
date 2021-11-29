#!/bin/bash

# Update version in project
if [ -z $1 ]; then
    VERSION_STRING=`date -u +0.5.%Y%m%d%H%M%S`
else
    VERSION_STRING=$1
fi
FILE_NAME='hypercane/version.py'
DOC_FILE_NAME='docs/source/conf.py'

# Update Hypercane version
sed -i.bak "s/^__appversion__ = .*$/__appversion__ = '$VERSION_STRING'/g" $FILE_NAME
sed -i.bak "s/^release = u'.*'$/release = u'$VERSION_STRING'/g" $DOC_FILE_NAME
