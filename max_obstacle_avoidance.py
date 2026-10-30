from microbit import *
import machine
import utime

display.off()

# ==================================================
# MOTOR PINS
# ==================================================

FL1 = pin0
FL2 = pin1

FR1 = pin2
FR2 = pin8

RL1 = pin12
RL2 = pin13

RR1 = pin14
RR2 = pin15


# ==================================================
# ULTRASONIC SENSORS
# ==================================================

FRONT_TRIG = pin9
FRONT_ECHO = pin10

LEFT_TRIG = pin3
LEFT_ECHO = pin5

RIGHT_TRIG = pin7
RIGHT_ECHO = pin16

BACK_TRIG = pin6
BACK_ECHO = pin19


# ==================================================
# SETTINGS
# ==================================================

FRONT_STOP = 22
SIDE_STOP = 12
BACK_STOP = 18

FRONT_CLEAR = 30

BASE_SPEED = 480
MIN_SPEED = 300
MAX_SPEED = 600

CENTER_DEADBAND = 4
STEERING_GAIN = 8

TURN_SPEED = 420
REVERSE_SPEED = 420


# ==================================================
# DISTANCE SENSOR
# ==================================================

def distance_cm(trig, echo):

    trig.write_digital(0)
    utime.sleep_us(3)

    trig.write_digital(1)
    utime.sleep_us(10)

    trig.write_digital(0)

    pulse = machine.time_pulse_us(
        echo,
        1,
        30000
    )

    if pulse > 0:

        cm = int(pulse / 58)

        if cm < 2:
            return 2

        return cm

    return 400


# ==================================================
# SCAN ALL SENSORS
# ==================================================

def scan_all():

    front = distance_cm(
        FRONT_TRIG,
        FRONT_ECHO
    )

    sleep(45)

    left = distance_cm(
        LEFT_TRIG,
        LEFT_ECHO
    )

    sleep(45)

    right = distance_cm(
        RIGHT_TRIG,
        RIGHT_ECHO
    )

    sleep(45)

    back = distance_cm(
        BACK_TRIG,
        BACK_ECHO
    )

    sleep(45)

    print(
        "F:", front,
        "| L:", left,
        "| R:", right,
        "| B:", back
    )

    return front, left, right, back


# ==================================================
# STOP
# ==================================================

def stop():

    FL1.write_digital(0)
    FL2.write_digital(0)

    FR1.write_digital(0)
    FR2.write_digital(0)

    RL1.write_digital(0)
    RL2.write_digital(0)

    RR1.write_digital(0)
    RR2.write_digital(0)


# ==================================================
# SMOOTH FORWARD
# ==================================================

def smooth_forward(left_speed, right_speed):

    # LEFT wheels
    FL1.write_digital(0)
    FL2.write_analog(left_speed)

    RL1.write_digital(0)
    RL2.write_analog(left_speed)

    # RIGHT wheels
    FR1.write_digital(0)
    FR2.write_analog(right_speed)

    RR1.write_digital(0)
    RR2.write_analog(right_speed)


# ==================================================
# REVERSE
# ==================================================

def backward():

    FL1.write_analog(REVERSE_SPEED)
    FL2.write_digital(0)

    FR1.write_analog(REVERSE_SPEED)
    FR2.write_digital(0)

    RL1.write_analog(REVERSE_SPEED)
    RL2.write_digital(0)

    RR1.write_analog(REVERSE_SPEED)
    RR2.write_digital(0)


# ==================================================
# LEFT TURN
# ==================================================

def turn_left():

    FL1.write_analog(TURN_SPEED)
    FL2.write_digital(0)

    RL1.write_analog(TURN_SPEED)
    RL2.write_digital(0)

    FR1.write_digital(0)
    FR2.write_analog(TURN_SPEED)

    RR1.write_digital(0)
    RR2.write_analog(TURN_SPEED)


# ==================================================
# RIGHT TURN
# ==================================================

def turn_right():

    FL1.write_digital(0)
    FL2.write_analog(TURN_SPEED)

    RL1.write_digital(0)
    RL2.write_analog(TURN_SPEED)

    FR1.write_analog(TURN_SPEED)
    FR2.write_digital(0)

    RR1.write_analog(TURN_SPEED)
    RR2.write_digital(0)


