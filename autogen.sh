#!/bin/sh

set -e

srcdir="$(dirname "$0")"
test -n "$srcdir" || srcdir=.

olddir=$(pwd)
cd "$srcdir"

cp apphide.py apphide
autoreconf --force --install

cd "$olddir"

if test -z "$NOCONFIGURE"; then
  "$srcdir"/configure "$@"
fi
