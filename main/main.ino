#include <AccelStepper.h>
#include <CmdMessenger.h>
#include <Servo.h>

// init stepper motor
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

#define HALFSTEP 8

#define motorPin1 3
#define motorPin2 4
#define motorPin3 5
#define motorPin4 6

#define FULL_TURN 4200

AccelStepper stepper(HALFSTEP, motorPin1, motorPin3, motorPin2, motorPin4);

void init_stepper() {
  stepper.setMaxSpeed(1000.0);
  stepper.setAcceleration(1500.0);
}

// init servos
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

#define PITCH_PIN 8
#define YAW_PIN 9

Servo pitch_servo;
Servo yaw_servo;

void init_servos() {
  pitch_servo.attach(PITCH_PIN);
  yaw_servo.attach(YAW_PIN);
}

// init serial communication
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

enum {
  full,
  half,
  quater,
  one,
  set_speed,
  set_pitch,
  set_yaw,
};

const int BAUD_RATE = 9600;
CmdMessenger c = CmdMessenger(Serial,',',';','/');

void init_serial() {
  Serial.begin(BAUD_RATE);
  c.attach(full, on_full);
  c.attach(half, on_half);
  c.attach(quater, on_quater);
  c.attach(one, on_one);
  c.attach(set_speed, on_set_speed);
  c.attach(set_pitch, on_set_pitch);
  c.attach(set_yaw, on_set_yaw);
}

void on_full() {
  stepper.move(FULL_TURN);
}

void on_half() {
  stepper.move(FULL_TURN / 2);
}

void on_quater() {
  stepper.move(FULL_TURN / 4);
}

void on_one() {
  stepper.move(FULL_TURN / 16);
}

void on_set_speed() {
  float speed = c.readBinArg<float>();

  stepper.setSpeed(speed);
}

void on_set_yaw() {
  int yaw = c.readBinArg<int>();

  yaw_servo.write(yaw);
}

void on_set_pitch() {
  int pitch = c.readBinArg<int>();

  pitch_servo.write(pitch);
}

// boiler plate
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------
// ------------------------------------------------------------------------

void setup() {
  init_stepper();
  init_servos();
  init_serial();
}

void loop() {
  stepper.run();
  c.feedinSerialData();
}
