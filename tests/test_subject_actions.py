from unittest import mock

import pytest

from subject_actions import Move, Rotate, MoveAdapter, RotatableAdapter


def test_move_from_point_to_point():
    movable = mock.Mock()
    movable.get_position.return_value = [12, 5]
    movable.get_velocity.return_value = [-7, 3]
    move_action = Move(movable)

    move_action.execute()

    movable.set_position.assert_called_once_with([5, 8])


def test_move_cannot_read_position():
    movable = mock.Mock()
    movable.get_position = mock.Mock(side_effect=KeyError)
    move_action = Move(movable)

    with pytest.raises(KeyError):
        move_action.execute()


def test_move_cannot_read_velocity():
    movable = mock.Mock()
    movable.get_velocity = mock.Mock(side_effect=KeyError)
    move_action = Move(movable)

    with pytest.raises(KeyError):
        move_action.execute()


def test_move_cannot_set_position():
    movable = mock.Mock()
    movable.get_position.return_value = [12, 5]
    movable.get_velocity.return_value = [-7, 3]
    movable.set_position = mock.Mock(side_effect=AttributeError)
    move_action = Move(movable)

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
    rotate_action = Rotate(rotatable)

    rotate_action.execute()

    rotatable.set_direction.assert_called_once_with(1)
