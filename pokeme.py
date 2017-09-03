#!/usr/bin/env python

"""
pokeme.py  written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 motion tracking using web cam or pi-camera module

This is a raspberry pi python opencv motion tracking demonstration program.
It will detect motion in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.

Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is a my YouTube video demonstrating this demo program using a
Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

Requires a Raspberry Pi with a RPI camera module installed and configured
dependencies

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-opencv python-picamera
sudo apt-get install libgl1-mesa-dri

"""

import os
mypath=os.path.abspath(__file__)       # Find the full path of this python script
baseDir=mypath[0:mypath.rfind("/")+1]  # get the path location only (excluding script name)
baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]
progName = os.path.basename(__file__)
version = "0.52"

print("%s %s written by Claude Pageau" % (progName, version))
print("Loading Please Wait ....")

# import the necessary packages
import io
import time
from random import randint
import cv2
from threading import Thread

WEBCAM = False        # default = False False=PiCamera True=USB WebCamera

try:  # Bypass loading picamera library if not available eg. UNIX or WINDOWS
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except:
    WEBCAM = True

# Web Camera Settings
WEBCAM_SRC = 0        # default = 0   USB opencv connection number
WEBCAM_WIDTH = 640    # default = 320 USB Webcam Image width
WEBCAM_HEIGHT = 480   # default = 240 USB Webcam Image height
WEBCAM_HFLIP = True   # default = False USB Webcam flip image horizontally
WEBCAM_VFLIP = False  # default = False USB Webcam flip image vertically

# Pi Camera Settings
CAMERA_WIDTH = 640    # default = 320 PiCamera image width can be greater if quad core RPI
CAMERA_HEIGHT = 480   # default = 240 PiCamera image height
CAMERA_HFLIP = False  # True=flip camera image horizontally
CAMERA_VFLIP = True   # True=flip camera image vertically
CAMERA_ROTATION = 0   # Rotate camera image valid values 0, 90, 180, 270
CAMERA_FRAMERATE = 30 # default = 25 lower for USB Web Cam. Try different settings

if WEBCAM:   # Get centerline for movement counting
    x_center = int(WEBCAM_WIDTH/2)
    y_center = int(WEBCAM_HEIGHT/2)
    x_max = WEBCAM_WIDTH
    y_max = WEBCAM_HEIGHT
    x_buf = int(WEBCAM_WIDTH/10)
    y_buf = int(WEBCAM_HEIGHT/10)
else:
    x_center = int( CAMERA_WIDTH/2)
    y_center = int(CAMERA_HEIGHT/2)
    x_max = CAMERA_HEIGHT
    y_max = CAMERA_WIDTH
    x_buf = int(CAMERA_WIDTH/10)
    y_buf = int(CAMERA_HEIGHT/10)

pokefile = 'pokeme-1.png'  # Name of image file to initially load
pokefilesave = 'pokeme-s.png' #Name of crop image file to save

verbose = True       # Set to False for no data display
window_on = True     # Set to True displays opencv windows (GUI desktop reqd)
SHOW_CIRCLE = False  # show a circle otherwise show bounding rectancle on window
CIRCLE_SIZE = 8      # diameter of circle to show motion location in window
CIRCLE_LINE = 2      # width of line for drawing circle
FONT_SCALE = .5      # OpenCV window text font size scaling factor default=.5 (lower is smaller)
LINE_THICKNESS = 1   # thickness of bounding line in pixels
WINDOW_BIGGER = 1    # resize multiplier for speed photo image and if gui_window_on=True then makes opencv window bigger
                     # Note if the window is larger than 1 then a reduced frame rate will occur
FRAME_COUNTER = 1000 # Counter for Frames per Second Display

# Color data for OpenCV lines and text
cvWhite = (255,255,255)
cvBlack = (0,0,0)
cvBlue = (255,0,0)
cvGreen = (0,255,0)
cvRed = (0,0,255)
circleColor = cvGreen      # Color of motion Tracking circle

# Menu Box Setup
MENU_WIDTH = 200
MENU_HEIGHT = 75
MENU_LINE_WIDTH = 2

menucounter = 8
menuBorderColor = cvGreen  # Menu rectangle color
menuTextColor = cvBlue     # Menu rectangle text color
menuHitColor = cvRed       # Menu rectangle circle color when motion hit activated
menusetupdata = [10, 10, MENU_WIDTH, MENU_HEIGHT, "SETUP"]
menuplaydata = [220, 10, MENU_WIDTH, MENU_HEIGHT, "PLAY"]
menuquitdata = [430, 10, MENU_WIDTH, MENU_HEIGHT, "QUIT"]
menureviewdata = [10, 10, MENU_WIDTH, MENU_HEIGHT, "REVIEW"]
menuphotodata = [430, 220, MENU_WIDTH, MENU_HEIGHT, "TAKE PHOTO"]
menuexitdata = [10, 10, MENU_WIDTH, MENU_HEIGHT,"EXIT"]
menucanceldata = [220, 10, MENU_WIDTH, MENU_HEIGHT, "BACK"]

