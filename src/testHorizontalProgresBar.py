import lcdrw1063 as LCD
from time import sleep


# Test Horizontal Progress Bar

display = LCD.Lcd()
custom = LCD.CustomCharacters(display)

custom.char_1_data = ["10001",
# Data for custom character #1. Code {0x00}.
custom.char_1_data = ["11111",
                      "00000",
                      "00000",
                      "00000",
                      "00000",
                      "00000",
                      "00000",
                      "11111"]
custom.char_2_data = ["11111",
                      "00000",
                      "10000",
                      "10000",
                      "10000",
                      "10000",
                      "00000",
                      "11111"]
custom.char_3_data = ["11111",
                      "00000",
                      "11000",
                      "11000",
                      "11000",
                      "11000",
                      "00000",
                      "11111"]
custom.char_4_data = ["11111",
                      "00000",
                      "11100",
                      "11100",
                      "11100",
                      "11100",
                      "00000",
                      "11111"]
custom.char_5_data = ["11111",
                      "00000",
                      "11110",
                      "11110",
                      "11110",
                      "11110",
                      "00000",
                      "11111"]
custom.char_6_data = ["11111",
                      "00000",
                      "11111",
                      "11111",
                      "11111",
                      "11111",
                      "00000",
                      "11111"]

custom.load_custom_characters_data()
display.lcd_clear_display()

buffer = [0]*20
display.lcd_display_buffer(buffer, 1)

while True:
    for i in range(100) :
        for j in range (i / 5) :
            buffer[j] = 5
        if (i mod 5) > 0:
            buffer[i/5] = i mod 5
        for k in range (i / 5 + 1, 20) :
            buffer[k] = 0
        display.lcd_display_buffer(buffer, 1)
        sleep(.05) 