# ==================================================
# SAFE REVERSE
# ==================================================

def safe_reverse():

    print("REVERSING")

    backward()

    for i in range(8):

        front, left, right, back = scan_all()

        if back <= BACK_STOP:

            print("BACK BLOCKED")

            stop()

            return False

        if front >= FRONT_CLEAR:

            stop()

            return True

    stop()

    return True


# ==================================================
# SAFE LEFT TURN
# ==================================================

def safe_turn_left():

    print("TURNING LEFT")

    turn_left()

    for i in range(14):

        front, left, right, back = scan_all()

        if left <= SIDE_STOP:

            print("LEFT BLOCKED")

            stop()

            return False

        if back <= BACK_STOP:

            print("BACK BLOCKED")

            stop()

            return False

        if front >= FRONT_CLEAR:

            print("LEFT PATH CLEAR")

            stop()

            return True

    stop()

    return False


# ==================================================
# SAFE RIGHT TURN
# ==================================================

def safe_turn_right():

    print("TURNING RIGHT")

    turn_right()

    for i in range(14):

        front, left, right, back = scan_all()

        if right <= SIDE_STOP:

            print("RIGHT BLOCKED")

            stop()

            return False

        if back <= BACK_STOP:

            print("BACK BLOCKED")

            stop()

            return False

        if front >= FRONT_CLEAR:

            print("RIGHT PATH CLEAR")

            stop()

            return True

    stop()

    return False


# ==================================================
# FIND NEW PATH
# ==================================================

def find_path():

    stop()

    sleep(100)

    front, left, right, back = scan_all()

    # First create some room behind
    if back > BACK_STOP:

        safe_reverse()

        front, left, right, back = scan_all()

    # Choose more open side
    if left > right:

        print("MORE SPACE LEFT")

        success = safe_turn_left()

        if not success:

            front, left, right, back = scan_all()

            if right > SIDE_STOP:
                safe_turn_right()

    else:

        print("MORE SPACE RIGHT")

        success = safe_turn_right()

        if not success:

            front, left, right, back = scan_all()

            if left > SIDE_STOP:
                safe_turn_left()


# ==================================================
# START
# ==================================================

stop()

sleep(1000)

print("MAX READY")


# ==================================================
# MAIN LOOP
# ==================================================

while True:

    front, left, right, back = scan_all()


    # ==============================================
    # FRONT OBSTACLE
    # ==============================================

    if front <= FRONT_STOP:

        print("FRONT BLOCKED")

        stop()

        find_path()

        continue


    # ==============================================
    # EMERGENCY SIDE PROTECTION
    # ==============================================

    if left <= 6:

        print("LEFT EMERGENCY")

        stop()

        if right > SIDE_STOP:

            safe_turn_right()

        else:

            find_path()

        continue


    if right <= 6:

        print("RIGHT EMERGENCY")

        stop()

        if left > SIDE_STOP:

            safe_turn_left()

        else:

            find_path()

        continue


    # ==============================================
    # HALLWAY CENTERING
    # ==============================================

    difference = right - left


    # Robot centred
    if abs(difference) <= CENTER_DEADBAND:

        print("CENTRED")

        smooth_forward(
            BASE_SPEED,
            BASE_SPEED
        )


    # Too close to LEFT wall
    elif left < right:

        correction = difference * STEERING_GAIN

        if correction > 120:
            correction = 120

        left_speed = BASE_SPEED + correction
        right_speed = BASE_SPEED - correction

        if left_speed > MAX_SPEED:
            left_speed = MAX_SPEED

        if right_speed < MIN_SPEED:
            right_speed = MIN_SPEED

        print("GENTLE RIGHT")

        smooth_forward(
            left_speed,
            right_speed
        )


    # Too close to RIGHT wall
    else:

        correction = (-difference) * STEERING_GAIN

        if correction > 120:
            correction = 120

        left_speed = BASE_SPEED - correction
        right_speed = BASE_SPEED + correction

        if left_speed < MIN_SPEED:
            left_speed = MIN_SPEED

        if right_speed > MAX_SPEED:
            right_speed = MAX_SPEED

        print("GENTLE LEFT")

        smooth_forward(
            left_speed,
            right_speed
        )
