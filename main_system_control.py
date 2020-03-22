import RPi.GPIO as GPIO
from threading import Thread, Event, Timer
from queue import Queue
import time
import lcd


vac_interface = Mks901P(com_port)
pressure_unit = ' {}'.format(vac_interface.get_pressure_unit())
lcd.setup_gpio()
thermal_interface = DS18B20()
thermometer_count = thermal_interface.device_count()
file_prefix = 'pressure_log_'
num_prev_files = len([item for item in os.listdir('.') if item.startswith(file_prefix)])
logfile = open(file_prefix+str(num_prev_files), 'w', buffering=128)
logfile.write(pressure_unit+'\n')


# use P1 header pin numbering convention
GPIO.setmode(GPIO.BCM) #BOARD)
WATER = LEFT = 10 #orange wire, leftmost
FDTS = MIDDLE = 9 #yellow wire, middle
ISOLATION = RIGHT = 11  #brown wire, rightmost from powersupply
GPIO.setup(LEFT, GPIO.OUT)
GPIO.setup(MIDDLE, GPIO.OUT)
GPIO.setup(RIGHT, GPIO.OUT)

# Input from pin 11
#input_value = GPIO.input(11)


vac_msg = Queue()
therm_msg = Queue()
lcd_msg = Queue()
log_msg = Queue()
emergency_stop = False


def read_vac():
    while not emergency_stop:
        pressure = '{}'.format(vac_interface.get_pressure_combined_4_digit())
        pressure_float = float(pressure)
        pressure_string = '{}{}'.format(pressure, pressure_unit)
        vac_msg.put((pressure_float, pressure_string))


def read_therms():
    while not emergency_stop:
        temp_list = [str(thermal_interface.tempC(i)) for i in range(thermometer_count)]
        temp_string = ' '.join(temp_list)
        therm_msg.put(temp_list, temp_string)

def update_LCD():
    while not emergency_stop:
        if lcd_msg.qsize() > 0:
            pressure_string, temperature_string = lcd_msg.get()
            lcd.lcd_text(pressure_string, lcd.LCD_LINE_1)
            lcd.lcd_text(temperature_string, lcd.LCD_LINE_2)

def update_log():
    while not emergency_stop:
        if log_msg.qsize() > 0:
            pressure_string, temperature_string = lcd_msg.get()
            logfile.write('{} {}\n'.format(pressure_string, temperature_string))


phase0_target_pressure = 0.3 # torr
phase1_target_pressure = 5   # torr
phase2_start=False           # doesn't start immediately, there's a delay for reaction to proceed
phase2_start_delay=60        # seconds
phase3_target_pressure = 1   # torr
phase3_degas_done = False    # first opening of FDTS valve will "burp" the air
phase4_fdts_target_pressure = 5
reaction_cycles = 0
max_reaction_cycles = 2

def set_phase2_start():
    phase2_start=True

def set_phase5_start():
    phase5_start=True

def run_deposition():
    while not emergency_stop:
        vac = None
        therm = None
        while vac is None or therm is None:
            if vac_msg.qsize() > 0:
                vac = vac_msg.get()
            if therm_msg.qsize() > 0:
                therm = therm_msg.get()
        pressure_float, pressure_string = vac
        temperature_list, temperature_string = therm
        lcd_msg.put(pressure_string, temperature_string)
        log_msg.put(pressure_string, temperature_string)
        print('Phase: {}'.format(phase))
        if phase==0:
            # wait til vacuum gets to 0.3 torr (3*10^1)
            if pressure_float < phase0_target_pressure:
                # stop pumping the chamber
                GPIO.output(ISOLATION, GPIO.LOW)
                phase=1
        elif phase==1:
            # pulse WATER til it increases to at least 5 torr
            GPIO.output(WATER, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(WATER, GPIO.LOW)
            if pressure_float>phase1_target_pressure:
                Timer(phase2_start_delay, set_phase2_start).start()
                phase=2
        elif phase==2:
            #wait X minutes for surface adsorption before restarting pumpdown
            if phase2_start:
                phase2_start=False
                GPIO.output(ISOLATION, GPIO.HIGH)
                phase = 3
        elif phase==3:
            # wait til vacuum gets to 1 torr
            if pressure_float<phase3_target_pressure:
                if phase3_degas_done:
                    # stop pumping the chamber
                    GPIO.output(ISOLATION, GPIO.LOW)
                    phase3_degas_done = False
                    phase=4
                else:
                    #degas
                    GPIO.output(FDTS, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(FDTS, GPIO.LOW)
                    phase3_degas_done = True
        elif phase==4:
            # pulse FDTS til it increases to at least 5 torr
            GPIO.output(FDTS, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(FDTS, GPIO.LOW)
            if pressure_float > phase4_fdts_target_pressure:
                Timer(phase5_start_delay, set_phase5_start).start()
                phase=5
        elif phase==5:
            #wait X minutes for FDTS to react before restarting pumpdown
            if phase5_start:
                phase5_start=False
                reaction_cycles+=1
                if reaction_cycles>=max_reaction_cycles:
                    break
                else:
                    GPIO.output(ISOLATION, GPIO.HIGH)
                    phase = 0
        #time.sleep(0.1)

print("Starting all deposition support threads")

t1 = Thread(target=read_vac)
t2 = Thread(target=read_therms)
t3 = Thread(target=run_deposition)
t4 = Thread(target=update_LCD)
t5 = Thread(target=update_log)
threads = [t1, t2, t3, t4, t5]

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

# open the isolation valve between the rough pump and the chamber
GPIO.output(ISOLATION, GPIO.HIGH)

try:
    for tloop in threads:
        tloop.join()
except KeyboardInterrupt:
    pass 
finally:
    GPIO.output(WATER, GPIO.LOW)
    GPIO.output(FDTS, GPIO.LOW)
    GPIO.output(ISOLATION, GPIO.LOW)
    emergency_stop = True
    lcd.lcd_write(0x01, lcd.LCD_CMD)
    lcd.lcd_text("Vacuum System Stopped!", lcd.LCD_LINE_1)
    GPIO.cleanup()

print("End of Vacuum System Control Code")
