#!/bin/sh

sudo apt update
sudo apt install build-essential clang autoconf automake autopoint gettext texinfo bison gperf patch -y

if sudo test -f /usr/local/bin/ls-icons; then
    echo "ls-icons already installed" >&2
    exit 0
fi

mkdir -p tmp; pushd tmp
git clone https://github.com/sebastiencs/ls-icons.git --depth=1
pushd ls-icons

git clone https://github.com/coreutils/gnulib.git --depth=1

./bootstrap --gnulib-srcdir=gnulib
export CC=clang CXX=clang++
./configure --prefix=/opt/coreutils

make
patch ../../Bash/ls-icons.patch
sudo cp src/ls $(which ls)
sudo touch /usr/local/bin/ls-icons

popd; popd
rm -rf tmp
unset CC CXX