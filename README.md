# elastic
Elastic band gun equipt with facial recognition

# Thoughts
The design was done in blender which was a mistake. I need to learn a cad program. Additionally the pitch and yaw was applied in the wrong order which meant that the video stream had to be counter rotated to get the haar cascade to work.

Initially I planned to catagorise people via faces into friendly and not friendly via a database. The single threaded implementation turned out to be too slow for real time usage but multithreading the clasification and tracking the face as unknown until the second thread completes should provide a method for classifying people.

# Software
- Put photos of yourself into the db directory then run
- Upload main.ino to the arduino and check the port, if not ttyACM0 then change the constant in main.py
```bash
git clone https://github.com/JeremyS2002/elastic.git && cd elastic
./download.sh
python3 embed.py
python3 main.py
```

## Hardware
- Arduino Uno
- 28BYJ-48 stepper motor
- ULN2003 stepper driver
- MG 996R servo motor
- Light webcam (I don't know the name of the one I have)

Wiring
Pitch servo control wire (Orange) pin 8
Yaw servo control wire (Orange) pin 9
Motor driver 
- IN1 pin 3
- IN2 pin 4
- IN3 pin 5
- IN4 pin 6

![photo1](/images/IMG_20210521_181749.jpg)
![photo2](/images/IMG_20210521_181752.jpg)
