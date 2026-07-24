#!/bin/sh

mkdir -p tmp; pushd tmp
git clone https://github.com/sebastiencs/icons-in-terminal.git --depth=1
pushd icons-in-terminal
sh install.sh
source $HOME/.bashrc
popd; popd
rm -rf tmp