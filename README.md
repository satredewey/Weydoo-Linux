Mes fichiers de config Linux
============================
----------------------------


# Bash


## Startship

You'll need a [nerd font](https://www.nerdfonts.com/) installed and enabled in your terminal.
Then execute:
``` bash
sudo apt install -y curl
curl -sS https://starship.rs/install.sh | sh
mkdir -p $HOME/.config
cp Bash/starship.toml $HOME/.config/starship.toml 
```
or
``` bash
sh Bash/scripts/install-starship.sh
```


## ~/.bashrc

You'll need bash installed in your computer.
To install, execute:
``` bash
cp Bash/bashrc $HOME/.bashrc
source $HOME/.bashrc
```
or
``` bash
sh Bash/scripts/install-bashrc.sh
```


## ls-icons

You'll need `git`:
``` bash
sh Bash/scripts/install-git.sh
```

You'll need to check if you're terminal support TRUECOLOR, you should see a rainbow:
``` bash
sh Bash/scripts/check-truecolors.sh
```

You need to install [icons-in-terminal](https://github.com/sebastiencs/icons-in-terminal) first.
``` bash
mkdir -p tmp; pushd tmp
git clone https://github.com/sebastiencs/icons-in-terminal.git --depth=1
pushd icons-in-terminal
sh install.sh
source $HOME/.bashrc
popd; popd
rm -rf tmp
```
or 
``` bash
sh Bash/scripts/install-icons-in-terminal.sh
```

Now you can compile and install [ls-icons](https://github.com/sebastiencs/ls-icons) by running:
``` bash
sh Bash/scripts/install-ls-icons.sh
```