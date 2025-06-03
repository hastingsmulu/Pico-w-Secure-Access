
-----

# PicoSecure-Access: Smart Lock with RFID, Keypad, and BSSID-Secured Web Control

-----

## Project Overview

**PicoSecure-Access** is a robust and feature-rich smart lock system built on the Raspberry Pi Pico W. It combines physical security with network monitoring, allowing for secure access control via RFID tags and a keypad, all while providing real-time status updates through a web interface. A key security feature is its ability to connect to your Wi-Fi network using a **specific router MAC address (BSSID)**, mitigating "Evil Twin" hotspot attacks.

This project is ideal for those looking to build a secure, connected access control system for doors, cabinets, or any other physical barrier.

-----

## Features

  * **Wi-Fi Connectivity:** Connects the Pico W to your local network.
  * **BSSID-Secured Connection:** Enhances network security by ensuring the Pico W only connects to your legitimate Wi-Fi router's specific MAC address (BSSID), preventing connection to spoofed hotspots.
  * **Web Server Interface:** Hosts a simple webpage to display:
      * Network status (IP address, connected SSID, router MAC/BSSID, signal strength).
      * The current 5-digit random code required for keypad entry after a valid RFID scan.
      * Real-time lock status (open, closed, awaiting input, unauthorized, incorrect code).
  * **RFID Reader (RC522):**
      * Reads RFID tags to initiate the access process.
      * Only **authorized RFID tags** trigger the next step (keypad challenge).
  * **4x4 Keypad Input:**
      * Used to enter a dynamic 5-digit random code.
      * This code changes upon each successful authorized RFID scan, providing a unique challenge for every entry attempt.
  * **Solenoid Lock Control:**
      * Actuates a solenoid lock via a relay module.
      * The lock opens for a configurable duration (e.g., 5 seconds) upon successful RFID scan AND correct keypad code entry.
  * **Status Feedback:** Utilizes the Pico W's onboard LED for basic connection status indication and provides detailed messages on the web interface and serial output.

-----

## Hardware Requirements

  * **Raspberry Pi Pico W**
  * **MFRC522 RFID Reader Module**
  * **4x4 Matrix Keypad**
  * **Single-Channel Relay Module** (compatible with 3.3V logic)
  * **Solenoid Lock** (and a suitable power supply for it, e.g., 12V DC)
  * Jumper Wires
  * Breadboard (optional, for prototyping)

-----

