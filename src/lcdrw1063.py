"""
Python Driver for the RW1063, LCD driver & controller
https://www.orientdisplay.com/wp-content/uploads/2020/07/RW1063.pdf

"""


from smbus2 import SMBus
from RPi.GPIO import RPI_REVISION
from time import sleep
from re import findall, match
from subprocess import check_output
from os.path import exists

# old and new versions of the RPi have swapped the two i2c buses
# they can be identified by RPI_REVISION (or check sysfs)
BUS_NUMBER = 0 if RPI_REVISION == 1 else 1

# Displays
MIDAS_20x4 = 0

# Four 7-bit slave addresses (0111100, 0111101, 0111110 and 0111111) are reserved for the RW1063
LCD_ADDRESS_3C = 0b_0011_1100 # 0x3C
LCD_ADDRESS_3D = 0b_0011_1101 # 0x3D
LCD_ADDRESS_3D = 0b_0011_1110 # 0x3E
LCD_ADDRESS_3F = 0b_0011_1111 # 0x3F

# 2 x 8 bit registers, DR - Data Register, IR - Instruction Register

# 8-bit Data Register
LCD_DR_CLEAR_DISPLAY        = 0b_0000_0001
LCD_DR_RETURN_HOME          = 0b_0000_0010
LCD_DR_ENTRY_MODE_SET       = 0b_0000_0100
LCD_DR_DISPLAY_ON_OFF       = 0b_0000_1000
LCD_DR_CURSOR_DISPLAY_SHIFT = 0b_0001_0000
LCD_DR_FUNCTION_SET         = 0b_0010_0000
LCD_DR_SET_CGRAM_ADDRESS    = 0b_0100_0000
LCD_DR_SET_DDRAM_ADDRESS    = 0b_1000_0000

# Entry mode set modes
LCD_ENTRY_MODE_LEFT   = 0b_0000_0000
LCD_ENTRY_MODE_RIGHT  = 0b_0000_0010
LCD_ENTRY_SHIFT_ON    = 0b_0000_0001
LCD_ENTRY_SHIFT_OFF   = 0b_0000_0000

# Display ON/OFF
LCD_DISPLAY_ON                  = 0b_0000_00100
LCD_DISPLAY_OFF                 = 0b_0000_00000
LCD_DISPLAY_CURSOR_ON           = 0b_0000_00010
LCD_DISPLAY_CURSOR_OFF          = 0b_0000_00000
LCD_DISPLAY_CURSOR_BLINK_ON     = 0b_0000_00001
LCD_DISPLAY_CURSOR_BLINK_OFF    = 0b_0000_00000

# Function set modes
# IF using IIC and 4-SPI interface DL bit must be setting to 1
LCD_FUNC_SET_DATA_LENGTH_8BIT   = 0b_0001_0000 
LCD_FUNC_SET_DATA_LENGTH_4BIT   = 0b_0000_0000
LCD_FUNC_SET_ONE_LINE_NUMBER    = 0b_0000_0000
LCD_FUNC_SET_TWO_LINE_NUMBER    = 0b_0000_1000
LCD_FUNC_SET_FONT_5x8           = 0b_0000_0000
LCD_FUNC_SET_FONT_5x11          = 0b_0000_0100

# 8-bit Instruction register (IR) is used only to store instruction code transferred from MPU
# RS|R/W , R/W always 0, only slave operation
LCD_IR_INSTRUCTION_WRITE_OP  = 0b_0000_0000 # 0x00
LCD_IR_DATA_WRITE_OP         = 0b_0100_0000 # 0x40

LCD_LINE1_BASE_ADDRESS= 0x80 # 0000 0000 DDRAM Address 0x00
LCD_LINE2_BASE_ADDRESS= 0xC0 # 0100 0000 DDRAM Address 0x40
LCD_LINE3_BASE_ADDRESS= 0x94 # 0001 0100 DDRAM Address 0x14
LCD_LINE4_BASE_ADDRESS= 0xD4 # 0101 0100 DDRAM Address 0x54



lcd_address = LCD_ADDRESS_3C
bus = SMBus(1)

