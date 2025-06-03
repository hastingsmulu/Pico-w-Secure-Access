import network
import time
from machine import Pin, Timer, SPI
import usocket as socket
import urandom
from lcd_api import LcdApi # <--- NEW: Import LCD library

# --- Network Configuration ---
ssid = 'Wifi'
password = 'JMULU1234'

# !!! IMPORTANT !!!
# REPLACE THIS WITH THE ACTUAL MAC ADDRESS (BSSID) OF YOUR ROUTER'S WI-FI INTERFACE.
# It MUST be in bytes format (e.g., b'\x00\x11\x22\xAA\xBB\xCC').
# Run your existing code (or a simple script) and copy the 'ap_mac' value as bytes for your "Wifi" network.
# Example: If your router's MAC is 3E:DA:3D:76:C9:C8, it would be b'\x3e\xda\x3d\x76\xc9\xc8'
KNOWN_AP_MAC_BYTES = b'\x3e\xda\x3d\x76\xc9\xc8' # <--- CONFIRM AND REPLACE THIS!

WEB_PORT = 80
MAX_CONNECTIONS = 5

# --- LED Configuration ---
led = Pin("LED", Pin.OUT)
timer = Timer()

# --- Global variables to store network details and dynamic data ---
ip_address = "N/A"
ap_mac_formatted = "N/A"
rssi = "N/A"
random_number_for_keypad = ""
keypad_input_buffer = ""
lock_status_message = "Awaiting RFID/Keypad input..."
last_lock_action_time = 0

# --- Hardware Pin Assignments ---
# --- MFRC522 (RFID) Pins ---
RFID_SCK_PIN = 2
RFID_MOSI_PIN = 3
RFID_MISO_PIN = 4
RFID_SDA_PIN = 5
RFID_RST_PIN = 14

# --- Keypad Pins ---
KEYPAD_R1 = 16
KEYPAD_R2 = 17
KEYPAD_R3 = 18
KEYPAD_R4 = 19
KEYPAD_C1 = 20
KEYPAD_C2 = 21
KEYPAD_C3 = 22
KEYPAD_C4 = 26

# --- Relay Pin (for Solenoid Lock) ---
RELAY_PIN = 15

# --- LCD Pins (16x2 Parallel) --- <--- NEW: LCD PIN DEFINITIONS
LCD_RS_PIN = 0
LCD_E_PIN = 1
LCD_D4_PIN = 6
LCD_D5_PIN = 7
LCD_D6_PIN = 8
LCD_D7_PIN = 9
# You might also want to control the LCD backlight via a pin if available, e.g.:
# LCD_BL_PIN = 13 # If using GP13 for backlight control
# For now, assume you connect LED+ on LCD to 3V3 directly, and LED- to GND.

# --- Lock Configuration ---
LOCK_OPEN_DURATION_MS = 5000

# --- Authorized RFID UIDs ---
AUTHORIZED_TAGS = [
    [0x04, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70] # Replace with your RFID tag UID!
]

# --- Hardware Initialization ---
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)

from mfrc522 import MFRC522
rdr = MFRC522(spi_id=0, sck=Pin(RFID_SCK_PIN), mosi=Pin(RFID_MOSI_PIN), miso=Pin(RFID_MISO_PIN), rst=Pin(RFID_RST_PIN), cs=Pin(RFID_SDA_PIN))

rows = [Pin(KEYPAD_R1, Pin.OUT), Pin(KEYPAD_R2, Pin.OUT), Pin(KEYPAD_R3, Pin.OUT), Pin(KEYPAD_R4, Pin.OUT)]
cols = [Pin(KEYPAD_C1, Pin.IN, Pin.PULL_UP), Pin(KEYPAD_C2, Pin.IN, Pin.PULL_UP), Pin(KEYPAD_C3, Pin.IN, Pin.PULL_UP), Pin(KEYPAD_C4, Pin.IN, Pin.PULL_UP)]
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# LCD Display Initialization <--- NEW: LCD OBJECT CREATION
lcd = LcdApi(LCD_RS_PIN, LCD_E_PIN, LCD_D4_PIN, LCD_D5_PIN, LCD_D6_PIN, LCD_D7_PIN)
# If you decided to control backlight via a GPIO:
# lcd_backlight = Pin(LCD_BL_PIN, Pin.OUT)
# lcd_backlight.value(1) # Turn backlight ON

