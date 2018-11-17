"""
This module provides classes for interfacing with a PCA9685 PWM extension.
"""
import time

from myDevices.devices.i2c import I2C
from myDevices.devices.analog import PWM
from myDevices.plugins.analog import AnalogOutput


class PCA9685(PWM, I2C):
    """Base class for interacting with a PCA9685 extension."""

    MODE1    = 0x00
    PWM_BASE = 0x06
    PRESCALE = 0xFE
    
    M1_SLEEP    = 1<<4
    M1_AI       = 1<<5
    M1_RESTART  = 1<<7
    
    def __init__(self, slave=0x40, frequency=50):
        """Initializes PCA9685 device.

        Arguments:
        slave: The slave address
        frequency: The PWM control frequency
        """
        I2C.__init__(self, int(slave))
        PWM.__init__(self, 16, 12, int(frequency))        
        self.VREF = 0
        self.prescale = int(25000000.0/((2**12)*self.frequency))
        self.mode1 = self.M1_RESTART | self.M1_AI
        self.writeRegister(self.MODE1, self.M1_SLEEP)
        self.writeRegister(self.PRESCALE, self.prescale)
        time.sleep(0.01)
        self.writeRegister(self.MODE1, self.mode1)
        
    def __str__(self):
        """Returns friendly name."""
        return "PCA9685(slave=0x%02X)" % self.slave

    def __pwmRead__(self, channel):
        """Returns the value for the specified channel. Overrides PWM.__pwmRead__."""
        addr = self.getChannelAddress(channel)
        d = self.readRegisters(addr, 4)
        start = d[1] << 8 | d[0]
        end   = d[3] << 8 | d[2]
        return end-start
    
    def __pwmWrite__(self, channel, value):
        """Writes the value to the specified channel. Overrides PWM.__pwmWrite__."""
        addr = self.getChannelAddress(channel)
        d = bytearray(4)
        d[0] = 0
        d[1] = 0
        d[2] = (value & 0x0FF)
        d[3] = (value & 0xF00) >> 8
        self.writeRegisters(addr, d)

    def getChannelAddress(self, channel):
        """Returns the address for the specified channel."""
        return int(channel * 4 + self.PWM_BASE)


class PCA9685Test(PCA9685):
    """Class for simulating a PCA9685 device."""

    def __init__(self):
        """Initializes the test class."""
        self.registers = {}
        PCA9685.__init__(self)

    def readRegister(self, addr):
        """Read value from a register."""
        if addr not in self.registers:
            self.registers[addr] = 0
        return self.registers[addr]

    def readRegisters(self, addr, size):
        """Read value from a register."""
        if addr not in self.registers:
            self.registers[addr] = bytearray(size)
        return self.registers[addr]

    def writeRegister(self, addr, value):
        """Write value to a register."""
        self.registers[addr] = value

    def writeRegisters(self, addr, value):
        """Write value to a register."""
        self.registers[addr] = value        