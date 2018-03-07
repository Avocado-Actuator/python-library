from math import radians
from enum import Enum
from typing import Any
import serial
import time

class PosUnit(Enum):
	RADIANS = 1 # prefer radians based on project specifications
	DEGREES = 2

class VelUnit(Enum):
	RPS = 1 # radians per second - prefer radians based on project specifications
	RPM = 2 # rotations per minute

class Communicator:
	"""
		Provides abstractions for communication with an arbitrary number of actuators

		Attributes:
			port_num (int): Specifies serial port used for communication. On *NIX this
				looks like '/dev/ttyACM0', on windows like 'COM3'
			pos_unit (PosUnit): Unit for position
			vel_unit (VelUnit): Unit for velocity
			ser (Serial): The Serial object for serial communication (timeout
				arbitrarily set to 0.01s)

		TODO:
			- Specify types of message (probably just strings but maybe worth discussing)
	"""
	def __init__(self, port_num: str, pos_unit: PosUnit = PosUnit.RADIANS, vel_unit: VelUnit = VelUnit.RPS) -> None:
		"""
			Constructor simply setting attributes
		"""
		self.port_num = port_num
		self.pos_unit = pos_unit
		self.vel_unit = vel_unit
		self.ser = serial.Serial(port_num, 9600, timeout=0.05)

	def __del__(self) -> None:
		self.ser.close()

	def _convert_pos_to_radians(self, pos: float) -> float:
		"""
			Allow users to specify multiple units but simplify MCU communications by
			supporting a single unit on the MCU and converting user provided units to
			that unit. Choosing radians based on user specifications.

			Args:
				pos (float): Position specified in self.pos_unit units

			Returns:
				float
		"""
		return pos if self.pos_unit == PosUnit.RADIANS else radians(pos)

	def rotate_to_position(self, addr: int, pos: float) -> str:
		"""
			Rotates actuator given by addr to postion given by pos

			Args:
				addr (int): Identifier for specific actuator to rotate
				pos (float): Position specified in self.pos_unit units

			Returns:
				str: whether or not operation succeeded (may want higher fidelity
					response in future)

			TODO:
				- Allow user to specify timing/speed on rotation?
		"""
		# the below is pseudocode and should not be expected to run

		# currently pretending send_to_mcu accepts strings
		pos_message: str = f'setpos {pos}'
		self._send_to_mcu(addr, pos_message)
		time.sleep(0.5)
		# currently pretending read_from_mcu returns strings
		response: str = self._read_from_mcu()
		# in reality unlikely there will only be two possible messages we care about
		return response

	def rotate_at_velocity(self, addr: int, vel: float) -> str:
		"""
			Rotates actuator given by addr at velocity given by vel

			Args:
				addr (int): Identifier for specific actuator to rotate
				vel (float): Velocity specified in self.vel_unit units

			Returns:
				str: whether or not operation succeeded (may want higher fidelity
					response in future)

			TODO:
				- Allow user to specify how long they would like rotation to occur for?
		"""
		# the below is pseudocode and should not be expected to run

		# currently pretending send_to_mcu accepts strings
		# vel_message: str = f'some message here plus insert given vel {vel}'
		vel_message: str = f'setvel {vel}'
		self._send_to_mcu(addr, vel_message)
		time.sleep(0.5)
		# currently pretending read_from_mcu returns strings
		response: str = self._read_from_mcu()
		# in reality unlikely there will only be two possible messages we care about
		return response

	def rotate_at_current(self, addr: int, cur: float) -> str:
		"""
			Rotates actuator given by addr at current given by cur

			Args:
				addr (int): Identifier for specific actuator to rotate
				cur (float): Current specified in amperes

			Returns:
				str: whether or not operation succeeded (may want higher fidelity
					response in future)
		"""
		# the below is pseudocode and should not be expected to run

		# currently pretending send_to_mcu accepts strings
		cur_message: str = 'setcur {cur}'
		self._send_to_mcu(addr, cur_message)
		time.sleep(0.5)
		# currently pretending read_from_mcu returns strings
		response: str = self._read_from_mcu()
		# in reality unlikely there will only be two possible messages we care about
		return response

	def get_position(self, addr: int) -> str:
		"""
			Returns the current position the actuator is at

			Args:
				addr (int): Identifier for specific actuator

			Returns:
				str: the response of the mcu
		"""
		self._send_to_mcu(addr, 'getpos')
		time.sleep(0.5)
		response: str = self._read_from_mcu()
		return response

	def get_velocity(self, addr: int) -> str:
		"""
			Returns the current velocity the actuator is rotating at

			Args:
				addr (int): Identifier for specific actuator

			Returns:
				str: the response of the mcu
		"""
		self._send_to_mcu(addr, 'getvel')
		time.sleep(0.5)
		response: str = self._read_from_mcu()
		return response

	def get_current(self, addr: int) -> str:
		"""
			Returns the current the actuator is operating at

			Args:
				addr (int): Identifier for specific actuator

			Returns:
				str: the response of the mcu
		"""
		self._send_to_mcu(addr, 'getcur')
		time.sleep(0.5)
		response: str = self._read_from_mcu()
		return response

	def _send_to_mcu(self, addr: int, message: str) -> bool:
		"""
			Serialize and send a message to MCU

			Args:
				addr (int): Placeholder argument for actuator id
				message (str): Placeholder argument/type for user message

			Returns:
				true for success (placeholder)
		"""
		cmd: str = f'{addr} {message}'
		self.ser.write(cmd.encode('utf-8'))
		return True

	def _read_from_mcu(self) -> str:
		"""
			Purpose is to receive messages from MCU

			Returns:
				str: the contents of the receive buffer
		"""
		return self.ser.readlines()

def main():
	print("\n*** Running main function ***\n")
  comm = Communicator('COM7') # replace with the port the MCU is connected to!
	print(comm.rotate_at_velocity(1337, 50.0))
	time.sleep(0.5)
	print(comm.rotate_at_current(1337, 50.0))
	time.sleep(0.5)
	print(comm.rotate_to_position(1337, 50.0))
	time.sleep(0.5)
	print(comm.get_velocity(1337))
	time.sleep(0.5)
	print(comm.get_position(1337))
	time.sleep(0.5)
	print(comm.get_current(1337))
	time.sleep(0.5)
	# comm._send_to_mcu(0, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	# comm._send_to_mcu(1, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	# comm._send_to_mcu(2, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	# comm._send_to_mcu(3, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	# comm._send_to_mcu(4, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	# comm._send_to_mcu(5, '')
	# time.sleep(0.5)
	# print(comm._read_from_mcu())
	del comm

if __name__ == "__main__":
	main()
