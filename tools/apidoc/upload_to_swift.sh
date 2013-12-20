#!/bin/bash

TARGETDIR="./target/xmldoc/html"
RBSWIFTCOMMAND="rbswift"

if [ ! $# -eq 1 ];
then
    echo "$0 <version> (v1,v2,v3 and so on...)"
    exit
fi

command -v ${RBSWIFTCOMMAND} >/dev/null 2>&1 || { echo -e >&2 "I require a command/script/alias named ${RBSWIFTCOMMAND} that validates to rbcloud... for example:\nalias ${RBSWIFTCOMMAND}='swift -A https://objekt.rbcloud.net/auth/v1.0 -U redbridge-ab:<username>@redbridge.se -K <key>' \nAborting."; exit 1; }

if [ -d $1 ];
then
    echo "Directory exist... Delete? (y/n)"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) rm -r $1; break;;
            No ) exit;;
        esac
    done
fi

mkdir $1

cp -r ${TARGETDIR}/images ${TARGETDIR}/includes ${TARGETDIR}/TOC_User.html ${TARGETDIR}/user $1
${RBSWIFTCOMMAND} upload api $1
rm -r $1

echo "Done!"
