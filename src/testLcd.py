import lcdrw1063 as LCD
from time import sleep


# Test Display

display = LCD.Lcd()
custom = LCD.CustomCharacters(display)

display.lcd_display_string("- Display Line 1", 1)  # Write line of text to first line of display
sleep(1)
display.lcd_display_string("- Display Line 2", 2)  # Write line of text to first line of display
sleep(1)
display.lcd_display_string("- Display Line 3", 3)  # Write line of text to first line of display
sleep(1)
display.lcd_display_string("- Display Line 4", 4)  # Write line of text to first line of display
sleep(1)
sleep(2)
custom.load_custom_characters_data()
display.lcd_clear_display()

display.lcd_display_buffer([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 1)
display.lcd_display_buffer([255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255], 3)
display.lcd_display_buffer([255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255], 4)
while True:
    display.lcd_display_buffer([0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7,0,1,2,3], 2)
    sleep(.05)                                               
    display.lcd_display_buffer([1,2,3,4,5,6,7,6,1,2,3,4,5,6,7,6,1,2,3,4], 2)
    sleep(.05)                                                
    display.lcd_display_buffer([2,3,4,5,6,7,6,5,2,3,4,5,6,7,6,5,2,3,4,5], 2)
    sleep(.05)                                              
    display.lcd_display_buffer([3,4,5,6,7,6,5,4,3,4,5,6,7,6,5,4,3,4,5,6], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([4,5,6,7,6,5,4,3,4,5,6,7,6,5,4,3,4,5,6,7], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([5,6,7,6,5,4,3,2,5,6,7,6,5,4,3,2,5,6,7,6], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([6,7,6,5,4,3,2,1,6,7,6,5,4,3,2,1,6,7,6,5], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([7,6,5,4,3,2,1,0,7,6,5,4,3,2,1,0,7,6,5,4], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([6,5,4,3,2,1,0,1,6,5,4,3,2,1,0,1,6,5,4,3], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([5,4,3,2,1,0,1,2,5,4,3,2,1,0,1,2,5,4,3,2], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([4,3,2,1,0,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([3,2,1,0,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,0], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([2,1,0,1,2,3,4,5,2,1,0,1,2,3,4,5,2,1,0,1], 2)
    sleep(.05)                                 
    display.lcd_display_buffer([1,0,1,2,3,4,5,6,1,0,1,2,3,4,5,6,1,0,1,2], 2)