class I2CDevice:
    def __init__(self, addr=None, addr_default=LCD_ADDRESS_3C, busNumber=BUS_NUMBER):
        if not addr:
            # try autodetect address, else use default if provided
            try:
                self.addr = int('0x{}'.format(
                    findall("[0-9a-z]{2}(?!:)", \
                    check_output(['/usr/sbin/i2cdetect', '-y', str(BUS_NUMBER)]).decode())[0]), base=16) \
                    if exists('/usr/sbin/i2cdetect') else addr_default
            except:
                self.addr = addr_default
        else:
            self.addr = addr
            
        self.busNumber = busNumber
    
    def write_i2c_block_data(self, cmd, data):
        with SMBus(self.busNumber) as bus:
            bus.write_i2c_block_data(self.addr , cmd, data)
        sleep(0.0001)


class Lcd:
    def __init__(self, addr=None):
        self.addr = addr
        self.i2c = I2CDevice(addr=self.addr, addr_default=LCD_ADDRESS_3C)
        self.lcd_init_function_set()
        self.lcd_set_display_on()
        self.lcd_clear_display()
        self.lcd_entry_mode_set_left_shift_off()
        sleep(0.2)


    def lcd_i2c_send_block_data(self, instructionRegister, data):
        self.i2c.write_i2c_block_data(instructionRegister, data)

    def lcd_send_instruction_write_command(self, command) :
        self.lcd_i2c_send_block_data( LCD_IR_INSTRUCTION_WRITE_OP, [command])
        
    def lcd_send_data_write_command(self, buffer) :
        self.lcd_i2c_send_block_data( LCD_IR_DATA_WRITE_OP, buffer)
        

    def lcd_clear_display(self):
        """
        Clear all the display data by writing "20H" (space code) to all DDRAM address, and set DDRAM
        address to "00H" into AC (address counter). Return cursor to the original status; namely, bring
        the cursor to the left edge on first line of the display. Make entry mode increment (I/D = "1").
        """    
        self.lcd_send_instruction_write_command( LCD_DR_CLEAR_DISPLAY)
        
    def lcd_return_home(self):
        """
        Return Home is cursor return home instruction. Set DDRAM address to "00H" into the address counter. Return 
        cursor to its original site and return display to its original status, if shifted. A content of DDRAM does not change. 
        """
        self.lcd_send_instruction_write_command( LCD_DR_RETURN_HOME)

    def lcd_entry_mode_set(self, mode) :
        """
        Set the moving direction of cursor and display. 
        I/D: Increment/decrement of DDRAM address (cursor or blink) 
        I/D = 1: cursor/blink moves to right and DDRAM address is increased by 1. 
        I/D = 0: cursor/blink moves to left and DDRAM address is decreased by 1. 
        * CGRAM operates the same as DDRAM, when read/write from or to CGRAM 
        S: Shift of entire display 
        When DDRAM read (CGRAM read/write) operation or S = "Low", shift of entire display is not performed. 
         If S= "High" and DDRAM write operation, shift of entire display is performed according to I/D value (I/D = "1”: 
        shift left, I/D = "0”: shift right). 
        """
        self.lcd_send_instruction_write_command(LCD_DR_ENTRY_MODE_SET | mode)
        
    def lcd_entry_mode_set_left_shift_on(self) :
        """
        Shift all the display to the left, cursor moves according to the display
        """
        self.lcd_entry_mode_set(LCD_ENTRY_MODE_LEFT | LCD_ENTRY_SHIFT_ON)
        
    def lcd_entry_mode_set_left_shift_off(self) :
        """
        Shift cursor to the left, address counter is decreased by 1
        """
        self.lcd_entry_mode_set( LCD_ENTRY_MODE_LEFT | LCD_ENTRY_SHIFT_OFF)
        
    def lcd_entry_mode_set_right_shift_on(self) :
        """
        Shift all the display to the right, cursor moves according to the display
        """
        self.lcd_entry_mode_set(LCD_ENTRY_MODE_RIGHT | LCD_ENTRY_SHIFT_ON)
        
    def lcd_entry_mode_set_right_shift_off(self) :
        """
        Shift cursor to the right, address counter is increased by 1 
        """
        self.lcd_entry_mode_set( LCD_ENTRY_MODE_RIGHT | LCD_ENTRY_SHIFT_OFF)
        

    def lcd_set_display_on(self, cursorOn = False, cursorBlinkOn = False) :
        """
        entire display is turned on
        cursorOn
            True  : cursor is turned on
            False : cursor is disappeared in current display, but I/D register remains its data. 
        cursorBlinkOn
            True  : cursor blink is on, that performs alternate between all the high data and 
                    display character at the cursor position. If fosc has 540 kHz frequency, 
                    blinking has 185 ms interval
            False : blink is off. 
        """
        command = LCD_DR_DISPLAY_ON_OFF | LCD_DISPLAY_ON
        if cursorOn:
            command = command | LCD_DISPLAY_CURSOR_ON
            
        if cursorBlinkOn:
            command = command | LCD_DISPLAY_CURSOR_BLINK_ON
            
        self.lcd_send_instruction_write_command( command)
        
    def lcd_set_display_off(self) :
        """
        Display is turned off, but display data is remained in DDRAM.
        """
        self.lcd_send_instruction_write_command( LCD_DR_DISPLAY_ON_OFF | LCD_DISPLAY_OFF )    
        
    def lcd_init_function_set(self) :
        """
        Default Configurations
        """        
        command = LCD_DR_FUNCTION_SET | LCD_FUNC_SET_DATA_LENGTH_8BIT | LCD_FUNC_SET_TWO_LINE_NUMBER | LCD_FUNC_SET_FONT_5x8
        self.lcd_send_instruction_write_command( command)
                
        
    def lcd_set_cgram_address(self, sixBitAddress) :
        """
        Set CGRAM address to AC. This instruction makes CGRAM data available from MPU. 
        """
        self.lcd_send_instruction_write_command( LCD_DR_SET_CGRAM_ADDRESS | sixBitAddress )
        
    def lcd_set_ddram_address(self, sevenBitAddress) :
        """
        Set DDRAM address to AC. This instruction makes DDRAM data available from MPU.
        When 1-line display mode (N=0), DDRAM address is from “00H” to “4FH” 
        In 2-line display mode (NW = 0), DDRAM address in the 1st line is from "00H" - "27H",
        and DDRAM address in the 2nd line is from "40H" - "67H".
        """
        self.lcd_send_instruction_write_command( LCD_DR_SET_DDRAM_ADDRESS | sevenBitAddress)
        
    def lcd_write_ram_data(self, eightBitData):
        """
        Write binary 8-bit data to DDRAM/CGRAM. 
        The selection of RAM from DDRAM, CGRAM, is set by the previous address set instruction: 
        DDRAM address set, CGRAM address set. RAM set instruction can also determine the AC direction to RAM. 
        After write operation, the address is automatically increased/decreased by 1, according to the entry mode. 
        """
        self.lcd_send_data_write_command( [eightBitData & 0b_1111_1111])
        
        
       
    def lcd_display_string(self, string, line):
        """
        Display String in predefined line 1 to 4
        """
        if line == 1:
            self.lcd_set_ddram_address(LCD_LINE1_BASE_ADDRESS)
        if line == 2:
            self.lcd_set_ddram_address(LCD_LINE2_BASE_ADDRESS)
        if line == 3:
            self.lcd_set_ddram_address(LCD_LINE3_BASE_ADDRESS)
        if line == 4:
            self.lcd_set_ddram_address(LCD_LINE4_BASE_ADDRESS)
        
        self.lcd_send_data_write_command( string.encode())
        
    def lcd_display_buffer(self, buffer, line):
        """
        Display String in predefined line 1 to 4
        """
        if line == 1:
            self.lcd_set_ddram_address(LCD_LINE1_BASE_ADDRESS)
        if line == 2:
            self.lcd_set_ddram_address(LCD_LINE2_BASE_ADDRESS)
        if line == 3:
            self.lcd_set_ddram_address(LCD_LINE3_BASE_ADDRESS)
        if line == 4:
            self.lcd_set_ddram_address(LCD_LINE4_BASE_ADDRESS)
        sleep(.01)
        self.lcd_send_data_write_command( buffer)
    
    
    def lcd_clear(self):
        """
        clear lcd and set to home
        """
        self.lcd_clear_display()
        self.lcd_return_home()
        

