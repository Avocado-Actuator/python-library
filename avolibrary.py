from math import radians
from enum import Enum
from typing import Any
import serial, time, sys

STOP_BYTE = '\0'

class PosUnit(Enum):
  RADIANS = 1 # prefer radians based on project specifications
  DEGREES = 2

class VelUnit(Enum):
  RPS = 1 # radians per second - prefer radians based on project specifications
  RPM = 2 # rotations per minute

class Communicator:
  """Provides abstractions for communication with an arbitrary number of actuators

    Attributes:
      port_num: specifies serial port used for communication. On *NIX this
        looks like '/dev/ttyACM0', on Windows like 'COM3'
      pos_unit: unit for position
      vel_unit: unit for velocity
      ser: Serial object for serial communication (timeout arbitrarily
        set to 0.01s)

    TODO:
      - Specify types of message (probably just strings but maybe worth discussing)
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
    """Allow users to specify multiple units but simplify MCU communications by
      supporting a single unit on the MCU and converting user provided units to
      that unit. Choosing radians based on user specifications.

      Args:
        position specified in self.pos_unit units

      Returns:
        float
    """
    return pos if self.pos_unit == PosUnit.RADIANS else radians(pos)

  def rotate_to_position(self, addr: int, pos: float) -> str:
    """Rotates actuator given by addr to postion given by pos

      Args:
        addr: identifier for specific actuator to rotate
        pos: position specified in self.pos_unit units

      Returns:
        whether or not operation succeeded (may want higher fidelity
          response in future)

      TODO:
        - Allow user to specify timing/speed on rotation?
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    pos_message: str = f'set pos {pos}'
    self._send_to_mcu(addr, pos_message)
    # currently pretending read_from_mcu returns strings
    response: str = self._read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response

  def rotate_at_velocity(self, addr: int, vel: float) -> str:
    """Rotates actuator given by addr at velocity given by vel

      Args:
        addr: identifier for specific actuator to rotate
        vel: velocity specified in self.vel_unit units

      Returns:
        whether or not operation succeeded (may want higher fidelity
          response in future)

      TODO:
        - Allow user to specify how long they would like rotation to occur for?
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    # vel_message: str = f'some message here plus insert given vel {vel}'
    vel_message: str = f'set vel {vel}'
    self._send_to_mcu(addr, vel_message)
    # currently pretending read_from_mcu returns strings
    response: str = self._read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response

  def rotate_at_current(self, addr: int, cur: float) -> str:
    """Rotates actuator given by addr at current given by cur

      Args:
        addr: identifier for specific actuator to rotate
        cur: current specified in amperes

      Returns:
        whether or not operation succeeded (may want higher fidelity
          response in future)
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    cur_message: str = f'set cur {cur}'
    self._send_to_mcu(addr, cur_message)
    # currently pretending read_from_mcu returns strings
    response: str = self._read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response

  def get_position(self, addr: int) -> str:
    """Returns the current position the actuator is at

      Args:
        addr: identifier for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get pos')
    response: str = self._read_from_mcu()
    return response

  def get_velocity(self, addr: int) -> str:
    """Returns the current velocity the actuator is rotating at

      Args:
        addr: identifier for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get vel')
    response: str = self._read_from_mcu()
    return response

  def get_current(self, addr: int) -> str:
    """Returns the current the actuator is operating at

      Args:
        addr: Identifier for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get cur')
    response: str = self._read_from_mcu()
    return response

  def get_temperature(self, addr: int) -> str:
    """Returns the temperature the actuator is operating at

      Args:
        addr: identifier for specific actuator

      Returns:
        the response of the mcu
    """
    self._send_to_mcu(addr, 'get tmp')
    response: str = self._read_from_mcu()
    return response

  def _send_to_mcu(self, addr: int, message: str) -> bool:
    """Serialize and send a message to MCU

      Args:
        addr: Placeholder argument for actuator id
        message: Placeholder argument/type for user message

      Returns:
        true for success (placeholder)
    """
    cmd: str = f'{addr} {message}{STOP_BYTE}'
    self.ser.write(cmd.encode('utf-8'))
    return True

  def _read_from_mcu(self) -> str:
    """Purpose is to receive messages from MCU

      Returns:
        the contents of the receive buffer
    """
    lines = self.ser.readlines()
    if(len(lines) > 1): raise ValueError("Multiline buffer returned")

    return lines[0].decode("utf-8").replace(STOP_BYTE, ' ') if lines else []

def main():
  print("\n*** Running main function ***\n")
  # placeholder port
  port = 'COM5'
  if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in ['win', 'mac']:
      port = '/dev/tty.usbserial-FTJRNS8A' if arg == 'mac' else 'COM5'
    else:
      port = arg

  comm = Communicator(port)

  print(comm.rotate_at_velocity(1, 50.0))
  print(comm.rotate_at_current(2, 50.0))
  print(comm.rotate_to_position(1, 50.0))
  print(comm.get_velocity(1))
  print(comm.get_position(2))
  print(comm.get_current(1))
  del comm

if __name__ == "__main__":
  main()
