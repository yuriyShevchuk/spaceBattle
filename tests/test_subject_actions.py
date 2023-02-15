from unittest import mock

import pytest

from subject_actions import (MoveCommand, RotateCommand, MoveAdapter, CheckFuelCommand, BurnFuelCommand,
                             CommandException, NotEnoughFuelForMove, SimpleMacroCommand, MoveWithFuel,
                             ChangeVelocityDirection)


def test_move_from_point_to_point():
    movable = mock.Mock()
    movable.get_position.return_value = [12, 5]
    movable.get_velocity.return_value = [-7, 3]
    move_action = MoveCommand(movable)

    move_action.execute()

    movable.set_position.assert_called_once_with([5, 8])


def test_move_cannot_read_position():
    movable = mock.Mock()
    movable.get_position = mock.Mock(side_effect=KeyError)
    move_action = MoveCommand(movable)

    with pytest.raises(KeyError):
        move_action.execute()


def test_move_cannot_read_velocity():
    movable = mock.Mock()
    movable.get_velocity = mock.Mock(side_effect=KeyError)
    move_action = MoveCommand(movable)

    with pytest.raises(KeyError):
        move_action.execute()


def test_move_cannot_set_position():
    movable = mock.Mock()
    movable.get_position.return_value = [12, 5]
    movable.get_velocity.return_value = [-7, 3]
    movable.set_position = mock.Mock(side_effect=AttributeError)
    move_action = MoveCommand(movable)

    with pytest.raises(AttributeError):
        move_action.execute()


def test_move_adapter_cannot_read_position():
    def cant_get_position(key):
        if key == 'position':
            raise KeyError("Can't get position")

    subject = mock.Mock()
    subject.get_property = cant_get_position
    movable = MoveAdapter(subject)

    with pytest.raises(KeyError) as exception_info:
        movable.get_position()
    assert "Can't get position" in str(exception_info.value)


def test_rotate_more_than_directions_number():
    rotatable = mock.Mock()
    rotatable.get_directions_number.return_value = 8
    rotatable.get_direction.return_value = 7
    rotatable.get_angular_velocity.return_value = 2
    rotate_action = RotateCommand(rotatable)

    rotate_action.execute()

    rotatable.set_direction.assert_called_once_with(1)


def test_rotate_velocity_direction():
    current_direction = 1
    velocity_rotatable = mock.Mock()
    velocity_rotatable.is_movable.return_value = True
    velocity_rotatable.get_direction.return_value = current_direction
    change_velocity_direction = ChangeVelocityDirection(velocity_rotatable)

    change_velocity_direction.execute()

    velocity_rotatable.set_velocity_direction.assert_called_once_with(current_direction)


def test_rotate_velocity_direction_on_not_movable():
    velocity_rotatable = mock.Mock()
    velocity_rotatable.is_movable.return_value = False
    change_velocity_direction = ChangeVelocityDirection(velocity_rotatable)

    with pytest.raises(CommandException):
        change_velocity_direction.execute()


def test_check_fuel_command_raises_not_enough_fuel():
    fuel_checker = mock.Mock()
    fuel_checker.get_velocity_module.return_value = 15
    fuel_checker.get_fuel_consumption.return_value = 1
    fuel_checker.get_fuel_in_tank.return_value = 14
    check_fuel_command = CheckFuelCommand(fuel_checker)

    with pytest.raises(CommandException) as exc:
        check_fuel_command.execute()
    assert exc.type == NotEnoughFuelForMove


def test_check_fuel_command_set_fuel_for_next_move():
    fuel_checker = mock.Mock()
    fuel_checker.get_velocity_module.return_value = 5
    fuel_checker.get_fuel_consumption.return_value = 1
    fuel_checker.get_fuel_in_tank.return_value = 15
    check_fuel_command = CheckFuelCommand(fuel_checker)

    check_fuel_command.execute()

    fuel_checker.set_fuel_for_next_move.assert_called_once_with(5)


def test_burn_fuel_command():
    fuel_consumer = mock.Mock()
    fuel_consumer.get_fuel_in_tank.return_value = 15
    fuel_consumer.get_fuel_for_next_move.return_value = 5
    burn_fuel_command = BurnFuelCommand(fuel_consumer)

    burn_fuel_command.execute()

    fuel_consumer.set_fuel_in_tank.assert_called_once_with(10)


def test_simple_macro_command():
    command_one = mock.Mock()
    command_two = mock.Mock()
    macro_command = SimpleMacroCommand(command_one, command_two)

    macro_command.execute()

    command_one.execute.assert_called_once()
    command_two.execute.assert_called_once()


def test_move_with_fuel():
    fuel_checker = mock.Mock()
    move_command = mock.Mock()
    fuel_burner = mock.Mock()
    macro_command = MoveWithFuel(move=move_command, check_fuel=fuel_checker, burn_fuel=fuel_burner)

    macro_command.execute()

    fuel_checker.execute.assert_called_once()
    move_command.execute.assert_called_once()
    fuel_burner.execute.assert_called_once()


if __name__ == '__main__':
    pass
