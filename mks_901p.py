"""
usage: mks_901p.py [-h] [--find_baud] [--baud BAUD] [-unit] serial_port

positional arguments:
  serial_port  the Windows COM port or path to a linux serial port

optional arguments:
  -h, --help   show this help message and exit
  --find_baud  tries to access the sensor over all supported baud rates,
               prints which is successful
  --baud BAUD  baud rate to connect with, defaults to 9600 (901p factory
               default)
  -unit        print pressure unit with each reading
"""
# xxx = Transducer communication address (001 to 253. Broadcast addresses: 254, 255)
baud_supported = [4800, 9600, 19200, 38400, 57600, 115200, 230400]
commands = {
    'Communication information': {
        'get_baud_rate': {
            'Command':     '@{}BR?;FF',
            'Response':    '@xxxACK9600;FF', 
            'Explanation': 'Communication baud rate (4800, 9600, 19200, 38400, 57600, 115200,230400)'
        },
        'get_address': {
            'Command':     '@{}AD?;FF',
            'Response':    '@xxxACK253;FF', 
            'Explanation': 'Transducer communication address (001 to 253)'
        },
        'get_comms_delay': {
            'Command':     '@{}RSD?;FF',
            'Response':    '@xxxACKON;FF', 
            'Explanation': 'Communication delay between receive and transmit sequence.'
        }
    },
    'Pressure reading': {
        'pirani': {
            'Command':     '@{}PR1?;FF',
            'Response':    '@xxxACK1.23E-3;FF', 
            'Explanation': 'MicroPirani sensor pressure as 3 digit floating point value.'},
        'piezo': {
            'Command':     '@{}PR2?;FF',
            'Response':    '@xxxACK-7.60E+2;FF',
            'Explanation': 'Piezo differential sensor pressure as 3 digit floating point value.'},
        'combined_3_digit': {
            'Command':     '@{}PR3?;FF',
            'Response':    '@xxxACK1.23E-3;FF', 
            'Explanation': 'Combined reading as 3 digit floating point value.'},
        'combined_4_digit': {
            'Command':     '@{}PR4?;FF',
            'Response':    '@xxxACK1.234E-3;FF',
            'Explanation': 'Combined reading as 4 digit floating point value.'}
    },
    'Setpoint information': {
        'get_setpoint_1_status': {
            'Command':     '@{}SS1?;FF',
            'Response':    '@xxxACKSET;FF',  
            'Explanation': 'Set point relay 1-3 status (SET=Relay energized / CLEAR=Relay deenergized'},
        'get_setpoint_2_status': {
            'Command':     '@{}SS2?;FF',
            'Response':    '@xxxACKSET;FF',  
            'Explanation': 'Set point relay 1-3 status (SET=Relay energized / CLEAR=Relay deenergized'},
        'get_setpoint_3_status': {
            'Command':     '@{}SS3?;FF',
            'Response':    '@xxxACKSET;FF',  
            'Explanation': 'Set point relay 1-3 status (SET=Relay energized / CLEAR=Relay deenergized'},
        'get_setpoint_1': {
            'Command':     '@{}SP1?;FF',
            'Response':    '@xxxACK1.00E-2;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'get_setpoint_2': {
            'Command':     '@{}SP2?;FF',
            'Response':    '@xxxACK1.00E-2;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'get_setpoint_3': {
            'Command':     '@{}SP3?;FF',
            'Response':    '@xxxACK1.00E-2;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'get_hysteresis_1': {
            'Command':     '@{}SH1?;FF',
            'Response':    '@xxxACK1.10E-2;FF',
            'Explanation': 'Set point 1-3 hystereses switch value.'},
        'get_hysteresis_2': {
            'Command':     '@{}SH2?;FF',
            'Response':    '@xxxACK1.10E-2;FF',
            'Explanation': 'Set point 1-3 hystereses switch value.'},
        'get_hysteresis_3': {
            'Command':     '@{}SH3?;FF',
            'Response':    '@xxxACK1.10E-2;FF',
            'Explanation': 'Set point 1-3 hystereses switch value.'},
        'get_setpoint_1_enabled': {
            'Command':     '@{}EN1?;FF',
            'Response':    '@xxxACKDIFF;FF',  
            'Explanation': 'Set point 1-3 enable status ( OFF, DIFF=Piezo differential or ABS=Absolute Piezo)'},
        'get_setpoint_2_enabled': {
            'Command':     '@{}EN2?;FF',
            'Response':    '@xxxACKDIFF;FF',  
            'Explanation': 'Set point 1-3 enable status ( OFF, DIFF=Piezo differential or ABS=Absolute Piezo)'},
        'get_setpoint_3_enabled': {
            'Command':     '@{}EN3?;FF',
            'Response':    '@xxxACKDIFF;FF',  
            'Explanation': 'Set point 1-3 enable status ( OFF, DIFF=Piezo differential or ABS=Absolute Piezo)'},
        'get_setpoint1_relay_direction': {
            'Command':     '@{}SD1?;FF',
            'Response':    '@xxxACKBELOW;FF',  
            'Explanation': 'Set point relay direction (ABOVE or BELOW) If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'get_setpoint2_relay_direction': {
            'Command':     '@{}SD2?;FF',
            'Response':    '@xxxACKBELOW;FF',  
            'Explanation': 'Set point relay direction (ABOVE or BELOW) If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'get_setpoint3_relay_direction': {
            'Command':     '@{}SD3?;FF',
            'Response':    '@xxxACKBELOW;FF',  
            'Explanation': 'Set point relay direction (ABOVE or BELOW) If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'get_setpoint_safety_delay': {
            'Command':     '@{}SPD?;FF',
            'Response':    '@xxxACKON;FF',  
            'Explanation': 'Setpoint safety delay'}
    },
    'Transducer information': {
        'get_model': {
            'Command':     '@{}MD?;FF',
            'Response':    '@xxxACK901P;FF',
            'Explanation': 'Model number (901P)'},
        'get_devicetype': {
            'Command':     '@{}DT?;FF',
            'Response':    '@xxxACKLoadlock;FF',
            'Explanation': 'Device type name (MicroPirani)'},
        'get_mfg': {
            'Command':     '@{}MF?;FF',
            'Response':    '@xxxACKMKS;FF',
            'Explanation': 'Manufacturer name (MKS)'},
        'get_hw_version': {
            'Command':     '@{}HV?;FF',
            'Response':    '@xxxACKA;FF',
            'Explanation': 'Hardware version'},
        'get_fw_version': {
            'Command':     '@{}FV?;FF',
            'Response':    '@xxxACK1.00;FF',
            'Explanation': 'Firmware version'},
        'get_serial_num': {
            'Command':     '@{}SN?;FF',
            'Response':    '@xxxACK08350123456;FF',
            'Explanation': 'Serial number'},
        'get_switch': {
            'Command':     '@{}SW?;FF',
            'Response':    '@xxxACKON;FF',
            'Explanation': 'Switch enable'},
        'get_time_on': {
            'Command':     '@{}TIM?;FF',
            'Response':    '@xxxACK12345;FF',
            'Explanation': 'Time on (hours of operation )'},
        'get_pirani_temp': {
            'Command':     '@{}TEM?;FF',
            'Response':    '@xxxACK2.50E+1;FF',
            'Explanation': 'MicroPirani sensor temperature'},
        'get_usertext': {
            'Command':     '@{}UT?;FF',
            'Response':    '@xxxACKVACUUM1;FF',
            'Explanation': 'User programmed text string'},
        'get_status': {
            'Command':     '@{}T?;FF',
            'Response':    '@xxxACKO;FF',
            'Explanation': 'Transducer status check'}
    },
    'Calibration and adjustment information': {
        'get_pressure_unit': {
            'Command':     '@{}U?;FF',
            'Response':    '@xxxACKTORR;FF',
            'Explanation': 'Pressure unit setup (Torr, mbar or Pascal)'},
        'get_calibration_gas': {
            'Command':     '@{}GT?;FF',
            'Response':    '@xxxACKNITROGEN;FF',
            'Explanation': 'MicroPirani sensor calibration gas (Nitrogen, Air, Argon, Helium, Hydrogen, H2O, Neon, CO2, Xenon)'},
        'get_factory_diff_zero_point': {
            'Command':     '@{}VAC?;FF',
            'Response':    '@xxxACK5.12E-5;FF',
            'Explanation': 'Provides delta pressure value between current vacuum zero adjustment and factory calibration.'},
        'get_factory_diff_atmosphere': {
            'Command':     '@{}ATM?;FF',
            'Response':    '@xxxACK1.22E+1;FF',
            'Explanation': 'Provides delta pressure value between current atmospheric adjustment and factory calibration.'},
        'get_analog_out_1': {
            'Command':     '@{}AO1?;FF',
            'Response':    '@xxxACK10;FF',
            'Explanation': 'Analog voltage output 1: Pressure assignment and calibration. (first digit is pressure assignment, second and third digit is calibration)'},
        'get_analog_out_2': {
            'Command':     '@{}AO2?;FF',
            'Response':    '@xxxACK10;FF',
            'Explanation': 'Analog voltage output 2: Pressure assignment and calibration. (first digit is pressure assignment, second and third digit is calibration)'}
    },
    'Setpoint setup and configuration': {
        'set_setpoint_1':{
            'Command':     '@{}SP1!2.00E+1;FF',
            'Response':    '@xxxACK2.00E+1;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'set_setpoint_2':{
            'Command':     '@{}SP2!2.00E+1;FF',
            'Response':    '@xxxACK2.00E+1;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'set_setpoint_3':{
            'Command':     '@{}SP3!2.00E+1;FF',
            'Response':    '@xxxACK2.00E+1;FF',
            'Explanation': 'Set point 1-3 switch value.'},
        'set_hysteresis_1':{
            'Command':     '@{}SH1!5.00E+1;FF',
            'Response':    '@xxxACK5.00E+1;FF',
            'Explanation': 'Set point 1-3 hysteresis switch value.'},
        'set_hysteresis_2':{
            'Command':     '@{}SH2!5.00E+1;FF',
            'Response':    '@xxxACK5.00E+1;FF',
            'Explanation': 'Set point 1-3 hysteresis switch value.'},
        'set_hysteresis_3':{
            'Command':     '@{}SH3!5.00E+1;FF',
            'Response':    '@xxxACK5.00E+1;FF',
            'Explanation': 'Set point 1-3 hysteresis switch value.'},
        'enable_setpoint_1':{
            'Command':     '@{}EN1!ON;FF',
            'Response':    '@xxxACKON;FF',
            'Explanantion': 'Set point 1-3 enable status (ON or OFF)'},
        'enable_setpoint_2':{
            'Command':     '@{}EN2!ON;FF',
            'Response':    '@xxxACKON;FF',
            'Explanantion': 'Set point 1-3 enable status (ON or OFF)'},
        'enable_setpoint_3':{
            'Command':     '@{}EN3!ON;FF',
            'Response':    '@xxxACKON;FF',
            'Explanantion': 'Set point 1-3 enable status (ON or OFF)'},
        'set_setpoint1_relay_direction':{
            'Command':     '@{}SD1!BELOW;FF',
            'Response':    '@xxxACKBELOW;FF',
            'Explanation': 'Set point relay direction (ABOVE or BELOW). If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'set_setpoint2_relay_direction':{
            'Command':     '@{}SD2!BELOW;FF',
            'Response':    '@xxxACKBELOW;FF',
            'Explanation': 'Set point relay direction (ABOVE or BELOW). If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'set_setpoint3_relay_direction':{
            'Command':     '@{}SD3!BELOW;FF',
            'Response':    '@xxxACKBELOW;FF',
            'Explanation': 'Set point relay direction (ABOVE or BELOW). If set to above relay will be energized above setpoint value. If set to below relay will be energized below setpoint value.'},
        'set_setpoint_safety_delay':{
            'Command':     '@{}SPD!ON;FF',
            'Response':    '@xxxACKON;FF',
            'Explanation': 'Setpoint safety delay (prevent pulse trig of setpoint)'}
    },
    'Communication setup': {
        'set_baud_rate': {
            'Command':     '@{}BR!19200;FF',
            'Response':    '@xxxACK19200;FF',
            'Explanation': 'Set communication Baud rate (4800, 9600, 19200, 38400, 57600, 115200, 230400)'},
        'set_address': {
            'Command':     '@{}AD!123;FF',
            'Response':    '@xxxACK123;FF',
            'Explanation': 'Set Transducer communication address (001 to 253)'},
        'set_comms_delay': {
            'Command':     '@{}RSD!OFF;FF',
            'Response':    '@xxxACKOFF;FF',
            'Explanation': 'Turn on or off communication delay between receive and transmit sequence.'}
    },
    'Calibration and adjustment': {
        'set_pressure_unit': {
            'Command':     '@{}U!MBAR;FF', 
            'Response':    '@xxxACKMBAR;FF', 
            'Explanation': 'Set pressure unit setup (Torr, mbar, Pascal)'},
        'set_calibration_gas': {
            'Command':     '@{}GT!ARGON;FF', 
            'Response':    '@xxxACKARGON;FF', 
            'Explanation': 'Set MicroPirani sensor calibration gas. (Nitrogen, Air, Argon, Helium, Hydrogen, H2O, Neon, CO2, Xenon)'},
        'perform_pirani_zero_adjustment': {
            'Command':     '@{}VAC!;FF', 
            'Response':    '@xxxACK;FF', 
            'Explanation': 'Executes MicroPirani zero adjustment'},
        'perform_pirani_atmosphere_adjustment': {
            'Command':     '@{}ATM!7.60E+2;FF', 
            'Response':    '@xxxACK;FF', 
            'Explanation': 'Executes MicroPirani full scale atmospheric adjustment.'},
        'perform_piezo_absolute_adjustment': {
            'Command':     '@{}ATD!7.60E+2;FF', 
            'Response':    '@xxxACK;FF', 
            'Explanation': 'Executes Piezo absolute reading at zero differential pressure.'},
        'perform_piezo_differential_adjustment': {
            'Command':     '@{}ATZ;FF', 
            'Response':    '@xxxACK;FF', 
            'Explanation': 'Executes Piezo differential zero adjustment'},
        'set_analog_out_1': {
            'Command':     '@{}AO1!10;FF', 
            'Response':    '@xxxACK10;FF', 
            'Explanation': 'Set analog voltage output 1 calibration.'},
        'set_analog_out_2': {
            'Command':     '@{}AO1!10;FF', 
            'Response':    '@xxxACK10;FF', 
            'Explanation': 'Set analog voltage output 2 calibration.'}
    },
    'Information setup': {
        'set_user_tag':{
            'Command':     '@{}UT!LOADLOCK;FF',
            'Response':    '@xxxACKLOADLOCK;FF',
            'Explanation': 'Set transducer user tag'
        }
    },
    'User Switch': {
        'set_userswitch_on_off': {
            'Command':     '@{}SW!ON;FF',
            'Response':    '@xxxACKON;FF',
            'Explanation': 'Enable / disable user switch'
        }
    }
}

