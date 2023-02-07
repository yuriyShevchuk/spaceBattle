import math
from abc import ABC, abstractmethod


class Action(ABC):
    @abstractmethod
    def execute(self):
        pass


class Movable(ABC):
    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def set_position(self, position):
        pass

    @abstractmethod
    def get_velocity(self):
        pass


class MoveAdapter(Movable):

    def __init__(self, subject):
        self.subject = subject

    def get_position(self):
        return self.subject.get_property('position')

    def set_position(self, position):
        self.subject.set_property('position', position)

    def get_velocity(self):
        angle = self.subject.get_property('direction') * math.pi*2 / self.subject.get_property('direction_number')
        dx, dy = self.subject.get_property('velocity')
        return [math.cos(angle) * dx, math.sin(angle) * dy]


class Move(Action):

    def __init__(self, movable: Movable):
        self.movable = movable

    def execute(self):
        new_position = [sum(coords) for coords in zip(self.movable.get_position(), self.movable.get_velocity())]
        self.movable.set_position(new_position)


class Rotatable(ABC):

    @abstractmethod
    def get_direction(self):
        pass

    @abstractmethod
    def get_angular_velocity(self):
        pass

    @abstractmethod
    def get_directions_number(self):
        pass

    @abstractmethod
    def set_direction(self, new_direction):
        pass


class RotatableAdapter(Rotatable):

    def __init__(self, subject):
        self.subject = subject

    def get_direction(self):
        return self.subject.get_property('direction')

    def get_angular_velocity(self):
        return self.subject.get_property('angular_velocity')

    def get_directions_number(self):
        return self.subject.get_property('directions_number')

    def set_direction(self, new_direction):
        self.subject.set_property('direction')


class Rotate(Action):

    def __init__(self, rotatable: Rotatable):
        self.rotatable = rotatable

    def execute(self):
        new_direction = self.rotatable.get_direction() + self.rotatable.get_angular_velocity()
        final_direction = new_direction % self.rotatable.get_directions_number()
        self.rotatable.set_direction(final_direction)
