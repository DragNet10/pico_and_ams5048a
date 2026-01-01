# pico_and_ams5048a
A diagnostic tool for the AMS5048A magnetic rotation position sensor. This is meant to be a minimal viable product project to test the sensistivity of the AMS5048A for particular applications. It is missing:
[ ] Limit switch zero
[ ] Advanced Diagnostics
[ ] Direct Memory Acess (DMA) embedded C version

This is clunky and in python. Python is slow. C would be better, but this is just a little test.

## Hardware Connections

![Pico Connected to the AS5048A](.documentation_assets/spi_conn.png)



# AS5048A to Raspberry Pi Pico Pinout

| AS5048A Pin       | Raspberry Pi Pico Pin      | Description                                                                 |
|-------------------|----------------------------|-----------------------------------------------------------------------------|
| VCC               | 3.3V (Pin 36)             | Power supply (sensor is 3.3V–5V tolerant; connect to 3.3V for logic compatibility) |
| GND               | GND (e.g., Pin 23)        | Ground (closest to prevent large ground loop)                             |
| SCK (CLK)         | GP18 (SPI0 SCK)           | SPI clock signal                                                            |
| MISO (DO)         | GP16 (SPI0 RX)            | Master In Slave Out – data output from the AS5048A sensor to the Pico        |
| MOSI (DI)         | GP19 (SPI0 TX)            | Master Out Slave In – command/data input to the AS5048A sensor from the Pico |
| CS                | GP17 (any GPIO)           | Chip Select (active low) – used to select the sensor on the SPI bus         |
| PROG (optional)   | Not needed                | Programming pin for firmware updates; leave floating/unconnected for normal operation |


AS5048A PinRaspberry Pi Pico PinDescriptionVCC3.3V (Pin 36)Power (3.3V-5V tolerant)GNDGND (e.g., Pin 38)GroundSCK (CLK)GP18 (SPI0 SCK)ClockMISO (DO)GP16 (SPI0 RX)Master In Slave Out (data from sensor)MOSI (DI)GP19 (SPI0 TX)Master Out Slave In (commands to sensor)CSGP17 (any GPIO)Chip Select (active low)PROG (optional)Not neededFor programming, leave floating

## Software Development - Thonny

### Windows Install
https://thonny.org/

### Linux (Ubuntu/Debian) Install
```bash
apt install thonny
```

# How to Use in Thonny

1. Connect your Pico and ensure Thonny is set to MicroPython (Raspberry Pi Pico) interpreter.
2. Copy the script into a new file (e.g., as5048a.py).
3. Adjust the CS pin if you're using a different GPIO.
4. Run the script. You should see continuous angle readings in degrees.

# Troubleshooting

## Pico Not Connecting
Thonny is pretty clever. If the pico is plugged in using the mico-USB cable. Thonny should see it. I havne't encountered this issue unless the pico was disconnected.
![Pico Not Connecting](.documentation_assets/pico_no_connect.png)
## SPI Bus Not Working
There isn't any smarts when it comes to debugging the SPI connection. It just reads the SPI register data and assumes you're good. In practice you'd compare the diagnostics output with expected values and throw an error if data is bad.
![SPI Bus Not Working](.documentation_assets/terminal_bad_spi.png)
## No Magnet On Sensor (Or magnetic field too weak)
The AS5048A has a nice diagnostic register (see the AS5048A datasheet page 17.)

The Automatic Gain Control (AGC) register contains how strong the magnetic field is. A good value is close to 0. Bad values I've seen are around 60. Proper firmware would find a way to ouptu errors if AGC was too high for too long (weakened magnet, broken sensor, etc.)
![Weak Magnet](.documentation_assets/terminal_bad_acg.png)


