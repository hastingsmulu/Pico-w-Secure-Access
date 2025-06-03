# lcd_api.py - Basic API for HD44780 LCD in 4-bit mode
from machine import Pin
import time

class LcdApi:
    """
    Generic LCD API for HD44780 compatible displays.
    Supports 4-bit mode.
    """
    def __init__(self, rs_pin, e_pin, d4_pin, d5_pin, d6_pin, d7_pin, num_lines=2, num_columns=16):
        self.rs_pin = Pin(rs_pin, Pin.OUT)
        self.e_pin = Pin(e_pin, Pin.OUT)
        # Data pins are listed from D4 to D7, so index 0 is D4, 1 is D5, etc.
        self.data_pins = [Pin(d4_pin, Pin.OUT), Pin(d5_pin, Pin.OUT), Pin(d6_pin, Pin.OUT), Pin(d7_pin, Pin.OUT)]
        self.num_lines = num_lines
        self.num_columns = num_columns

        # HD44780 commands
        self.CMD_CLEAR_DISPLAY = 0x01
        self.CMD_RETURN_HOME = 0x02
        self.CMD_ENTRY_MODE_SET = 0x04
        self.CMD_DISPLAY_CONTROL = 0x08
        self.CMD_CURSOR_SHIFT = 0x10
        self.CMD_FUNCTION_SET = 0x20
        self.CMD_SET_CGRAM_ADDR = 0x40
        self.CMD_SET_DDRAM_ADDR = 0x80 # Set DDRAM Address (used for cursor position)

        # Display Control bits
        self.SET_DISPLAY_ON = 0x04
        self.SET_CURSOR_ON = 0x02
        self.SET_BLINK_ON = 0x01

        # RS pin states
        self.RS_COMMAND = 0
        self.RS_DATA = 1

        self.init_display()

    def _pulse_enable(self):
        """Puts a short pulse on the Enable pin."""
        self.e_pin.value(0)
        time.sleep_us(1)
        self.e_pin.value(1) # High pulse
        time.sleep_us(1)
        self.e_pin.value(0)
        time.sleep_us(100) # Commands need this time to settle

    def _send_4_bits(self, data):
        """Sends 4 bits of data to the LCD data pins."""
        for i in range(4):
            self.data_pins[i].value((data >> i) & 0x01) # Set D4-D7 based on data bits
        self._pulse_enable()

    def _send_byte(self, value, mode):
        """Sends a full byte (8 bits) by splitting it into two 4-bit nibbles."""
        self.rs_pin.value(mode) # Set RS pin for Command or Data mode
        time.sleep_us(50) # RS setup time

        # Send high nibble first (D7-D4)
        self._send_4_bits(value >> 4)
        # Send low nibble second (D3-D0)
        self._send_4_bits(value & 0x0F)

    def command(self, cmd):
        """Sends a command byte to the LCD."""
        self._send_byte(cmd, self.RS_COMMAND)

    def data(self, char_code):
        """Sends a data byte (character code) to the LCD."""
        self._send_byte(char_code, self.RS_DATA)

    def init_display(self):
        """Initializes the LCD into 4-bit mode."""
        time.sleep_ms(50) # Power-on delay according to HD44780 datasheet

        self.rs_pin.value(0) # Start in Command mode
        self.e_pin.value(0)

        # Required initialization sequence for 4-bit mode (see HD44780 datasheet)
        # Send 0x03 three times (these are 8-bit commands, but only D4-D7 are used)
        self._send_4_bits(0x03)
        time.sleep_ms(5)
        self._send_4_bits(0x03)
        time.sleep_us(150)
        self._send_4_bits(0x03)
        time.sleep_us(150)

        # Set to 4-bit mode (actual 4-bit function set command)
        self._send_4_bits(0x02) # This is the crucial command to switch to 4-bit interface
        time.sleep_us(100) # Small delay after setting 4-bit mode

        # Function Set: 4-bit mode, 2 lines, 5x8 dots (0x08 for 2 lines)
        self.command(self.CMD_FUNCTION_SET | 0x08 | 0x00)

        # Display Control: Display ON, Cursor OFF, Blink OFF
        self.command(self.CMD_DISPLAY_CONTROL | self.SET_DISPLAY_ON | self.SET_CURSOR_ON | self.SET_BLINK_ON) # Cursor and Blink ON for initial testing visibility

        # Clear Display
        self.clear()

        # Entry Mode Set: Increment cursor, No shift
        self.command(self.CMD_ENTRY_MODE_SET | 0x02) # I/D=1 (increment), S=0 (no shift)

        # Return Home
        self.home()

    def clear(self):
        """Clears the LCD display."""
        self.command(self.CMD_CLEAR_DISPLAY)
        time.sleep_ms(2) # Clear display requires longer time

    def home(self):
        """Sets the cursor to the home position (0,0)."""
        self.command(self.CMD_RETURN_HOME)
        time.sleep_ms(2) # Return home requires longer time

    def set_cursor(self, col, row):
        """Sets the cursor position (column, row)."""
        if row == 0:
            self.command(self.CMD_SET_DDRAM_ADDR | (col & 0x7F))
        elif row == 1:
            self.command(self.CMD_SET_DDRAM_ADDR | (0x40 + (col & 0x7F))) # Second line address offset

    def message(self, text):
        """Writes a string message to the LCD at the current cursor position."""
        for char in text:
            self.data(ord(char)) # Send ASCII value of character
