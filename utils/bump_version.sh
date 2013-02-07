#!/bin/bash
exit_usage() {
    echo "Usage: $0 openerp_version release_number"
    echo ""
    echo "openerp_version: Openerp version this release is built for"
    echo "release_number: Release number in format yyyymmddxx xx is the release number of the day first release 00, second release 01. ie. 1978091500"
    echo ""
    echo "example:"
    echo "$0 6.1 2012021000"
    exit 1
}

case $# in
    2 ) oe_version=$1
        release_number=$2;;
    * ) exit_usage;;
esac

version="openerp$oe_version-rev$release_number"

for I in $(ls src/*/__openerp__.py); do
    echo "Bumping $version into $I"
    sed -i "s/openerp[0-9].[0-9]-rev[0-9]\{10\}/$version/g" $I
done

echo "Bumping $version into Changes"
sed -i "1s/.*/$version\n&/" Changes

