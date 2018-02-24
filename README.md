# Python Library for Avocado Actuator

This library provides abstractions for interacting with the avocado actuator. It supports rotation to a position, at a velocity and at a current.

## Current State

Communicator class provides ability to communicate with arbitrary number of actuators.

## Future Considerations

Potential improvements/modifications to consider in the future:

- [ ] Allow specifying devices by index in chain of actuators
- [ ] Allow users to respond reactively to MCU messages
- [ ] Relative methods (increase_velocity, rotate_x_units, etc.)
- [ ] Create Actuator class whose instances represent individual actuators