error_responses = [
    ['NAK Code', 'Error',                                      'description'],
    ['8',        'Zero adjustment at too high pressure',       '@253VAC!;FF'],
    ['9',        'Atmospheric adjustment at too low pressure', '@253ATM!7.60;FF'],
    ['160',      'Unrecognized message',                       '@253S%;FF'],
    ['169',      'Invalid argument',                           '@253EN1!of;FF'],
    ['172',      'Value out of range',                         '@253SP1!5.00E+9;FF'],
    ['175',      'Command/query character invalid',            '@253FV!;FF'],
    ['180',      'Not in setup mode (locked)',                 '-'],
]


# xxx = Transducer communication address (001 to 253. Broadcast addresses: 254, 255)
broadcast_address_1 = 254  # 254 WILL cause any listening sensors to reply
broadcast_address_2 = 255  # 255 will NOT cause any listening sensors to reply

DEBUG = False

import serial
class Mks901P(object):
    def __init__(self, com_port_name, baud=9600):
        self.com_port_name = com_port_name
        if DEBUG:
            print('creating new MKS 901p object with baud of {}'.format(baud))
        self.serial_port = serial.Serial(com_port_name, baudrate=baud, timeout=1)
        #self.serial_port.read()
        self.pressure_unit = None

    def get_pressure_unit(self, address=broadcast_address_1):
        cmd = commands['Calibration and adjustment information']['get_pressure_unit']
        expect = cmd['Response']
        cmd = cmd['Command']
        output = self.send_cmd(cmd, expect, address)
        if output:
            self.pressure_unit = output[1]
            return self.pressure_unit

    def get_pressure_combined_4_digit(self, address=broadcast_address_1, return_address=False):
        cmd = commands['Pressure reading']['combined_4_digit']['Command']
        expect = commands['Pressure reading']['combined_4_digit']['Response']
        output = self.send_cmd(cmd, expect, address)
        if output and not return_address:
            return output[1]
        return output

    def send_cmd(self, cmd, expected_response, address):
        cmd = cmd.format(address)
        if not self.serial_port:
            return('no connection')
        self.serial_port.write(bytes(cmd.encode()))
        raw_data = self.serial_port.read(len(expected_response))
        data = raw_data.decode()
        if 'ACK' in data:
            addr = data[data.index('@')+len('@'):data.index('ACK')]
            value = data[data.index('ACK')+len('ACK'):].split(';')[0]
            return (addr,value)
        else:
            if DEBUG:
                print('no ACK received from cmd')
            return None


