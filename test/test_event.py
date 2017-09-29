import unittest

from evl import command as cmd
from evl import event
from evl.util import merge_dicts


class TestEventManager(unittest.TestCase):

    def test_command_describe_default(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        desc = event.COMMAND_NAMES[command.command_type]
        mgr = event.EventManager(None)

        self.assertEqual(desc, mgr._describe_command(command))

    def test_command_describe_override(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        cmd_names = {cmd.CommandType.LOGIN: "LOGIN!"}
        mgr = event.EventManager(None)
        event.EventManager.command_names = merge_dicts(event.COMMAND_NAMES, cmd_names)

        self.assertEqual("LOGIN!", mgr._describe_command(command))

    def test_led_state_describe(self):
        state = "83"
        state_str = "Backlight, Armed, Ready"
        mgr = event.EventManager(None)

        self.assertEqual(state_str, mgr._describe_led_state(state))
