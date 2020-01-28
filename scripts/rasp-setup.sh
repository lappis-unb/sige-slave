#!/bin/bash

BRIDGE_FILE=/etc/systemd/network/bridge.network

echo "========== Upgrading pkgs =========="

sudo apt update -y && sudo apt upgrade -y

echo "========== Removing file =========="
sudo apt-get remove -y docker \
                       docker-ce \
                       docker-engine \
                       docker.io \
                       containerd \
                       runc

echo "========== Creating Bridge file =========="
if [ ! -f $BRIDGE_FILE ]; then
    sudo tee -a $BRIDGE_FILE > /dev/null << EOF
[Network]

IPFoward=kernel
EOF
    cat $BRIDGE_FILE
else
    echo -e "Bridge file already exists...\n"
    echo $BRIDGE_FILE && cat $BRIDGE_FILE
fi

echo "========== Setting Bash color =========="
echo -e "
function git_branch_name() {
    git branch 2>/dev/null | grep -e '^*' | sed -E 's/^\* (.+)$/(\1)/'
}

function show_colored_git_branch_in_prompt() {\n
    PS1='\[\033[01;32m\]\u@\h:\[\033[01;34m\]\w\[\033[31m\]\$(git_branch_name)\[\033[m\]$'
}

show_colored_git_branch_in_prompt
" >> ~/.bashrc
source ~/.bashrc

echo "========== Restarting Network service =========="
sudo systemctl restart systemd-networkd.service

echo "========== Installing required Docker dependencies =========="
sudo apt-get install --no-install-recommends \
                        apt-transport-https \
                        ca-certificates \
                        curl \
                        gnupg2 \
                        software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

sudo tee -a /etc/apt/sources.list.d/docker.list > /dev/null << EOF
deb [arch=armhf] https://download.docker.com/linux/debian buster stable
EOF

sudo apt-get update

echo "========== Installing Docker =========="
sudo apt-get install --no-install-recommends docker-ce

echo "========== Adding pi to docker group =========="
sudo usermod -aG docker pi

echo "========== Installing Docker Compose =========="
sudo pip install docker-compose

echo "========== SUCESSFULLY INSTALLED ALL NEEDED PKGs =========="

echo "========== Cloning SMI-Slave project =========="
mkdir -p /smi
git clone https://gitlab.com/lappis-unb/projects/SMI/smi-slave.git /smi/slave

echo "*Successfully cloned SMI-Slave into /smi/slave"

read -p "Do you want to reboot now? Yes | No" INPUT
if [ $INPUT == 'Yes' ]; then
    echo "========== Rebooting to apply changes =========="
    sudo reboot
if [ $INPUT == 'No' ]; then
    echo "You must reboot to apply changes!"
else
    echo "Type 'Yes' or 'No'"
fi
fi