# --- Function to connect to WiFi ---
def connect_to_wifi():
    global ip_address, ap_mac_formatted, rssi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    known_mac_display = ':'.join('{:02x}'.format(b) for b in KNOWN_AP_MAC_BYTES)
    print(f"Attempting to connect to SSID: {ssid} with known BSSID: {known_mac_display}")
    lcd.clear() # <--- NEW: LCD update
    lcd.message("Connecting WiFi..") # <--- NEW: LCD update
    lcd.set_cursor(0,1) # <--- NEW: LCD update
    lcd.message(ssid) # <--- NEW: LCD update


    if not wlan.isconnected():
        print("Connecting to WiFi...")
        try:
            wlan.connect(ssid, password, bssid=KNOWN_AP_MAC_BYTES)
        except OSError as e:
            print(f"Initial connection attempt failed: {e}. BSSID might not be available or incorrect.")
            lcd.clear() # <--- NEW: LCD update
            lcd.message("WiFi Err: Init") # <--- NEW: LCD update
            lcd.set_cursor(0,1) # <--- NEW: LCD update
            lcd.message("Check BSSID/AP") # <--- NEW: LCD update
            time.sleep(2) # <--- NEW: LCD update
            return False

        for _ in range(100):
            if wlan.isconnected():
                break
            time.sleep(0.1)

    if wlan.isconnected():
        ip_address = wlan.ifconfig()[0]
        rssi = wlan.status('rssi')
        ap_mac_formatted = known_mac_display
            
        print("\nWiFi Connection Details:")
        print("------------------------")
        print("Connected to:", ssid)
        print("AP MAC (BSSID):", ap_mac_formatted)
        print("IP Address:", ip_address)
        print("Signal Strength:", rssi, "dBm")
        print("------------------------")
        
        lcd.clear() # <--- NEW: LCD update
        lcd.message("WiFi Connected!") # <--- NEW: LCD update
        lcd.set_cursor(0,1) # <--- NEW: LCD update
        lcd.message(f"IP:{ip_address}") # <--- NEW: LCD update
        time.sleep(2) # <--- NEW: LCD update
        return True
    else:
        print("\nFailed to connect to WiFi with specified BSSID.")
        print("Connection Status:", wlan.status())
        if wlan.isconnected():
            wlan.disconnect()
        
        lcd.clear() # <--- NEW: LCD update
        lcd.message("WiFi Failed!") # <--- NEW: LCD update
        lcd.set_cursor(0,1) # <--- NEW: LCD update
        lcd.message("No Connection") # <--- NEW: LCD update
        time.sleep(2) # <--- NEW: LCD update
        return False

# --- Function to generate a random 5-digit number ---
def generate_random_5digit_number():
    return str(urandom.getrandbits(14) % 90000 + 10000)

# --- Function to open the lock ---
def open_lock():
    global last_lock_action_time, lock_status_message
    print("Lock opened!")
    lcd.clear() # <--- NEW: LCD update
    lcd.message("Lock OPENED!") # <--- NEW: LCD update
    relay.value(1)
    lock_status_message = "Lock is OPEN!"
    last_lock_action_time = time.ticks_ms()

# --- Function to close the lock ---
def close_lock():
    global lock_status_message
    print("Lock closed!")
    lcd.clear() # <--- NEW: LCD update
    lcd.message("Lock CLOSED!") # <--- NEW: LCD update
    relay.value(0)
    lock_status_message = "Awaiting RFID/Keypad input..."

# --- Function to handle keypad input ---
def read_keypad():
    for r_idx, row_pin in enumerate(rows):
        row_pin.value(0)
        for c_idx, col_pin in enumerate(cols):
            if col_pin.value() == 0:
                time.sleep_ms(20)
                if col_pin.value() == 0:
                    key = keys[r_idx][c_idx]
                    while col_pin.value() == 0:
                        time.sleep_ms(10)
                    row_pin.value(1)
                    return key
        row_pin.value(1)
    return None

