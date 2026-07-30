#!/bin/bash
clear
echo "                                                                                                                                                                                 ";
echo "░██       ░██                              ░██                          ░████████                         ░██             ░██████                            ░████ ░██           ";
echo "░██  ░██  ░██  ░███████  ░██    ░██  ░████████  ░███████   ░███████     ░██    ░██   ░██████    ░███████  ░████████     ░██         ░███████  ░████████  ░████████ ░██ ░████████ ";
echo "░██ ░████ ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██    ░████████         ░██  ░██        ░██    ░██    ░██        ░██    ░██ ░██    ░██    ░██    ░██░██    ░██ ";
echo "░██░██ ░██░██ ░█████████ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██    ░██     ░██  ░███████   ░███████  ░██    ░██    ░██        ░██    ░██ ░██    ░██    ░██    ░██░██    ░██ ";
echo "░████   ░████ ░██        ░██   ░███ ░██   ░███ ░██    ░██ ░██    ░██    ░██     ░██ ░██   ░██         ░██ ░██    ░██     ░██   ░██ ░██    ░██ ░██    ░██    ░██    ░██░██   ░███ ";
echo "░███     ░███  ░███████   ░█████░██  ░███████░██  ░███░██  ░███████   ░███████     ░█████████   ░█████░██  ░███████  ░██    ░██      ░██████   ░███████  ░██    ░██    ░██    ░██ ░█████░██ ";
echo "                                ░██                                                                                                                                          ░██ ";
echo "                          ░███████                                                                                                                                     ░███████  ";
echo "                                                                                                                                                                                 ";

ask() {
    read -rp "$1 [y/n] " answer
    case "$answer" in
        [Yy]* ) return 0 ;;
        * ) return 1 ;;
    esac
}

# Git
if ask "Install Git?"; then
    bash Bash/scripts/install-git.sh
fi

# Starship
if ask "Install Starship?"; then
    echo "Checking Truecolor support..."
    bash Bash/scripts/check-truecolors.sh
    if ask "Do you see a rainbow strip (y/n) ?"; then
        echo "Installing Starship..."
        bash Bash/scripts/install-starship.sh
        echo "Starship installed."
    else
        echo "Your terminal doesn't support Truecolor, aborting installation of Starship..."
    fi
fi

# Bashrc
if ask "Install .bashrc?"; then
    bash Bash/scripts/install-bashrc.sh
fi

# Icons-in-terminal
if ask "Install Icons in Terminal?"; then
    bash Bash/scripts/install-icons-in-terminal.sh
fi

# ls-icons
if ask "Install ls-icons?"; then
    echo -e ""  # using echo -e to interpret unicode
    if ask "Can you see this symbol (y/n) ?"; then
        echo "Installing ls-icons (this might take a moment)..."
        bash Bash/scripts/install-ls-icons.sh
    else
        echo "You need to install Icons In Terminal first."
    fi
fi

echo "Installation finished."