import os
import sys
import time
from ds18b20 import DS18B20	

this_files_path = os.path.abspath(__file__)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("serial_port", help='the Windows COM port or path to a linux serial port')
    parser.add_argument("--find_baud", help='tries to access the sensor over all supported baud rates, prints which is successful', action="store_true")
    parser.add_argument("--baud", help='baud rate to connect with, defaults to 9600 (901p factory default)', type=int)
    parser.add_argument("-unit", help='print pressure unit with each reading', action="store_true")
    parser.add_argument("-pi_lcd", help='print pressure to RasPi LCD', action="store_true")
    parser.add_argument("-sleep", help='amount to sleep between pressure readings, default 1 second', type=int)
    args = parser.parse_args()
    com_port = args.serial_port
    if args.find_baud and not args.baud:
        from subprocess import STDOUT, check_output, TimeoutExpired
        for baud in baud_supported:
            print("attempting to ask MKS 901p for it's baudrate using baudrate of {}".format(baud))
            cmd = [sys.executable, this_files_path, com_port, '--find_baud', '--baud={}'.format(baud)]
            try:
                output = check_output(cmd, stderr=STDOUT, timeout=1)
                if output:
                    output = output.decode().split(',')
                    output = [o.strip("() '\n") for o in output]
                    print('sensor ({}) replied with baudrate of ({})'.format(output[0], output[1]))
                    break
            except TimeoutExpired:
                pass
    elif args.find_baud and args.baud:
        if DEBUG:
            print('setting up connection using baudrate of: {}'.format(args.baud))
        m = Mks901P(com_port, args.baud)
        cmd = commands['Communication information']['get_baud_rate']['Command']
        expect = commands['Communication information']['get_baud_rate']['Response']
        print(m.send_cmd(cmd, expect, broadcast_address_1))
    else:
        if args.baud:
            m = Mks901P(com_port, args.baud)
        else:
            m = Mks901P(com_port)
        unit = ''
        sleep_time = 1
        if args.sleep:
            sleep_time = args.sleep
        if args.unit:
            unit = ' {}'.format(m.get_pressure_unit())
        if args.pi_lcd:
            import lcd
            lcd.setup_gpio()
            x = DS18B20()
            count=x.device_count()
            file_prefix = 'pressure_log_'
            num_prev_files = len([item for item in os.listdir('.') if item.startswith(file_prefix)])
            logfile = open(file_prefix+str(num_prev_files), 'w', buffering=128)
            logfile.write(unit+'\n')
            try:
                while True:
                    pressure = '{}'.format(m.get_pressure_combined_4_digit())
                    pressure_float = float(pressure)
                    pressure_string = '{}{}'.format(pressure, unit)
                    temps = ' '.join([str(x.tempC(i)) for i in range(count)])
                    logfile.write('{} {}\n'.format(pressure, temps))
                    lcd.lcd_text(pressure_string, lcd.LCD_LINE_1)
                    lcd.lcd_text('{}'.format(temps), lcd.LCD_LINE_2)
                    time.sleep(sleep_time)
            except KeyboardInterrupt:
                pass 
            finally:
                lcd.lcd_write(0x01, lcd.LCD_CMD)
                import RPi.GPIO as GPIO
                lcd.lcd_text("Reading stopped!", lcd.LCD_LINE_1)
                GPIO.cleanup()
        else:
            while True:
                print('{}{}'.format(m.get_pressure_combined_4_digit(), unit))
                time.sleep(sleep_time)
