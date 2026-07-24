#!/bin/bash

clear
echo "                                                                                                                                                                                 ";
echo "░██       ░██                              ░██                          ░████████                         ░██             ░██████                            ░████ ░██           ";
echo "░██       ░██                              ░██                          ░██    ░██                        ░██            ░██   ░██                          ░██                  ";
echo "░██  ░██  ░██  ░███████  ░██    ░██  ░████████  ░███████   ░███████     ░██    ░██   ░██████    ░███████  ░████████     ░██         ░███████  ░████████  ░████████ ░██ ░████████ ";
echo "░██ ░████ ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██    ░████████         ░██  ░██        ░██    ░██    ░██        ░██    ░██ ░██    ░██    ░██    ░██░██    ░██ ";
echo "░██░██ ░██░██ ░█████████ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██    ░██     ░██  ░███████   ░███████  ░██    ░██    ░██        ░██    ░██ ░██    ░██    ░██    ░██░██    ░██ ";
echo "░████   ░████ ░██        ░██   ░███ ░██   ░███ ░██    ░██ ░██    ░██    ░██     ░██ ░██   ░██         ░██ ░██    ░██     ░██   ░██ ░██    ░██ ░██    ░██    ░██    ░██░██   ░███ ";
echo "░███     ░███  ░███████   ░█████░██  ░█████░██  ░███████   ░███████     ░█████████   ░█████░██  ░███████  ░██    ░██      ░██████   ░███████  ░██    ░██    ░██    ░██ ░█████░██ ";
echo "                                ░██                                                                                                                                          ░██ ";
echo "                          ░███████                                                                                                                                     ░███████  ";
echo "                                                                                                                                                                                 ";


if read -p "Do you want to install the Bash config (y/n) : " reponse && ! [[ "$reponse" =~ ^[yYoO]$ ]]; then
    echo "Cancelling..."
    exit 1
fi

echo ""
echo "==================== Starship ===================="
if read -p "Do you want to install Starship (y/n) : " reponse && ! [[ "$reponse" =~ ^[yYoO]$ ]]; then
    echo "Skipping Starship..."
else
    echo "Checking Truecolor support..."
    sh 'Bash/scripts/check-truecolors.sh'
    
    if read -p "Do you see a rainbow strip (y/n) : " reponse && [[ "$reponse" =~ ^[yYoO]$ ]]; then
        echo "Installing Starship..."
        sh 'Bash/scripts/install-starship.sh' > /dev/null
        echo "Starship installed."
    else
        echo "Your terminal doesn't support Truecolor, aborting installation of Starship..."
    fi
fi

echo ""
echo "==================== ~/.bashrc ==================="
if read -p "Do you want to install the .bashrc config (y/n) : " reponse && ! [[ "$reponse" =~ ^[yYoO]$ ]]; then
    echo "Skipping .bashrc..."
else
    sh 'Bash/scripts/install-bashrc.sh' > /dev/null
fi

echo "Finished !"