# --- Main loop for hardware handling (non-blocking) ---
def hardware_loop():
    global keypad_input_buffer, random_number_for_keypad, lock_status_message

    # Handle lock timeout
    if relay.value() == 1 and (time.ticks_ms() - last_lock_action_time) > LOCK_OPEN_DURATION_MS:
        close_lock()
        lcd.clear() # <--- NEW: LCD update for timeout
        lcd.message("Lock Closed!") # <--- NEW: LCD update for timeout
        lcd.set_cursor(0,1) # <--- NEW: LCD update for timeout
        lcd.message("Timeout") # <--- NEW: LCD update for timeout

    # Read RFID
    (status, tag_type) = rdr.request(rdr.REQIDL)
    if status == rdr.OK:
        (status, uid) = rdr.SelectTag(tag_type)
        if status == rdr.OK:
            if uid in AUTHORIZED_TAGS:
                print("Authorized RFID Tag detected! Enter 5-digit number on keypad.")
                lock_status_message = "Authorized RFID. Enter code on keypad."
                random_number_for_keypad = generate_random_5digit_number()
                keypad_input_buffer = ""
                lcd.clear() # <--- NEW: LCD update
                lcd.message("RFID Authorized!") # <--- NEW: LCD update
                lcd.set_cursor(0,1) # <--- NEW: LCD update
                lcd.message(f"Code: {random_number_for_keypad}") # <--- NEW: LCD update
            else:
                print("Unauthorized RFID Tag.")
                lock_status_message = "Unauthorized RFID Tag."
                random_number_for_keypad = ""
                keypad_input_buffer = ""
                lcd.clear() # <--- NEW: LCD update
                lcd.message("Unauthorized Tag!") # <--- NEW: LCD update
                lcd.set_cursor(0,1) # <--- NEW: LCD update
                lcd.message("Access Denied") # <--- NEW: LCD update
    
    # Read Keypad
    key = read_keypad()
    if key:
        print("Keypad Input:", key)
        if '0' <= key <= '9':
            keypad_input_buffer += key
            lock_status_message = f"Code: {keypad_input_buffer}"
            lcd.clear() # <--- NEW: LCD update
            lcd.message("Enter Code:") # <--- NEW: LCD update
            lcd.set_cursor(0,1) # <--- NEW: LCD update
            lcd.message(keypad_input_buffer + "_") # Show input with underscore
            if len(keypad_input_buffer) == 5:
                if keypad_input_buffer == random_number_for_keypad:
                    print("Correct 5-digit number entered!")
                    open_lock()
                else:
                    print("Incorrect 5-digit number.")
                    lock_status_message = "Incorrect code. Try again."
                    lcd.clear() # <--- NEW: LCD update
                    lcd.message("Incorrect Code!") # <--- NEW: LCD update
                    lcd.set_cursor(0,1) # <--- NEW: LCD update
                    lcd.message("Try Again") # <--- NEW: LCD update
                    time.sleep(1) # Short delay
                keypad_input_buffer = ""
                random_number_for_keypad = ""
                lcd.clear() # Clear after attempt
                lcd.message("Waiting for RFID")
            elif len(keypad_input_buffer) > 5:
                keypad_input_buffer = "" # Reset if too long
                lcd.clear() # <--- NEW: LCD update
                lcd.message("Input too long!") # <--- NEW: LCD update
                time.sleep(1) # Short delay
                lcd.clear() # Clear after attempt
                lcd.message("Waiting for RFID")
        elif key == '*': # Clear/Reset button
            keypad_input_buffer = ""
            random_number_for_keypad = ""
            lock_status_message = "Input cleared."
            lcd.clear() # <--- NEW: LCD update
            lcd.message("Input Cleared!") # <--- NEW: LCD update
            time.sleep(1) # Short delay
            lcd.clear() # Clear after attempt
            lcd.message("Waiting for RFID")

