#!/bin/sh

if command -v git >/dev/null 2>&1; then
    echo "Git is already installed" >&2
    exit 0
fi

sudo add-apt-repository ppa:git-core/ppa
sudo apt update; sudo apt install git
