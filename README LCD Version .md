-----

# PicoSecure-Access: Smart Lock with RFID, Keypad, BSSID-Secured Web & LCD Display

-----

## Project Overview

**PicoSecure-Access** is an advanced smart lock system built on the Raspberry Pi Pico W. It combines physical security with network monitoring and local user feedback, offering secure access control via RFID tags and a keypad. It provides real-time status updates through both a web interface and a directly connected 16x2 LCD display.

A critical security enhancement is its ability to connect to your Wi-Fi network using a **specific router MAC address (BSSID)**. This prevents "Evil Twin" hotspot attacks, ensuring your Pico W only connects to your legitimate access point.

This project is perfect for those looking to implement a secure, connected, and user-friendly access control system for various applications.

-----

## Features

  * **Wi-Fi Connectivity:** Connects the Pico W to your local network.
  * **BSSID-Secured Connection:** Enhances network security by ensuring the Pico W only connects to your legitimate Wi-Fi router's specific MAC address (BSSID), preventing connection to spoofed hotspots.
  * **Web Server Interface:** Hosts a simple webpage to display:
      * Network status (IP address, connected SSID, router MAC/BSSID, signal strength).
      * The current 5-digit random code required for keypad entry after a valid RFID scan.
      * Real-time lock status (open, closed, awaiting input, unauthorized, incorrect code).
  * **16x2 LCD Display:** Provides immediate local feedback on:
      * Wi-Fi connection status and IP address.
      * RFID authorization status.
      * Keypad input prompt and the current 5-digit code.
      * Lock open/closed status.
  * **RFID Reader (RC522):**
      * Reads RFID tags to initiate the access process.
      * Only **authorized RFID tags** trigger the next step (keypad challenge).
  * **4x4 Keypad Input:**
      * Used to enter a dynamic 5-digit random code.
      * This code changes upon each successful authorized RFID scan, providing a unique challenge for every entry attempt.
  * **Solenoid Lock Control:**
      * Actuates a solenoid lock via a relay module.
      * The lock opens for a configurable duration (e.g., 5 seconds) upon successful RFID scan AND correct keypad code entry.
  * **Status Feedback:** Utilizes the Pico W's onboard LED for basic connection status indication, and provides detailed messages on both the web interface and the local LCD.

-----

## Hardware Requirements

  * **Raspberry Pi Pico W**
  * **MFRC522 RFID Reader Module**
  * **4x4 Matrix Keypad**
  * **16x2 Character LCD Display** (HD44780 compatible, non-I2C version)
  * **Single-Channel Relay Module** (compatible with 3.3V logic)
  * **Solenoid Lock** (and a suitable external power supply for it, e.g., 12V DC)
  * Jumper Wires
  * Breadboard (optional, for prototyping)

-----

