import cv2
import dlib
import os
import numpy as np
from collections import deque

class pathTracker(object):

    def __init__(self, windowName, videoName):
        self.selection = None
        self.track_window = None
        self.drag_start = None
        self.speed = 20
        self.video_size = (700,600)     
        self.box_color = (0,255,0)      
        self.path_color = (0,0,255)

        # create tracker window
        cv2.namedWindow(windowName,cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(windowName,self.onmouse)
        self.windowName = windowName
        # load video
        self.cap = cv2.VideoCapture(videoName)
        if not self.cap.isOpened():
            print("Video doesn't exit!", videoName)
        self.frames_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # store all center points for each frame
        self.points = deque(maxlen = self.frames_count)

        self.tracker = dlib.correlation_tracker()

    def onmouse(self,event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.track_window = None

        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax, ymax)
        if event == cv2.EVENT_LBUTTONUP:

            self.track_window = self.selection
         
    def drawing(self,image,x,y,w,h,timer):

        center_point_x = int(x+ 0.5*w)
        center_point_y = int(y + 0.5*h)
        center = (center_point_x,center_point_y)

        self.points.appendleft(center)
        # tracker's bound
        cv2.rectangle(image, (int(x),int(y)), (int(x+w),int(y+h)), self.box_color, 2)
        # center point
        cv2.circle(image, center, 2, self.path_color, -1)

        for i in range(1, len(self.points)):
            if self.points[i-1] is None or self.points[i] is None:
                continue
            # path of center point
            cv2.line(image, self.points[i-1], self.points[i], self.path_color,2)

    def start_tracking(self):

        i = 0
        for f in range(self.frames_count):
            timer = cv2.getTickCount()
            ret, self.frame = self.cap.read()
            if not ret:
                print("End!")
                break
            print("Processing Frame {}".format(i))
            img_raw = self.frame
            image = cv2.resize(img_raw.copy(), self.video_size, interpolation = cv2.INTER_CUBIC)
            # only need to select object on the first frame
            if i == 0: 
                while(True):
                    img_first = image.copy()
                    if self.track_window:
                        cv2.rectangle(img_first, (self.track_window[0],self.track_window[1]), (self.track_window[2], self.track_window[3]), self.box_color, 1)
                    elif self.selection:
                        cv2.rectangle(img_first, (self.selection[0],self.selection[1]), (self.selection[2], self.selection[3]), self.box_color, 1)
                    cv2.imshow(self.windowName, img_first)
                    # if press enter then selection is end
                    if cv2.waitKey(self.speed) == 13:
                        break
                # Dlib

                self.tracker.start_track(image, dlib.rectangle(self.track_window[0], self.track_window[1], self.track_window[2], self.track_window[3]))
                

            # start tracking at the end of the first frame
            # (x, y) is the left-top point's postion of tracker's bound
            # w and h is width and height of tracker's bound

            self.tracker.update(image)
            tracker_box = self.tracker.get_position()
            x,y,w,h = tracker_box.left(),tracker_box.top(),tracker_box.width(),tracker_box.height()

            self.drawing(image,x,y,w,h,timer)
            cv2.imshow(self.windowName,image)
            # if press esc
            if cv2.waitKey(self.speed) == 27:
                break
            i += 1
            save picture
            if i == self.frames_count:
                cv2.imwrite('track_result.jpg',image)

        cv2.destroyAllWindows()

if __name__ == '__main__':
    Tracker = pathTracker(windowName = 'Tracker',videoName = "squat.mp4")
    Tracker.start_tracking()