# photo window settings
photo_window_line_w = 2
photo_window_w = 150
photo_window_h = 150
photo_window_x = int( x_center - ( photo_window_w / 2 ))
photo_window_y = int( y_center - ( photo_window_h / 2 ))

poke_w = 100    # Width of Pokeme image
poke_h = 100    # Height of Pokeme image

# OpenCV Motion Tracking Settings
MIN_AREA = 1000     # excludes all contours less than or equal to this Area

THRESHOLD_SENSITIVITY = 25  # These two settings should not need changing
BLUR_SIZE = 10

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
class WebcamVideoStream:
    def __init__(self, CAM_SRC=WEBCAM_SRC, CAM_WIDTH=WEBCAM_WIDTH, CAM_HEIGHT=WEBCAM_HEIGHT):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(CAM_SRC)
        self.stream.set(3,CAM_WIDTH)
        self.stream.set(4,CAM_HEIGHT)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
def show_FPS(start_time,frame_count):
    if verbose:
        if frame_count >= FRAME_COUNTER:
            duration = float(time.time() - start_time)
            FPS = float(frame_count / duration)
            print("Processing at %.2f fps last %i frames" %( FPS, frame_count))
            frame_count = 0
            start_time = time.time()
        else:
            frame_count += 1
    return start_time, frame_count

#-----------------------------------------------------------------------------------------------
def menu_make( menudata, image, cxy, menuhits ):
    if menudata:
        cv2.rectangle(image,(menudata[0], menudata[1]),
                            (menudata[0]+ menudata[2], menudata[1] + menudata[3]),
                            menuBorderColor, MENU_LINE_WIDTH)
        cv2.putText(image, menudata[4], ( menudata[0] + int(menudata[2]/4),
                                          menudata[1] + int(menudata[3]/2)),
                                          cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE,
                                          menuTextColor, MENU_LINE_WIDTH)
    if cxy:
        if (cxy[0] > menudata[0] and
            cxy[0] < menudata[0] + menudata[2] and
            cxy[1] > menudata[1] and
            cxy[1] < menudata[1] + menudata[3]):
            cv2.circle(image, cxy, CIRCLE_SIZE, menuHitColor, CIRCLE_LINE)
            menuhits += 1
    return image, menuhits

def flip_Webcam_image(image):
    if WEBCAM:
        if ( WEBCAM_HFLIP and WEBCAM_VFLIP ):
            image = cv2.flip( image, -1 )
        elif WEBCAM_HFLIP:
            image = cv2.flip( image, 1 )
        elif WEBCAM_VFLIP:
            image = cv2.flip( image, 0 )
    return image