## Software Requirements

  * **MicroPython Firmware:** Latest official MicroPython firmware for Raspberry Pi Pico W.
  * **Thonny IDE (Recommended):** For easy code upload, file management, and serial monitoring.
  * **MicroPython Libraries:**
      * [`mfrc522.py`](https://www.google.com/search?q=%5Bhttps://github.com/dvele/mfrc522-micropython/blob/master/mfrc522.py%5D\(https://github.com/dvele/mfrc522-micropython/blob/master/mfrc522.py\))
      * `lcd_api.py` (provided in this project, specific for parallel HD44780 LCDs)

-----

## Setup and Installation

### 1\. Flash MicroPython Firmware

  * Download the latest `rp2-pico-w-xxxxxx.uf2` file from the official [MicroPython Downloads for Pico W](https://micropython.org/download/rp2-pico-w/).
  * **Hold the `BOOTSEL` button** on your Pico W while plugging it into your computer's USB port.
  * Drag and drop the downloaded `.uf2` file onto the `RPI-RP2` drive that appears. The Pico W will automatically reboot after flashing.

### 2\. Upload Libraries

  * In Thonny, connect to your Pico W (Run \> Select Interpreter \> MicroPython (Raspberry Pi Pico) \> select your COM port).
  * Download `mfrc522.py` and the `lcd_api.py` file (from this project's repository) to your computer.
  * In Thonny, go to `View > Files`.
  * Navigate to your downloaded library files on your computer.
  * Right-click on each `.py` file and select **`Upload to /`** (or `Upload to Raspberry Pi Pico`). Ensure these files are in the root directory of your Pico W.

### 3\. Wiring

**Carefully follow these pin assignments. Refer to the code for pin numbers and adjust them in `main.py` if your wiring differs.**

  * **MFRC522 RFID Reader:**

      * `SDA` (or `CS`) to Pico W **GP5**
      * `SCK` to Pico W **GP2**
      * `MOSI` to Pico W **GP3**
      * `MISO` to Pico W **GP4**
      * `RST` to Pico W **GP14** (or any other available GPIO)
      * `VCC` to Pico W **3V3**
      * `GND` to Pico W **GND**

  * **4x4 Matrix Keypad:**

      * Keypad Rows (outputs) to Pico W: **GP16, GP17, GP18, GP19**
      * Keypad Columns (inputs) to Pico W: **GP20, GP21, GP22, GP26**

  * **Single-Channel Relay Module (for Solenoid Lock):**

      * `IN` (or `SIGNAL`) to Pico W **GP15**
      * `VCC` to Pico W **3V3** (or 5V if your relay needs it and you have a 5V source)
      * `GND` to Pico W **GND**
      * Connect your Solenoid Lock to the **Normally Open (NO)** and **COMMON** terminals of the relay. The solenoid **MUST** be powered by its **separate external power supply** (e.g., a 12V DC adapter). **Do NOT power the solenoid directly from the Pico W\!**

  * **16x2 Character LCD Display (HD44780, Non-I2C):**
    | LCD Pin Name | Description          | Pico W GPIO Pin |
    | :----------- | :------------------- | :-------------- |
    | **VSS (GND)**| Ground               | GND             |
    | **VDD (VCC)**| Power (5V or 3.3V)   | 3V3 (Out)       |
    | **VO** | Contrast             | Connect to **GND** for basic contrast, or to the middle pin of a 10k potentiometer (other potentiometer pins to 3.3V and GND) for adjustable contrast. |
    | **RS** | Register Select      | **GP0** |
    | **RW** | Read/Write           | Connect to **GND** (fixed to Write mode) |
    | **E** | Enable               | **GP1** |
    | **D0-D3** | Data Lines (unused in 4-bit mode) | -               |
    | **D4** | Data Line 4          | **GP6** |
    | **D5** | Data Line 5          | **GP7** |
    | **D6** | Data Line 6          | **GP8** |
    | **D7** | Data Line 7          | **GP9** |
    | **A (LED+)** | Backlight Anode      | 3V3 (Out)       |
    | **K (LED-)** | Backlight Cathode    | GND             |

### 4\. Configuration (`main.py`)

Open `main.py` in Thonny and modify the following variables at the top of the file:

  * **Wi-Fi Credentials:**
    ```python
    ssid = 'YourWiFiNetworkName'
    password = 'YourWiFiPassword'
    ```
  * **Known AP MAC Address (BSSID):**
      * **Crucial Security Step:** To obtain your router's exact BSSID in `bytes` format, temporarily run your current `main.py` code (or a simple Wi-Fi scanning script on your Pico W). It will print the `AP MAC (BSSID):` in a human-readable string format (e.g., `3E:DA:3D:76:C9:C8`). You need to convert this to the byte literal format.
      * For example, if your router's MAC is `3E:DA:3D:76:C9:C8`, the line should be:
        ```python
        KNOWN_AP_MAC_BYTES = b'\x3e\xda\x3d\x76\xc9\xc8' # REPLACE WITH YOUR ACTUAL ROUTER'S BSSID!
        ```
  * **Authorized RFID Tags:**
      * You'll need to read your RFID tags (e.g., using a simple RFID read example script) to get their Unique IDs (UIDs).
      * Add your authorized tags to the `AUTHORIZED_TAGS` list in bytes format:
        ```python
        AUTHORIZED_TAGS = [
            [0x04, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70], # Example Tag 1
            # Add more authorized tags here as needed
        ]
        ```
  * **Lock Open Duration:**
    ```python
    LOCK_OPEN_DURATION_MS = 5000 # Lock opens for 5 seconds (adjust as needed)
    ```
  * **Relay Logic:**
      * Verify the initial `relay.value(0)` (closed/inactive) and `relay.value(1)` (open/active) in the `open_lock()` function are correct for your specific relay module (some are active-HIGH, some active-LOW).

### 5\. Upload `main.py`

  * Save your modified `main.py` file.
  * In Thonny, right-click on your `main.py` file on your computer and select **`Upload to /`** (or `Upload to Raspberry Pi Pico`). This will overwrite the existing `main.py` on the Pico W.

-----

## How to Use

1.  **Power Up:** Connect your Pico W to power.
      * The LCD will initially display "PicoSecure-Access" and "Initializing...".
      * It will then attempt to connect to your configured Wi-Fi network. The onboard LED will blink quickly if connected, slowly if not.
      * The LCD will update to show "Connecting WiFi.." and then "WiFi Connected\!" with the IP address, or "WiFi Failed\!".
2.  **Access Web Interface (Optional):** Once connected to Wi-Fi, open a web browser on a device connected to the same network and navigate to the Pico W's IP address (e.g., `http://192.168.1.100`). The IP address will be printed in the Thonny serial monitor and shown on the LCD.
3.  **Initiate Access (RFID):**
      * Scan an **authorized RFID tag** with the MFRC522 reader.
      * The LCD will display "RFID Authorized\!" and the 5-digit code.
      * The web interface's "Lock Status" will update, and the "Current Code for Entry" will display a new 5-digit random number.
4.  **Enter Code (Keypad):**
      * On the physical 4x4 keypad, enter the 5-digit code displayed on the LCD and web page.
      * As you type, the LCD will show your input (e.g., `Code: 123_`).
5.  **Lock Actuation:**
      * If the correct code is entered, the solenoid lock will open for the configured `LOCK_OPEN_DURATION_MS`.
      * The LCD will display "Lock OPENED\!".
      * The web interface will show "Lock is OPEN\!".
      * After the duration, the lock will close, and the LCD will show "Lock CLOSED\!" and "Timeout".
      * If an incorrect code is entered, the lock will remain closed, and the LCD will display "Incorrect Code\!". The webpage will show "Incorrect code. Try again."
      * Pressing `*` on the keypad will clear the current input buffer on the LCD and web page.

-----

## Troubleshooting

  * **LCD Not Displaying:**
      * Double-check all wiring, especially RS, E, and the D4-D7 data lines.
      * Ensure `lcd_api.py` is correctly uploaded to your Pico W.
      * Adjust the contrast (`Vo` pin) connection. Try connecting it directly to GND.
      * Verify the backlight (A/K) has power.
  * **No Wi-Fi Connection:**
      * Double-check `ssid`, `password`, and **especially `KNOWN_AP_MAC_BYTES`**. Even a single incorrect byte in the BSSID will prevent connection.
      * Ensure your router is broadcasting the SSID and is within range.
      * Monitor the Thonny serial output for detailed connection status.
  * **RFID Not Reading/Authorizing:**
      * Check MFRC522 wiring carefully, especially SCK, MOSI, MISO, SDA, RST pins.
      * Ensure `mfrc522.py` is uploaded to the Pico W.
      * Verify your `AUTHORIZED_TAGS` list contains the correct UIDs in the right format.
  * **Keypad Not Responding:**
      * Check keypad wiring to the Pico W (rows to output pins, columns to input pins with pull-ups).
  * **Lock Not Actuating:**
      * Check relay wiring to the Pico W (`RELAY_PIN`).
      * Verify the relay's `VCC` and `GND` connections.
      * Ensure your solenoid lock has its own dedicated power supply and is correctly wired through the relay's NO and COMMON terminals.
      * Check the `relay.value(0)` and `relay.value(1)` logic in the code to match your relay's activation state.

-----

## Future Enhancements

  * **Persistent Configuration:** Store Wi-Fi credentials and authorized tags in `boot.py` or a separate `config.py` file, or use `micropython-json` for more robust configuration that persists across reboots.
  * **Advanced Keypad Features:** Implement a fixed master code for administrative access, or more complex keypad input sequences.
  * **Logging:** Implement more detailed logging of access attempts (success/failure) to flash memory or an external service (e.g., MQTT, HTTP POST).
  * **Time-based Access:** Add a real-time clock (RTC) module to enable time-restricted access for specific RFID tags or codes.
  * **Remote Notifications:** Integrate with a notification service (e.g., Pushover, IFTTT, email) to send alerts on access events or failed attempts.
  * **OTA Updates:** Implement Over-The-Air (OTA) firmware updates for easier deployment of new features or bug fixes.

-----

This project provides a robust and secure foundation for various access control applications. Enjoy building and securing your space with PicoSecure-Access\!
