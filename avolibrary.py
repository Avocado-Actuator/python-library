from math import radians
from enum import Enum
from typing import Any
import serial, time, sys

STOP_BYTE = '\0'
CRC_TABLE = [
    0xea, 0xd4, 0x96, 0xa8, 0x12, 0x2c, 0x6e, 0x50, 0x7f, 0x41, 0x03, 0x3d,
    0x87, 0xb9, 0xfb, 0xc5, 0xa5, 0x9b, 0xd9, 0xe7, 0x5d, 0x63, 0x21, 0x1f,
    0x30, 0x0e, 0x4c, 0x72, 0xc8, 0xf6, 0xb4, 0x8a, 0x74, 0x4a, 0x08, 0x36,
    0x8c, 0xb2, 0xf0, 0xce, 0xe1, 0xdf, 0x9d, 0xa3, 0x19, 0x27, 0x65, 0x5b,
    0x3b, 0x05, 0x47, 0x79, 0xc3, 0xfd, 0xbf, 0x81, 0xae, 0x90, 0xd2, 0xec,
    0x56, 0x68, 0x2a, 0x14, 0xb3, 0x8d, 0xcf, 0xf1, 0x4b, 0x75, 0x37, 0x09,
    0x26, 0x18, 0x5a, 0x64, 0xde, 0xe0, 0xa2, 0x9c, 0xfc, 0xc2, 0x80, 0xbe,
    0x04, 0x3a, 0x78, 0x46, 0x69, 0x57, 0x15, 0x2b, 0x91, 0xaf, 0xed, 0xd3,
    0x2d, 0x13, 0x51, 0x6f, 0xd5, 0xeb, 0xa9, 0x97, 0xb8, 0x86, 0xc4, 0xfa,
    0x40, 0x7e, 0x3c, 0x02, 0x62, 0x5c, 0x1e, 0x20, 0x9a, 0xa4, 0xe6, 0xd8,
    0xf7, 0xc9, 0x8b, 0xb5, 0x0f, 0x31, 0x73, 0x4d, 0x58, 0x66, 0x24, 0x1a,
    0xa0, 0x9e, 0xdc, 0xe2, 0xcd, 0xf3, 0xb1, 0x8f, 0x35, 0x0b, 0x49, 0x77,
    0x17, 0x29, 0x6b, 0x55, 0xef, 0xd1, 0x93, 0xad, 0x82, 0xbc, 0xfe, 0xc0,
    0x7a, 0x44, 0x06, 0x38, 0xc6, 0xf8, 0xba, 0x84, 0x3e, 0x00, 0x42, 0x7c,
    0x53, 0x6d, 0x2f, 0x11, 0xab, 0x95, 0xd7, 0xe9, 0x89, 0xb7, 0xf5, 0xcb,
    0x71, 0x4f, 0x0d, 0x33, 0x1c, 0x22, 0x60, 0x5e, 0xe4, 0xda, 0x98, 0xa6,
    0x01, 0x3f, 0x7d, 0x43, 0xf9, 0xc7, 0x85, 0xbb, 0x94, 0xaa, 0xe8, 0xd6,
    0x6c, 0x52, 0x10, 0x2e, 0x4e, 0x70, 0x32, 0x0c, 0xb6, 0x88, 0xca, 0xf4,
    0xdb, 0xe5, 0xa7, 0x99, 0x23, 0x1d, 0x5f, 0x61, 0x9f, 0xa1, 0xe3, 0xdd,
    0x67, 0x59, 0x1b, 0x25, 0x0a, 0x34, 0x76, 0x48, 0xf2, 0xcc, 0x8e, 0xb0,
    0xd0, 0xee, 0xac, 0x92, 0x28, 0x16, 0x54, 0x6a, 0x45, 0x7b, 0x39, 0x07,
    0xbd, 0x83, 0xc1, 0xff]

def crc8(crc: bytes, msg: str) -> bytes:
  if msg == '':
    return bytes.fromhex('00')
  crc &= 0xff
  for c in msg:
    crc = CRC_TABLE[crc ^ bytes(c, 'ascii')[0]]
  return crc

class PosUnit(Enum):
  RADIANS = 1 # prefer radians based on project specifications
  DEGREES = 2

class VelUnit(Enum):
  RPS = 1 # radians per second - prefer radians based on project specifications
  RPM = 2 # rotations per minute

