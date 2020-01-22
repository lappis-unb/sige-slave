#!/bin/bash

BRIDGE_FILE=/etc/systemd/network/bridge.network

echo "========== Upgrading pkgs =========="

sudo apt update && sudo apt upgrade

echo "========== Removing file =========="
sudo apt-get remove -y docker \
                       docker-ce \
                       docker-engine \
                       docker.io \
                       containerd \
                       runc

echo "========== Creating Bridge file =========="
if [ -f $BRIDGE_FILE ]; then
    sudo echo -e "[Network]\n\nIPFoward=kernel" > $BRIDGE_FILE
    cat $BRIDGE_FILE
fi
