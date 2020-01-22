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
    echo "Bridge file already exists..."
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
