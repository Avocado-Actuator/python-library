from math import degrees
from enum import Enum

class PosUnit(Enum):
  DEGREES = 1
  RADIANS = 2

class VelUnit(Enum):
  RPM = 1

class Communicator:
  """
    Provides abstractions for communication with an arbitrary number of actuators.

    Attributes:
      port_num (int): Specifies serial port used for communication
      pos_unit (PosUnit): Unit for position
      vel_unit (VelUnit): Unit for velocity

    TODO:
      - Specify types of message (probably just strings but maybe worth discussing)
  """
  def __init__(self, port_num: int, pos_unit: PosUnit = PosUnit.DEGREES, vel_unit: VelUnit = VelUnit.RPM):
    """
      Constructor simply setting attributes
    """
    self.port_num = port_num
    self.pos_unit = pos_unit
    self.vel_unit = vel_unit

  def _convert_pos_to_degrees(self, pos: float) -> float:
    """
      Allow users to specify multiple units but simplify MCU communications by
      supporting a single unit on the MCU and converting user provided units to
      that unit. Arbitrarily choosing degrees for the MCU unit.

      Args:
        pos (float): Position specified in self.pos_unit units

      Returns:
        float
    """
    return pos if self.pos_unit == PosUnit.DEGREES else degrees(pos)

  def rotate_to_position(self, id: int, pos: float) -> bool:
    """
      Rotates actuator given by id to postion given by pos

      Args:
        id (int): Identifier for specific actuator to rotate
        pos (float): Position specified in self.pos_unit units

      Returns:
        bool: whether or not operation succeeded (may want higher fidelity response in future)

      TODO:
        - Allow user to specify timing/speed on rotation?
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    pos_message: str = f'some message here plus insert given pos {pos}'
    send_to_mcu(id, pos_message)

    # currently pretending read_from_mcu returns strings
    response: str = read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response == 'some message'

  def rotate_at_velocity(self, id: int, vel: float) -> bool:
    """
      Rotates actuator given by id at velocity given by vel

      Args:
        id (int): Identifier for specific actuator to rotate
        vel (float): Velocity specified in self.vel_unit units

      Returns:
        bool: whether or not operation succeeded (may want higher fidelity response in future)

      TODO:
        - Allow user to specify how long they would like rotation to occur for?
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    vel_message: str = f'some message here plus insert given vel {vel}'
    send_to_mcu(id, vel_message)

    # currently pretending read_from_mcu returns strings
    response: str = read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response == 'some message'

  def rotate_at_current(self, id: int, cur: float) -> bool:
    """
      Rotates actuator given by id at current given by cur

      Args:
        id (int): Identifier for specific actuator to rotate
        cur (float): Current specified in amperes

      Returns:
        bool: whether or not operation succeeded (may want higher fidelity response in future)
    """
    # the below is pseudocode and should not be expected to run

    # currently pretending send_to_mcu accepts strings
    cur_message: str = f'some message here plus insert given cur {cur}'
    send_to_mcu(id, cur_message)

    # currently pretending read_from_mcu returns strings
    response: str = read_from_mcu()
    # in reality unlikely there will only be two possible messages we care about
    return response == 'some message'

  def send_to_mcu(self, id: int, message: any):
    """
      Currently unimplemented, purpose is to serialize and send a message to MCU

      Args:
        id (int): Placeholder argument for actuator id
        message (any): Placeholder argument/type for user message

      Returns:
        Placeholder for now
    """
    pass

  def read_from_mcu(self):
    """
      Currently unimplemented, purpose is to receive messages from MCU

      Args:
        message (any): Placeholder argument/type for now

      Returns:
        Placeholder for now
    """
    pass