class CustomCharacters:
    def __init__(self, lcd):
        self.lcd = lcd
        # Data for custom character #1. Code {0x00}.
        self.char_1_data = ["10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001"]
        # Data for custom character #2. Code {0x01}
        self.char_2_data = ["10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #3. Code {0x02}
        self.char_3_data = ["10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111",
                            "11111"]
        # Data for custom character #4. Code {0x03}
        self.char_4_data = ["10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111",
                            "11111",
                            "11111"]
        # Data for custom character #5. Code {0x04}
        self.char_5_data = ["10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111",
                            "11111",
                            "11111",
                            "11111"]
        # Data for custom character #6. Code {0x05}
        self.char_6_data = ["10001",
                            "10001",
                            "10001",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111"]
        # Data for custom character #7. Code {0x06}
        self.char_7_data = ["10001",
                            "10001",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111"]
        # Data for custom character #8. Code {0x07}
        self.char_8_data = ["10001",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111",
                            "11111"]

    # load custom character data to CG RAM for later use 
    # These custom characters can be used in printing of extended string with a
    # placeholder with desired character codes: 1st - {0x00}, 2nd - {0x01}, 3rd - {0x02},
    # 4th - {0x03}, 5th - {0x04}, 6th - {0x05}, 7th - {0x06} and 8th - {0x07}.
    def load_custom_characters_data(self):
        self.chars_list = [self.char_1_data, self.char_2_data, self.char_3_data,
                           self.char_4_data, self.char_5_data, self.char_6_data,
                           self.char_7_data, self.char_8_data]
        

        for char_num in range(8):
            self.lcd.lcd_set_cgram_address( 0x08 * (char_num))
            for line_num in range(8):
                line = self.chars_list[char_num][line_num]
                binary_str_cmd = "0b000{0}".format(line)
                self.lcd.lcd_write_ram_data(int(binary_str_cmd, 2))
                
# display = Lcd()
# custom = CustomCharacters(display)
# 
# display.lcd_display_string("- Display Line 1", 1)  # Write line of text to first line of display
# sleep(1)
# display.lcd_display_string("- Display Line 2", 2)  # Write line of text to first line of display
# sleep(1)
# display.lcd_display_string("- Display Line 3", 3)  # Write line of text to first line of display
# sleep(1)
# display.lcd_display_string("- Display Line 4", 4)  # Write line of text to first line of display
# sleep(1)
# sleep(2)
# custom.load_custom_characters_data()
# display.lcd_clear_display()
# 
# display.lcd_display_buffer([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 1)
# display.lcd_display_buffer([255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255], 3)
# display.lcd_display_buffer([255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255], 4)
# while True:
#     display.lcd_display_buffer([0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7,0,1,2,3], 2)
#     sleep(.05)                                               
#     display.lcd_display_buffer([1,2,3,4,5,6,7,6,1,2,3,4,5,6,7,6,1,2,3,4], 2)
#     sleep(.05)                                                
#     display.lcd_display_buffer([2,3,4,5,6,7,6,5,2,3,4,5,6,7,6,5,2,3,4,5], 2)
#     sleep(.05)                                              
#     display.lcd_display_buffer([3,4,5,6,7,6,5,4,3,4,5,6,7,6,5,4,3,4,5,6], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([4,5,6,7,6,5,4,3,4,5,6,7,6,5,4,3,4,5,6,7], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([5,6,7,6,5,4,3,2,5,6,7,6,5,4,3,2,5,6,7,6], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([6,7,6,5,4,3,2,1,6,7,6,5,4,3,2,1,6,7,6,5], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([7,6,5,4,3,2,1,0,7,6,5,4,3,2,1,0,7,6,5,4], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([6,5,4,3,2,1,0,1,6,5,4,3,2,1,0,1,6,5,4,3], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([5,4,3,2,1,0,1,2,5,4,3,2,1,0,1,2,5,4,3,2], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([4,3,2,1,0,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([3,2,1,0,1,2,3,4,3,2,1,0,1,2,3,4,3,2,1,0], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([2,1,0,1,2,3,4,5,2,1,0,1,2,3,4,5,2,1,0,1], 2)
#     sleep(.05)                                 
#     display.lcd_display_buffer([1,0,1,2,3,4,5,6,1,0,1,2,3,4,5,6,1,0,1,2], 2)
# 