#-----------------------------------------------------------------------------------------------
def pokemen():
    print("Initializing Camera ....")
    # Save images to an in-program stream
    if window_on:
        print("press q to quit opencv display")
    else:
        print("press ctrl-c to quit")
    print("Start Motion Tracking ....")
    frame_count = 0
    start_time = time.time()
    still_scanning = True

    menumain = True    # Main Menu
    menuedit = False   # Edit Menu
    menuexit = False   # Exit Menu
    menuplay = False   # Play


    menusetuphits = 0
    menuplayhits = 0
    menuquithits = 0

    menuphotohits = 0
    menucancelhits = 0

    menureviewhits = 0

    pokeme = cv2.imread(pokefile)
    pw = pokeme.shape[1]
    ph = pokeme.shape[0]
    print ("%s - Loaded %s w=%i h=%i" % (progName, pokefile, pw, ph))
    try:
        image2 = vs.read()
        image2 = flip_Webcam_image(image2)
        grayimage1 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    except:
        return False   # Failed to process initial image

    while still_scanning:
        motion_found = False
        start_time, frame_count = show_FPS(start_time, frame_count)

        image2 = vs.read()   # Read frame from video stream
        image2 = flip_Webcam_image(image2)

        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed, blurred images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        grayimage1 = grayimage2
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
        # Get all the contours found in the thresholdimage
        try:
            thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
        except:
            contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        cxy = ()
        if contours:
            total_contours = len(contours)
            biggest_area = MIN_AREA
            for c in contours:
                # get area of next contour
                found_area = cv2.contourArea(c)
                # find the middle of largest bounding rectangle
                if found_area > biggest_area:
                    motion_found = True
                    biggest_area = found_area
                    (x, y, w, h) = cv2.boundingRect(c)
                    cx = int(x + w/2)   # put circle in middle of width
                    cy = int(y + h/2)   # put circle closer to top
                    cxy = (cx, cy)
                    cw = w
                    ch = h

        if verbose and motion_found:
            print("Motion at cx,cy(%i,%i)  C=%2i  A:%ix%i=%i SqPx" %
                            (cx ,cy, total_contours, cw, ch, biggest_area))

        if not menuplay and motion_found:
            cv2.circle(image2, cxy, CIRCLE_SIZE, circleColor, 4)

        if menumain:
            image2, menusetuphits = menu_make( menusetupdata, image2, cxy, menusetuphits )
            image2, menuplayhits = menu_make( menuplaydata, image2, cxy, menuplayhits )
            image2, menuquithits = menu_make( menuquitdata, image2, cxy, menuquithits )
            if menusetuphits > menucounter:
                menuedit = True
                menumain = False
            elif menuplayhits > menucounter:
                menuplay = True
                menumain = False
            elif menuquithits > menucounter:
                menuexit = True
                menumain = False

            if not menumain:
                menusetuphits = 0
                menuplayhits = 0
                menuquithits = 0
                menuphotohits = 0
                menucancelhits = 0
        elif menuexit:
            image2, menuquithits = menu_make( menuquitdata, image2, cxy, menuquithits )
            image2, menucancelhits = menu_make( menucanceldata, image2, cxy, menucancelhits )
            if menuquithits > menucounter:
                menuquithits = 0
                menucancelhits = 0
                break
            elif menucancelhits > menucounter:
                menuexithits = 0
                menucancelhits = 0
                menuquithits = 0
                menusetuphits = 0
                menuplayhits = 0
                menuphotohits = 0
                menuexit = False
                menumain = True
        elif menuedit:
            image2, menucancelhits = menu_make( menucanceldata, image2, cxy, menucancelhits )
            image2, menuphotohits = menu_make( menuphotodata, image2, cxy, menuphotohits )
            cv2.rectangle(image2,( photo_window_x, photo_window_y),
                                 ( photo_window_x + photo_window_w, photo_window_y + photo_window_h ),
                                   cvBlue, photo_window_line_w)   # Window for taking photo of pokeme
            if menuphotohits > menucounter:
                image3=image2
                image3.flags.writeable = True
                crop_y1 = photo_window_y + photo_window_line_w
                crop_y2 = crop_y1 + photo_window_w - ( photo_window_line_w * 2 )
                crop_x1 = photo_window_x + photo_window_line_w
                crop_x2 = crop_x1 + photo_window_w - ( photo_window_line_w *2 )
                pokeme = image3[ crop_y1 : crop_y2, crop_x1 : crop_x2 ]  # Crop from x, y, w, h
                cv2.imwrite(pokefilesave,pokeme)
                pokeme = cv2.resize( pokeme,( poke_w, poke_h ))
                pw = pokeme.shape[1]
                ph = pokeme.shape[0]
                menuedit = False
                menuplay = True

            if menucancelhits > menucounter:
                menuedit = False
                menumain = True

            if not menuedit:
                menuexithits = 0
                menucancelhits = 0
                menuquithits = 0
                menusetuphits = 0
                menuplayhits = 0
                menuphotohits = 0
        elif menuplay:
            image3 = image2
            image3.flags.writeable = True
            # make sure poke stays on the screen
            if x > CAMERA_WIDTH - pw:
                x = CAMERA_WIDTH - pw
            if y > CAMERA_HEIGHT - ph:
                y = CAMERA_HEIGHT - ph
            image3[y:y+ph, x:x+pw] = pokeme
            image2 = image3

        if WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
            big_w = CAMERA_WIDTH * WINDOW_BIGGER
            big_h = CAMERA_HEIGHT * WINDOW_BIGGER
            image2 = cv2.resize( image2,( big_w, big_h ))

        # Full screen does not work on RPI as far as I can see.
        # cv2.namedWindow("pokeme", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("pokeme",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("pokeme q=quit m=menu", image2)

        if cv2.waitKey(1) & 0xFF == ord('m'):
            image2 = vs.read()
            image2 = flip_Webcam_image(image2)
            grayimage1 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            menusetuphits = 0
            menuplayhits = 0
            menuquithits = 0
            menuphotohits = 0
            menucancelhits = 0
            menuplay = False
            menumain = True

        elif cv2.waitKey(1) & 0xFF == ord('q'):  # Close Window if q pressed
            vs.stop()
            cv2.destroyAllWindows()
            print("End Motion Tracking ......")
            still_scanning = False

    return True

#-----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    while True:
        try:
            # Save images to an in-program stream
            # Setup video stream on a processor Thread for faster speed
            if WEBCAM:   #  Start Web Cam stream (Note USB webcam must be plugged in)
                print("Initializing USB Web Camera ....")
                vs = WebcamVideoStream().start()
                vs.CAM_SRC = WEBCAM_SRC
                vs.CAM_WIDTH = WEBCAM_WIDTH
                vs.CAM_HEIGHT = WEBCAM_HEIGHT
                time.sleep(4.0)  # Allow WebCam to initialize
            else:
                print("Initializing Pi Camera ....")
                vs = PiVideoStream().start()
                vs.camera.rotation = CAMERA_ROTATION
                vs.camera.hflip = CAMERA_HFLIP
                vs.camera.vflip = CAMERA_VFLIP
                time.sleep(2.0)  # Allow PiCamera to initialize
            if pokemen():
                quit(0)
        except KeyboardInterrupt:
            vs.stop()
            print("")
            print("+++++++++++++++++++++++++++++++++++")
            print("User Pressed Keyboard ctrl-c")
            print("%s %s - Exiting" % (progName, version))
            print("+++++++++++++++++++++++++++++++++++")
            print("")
            quit(0)
