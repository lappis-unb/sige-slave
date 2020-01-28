#!/bin/bash

BRIDGE_FILE=/etc/systemd/network/bridge.network
DOCKER_SRC_FILE=/etc/apt/sources.list.d/docker.list

function_test_internet_connection() {
    if nc -zw1 google.com 443; then
        echo "The network is up!"
    else
        echo "The network is down..."
    fi
}

function_check_pkg_installed() {
    pkgs=("$@")
    for i in "${pkgs[@]}"
    do
        dpkg -s $i &> /dev/null
        if [ $? -eq 0 ]; then
            echo "Package is installed!"
        else
            sudo apt-get --assume-yes --no-install-recommends install $i
        fi
    done
}

echo "========== Upgrading pkgs =========="
sudo apt-get --assume-yes update && sudo apt-get --assume-yes upgrade

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

echo "========== Removing old unwanted docker-related pkgs =========="
sudo apt-get --assume-yes remove docker \
                                 docker-ce \
                                 docker-engine \
                                 docker.io \
                                 containerd \
                                 runc

echo "========== Creating Bridge file =========="
if [ ! -f "$BRIDGE_FILE" ]; then
    sudo tee -a $BRIDGE_FILE > /dev/null << EOF
[Network]

IPFoward=kernel
EOF
    cat $BRIDGE_FILE
else
    echo -e "Bridge file already exists...\n"
    echo $BRIDGE_FILE && cat $BRIDGE_FILE
fi

echo "========== Restarting Network service =========="
sudo systemctl restart systemd-networkd.service

until function_test_internet_connection; do
  echo "Network is still unavailable, waiting..."
  sleep 2
done

echo "========== Installing required Docker dependencies =========="
packages=( "apt-transport-https" "ca-certificates" "curl" "gnupg2" "software-properties-common" )
function_check_pkg_installed "${packages[@]}"

if [ ! -f "$DOCKER_SRC_FILE" ]; then
   sudo tee -a /etc/apt/sources.list.d/docker.list > /dev/null << EOF
deb [arch=armhf] https://download.docker.com/linux/debian buster stable
EOF
   cat $DOCKER_SRC_FILE
else
   echo -e "Docker source file already exists...\n"
   echo $DOCKER_SRC_FILE && cat $DOCKER_SRC_FILE
fi
sudo apt-get --assume-yes update

echo "========== Installing Docker =========="
function_check_pkg_installed docker-ce

echo "========== Adding pi to docker group =========="
sudo usermod -aG docker pi

echo "========== Installing Docker Compose =========="
sudo pip install docker-compose

sudo apt-get --assume-yes autoremove

echo "========== SUCESSFULLY INSTALLED ALL NEEDED PKGs =========="

echo "========== Setting SMI-Slave project =========="

mkdir -p /smi
git clone https://gitlab.com/lappis-unb/projects/SMI/smi-slave.git /smi/slave

function_ask_reboot() {
    read -p "Do you want to reboot now? (y|n)    " INPUT

    case "$INPUT" in 
    y|Y ) echo "========== Rebooting to apply changes ==========" && sudo reboot;;
    n|N ) echo "You must reboot to apply changes!";;
    * ) echo "Type 'Y' or 'N'" && function_ask_reboot;;
    esac
}

function_ask_reboot