# pokeme.py  A motion tracking demonstration written by Claude Pageau
## Windows, Unix, Raspberry Pi python opencv 
## Demonstration motion menus and image overlays

## Program Description
This is a fun demonstration showing moving a clipped image graphic
and motion tracking activated menus.  To activate a menu move your
fingers/hand inside the menu box (a red indicator will show recording
of hits)  When the menu hits counter is exceeded the menu pick will
be activated.
Run Setup menu to create a new clipped image.  It will be saved prior to play.
Play does not do anything at this time but just moves image clip
to follow movement motion tracking.  

This python script will run under Windows or a non RPI unix distro using a 
web camera as well as on a Raspberry Pi computer using a pi-camera or 
web camera.  Note Download the latest python version that includes numpy
and opencv.

## Quick Install   
Easy Install of speed-cam onto a Raspberry Pi Computer with latest Raspbian. 

    curl -L https://raw.github.com/pageauc/pokeme/master/install.sh | bash

From a computer logged into the RPI via ssh(Putty) session use mouse to highlight 
command above, right click, copy.  Then select ssh(Putty) window, mouse right
click, paste.  The command should download and execute the github install.sh 
script for pokeme.py.  
Note - a raspbian apt-get update and upgrade will be performed as part of install 
so it may take some time if these are not up-to-date


## Windows or Non RPI Unix Installs
For Windows or Unix computer platforms (non RPI or Debian) ensure you have the 
most up-to-date python version. For Downloads visit https://www.python.org/downloads

The latest python versions include numpy and recent opencv that is required to run
this code. You will also need a USB web cam installed and working. To install this 
program access the GitHub project page at https://raw.github.com/pageauc/pokeme
and select the green Clone or download zip option. The files will be cloned or 
zipped to a pokeme folder. You can run the code from console, gui desktop or from
python IDLE application.

## Hardware Requirements
USB Web Camera or pi-camera module connected and working.
Computer monitor or HD Television needs to be connected via an HDMI cable
(composite video not tested) or a VGA adapter.
The program is run from the computers GUI desktop in an opencv window. 
The default 640x480 window can be resized using the WINDOW_BIGGER 
resize multiplier variable.

## How to Run Program

To launch program make sure camera and video display are connected. 
You must be in a GUI desktop session. Open a desktop terminal session, 
File Manger. or Menu Programming, Python IDLE program. 
Navigate to the pokme folder and load/execute

    cd ~/pokeme
    ./pokeme.py

or

    cd ~/pokeme
    python pokeme.py

Have Fun
Claude Pageau

YouTube Channel https://www.youtube.com/user/pageaucp    
GitHub https://github.com/pageauc    

   
    
    