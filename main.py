import PyCmdMessenger
import cv2 as cv
from time import time, sleep
from playsound import playsound
from random import sample
import threading
import pygame
import face_recognition
import pickle
import numpy as np
import imutils
from math import sin, cos, atan2, pi
from enum import Enum

TURRET_MAX_PITCH: int = 150
TURRET_MIN_PITCH: int = 30
TURRET_MAX_YAW: int = 180
TURRET_MIN_YAW: int = 0

AI_MIN_PITCH: int = 20
AI_MAX_PITCH: int = 90
AI_MIN_YAW: int = 120
AI_MAX_YAW: int = 45

AI_PITCH_SPEED: int = 15
AI_YAW_SPEED: int = -15

class Turret:
    def __init__(self, min_pitch=TURRET_MIN_PITCH, max_pitch=TURRET_MAX_PITCH, min_yaw=TURRET_MIN_YAW, max_yaw=TURRET_MAX_YAW) -> None:
        self.arduino = arduino = PyCmdMessenger.ArduinoBoard("/dev/ttyACM0", baud_rate=9600)
        commands = [
            ["full", ""], 
            ["half", ""], 
            ["quater", ""], 
            ["one", ""], 
            ["set_speed", "f"],
            ["set_pitch", "i"],
            ["set_yaw", "i"]
        ]
        self.c = PyCmdMessenger.CmdMessenger(arduino, commands)
        self.pitch = 90
        self.yaw = 90
        self.min_pitch = min_pitch
        self.max_pitch = max_pitch
        self.min_yaw = min_yaw
        self.max_yaw = max_yaw
        sleep(0.1)
        self.set_pitch(self.pitch)
        self.set_yaw(self.yaw)

    def image_rotation(self):
        pr = self.pitch * pi / 180.0
        yr = self.yaw * pi / 180.0
        return round(cos(pr) * cos(yr) * 90.0)

    def set_pitch(self, pitch: int):
        pitch = max(min(pitch, self.max_pitch), self.min_pitch)
        self.c.send("set_pitch", pitch)
        self.pitch = pitch

    def set_yaw(self, yaw: int):
        yaw = max(min(yaw, self.max_yaw), self.min_yaw)
        self.c.send("set_yaw", yaw)
        self.yaw = yaw

    def full(self):
        self.c.send("full")

    def half(self):
        self.c.send("half")

    def quater(self):
        self.c.send("quater")

    def one(self):
        self.c.send("one")

class Speech:
    def __init__(self) -> None:
        self.present = False
        self.first_seen = None
        self.time_lost = None
        self.on_detect_flag = True
        self.on_loss_flag = True
        self.last_played = time() - 5.0 # jank

        self.on_detect = [
            "target_acquired.mp3",
            "there_you_are.mp3",
            "i_see_you.mp3",
            #"hello_friend.mp3",
            #"whos_there.mp3",
        ]

        self.on_loss = [
            "are_you_still_there.mp3",
            "is_anyone_there.mp3",
            #"shutting_down.mp3",
            "searching.mp3",
            #"nap_time.mp3",
            "sentry_mode_activated.mp3",
        ]

    def update(self, faces):
        if len(faces) != 0:
            if not self.present:
                self.first_seen = time()
                self.on_detect_flag = True
                self.present = True
            else:
                current = time()
                if current - self.first_seen > 2.0:
                    self.time_lost = None
                    self.present = True
                    if self.on_detect_flag and current - self.last_played > 2.0:
                        t = threading.Thread(target=playsound, args=["audio/" + sample(self.on_detect, 1)[0]])
                        t.start()
                        self.on_detect_flag = False
                        self.on_loss_flag = True
                        self.last_played = time()
        elif self.present:
            if self.time_lost == None:
                self.time_lost = time()
                self.on_loss_flag = True
            else:
                current = time()
                if current - self.time_lost > 2.0:
                    self.present = False
                    self.first_seen = None
                    if self.on_loss_flag and current - self.last_played > 2.0:
                        t = threading.Thread(target=playsound, args=["audio/" + sample(self.on_loss, 1)[0]])
                        t.start()
                        self.on_loss_flag = False
                        self.on_detect_flag = True
                        self.last_played = time()

