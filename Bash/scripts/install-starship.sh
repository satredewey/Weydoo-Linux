#!/bin/sh

if command -v starship &> /dev/null; then
    echo "Starship already installed" >&2
    echo "Just installing config"
else
    sudo apt install -y curl
    curl -sS https://starship.rs/install.sh | sh
fi

mkdir -p $HOME/.config
cp Bash/starship.toml $HOME/.config/starship.toml 

source $HOME/.bashrc