class Communicator:
  """Provides abstractions for communication with an arbitrary number of actuators

    Attributes:
      port_num: specifies serial port used for communication. On *NIX this looks
        like '/dev/ttyACM0', on Windows like 'COM3'
      pos_unit: unit for position
      vel_unit: unit for velocity
      ser: Serial object for communication (timeout arbitrarily set to 0.01s)
  """
  def __init__(self, port_num: str, pos_unit: PosUnit = PosUnit.RADIANS, vel_unit: VelUnit = VelUnit.RPS) -> None:
    """Constructor simply setting attributes"""
    self.port_num: str = port_num
    self.pos_unit: PosUnit = pos_unit
    self.vel_unit: VelUnit = vel_unit
    self.ser: serial.Serial = serial.Serial(port_num, 115200, timeout=0.05)

  def __del__(self) -> None:
    self.ser.close()

  def _convert_pos_to_radians(self, pos: float) -> float:
    """Convert a given position to radians if it is not already

      Allows users to specify multiple units but simplify MCU communications by
      supporting a single unit on the MCU and converting user provided units to
      that unit. Choosing radians based on user specifications.

      Args:
        pos: position specified in self.pos_unit units

      Returns:
        position converted to radians
    """
    return pos if self.pos_unit == PosUnit.RADIANS else radians(pos)

  def rotate_to_position(self, addr: int, pos: float) -> str:
    """Rotates actuator given by addr to postion given by pos

      Args:
        addr: id for specific actuator to rotate
        pos: position specified in self.pos_unit units

      Returns:
        the response of the mcu

      TODO:
        - Allow user to specify timing/speed on rotation?
    """
    self._send_to_mcu(addr, f'set pos {pos}')
    return self._read_from_mcu()

  def rotate_at_velocity(self, addr: int, vel: float) -> str:
    """Rotates actuator given by addr at velocity given by vel

      Args:
        addr: id for specific actuator to rotate
        vel: velocity specified in self.vel_unit units

      Returns:
        the response of the mcu

      TODO:
        - Allow user to specify how long they would like rotation to occur for?
    """
    self._send_to_mcu(addr, f'set vel {vel}')
    return self._read_from_mcu()

  def rotate_at_current(self, addr: int, cur: float) -> str:
    """Rotates actuator given by addr at current given by cur

      Args:
        addr: id for specific actuator to rotate
        cur: current specified in amperes

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, f'set cur {cur}')
    return self._read_from_mcu()

  def get_position(self, addr: int) -> str:
    """Returns the current position the actuator is at

      Args:
        addr: id for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get pos')
    return self._read_from_mcu()

  def get_velocity(self, addr: int) -> str:
    """Returns the current velocity the actuator is rotating at

      Args:
        addr: id for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get vel')
    return self._read_from_mcu()

  def get_current(self, addr: int) -> str:
    """Returns the current the actuator is operating at

      Args:
        addr: id for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get cur')
    return self._read_from_mcu()

  def get_temperature(self, addr: int) -> str:
    """Returns the temperature the actuator is operating at

      Args:
        addr: id for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get tmp')
    return self._read_from_mcu()

  def _send_to_mcu(self, addr: int, message: str) -> None:
    """Serialize and send a message to MCU

      Args:
        addr: actuator id
        message: user message to send

      Returns:
        true for success
    """
    crc = crc8(0, message)
    cmd = f'{addr} {message}{crc}{STOP_BYTE}'
    self.ser.write(cmd.encode('utf-8'))

  def _read_from_mcu(self) -> str:
    """Receive messages from MCU

      Returns:
        the contents of the receive buffer
    """
    lines = self.ser.readlines()
    if(len(lines) > 1): raise ValueError("Multiline buffer returned")

    return lines[0].decode("utf-8").replace(STOP_BYTE, ' ') if lines else []

def main():
  print("\n*** Running main function ***\n")
  # placeholder port
  '''port = 'COM5'
  if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in ['win', 'mac']:
      port = '/dev/tty.usbserial-FTJRNS8A' if arg == 'mac' else 'COM5'
    else:
      port = arg

  comm = Communicator(port)

  print(comm.rotate_at_velocity(1, 99.999))
  print(comm.rotate_at_current(1, 50.0))
  print(comm.rotate_to_position(1, 10000.023))
  print(comm.get_velocity(1))
  print(comm.get_position(1))
  print(comm.get_current(1))
  print(comm.get_temperature(1))
  del comm'''
  msg = 'hello'
  crc = crc8(0, msg)
  print(msg + ' ' + str(crc) + '\n')

if __name__ == "__main__":
  main()