class Brain():
    class State(Enum):
        SEARCHING = 1
        TRACKING = 2

    def __init__(self):
        self.cap = cv.VideoCapture(4)

        #https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
        self.face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

        self.known_faces = []

        self.start_time = time()
        self.last_time = None

        self.state = Brain.State.SEARCHING


    def update(self, t: Turret, s: Speech = None) -> bool:
        _, frame = self.cap.read()
        frame = imutils.rotate_bound(frame, t.image_rotation())
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for x, y, w, h in faces:
            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        if s != None:
            s.update(faces)

        if self.state == Brain.State.TRACKING:
            self.track(t, frame, faces)            
        elif self.state == Brain.State.SEARCHING:
            self.search(t, faces)

        cv.imshow("video", frame)
        if cv.waitKey(1) == 27:
            return False

        return True

        
    def search(self, t: Turret, faces):
        if len(faces) != 0:
            if self.last_time != None:
                if time() - self.last_time > 0.25:
                    self.last_time = time()
                    self.start_time = time()
                    self.state = Brain.State.TRACKING
            else:
                self.last_time = time()
        else:
            self.last_time = None
        
        theta = 0
        if t.yaw != 90:
            y = float(t.pitch - 90.0) / 90.0
            x = float(t.yaw - 90.0) / 90.0
            theta = atan2(y, x)
        else:
            if t.pitch > 90:
                theta = 3 * pi / 2
            else:
                theta = pi / 2
    
        y = round(((1.0 + 0.5 * cos(theta - 0.05)) / 2.0) * 180)
        p = round(((1.0 + 0.5 * sin(theta - 0.05)) / 2.0) * 180)
        t.set_pitch(p)
        t.set_yaw(y)


    def track(self, t: Turret, frame, faces):
        tracked_faces = set()
        new_faces = set()

        for (x, y, w, h) in faces:
            for i in range(len(self.known_faces)):
                tx, ty, tw, th, name = self.known_faces[i]
                if (tx - x) + (ty - y) + (tw - w) + (th - h) < 250:
                    self.known_faces[i] = (x, y, w, h, name)
                    tracked_faces.add(i)
                    break
            else:
                new_faces.add((x, y, w, h))
                
        known_faces = [f for i, f in enumerate(self.known_faces) if i in tracked_faces]

        for x, y, w, h in new_faces:
            known_faces.append((x, y, w, h, "Unknown"))

        if len(known_faces) != 0:
            fy, fx, _ = frame.shape
            x, y, w, h, _ = known_faces[0]
            x = x + w / 2
            y = y + h / 2
            xs = (x - (fx + 20) / 2.0) / fx
            ys = (y - (fy + 20) / 2.0) / fy
            t.set_yaw(t.yaw + round(xs * AI_YAW_SPEED))
            t.set_pitch(t.pitch + round(ys * AI_PITCH_SPEED))

            self.last_time = time()
        else:
            if time() - self.last_time > 3.0:
                self.state = Brain.State.SEARCHING
                self.start_time = None
                self.last_time = time()


    def __del__(self):
        self.cap.release()
        cv.destroyAllWindows()

'''
creates a new turret and sets up a pygame window to control the turret
'''
def me():
    pygame.init()

    pygame.display.set_caption("control")
    window_surface = pygame.display.set_mode((800, 800))

    background = pygame.Surface((800, 600))
    background.fill(pygame.Color('#000000'))

    running = True

    t = Turret()

    pitch = 0
    yaw = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                t.half()
            if event.type == pygame.MOUSEBUTTONDOWN:
                t.full()

        x, y = pygame.mouse.get_pos()
        new_yaw = (x / 800) * 180
        new_pitch = (y / 800) * 180

        if new_pitch != pitch:
            pitch = new_pitch
            t.set_pitch(round(pitch))

        if new_yaw != yaw:
            yaw = new_yaw
            t.set_yaw(round(yaw))    

        window_surface.blit(background, (0, 0))

        pygame.display.update()
    
    pygame.display.quit()
    pygame.quit()

