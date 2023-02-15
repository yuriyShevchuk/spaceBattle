import math
from abc import ABC, abstractmethod


class Command(ABC):
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
        angle = (self.subject.get_property('velocity_direction') * math.pi * 2
                 / self.subject.get_property('direction_number'))
        dx, dy = self.subject.get_property('velocity')
        return [math.cos(angle) * dx, math.sin(angle) * dy]


class MoveCommand(Command):

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


class RotateCommand(Command):

    def __init__(self, rotatable: Rotatable):
        self.rotatable = rotatable

    def execute(self):
        new_direction = self.rotatable.get_direction() + self.rotatable.get_angular_velocity()
        final_direction = new_direction % self.rotatable.get_directions_number()
        self.rotatable.set_direction(final_direction)


class VelocityDirectionChangable(ABC):

    @abstractmethod
    def is_movable(self):
        pass

    @abstractmethod
    def get_direction(self):
        pass

    @abstractmethod
    def set_velocity_direction(self, new_direction):
        pass


class ChangeVelocityDirection(Command):

    def __init__(self, velocity_direction_changeable):
        self.velocity_direction_changeable = velocity_direction_changeable

    def execute(self):
        if not self.velocity_direction_changeable.is_movable():
            raise CommandException('Trying to rotate velocity of not movable object')

        self.velocity_direction_changeable.set_velocity_direction(self.velocity_direction_changeable.get_direction())


class CommandException(BaseException):
    pass


class NotEnoughFuelForMove(CommandException):
    pass


class FuelCheckable(ABC):

    @abstractmethod
    def get_velocity_module(self):
        pass

    @abstractmethod
    def get_fuel_consumption(self):
        pass

    @abstractmethod
    def get_fuel_in_tank(self):
        pass

    @abstractmethod
    def set_fuel_for_next_move(self, fuel):
        pass


class CheckFuelCommand(Command):

    def __init__(self, fuel_checker: FuelCheckable):
        self.fuel_checker = fuel_checker

    def execute(self):
        fuel_needed_for_move = self.fuel_checker.get_velocity_module() / self.fuel_checker.get_fuel_consumption()
        if self.fuel_checker.get_fuel_in_tank() - fuel_needed_for_move < 0:
            raise NotEnoughFuelForMove

        self.fuel_checker.set_fuel_for_next_move(fuel_needed_for_move)


class FuelBurnable(ABC):

    @abstractmethod
    def get_fuel_in_tank(self):
        pass

    @abstractmethod
    def get_fuel_for_next_move(self):
        pass

    @abstractmethod
    def set_fuel_in_tank(self, fuel):
        pass


class BurnFuelCommand(Command):

    def __init__(self, consumer: FuelBurnable):
        self.consumer = consumer

    def execute(self):
        fuel_remains = self.consumer.get_fuel_in_tank() - self.consumer.get_fuel_for_next_move()
        self.consumer.set_fuel_in_tank(fuel_remains)


class SimpleMacroCommand(Command):

    def __init__(self, *args: Command):
        self.commands = args

    def execute(self):
        try:
            for command in self.commands:
                command.execute()
        except Exception:
            raise CommandException


class MoveWithFuel(SimpleMacroCommand):

    def __init__(self, move: MoveCommand, check_fuel: CheckFuelCommand, burn_fuel: BurnFuelCommand):
        commands_sequence = [check_fuel, move, burn_fuel]
        super().__init__(*commands_sequence)


class RotateWithVelocityDirection(SimpleMacroCommand):

    def __init__(self, rotate: RotateCommand, rotate_velocity: ChangeVelocityDirection):
        commands_sequence = [rotate, rotate_velocity]
        super().__init__(*commands_sequence)


