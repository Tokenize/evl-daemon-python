import unittest

from evl import command as cmd
from evl import event


class TestEventManager(unittest.TestCase):

    def test_command_describe_default(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        desc = event.COMMAND_NAMES[command.command_type]
        mgr = event.EventManager(None)

        self.assertEqual(desc, mgr._describe_command(command))

    def test_command_describe_override(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        cmd_names = {cmd.CommandType.LOGIN: "LOGIN!"}
        mgr = event.EventManager(None, command_names=cmd_names)

        self.assertEqual("LOGIN!", mgr._describe_command(command))
