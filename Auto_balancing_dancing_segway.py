import pyb
from pyb import Pin, Timer, ADC, DAC, LED
import micropython    #for interrupt
import time
import machine

from oled_938 import OLED_938
from array import *
from motor import DRIVE

machine.disable_irq()
micropython.alloc_emergency_exception_buf(100)

#initialise various peripherals e.g. OLED, IMU etc
oled = OLED_938(pinout={'sda': 'Y10', 'scl': 'Y9', 'res': 'Y8'}, height=64,
                   external_vcc=False, i2c_devid=60)

motor = DRIVE()

#initialise different constants, variables, arrays etc

# define ports for microphone, LEDs and trigger out (X5)
mic = ADC(Pin('Y11'))
MIC_OFFSET = 1523		# ADC reading of microphone for silence
dac = pyb.DAC(1, bits=12)  # Output voltage on X5 (BNC) for debugging
b_LED = LED(4)		# flash for beats on blue LED

N = 160				# size of sample buffer s_buf[]
s_buf = array('H', 0 for i in range(N))  # reserve buffer memory
ptr = 0				# sample buffer index pointer
buffer_full = False	# semaphore - ISR communicate with main program

def flash():		# routine to flash blue LED when beat detected
	b_LED.on()
	pyb.delay(30)
	b_LED.off()
	
def energy(buf):	# Compute energy of signal in buffer
	sum = 0
	for i in range(len(buf)):
		s = buf[i] - MIC_OFFSET	# adjust sample to remove dc offset
		sum = sum + s*s			# accumulate sum of energy
	return sum


# ---- The following section handles interrupts for sampling data -----
# Interrupt service routine to fill sample buffer s_buf
def isr_sampling(dummy): 	# timer interrupt at 8kHz
	global ptr				# need to make ptr visible inside ISR
	global buffer_full		# need to make buffer_full inside ISR
	global s_buf
	global mic

	s_buf[ptr] = mic.read()	# take a sample every timer interrupt
	ptr += 1				# increment buffer pointer (index)
	if (ptr == N):			# wraparound ptr - goes 0 to N-1
		ptr = 0
		buffer_full = True	# set the flag (semaphore) for buffer full

# Create timer interrupt - one every 1/8000 sec or 125 usec
#pyb.disable_irq()
sample_timer = pyb.Timer(7, freq=8000)	# set timer 7 for 8kHz
sample_timer.callback(isr_sampling)		# specify interrupt service routine
machine.disable_irq()
#pyb.enable_irq()

# Define constants for main program loop - shown in UPPERCASE
M = 50						# number of instantaneous energy epochs to sum
BEAT_THRESHOLD = 2.0		# threshold for c to indicate a beat
SILENCE_THRESHOLD = 1.3		# threshold for c to indicate silence

# initialise variables for main program loop
e_ptr = 0					# pointer to energy buffer
e_buf = array('L', 0 for i in range(M))	# reserve storage for energy buffer
sum_energy = 0				# total energy in last 50 epochs
#oled.draw_text(0,20, 'Ready to GO')	# Useful to show what's happening?
#oled.display()
pyb.delay(100)
#tic = pyb.millis()			# mark time now in msec

#Read the dancing steps from file into array

f = open ("dance.txt", "r") # open myfile.txt and assign to file object f
data = f.read()
array = []
n = 1  #index to write the mov in array

for mov in data:
     #print(mov)     # print one line at a time in f until end-of-file
    array.insert(n, mov)
    n +=1 
f.close()        # close the file

# Wait for the user to switch pressed

oled.poweron()
oled.init_display()
oled.draw_text(0, 0, 'Sibylle')
oled.draw_text(0, 10, 'Challenge 4: Dancing')
oled.draw_text(0, 20, 'Press USR button')
oled.display()

mic.read()
print('Performing Challenge 4')
print('Waiting for button press')
trigger = pyb.Switch()    #create trigger switch object
while not trigger():
    time.sleep(0.001)
while trigger(): pass  #wait for release
print('Button pressed - Running')

 #rest of programm
tic = pyb.millis()   #mark time now in msec
i = 0  #index to read the movements

machine.enable_irq()
try:                #try to handle exception
    while True:				# Main program loop
        if buffer_full:		# semaphore signal from ISR - set if buffer is full
            print("full buffer")
            # Calculate instantaneous energy
            E = energy(s_buf)

            # compute moving sum of last 50 energy epochs
            sum_energy = sum_energy - e_buf[e_ptr] + E
            e_buf[e_ptr] = E		# over-write earlest energy with most recent
            e_ptr = (e_ptr + 1) % M	# increment e_ptr with wraparound - 0 to M-1
		
            # Compute ratio of instantaneous energy/average energy
            c = E*M/sum_energy
            dac.write(min(int(c*4095/3), 4095)) 	# useful to see on scope, can remove

            if (pyb.millis()-tic > 500):	# if more than 500ms since last beat
                if (c>BEAT_THRESHOLD):		# look for a beat
                    flash()					# beat found, flash blue LED
                    if (array[i] == "F"):
                        motor.set_speed(125)
                        i += 1
                    elif (array[i] == "B"):
                        motor.set_speed(-125)
                        i += 1
                    elif (array[i] == "R"):
                        motor.right_forward()
                        i += 1
                    elif (array[i] == "L"):
                        motor.left_forward()
                        i += 1
                    motor.drive() 
                    tic = pyb.millis()		# reset tic
            dac.write(0)					# sueful to see on scope, can remove
            buffer_full = False				# reset status flag
finally:        #always executed if exception
    machine.disable_irq()
    motor.stop()