## Software Requirements

  * **MicroPython Firmware:** Latest official MicroPython firmware for Raspberry Pi Pico W.
  * **Thonny IDE (Recommended):** For easy code upload and serial monitoring.
  * **MicroPython Libraries:**
      * [`mfrc522.py`](https://www.google.com/search?q=%5Bhttps://github.com/dvele/mfrc522-micropython/blob/master/mfrc522.py%5D\(https://github.com/dvele/mfrc522-micropython/blob/master/mfrc522.py\)) (or a similar compatible library)
      * A suitable `keypad.py` library (e.g., from `micropython-4x4-keypad` project or a custom one if the provided rudimentary function is used)

-----

## Setup and Installation

### 1\. Flash MicroPython Firmware

  * Download the latest `rp2-pico-w-xxxxxx.uf2` file from the official [MicroPython Downloads for Pico W](https://micropython.org/download/rp2-pico-w/).
  * Hold the `BOOTSEL` button on your Pico W while plugging it into your computer's USB port.
  * Drag and drop the downloaded `.uf2` file onto the `RPI-RP2` drive that appears. The Pico W will reboot.

### 2\. Upload Libraries

  * In Thonny, connect to your Pico W (Run \> Select Interpreter \> MicroPython (Raspberry Pi Pico) \> select your COM port).
  * Download `mfrc522.py` and your chosen `keypad.py` library file to your computer.
  * In Thonny, go to `View > Files`.
  * Navigate to your downloaded library files on your computer.
  * Right-click on each `.py` file and select `Upload to /` (or `Upload to Raspberry Pi Pico`). Ensure these files are in the root directory of your Pico W.

### 3\. Wiring

**Refer to the pin assignments in `main.py` and adjust them if necessary to match your physical connections.**

  * **MFRC522 RFID Reader:**

      * `SDA` (or `CS`) to Pico W **GP5**
      * `SCK` to Pico W **GP2**
      * `MOSI` to Pico W **GP3**
      * `MISO` to Pico W **GP4**
      * `RST` to Pico W **GP14** (or any other available GPIO)
      * `VCC` to Pico W **3V3**
      * `GND` to Pico W **GND**

  * **4x4 Keypad:**

      * Connect keypad rows (outputs) to Pico W **GP16, GP17, GP18, GP19**.
      * Connect keypad columns (inputs) to Pico W **GP20, GP21, GP22, GP26**.

  * **Relay Module (for Solenoid Lock):**

      * `IN` (or `SIGNAL`) to Pico W **GP15**
      * `VCC` to Pico W **3V3** (or 5V if your relay needs it and you have a 5V source)
      * `GND` to Pico W **GND**
      * Connect your Solenoid Lock to the **Normally Open (NO)** and **COMMON** terminals of the relay, powered by its **separate power supply**. **Do NOT power the solenoid directly from the Pico W\!**

### 4\. Configuration (`main.py`)

Open `main.py` in Thonny and make the following critical adjustments:

  * **Wi-Fi Credentials:**
    ```python
    ssid = 'YourWiFiNetworkName'
    password = 'YourWiFiPassword'
    ```
  * **Known AP MAC Address (BSSID):**
      * **Crucial Security Step:** To get your router's exact BSSID in `bytes` format, run your *current* `main.py` once (before making this BSSID change if you haven't yet). It will print the `AP MAC (BSSID):` in a human-readable format. For example, if it prints `3E:DA:3D:76:C9:C8`, then you would use `b'\x3e\xda\x3d\x76\xc9\xc8'`.
      * Update this line:
        ```python
        KNOWN_AP_MAC_BYTES = b'\x3e\xda\x3d\x76\xc9\xc8' # REPLACE WITH YOUR ACTUAL ROUTER'S BSSID!
        ```
  * **Authorized RFID Tags:**
      * You'll need to read your RFID tags (e.g., using a simple RFID read example script) to get their Unique IDs (UIDs).
      * Add your authorized tags to the `AUTHORIZED_TAGS` list in bytes format:
        ```python
        AUTHORIZED_TAGS = [
            [0x04, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70], # Example Tag 1
            [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11]  # Example Tag 2
        ]
        ```
  * **Lock Open Duration:**
    ```python
    LOCK_OPEN_DURATION_MS = 5000 # Lock opens for 5 seconds (adjust as needed)
    ```
  * **Relay Logic:**
      * Verify the initial `relay.value(0)` and the `relay.value(1)` in `open_lock()` are correct for your specific relay module (active-HIGH vs. active-LOW).

### 5\. Upload `main.py`

  * Save your modified `main.py` file.
  * In Thonny, right-click on your `main.py` file on your computer and select `Upload to /` (or `Upload to Raspberry Pi Pico`). This will overwrite the existing `main.py` on the Pico W.

-----

## How to Use

1.  **Power Up:** Connect your Pico W to power. It will attempt to connect to the configured Wi-Fi network. The onboard LED will blink quickly if connected, slowly if not.
2.  **Access Web Interface:** Once connected, open a web browser on a device connected to the same network and navigate to the Pico W's IP address (e.g., `http://192.168.1.100`). The IP address will be printed in the Thonny serial monitor.
3.  **Initiate Access:**
      * Scan an **authorized RFID tag** with the MFRC522 reader.
      * The web interface's "Lock Status" will update, and the "Current Code for Entry" will display a new 5-digit random number.
4.  **Enter Code:** On the physical 4x4 keypad, enter the 5-digit code displayed on the webpage.
5.  **Lock Actuation:**
      * If the correct code is entered, the solenoid lock will open for the configured `LOCK_OPEN_DURATION_MS`.
      * The web interface will show "Lock is OPEN\!"
      * If an incorrect code is entered, the lock will remain closed, and the webpage will show "Incorrect code. Try again."
      * The keypad supports `*` as a clear/reset button for the input buffer.

-----

## Troubleshooting

  * **`ValueError: bad SCK pin` or `bad MISO pin`:** Ensure your Pico W firmware is up-to-date and that your SPI pins (`GP2`, `GP3`, `GP4`, `GP5`) are wired correctly for `SPI0`. These are the most reliable SPI pins on the Pico.
  * **`ValueError: unknown config param`:** This error when checking BSSID has been addressed in the code. If it still occurs, ensure you've uploaded the latest `main.py`.
  * **No Wi-Fi Connection:**
      * Double-check `ssid`, `password`, and especially `KNOWN_AP_MAC_BYTES`. Even a single incorrect byte in the BSSID will prevent connection.
      * Ensure your router is broadcasting the SSID and is within range.
      * Monitor the serial output for connection status.
  * **RFID Not Reading:**
      * Check MFRC522 wiring carefully, especially SCK, MOSI, MISO, SDA, RST pins.
      * Ensure `mfrc522.py` is uploaded to the Pico W.
      * Verify your `AUTHORIZED_TAGS` list contains the correct UIDs in the right format.
  * **Keypad Not Responding:**
      * Check keypad wiring to the Pico W (rows to output pins, columns to input pins with pull-ups).
      * Ensure the keypad library (if used) is uploaded, or the `read_keypad()` function is correctly integrated.
  * **Lock Not Actuating:**
      * Check relay wiring to the Pico W (`RELAY_PIN`).
      * Verify the relay's `VCC` and `GND` connections.
      * Ensure your solenoid lock has its own dedicated power supply and is correctly wired through the relay's NO and COMMON terminals.
      * Check the `relay.value(0)` and `relay.value(1)` logic in the code to match your relay's activation state.

-----

## Future Enhancements

  * **Persistent Configuration:** Store Wi-Fi credentials and authorized tags in `boot.py` or a separate `config.py` file, or use `micropython-json` for more robust configuration.
  * **User Interface:** Add buttons to the webpage for manually opening/closing the lock (with appropriate security) or refreshing status.
  * **Logging:** Implement more detailed logging of access attempts (success/failure) to flash memory or an external service.
  * **Time-based Access:** Add a real-time clock (RTC) module to enable time-restricted access.
  * **Notifications:** Integrate with a notification service (e.g., MQTT, IFTTT) to send alerts on access events.

-----

This project provides a strong foundation for building sophisticated access control systems with MicroPython\! Enjoy securing your assets\!
