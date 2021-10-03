#!/bin/bash

set -e

version=$1
if [ -z "$version" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

function check_package_version {
    grep "^version = \"*\"" pyproject.toml | grep $1
}

package_version=${version:1:${#version}}
if check_package_version "$package_version"; then
    echo "$version is valid version"
else
    echo "$version is not valid version" 1>&2
    exit 1
fi
