from machine import Pin, SPI
import time

class AS5048A:
    ANGLE_REG = 0x3FFF  # Angle register
    DIAG_REG = 0x3FFD   # Diagnostics register (AGC, etc.)
    NOP = 0x0000        # No operation
    
    def __init__(self, spi_id=0, sck_pin=18, mosi_pin=19, miso_pin=16, cs_pin=17, baudrate=1000000):
        """
        Initialize SPI and CS pin.
        - spi_id: 0 or 1 for hardware SPI
        - Pins: Default for SPI0
        - baudrate: 1MHz recommended (up to 10MHz); try lower if issues
        """
        self.spi = SPI(spi_id,
                       baudrate=baudrate,
                       polarity=0,  # CPOL=0
                       phase=1,     # CPHA=1 → SPI Mode 1
                       sck=Pin(sck_pin),
                       mosi=Pin(mosi_pin),
                       miso=Pin(miso_pin))
        
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)  # Inactive high
        
        # Prime the sensor by reading once (clears any pending data)
        self.read_angle_raw()
    
    def _calc_parity_bit(self, value):
        """Calculate even parity bit (0 or 1) for 15-bit value."""
        v = value & 0x7FFF  # Lower 15 bits
        parity = 0
        while v:
            parity ^= (v & 1)
            v >>= 1
        return parity  # 1 if odd count (to make even), else 0
    
    def _build_command(self, address, read=True):
        """Build 16-bit command with read bit and parity."""
        cmd = address & 0x3FFF  # 14-bit address
        if read:
            cmd |= 0x4000  # Set read bit (bit 14)
        parity = self._calc_parity_bit(cmd)
        return cmd | (parity << 15)
    
    def _transfer(self, data):
        """Send 16-bit data and receive 16-bit response."""
        self.cs.value(0)  # Select
        try:
            tx = bytearray([data >> 8, data & 0xFF])  # MSB first
            rx = bytearray(2)
            self.spi.write_readinto(tx, rx)
            response = (rx[0] << 8) | rx[1]
        finally:
            self.cs.value(1)  # Deselect
        return response
    
    def _validate_response(self, data):
        """Validate even parity and return error flag."""
        # Compute XOR over all 16 bits; should be 0 for even parity
        v = data
        parity_check = 0
        for _ in range(16):
            parity_check ^= (v & 1)
            v >>= 1
        if parity_check != 0:
            raise ValueError("Parity error in response")
        
        error_flag = (data & 0x4000) >> 14  # Bit 14: EF (1=error)
        return error_flag
    
    def read_register(self, reg):
        """Generic read for any register."""
        cmd = self._build_command(reg, read=True)
        self._transfer(cmd)  # Send command
        data = self._transfer(self._build_command(self.NOP, read=False))  # Send NOP, get response
        ef = self._validate_response(data)
        if ef:
            raise ValueError("Sensor error flag set")
        return data & 0x3FFF  # Mask to 14 bits
    
    def read_angle_raw(self):
        """Read raw 14-bit angle value."""
        return self.read_register(self.ANGLE_REG)
    
    def read_diagnostics(self):
        """Read diagnostics: bits 13-9 reserved, 8 OCF, 7 COF, 6 LIN, 5-0 AGC."""
        diag = self.read_register(self.DIAG_REG)
        ocf = (diag & 0x0100) >> 8  # Offset compensation finished
        cof = (diag & 0x0080) >> 7  # CORDIC overflow
        lin = (diag & 0x0040) >> 6  # Linearity alarm
        agc = diag & 0x003F         # Automatic gain control (lower=stronger field)
        return {'ocf': ocf, 'cof': cof, 'lin': lin, 'agc': agc}
    
    def read_angle_degrees(self):
        """Return angle in degrees (0-360)."""
        raw = self.read_angle_raw()
        return (raw / 16383.0) * 360.0
    
    def read_angle_radians(self):
        """Return angle in radians (0-2π)."""
        raw = self.read_angle_raw()
        return (raw / 16383.0) * (2 * 3.141592653589793)

# Example usage
encoder = AS5048A(baudrate=500000)  # Try lower baudrate if needed

while True:
    try:
        degrees = encoder.read_angle_degrees()
        diag = encoder.read_diagnostics()
        print(f"Angle: {degrees:.2f} degrees | Diagnostics: {diag}")
    except ValueError as e:
        print(f"Error: {e}")
    time.sleep(0.1)