#!/bin/bash
# Quick Install of pokeme files
# install.sh script written by Claude Pageau 1-Sep-2017
ver="0.5"
APP_DIR='pokeme'  # Default folder install location

cd ~
if [ -d "$APP_DIR" ] ; then
  STATUS="Upgrade"
  echo "Upgrade pokeme files"
else
  echo "New pokeme Install"
  STATUS="New Install"
  mkdir -p $APP_DIR
  echo "$APP_DIR Folder Created"
fi

cd $APP_DIR
INSTALL_PATH=$( pwd )

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "------------------------------------------------"
echo "  pokeme Install.sh script ver $ver"
echo "  $STATUS pokeme for motion tracking"
echo "------------------------------------------------"
echo ""
echo "1 - Downloading GitHub Repo files to $INSTALL_PATH"
wget -O install.sh -q --show-progress https://raw.github.com/pageauc/pokeme/master/install.sh
if [ $? -ne 0 ] ;  then
  wget -O install.sh https://raw.github.com/pageauc/pokeme/master/install.sh
  wget -O pokeme.py https://raw.github.com/pageauc/pokeme/master/pokeme.py
  wget -O pokeme-1.png https://raw.github.com/pageauc/pokeme/master/pokeme-1.png
  wget -O pokeme-2.png https://raw.github.com/pageauc/pokeme/master/pokeme-2.png
  wget -O pokeme-3.png https://raw.github.com/pageauc/pokeme/master/pokeme-3.png
  wget -O pokeme-4.png https://raw.github.com/pageauc/pokeme/master/pokeme-4.png
  wget -O pokeme-5.png https://raw.github.com/pageauc/pokeme/master/pokeme-5.png
  wget -O pokeme-6.png https://raw.github.com/pageauc/pokeme/master/pokeme-6.png
  wget -O Readme.md https://raw.github.com/pageauc/pokeme/master/Readme.md
else
  wget -O pokeme.py -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme.py
  wget -O pokeme-1.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-1.png
  wget -O pokeme-2.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-2.png
  wget -O pokeme-3.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-3.png
  wget -O pokeme-4.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-4.png
  wget -O pokeme-5.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-5.png
  wget -O pokeme-6.png -q --show-progress https://raw.github.com/pageauc/pokeme/master/pokeme-6.png
  wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pokeme/master/Readme.md
fi
echo "Done Download"
echo "------------------------------------------------"
echo ""
echo "2 - Make required Files Executable"
chmod +x pokeme.py
chmod +x install.sh
echo "Done Permissions"
echo "------------------------------------------------"
# check if system was updated today
NOW="$( date +%d-%m-%y )"
LAST="$( date -r /var/lib/dpkg/info +%d-%m-%y )"
if [ "$NOW" == "$LAST" ] ; then
  echo "4 Raspbian System is Up To Date"
  echo ""
else
  echo ""
  echo "3 - Performing Raspbian System Update"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y update
  echo "Done update"
  echo "------------------------------------------------"
  echo ""
  echo "4 - Performing Raspbian System Upgrade"
  echo "    This Will Take Some Time ...."
  echo ""
  sudo apt-get -y upgrade
  echo "Done upgrade"
fi
echo "------------------------------------------------"
echo ""
echo "5 - Installing motion-track Dependencies"
sudo apt-get install -y python-opencv python-picamera
echo "Done Dependencies"
cd $DIR
# Check if motion-track-install.sh was launched from motion-track folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -e 'install.sh' ]; then
    echo "$STATUS Cleanup install.sh"
    rm install.sh
  fi
fi
echo "-----------------------------------------------"
echo "6 - $STATUS Complete"
echo "-----------------------------------------------"
echo ""
echo "1. Reboot RPI if there are significant Raspbian system updates"
echo "2. Raspberry pi needs a monitor/TV attached to display opencv window"
echo "3. Run pokeme.py with the Raspbian Desktop GUI running"
echo "4. To start open file manager or a Terminal session then change to"
echo "  pokeme folder and launch per commands below"
echo ""
echo "   cd ~/pokeme"
echo "   ./pokeme.py"
echo ""
echo "-----------------------------------------------"
echo "See Readme.md for Further Details"
echo $APP_DIR "Good Luck Claude ..."
echo "Bye"
echo ""