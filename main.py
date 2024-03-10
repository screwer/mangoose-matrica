#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep
#import signal
import atexit

#----------------------------------------------------------------------------------------

class Pin:
    battery     = 29    # GPIO 5    +12v battery line
    acc         = 31    # GPIO 6    +12v ACC line
    sw_1        = 33    # GPIO 13   door/hood limit switch
    sw_2        = 35    # GPIO 19   door/hood limit switch
    btn         = 37    # GPIO 26   emergancy button

#----------------------------------------------------------------------------------------
'''
def handler(signum, frame):
    GPIO.cleanup()
    exit(1)

signal.signal(signal.SIGINT, handler)
'''
#----------------------------------------------------------------------------------------

def battery_detach():
    GPIO.output(Pin.battery,GPIO.HIGH)

def battery_attach():
    GPIO.output(Pin.battery,GPIO.LOW)

def turn_acc_off():
    print('turn acc OFF')
    GPIO.output(Pin.acc,    GPIO.HIGH)

def turn_acc_on():
    print('turn acc ON')
    GPIO.output(Pin.acc,    GPIO.LOW)

def switch1_open():
    GPIO.output(Pin.sw_1,   GPIO.HIGH)

def switch1_close():
    GPIO.output(Pin.sw_1,   GPIO.LOW)

def switch2_open():
    GPIO.output(Pin.sw_2,   GPIO.HIGH)

def switch2_close():
    GPIO.output(Pin.sw_2,   GPIO.LOW)

def btn_unpress():
    GPIO.output(Pin.btn,    GPIO.HIGH)

def btn_press():
    GPIO.output(Pin.btn,    GPIO.LOW)

#----------------------------------------------------------------------------------------

def cleanup():

    print('Cleaning up')
    turn_acc_off()
    battery_detach()
    switch1_close()
    switch2_close()
    btn_unpress()

#----------------------------------------------------------------------------------------

def init(do_cleanup=True):

    if do_cleanup:
        atexit.register(cleanup)

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Pin.battery, GPIO.OUT)
    GPIO.setup(Pin.acc,     GPIO.OUT)
    GPIO.setup(Pin.sw_1,    GPIO.OUT)
    GPIO.setup(Pin.sw_2,    GPIO.OUT)
    GPIO.setup(Pin.btn,     GPIO.OUT)

#----------------------------------------------------------------------------------------
#
# Simulate emergency key pressing
#
def keypress_btn():
    btn_press()
    sleep(0.2)
    btn_unpress()
    sleep(0.3)

#----------------------------------------------------------------------------------------
#
# Simulate emergency key pressing by N times
#
def keypress_btn_n(n):
    print('keypressing %d' % n)
    for i in range(n):
        keypress_btn()
        
#----------------------------------------------------------------------------------------
#
# Trun ACC line OFF, then ON
#
def blink_off_acc():
    turn_acc_off()
    sleep(0.5)
    turn_acc_on()
    sleep(0.5)

#----------------------------------------------------------------------------------------
#
# Entering mode number by emergency keypressing and ACC switching
#
def enter_mode(num_1, num_2):
    print('Entring mode %d-%d' % (num_1, num_2))
    if num_1 > 0:
        keypress_btn_n(num_1)
        blink_off_acc()
    keypress_btn_n(num_2)
    
#----------------------------------------------------------------------------------------
#
# Entring PIN code
#
def enter_pin(pin, ):
    num_1 = (pin // 10)
    num_2 = (pin % 10)
    enter_mode(num_1, num_2)
    turn_acc_off()

#----------------------------------------------------------------------------------------
#
# Bruteforce all PIN combinations (90 in total: 9 (single digit) + 9*9 (double digits)
# No any feedback for automaion here. You can connect LED from alarm system module,
# and track all fast double-blinks (they means wrong PIN)
#
def bruteforce_pin():
    index = 0
    while index < 90:

        while True:
            num_1 = index // 9
            num_2 = (index % 9) + 1

            pin = (num_1 * 10) + num_2
            msg = 'Can test PIN=%d (%d, %d, %d) ? ' % (pin, index, num_1, num_2)

            s = input(msg)
            if 'n' != s:
                break
            index -= 1

        enter_mode(num_1, num_2)
        pin += 1

#----------------------------------------------------------------------------------------
#
# In such mode, press btn-1 on alarm RC key, to add it into allowed list
#
def enter_key_programming(pin):

    input('prepare turn ON acc')
    turn_acc_on()
    input('ACC ON')

    enter_pin(pin)
    turn_acc_on()
    input('Entered key programming mode')

#----------------------------------------------------------------------------------------

def finish_key_programming():
    turn_acc_off()
    keypress_btn()

#----------------------------------------------------------------------------------------

def enter_function_programming(pin):

    enter_key_programming(pin)
    
    turn_acc_off()
    input('Entering in function mode')
    sleep(0.5)
    turn_acc_on()
    print('Now function can be programmed')

#----------------------------------------------------------------------------------------
#
# Prerequisities: system in function programming mode
#
def progfunc_change_PIN():

    enter_mode(3, 1)

    print('Ready for set new PIN')
    input('On current remote: press btn1 for TENs, pross btn2 for UNITs')

    turn_acc_off()

#----------------------------------------------------------------------------------------
#
# Prerequisities: system in function programming mode
#
def progfunc_clear_all_remotes():

    enter_mode(3, 2)

    print('Ready for clear all remotes!')
    input('On current remote: press buttons 1 and 2 together!')

    turn_acc_off()

#----------------------------------------------------------------------------------------
#
# Complete sequence of programming new keys
#
def seq_add_key(pin):

    enter_key_programming(pin)
    finish_key_programming()

#----------------------------------------------------------------------------------------
#
# Complete sequence to test alarm via toggling switches
#
def seq_alarm():
    print('Lock ON and go test switches')

    while True:
        input('prepare to open SW1')    
        switch1_open()                      

        input('prepare to close SW1')
        switch1_close()

        input('prepare to open SW2')
        switch2_open()

        input('prepare to close SW2')
        switch2_close()

#----------------------------------------------------------------------------------------
#
# Complete sequence to test emergency OFF by entering PIN
#
def seq_test_pin(pin):

    input('prepare to alarm')
    switch1_open()

    input('prepare to input PIN')
    turn_acc_on()    
    sleep(0.5)
    enter_pin(pin)

    input('prepare to SW1 close')
    switch1_close()

#----------------------------------------------------------------------------------------

def main():

    init()
    switch1_close()
    switch2_close()

    input('Initialized, prepare sttach battery')
    battery_attach()
    print('Battery attached')

    #pin = 11
    #seq_add_key(pin)
    #seq_alarm()
    seq_test_pin(pin)



    #enter_function_programming(pin)
    #progfunc_clear_all_remotes()
    #progfunc_change_PIN()

    input('exiting')

#----------------------------------------------------------------------------------------

main()