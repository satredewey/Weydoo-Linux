#!/bin/sh

if command -v starship &> /dev/null; then
    echo "starship already installed" >&2
    echo "Just installing config"
    exit 0
else
    sudo apt install -y curl
    curl -sS https://starship.rs/install.sh | sh
fi

mkdir -p $HOME/.config
cp Bash/starship.toml $HOME/.config/starship.toml 