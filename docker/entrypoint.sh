#!/bin/bash
set -e

# Allow X11 connections without auth (works for WSLg local socket)
if [ -n "$DISPLAY" ]; then
    export DISPLAY
fi

exec "$@"
