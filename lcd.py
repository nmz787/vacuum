# MBTechWorks.com 2016
# Control an LCD 1602 display from Raspberry Pi with Python programming

#!/usr/bin/python

# Pinout of the LCD:
# 1 : GND
# 2 : 5V power
# 3 : Display contrast - Connect to middle pin potentiometer 
# 4 : RS (Register Select)
# 5 : R/W (Read Write) - Ground this pin (important)
# 6 : Enable or Strobe
# 7 : Data Bit 0 - data pin 0, 1, 2, 3 are not used
# 8 : Data Bit 1 - 
# 9 : Data Bit 2 - 
# 10: Data Bit 3 - 
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V
# 16: LCD Backlight GND

import RPi.GPIO as GPIO
import time

# GPIO to LCD mapping
LCD_RS = 27 # Pi pin 13
LCD_E = 17 # Pi pin 11
LCD_D4 = 25 # Pi pin 22
LCD_D5 = 24 # Pi pin 18
LCD_D6 = 23 # Pi pin 16
LCD_D7 = 22 # Pi pin 15
# Device constants
LCD_CHR = True # Character mode
LCD_CMD = False # Command mode
LCD_CHARS = 16 # Characters per line (16 max)
LCD_LINE_1 = 0x80 # LCD memory location for 1st line
LCD_LINE_2 = 0xC0 # LCD memory location 2nd line

# Define main program cod
def setup_gpio(): 
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM) # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT) # Set GPIO's to output mode
  GPIO.setup(LCD_RS, GPIO.OUT)
  GPIO.setup(LCD_D4, GPIO.OUT)
  GPIO.setup(LCD_D5, GPIO.OUT)
  GPIO.setup(LCD_D6, GPIO.OUT)
  GPIO.setup(LCD_D7, GPIO.OUT)
  # Initialize display
  lcd_init()

def test_loop():
  # Loop - send text and sleep 3 seconds between texts
  # Change text to anything you wish, but must be 16 characters or less
  while True:
    lcd_text("Hello World!",LCD_LINE_1)
    lcd_text("",LCD_LINE_2)
    lcd_text("Rasbperry Pi",LCD_LINE_1)
    lcd_text("16x2 LCD Display",LCD_LINE_2)
    time.sleep(3) # 3 second delay
    lcd_text("ABCDEFGHIJKLMNOP",LCD_LINE_1)
    lcd_text("1234567890123456",LCD_LINE_2)
    time.sleep(3) # 3 second delay

# Initialize and clear display
def lcd_init():
  lcd_write(0x33,LCD_CMD) # Initialize
  lcd_write(0x32,LCD_CMD) # Set to 4-bit mode
  lcd_write(0x06,LCD_CMD) # Cursor move direction
  lcd_write(0x0C,LCD_CMD) # Turn cursor off
  lcd_write(0x28,LCD_CMD) # 2 line display
  lcd_write(0x01,LCD_CMD) # Clear display
  time.sleep(0.0005) # Delay to allow commands to process

def lcd_write(bits, mode):
  # High bits
  GPIO.output(LCD_RS, mode) # RS
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
  # Toggle 'Enable' pin
  lcd_toggle_enable()
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  time.sleep(0.0005)
  GPIO.output(LCD_E, True)
  time.sleep(0.0005)
  GPIO.output(LCD_E, False)
  time.sleep(0.0005)

def lcd_text(message,line):
  # Send text to display
  message = message.ljust(LCD_CHARS," ")
  lcd_write(line, LCD_CMD)
  for i in range(LCD_CHARS):
    lcd_write(ord(message[i]),LCD_CHR)


if __name__=="__main__":
  #Begin program
  try:
    setup_gpio()
    test_loop()
  except KeyboardInterrupt:
    pass 
  finally:
    lcd_write(0x01, LCD_CMD)
    lcd_text("So long!",LCD_LINE_1)
    lcd_text("MBTechWorks.com",LCD_LINE_2)
    GPIO.cleanup()