# --- Function to serve the web page ---
# This remains unchanged, as LCD is for local display.
def serve_web_page(conn):
    global ip_address, ap_mac_formatted, rssi, random_number_for_keypad, lock_status_message
    
    display_random_number = random_number_for_keypad if random_number_for_keypad else generate_random_5digit_number()

    html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W Network & Lock Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f0f0; color: #333; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba<0,0,0,0.1); }
        h1 { color: #0056b3; }
        .network-details { font-size: 1.2em; line-height: 1.6; }
        .random-number { 
            font-size: 4em;
            font-weight: bold;
            color: #d9534f;
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        .label { font-weight: bold; }
        .lock-status { 
            font-size: 1.5em; 
            font-weight: bold; 
            margin-top: 20px; 
            padding: 10px; 
            border: 2px solid; 
            border-radius: 5px; 
            text-align: center;
        }
        .lock-open { background-color: #d4edda; border-color: #28a745; color: #155724; }
        .lock-closed { background-color: #f8d7da; border-color: #dc3545; color: #721c24; }
        .lock-info { background-color: #ffeeba; border-color: #ffc107; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Raspberry Pi Pico W Security System</h1>
        
        <h2>Network Status</h2>
        <p class="network-details"><span class="label">Connected to:</span> """ + ssid + """</p>
        <p class="network-details"><span class="label">AP MAC (BSSID):</span> """ + ap_mac_formatted + """</p>
        <p class="network-details"><span class="label">IP Address:</span> """ + ip_address + """</p>
        <p class="network-details"><span class="label">Signal Strength:</span> """ + str(rssi) + """ dBm</p>
        
        <h2>Current Code for Entry</h2>
        <div class="random-number">
            """ + display_random_number + """
        </div>
        <p style="text-align: center; font-size: 0.9em; color: #666;">(This code changes upon RFID scan or page refresh. Enter it on the keypad after a valid RFID scan.)</p>

        <h2>Lock Status</h2>
        <div class="lock-status """ + ("lock-open" if "OPEN" in lock_status_message else ("lock-closed" if "Unauthorized" in lock_status_message else "lock-info")) + """">
            """ + lock_status_message + """
        </div>
    </div>
</body>
</html>"""
    
    response = "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n" + html
    conn.send(response)

# --- Main Program Logic ---

# Initial LCD message on boot
lcd.clear() # <--- NEW: Initial LCD message
lcd.message("PicoSecure-Access") # <--- NEW: Initial LCD message
lcd.set_cursor(0, 1) # <--- NEW: Initial LCD message
lcd.message("Initializing...") # <--- NEW: Initial LCD message
time.sleep(1) # <--- NEW: Initial LCD message

if connect_to_wifi():
    addr = socket.getaddrinfo('0.0.0.0', WEB_PORT)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(MAX_CONNECTIONS)
    print("Web server listening on http://%s:%s" % (ip_address, WEB_PORT))

    timer.init(freq=2.5, mode=Timer.PERIODIC, callback=lambda t: led.toggle())

    random_number_for_keypad = generate_random_5digit_number()
    print("Initial 5-digit code for keypad:", random_number_for_keypad)
    lcd.clear() # <--- NEW: LCD update for initial code
    lcd.message("Scan RFID:") # <--- NEW: LCD update for initial code
    lcd.set_cursor(0,1) # <--- NEW: LCD update for initial code
    lcd.message(f"Code: {random_number_for_keypad}") # <--- NEW: LCD update for initial code

    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024)
            serve_web_page(conn)
            conn.close()
        except OSError as e:
            if e.args[0] == 110: # errno 110 is ETIMEDOUT (connection timeout)
                pass # Ignore timeout errors, they are normal for a server listening
            elif e.args[0] == 104: # errno 104 is ECONNRESET (connection reset by peer)
                pass # Client closed connection abruptly
            else:
                print('Error accepting connection: %s' % str(e))

        hardware_loop()
        
        time.sleep_ms(10) # Small delay to yield to other tasks
else:
    timer.init(freq=1, mode=Timer.PERIODIC, callback=lambda t: led.toggle())
    print("Web server not started due to WiFi connection failure.")
    lcd.clear() # <--- NEW: LCD update for WiFi failure
    lcd.message("WiFi Failed!") # <--- NEW: LCD update for WiFi failure
    lcd.set_cursor(0,1) # <--- NEW: LCD update for WiFi failure
    lcd.message("Web Svr OFF") # <--- NEW: LCD update for WiFi failure
    while True:
        hardware_loop()
        time.sleep_ms(100) # Slower loop when web server is off
