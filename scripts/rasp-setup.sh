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

fail() {
  echo $1 >&2
  exit 1
}

retry() {
  local n=1
  local max=5
  local delay=15
  while true; do
    "$@" && break || {
      if [[ $n -lt $max ]]; then
        ((n++))
        echo "Command failed. Attempt $n/$max:"
        sleep $delay;
      else
        fail "The command has failed after $n attempts."
      fi
    }
  done
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
retry sudo apt-get --assume-yes update
retry sudo apt-get --assume-yes upgrade

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

echo "========== Removing old unwanted docker-related pkgs =========="
sudo apt-get --assume-yes remove docker \
                                 docker-ce \
                                 docker-engine \
                                 docker.io \
                                 containerd \
                                 containerd.io \
                                 runc \
                                 docker-ce-cli \
                                 docker-engine-cs \
                                 lxc-docker \
                                 lxc-docker-virtual-package

sudo dpkg --purge docker-ce

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

retry function_test_internet_connection

echo "========== Installing required Docker dependencies =========="
packages=( "apt-transport-https" "ca-certificates" "curl" "git" "gnupg2" "software-properties-common" )
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

retry sudo apt-get --assume-yes update

echo "========== Installing Docker =========="
function_check_pkg_installed docker-ce

echo "========== Adding pi to docker group =========="
sudo usermod -aG docker pi

echo "========== Installing Docker Compose =========="
sudo pip install docker-compose

sudo apt-get --assume-yes autoremove

echo "========== SUCESSFULLY INSTALLED ALL NEEDED PKGs =========="

echo "========== Setting sige-Slave project =========="

mkdir -p /sige
git clone https://gitlab.com/lappis-unb/projects/sige/smi-slave.git /smi/slave

function_ask_reboot() {
    read -p "Do you want to reboot now? (y|n)    " INPUT

    case "$INPUT" in 
    y|Y ) echo "========== Rebooting to apply changes ==========" && sudo reboot;;
    n|N ) echo "You must reboot to apply changes!";;
    * ) echo "Type 'Y' or 'N'" && function_ask_reboot;;
    esac
}

function_ask_reboot