'''
creates a new turret and runs a haar cascade to detect and target faces
'''
def ai():
    cap = cv.VideoCapture(4)

    #https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
    face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

    s = Speech()
    t = Turret()

    known_faces = []

    data = pickle.loads(open('face_enc', "rb").read())

    known_encodings = data["encodings"]
    known_names = data["names"]

    last_tracked = time()
    tracking = False

    running = True

    while running:
        _, frame = cap.read()
        frame = imutils.rotate_bound(frame, t.image_rotation())
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        tracked_faces = set()
        new_faces = set()

        for (x, y, w, h) in faces:
            for i in range(len(known_faces)):
                tx, ty, tw, th, name = known_faces[i]
                if (tx - x) + (ty - y) + (tw - w) + (th - h) < 250:
                    known_faces[i] = (x, y, w, h, name)
                    tracked_faces.add(i)
                    break
            else:
                new_faces.add((x, y, w, h))
            
        known_faces = [f for i, f in enumerate(known_faces) if i in tracked_faces]

        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        #rgb = cv.resize(rgb, (0, 0), fx=0.25, fy=0.25)    
        
        for x, y, w, h in new_faces:
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes, model="large")
            if len(encodings) == 0:
                continue
            encoding = encodings[0]
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.6)
            distances = face_recognition.face_distance(known_encodings, encoding)
            idx = np.argmin(distances)
            name = None
            if matches[idx]:
                name = known_names[idx]
            
            known_faces.append((x, y, w, h, name))
            

        for (x, y, w, h, name) in known_faces:
            cv.putText(frame, str(name), (x, y), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        s.update(faces)

        if len(known_faces) != 0:
            fy, fx, _ = frame.shape
            x, y, w, h, _ = known_faces[0]
            x = x + w / 2 + 30
            y = y + h / 2 + 30
            xs = (x - (fx + 20) / 2.0) / fx
            ys = (y - (fy + 20) / 2.0) / fy
            t.set_yaw(t.yaw + round(xs * AI_YAW_SPEED))
            t.set_pitch(t.pitch + round(ys * AI_PITCH_SPEED))
            
            tracking = True
            last_tracked = time()
            #pitch, yaw = xy2py(x + w / 2, y + h / 2)
            #t.set_pitch(round(pitch))
            #t.set_yaw(round(yaw))
        else:
            if time() - last_tracked > 3.0:
                tracking = False
            
            start = time()

            first_seen = None

            while not tracking:
                _, frame = cap.read()
                frame = imutils.rotate_bound(frame, t.image_rotation())
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) != 0:
                    if first_seen != None:
                        if time() - first_seen > 0.5:
                            tracking = True
                            break
                    else:
                        first_seen = time()
                else:
                    first_seen = None

                current = time()
                theta = (current - start) / 3.0
                p = round(((1.0 + 0.5 * cos(theta)) / 2.0) * 180)
                y = round(((1.0 + 0.75 * sin(theta)) / 2.0) * 180)
                t.set_pitch(p)
                t.set_yaw(y)

                cv.imshow("video", frame)
                # exit on escape
                if cv.waitKey(1) == 27:
                    running = False
                    break 
                        
        cv.imshow("video", frame)
        # exit on escape
        if cv.waitKey(1) == 27:
            running = False

    cap.release()
    cv.destroyAllWindows()

def ai2():
    t = Turret()
    s = Speech()
    b = Brain()

    while b.update(t, s):
        pass

if __name__ == '__main__':
    #me()
    #ai()
    ai2()