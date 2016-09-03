#! /bin/bash

echo 'Dpkg::Progress-Fancy "1";' | sudo tee /etc/apt/apt.conf.d/99progressbar

# Install ppa for apt-fast, scudcloud, and git, and update the index
sudo add-apt-repository ppa:saiarcot895/myppa -y
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update

# Install apt-fast
sudo DEBIAN_FRONTEND=noninteractive apt-get install apt-fast -y --force-yes

# Upgrade installed packages
sudo apt-fast upgrade -y

# Install packages for pyenv, and several other odds and ends
sudo DEBIAN_FRONTEND=noninteractive apt-fast install -y --force-yes make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm ubuntu-restricted-extras vim gnome-do ssh synaptic zsh zsh-lovers xdotool git kupfer keepass2 network-manager-openconnect-gnome python-gpgme scudcloud libqupzilla-dev libqupzilla1 qupzilla libqtwebkit-qupzillaplugins safe-rm source-highlight

# Install pip
wget https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py

# Install pip managed packages
sudo -H pip install virtualenv

# Install pyenv
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
sed -i -e '$a\\' ~/.bashrc
echo 'source ~/.bash_profile' >> ~/.bashrc
echo 'alias ll="ls -lAh --color=auto --group-directories-first"' >> ~/.bash_profile
echo 'alias rm="safe-rm"' >> ~/.bash_profile
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile

# Copy in the zsh user file
cp -fv /etc/zsh/newuser.zshrc.recommended ~/.zshrc
echo 'source ~/.bash_profile' >> ~/.zshrc

# Set zsh to the default shell
sudo chsh -s /bin/zsh $USER


# set pyenv vars so usable by this script
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Have pyenv install python 3.4.3
pyenv install 3.4.3

# Install docker
wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker $USER

# Install Google Chrome
sudo mkdir -p /etc/apt/sources.list.d
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable -y

# Install Dropbox
wget https://www.dropbox.com/download?dl=packages/debian/dropbox_2015.02.12_amd64.deb -O dropbox_2015.02.12_amd64.deb
sudo dpkg -i dropbox_2015.02.12_amd64.deb
dropbox start -i

# Wait for user to login to Dropbox and the Dropbox folder to be created
while [ ! -d ~/Dropbox ]
do
    sleep 5
done

# Install sublime text 3
wget http://c758482.r82.cf2.rackcdn.com/sublime-text_build-3083_amd64.deb
sudo dpkg -i sublime-text_build-3083_amd64.deb
subl
ps aux | grep /sublime_text$ | awk '{print $2}' | xargs kill

# Install Package control
wget https://sublime.wbond.net/Package%20Control.sublime-package -O ~/.config/sublime-text-3/Installed\ Packages/Package\ Control.sublime-package

# Setup Sublime Text package syncing via Dropbox
rm -rf ~/.config/sublime-text-3/Packages/User
ln -s ~/Dropbox/Sublime/User ~/.config/sublime-text-3/Packages/User

# Clean up installers
rm -rf dropbox_2015.02.12_amd64.deb
rm -rf get-pip.py
rm -rf sublime-text_build-3083_amd64.deb

echo 'Setup complete. Please logout and back in again to apply group membership changes.'

