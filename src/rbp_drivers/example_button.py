import time
import RPi.GPIO as GPIO

PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    GPIO.wait_for_edge(PIN, GPIO.FALLING)
    print "Pressed"
    start = time.time()
    time.sleep(0.2)

    while GPIO.input(PIN) == GPIO.LOW:
        time.sleep(0.01)
    length = time.time() - start
    print length
