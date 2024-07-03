import unittest

import evl.command as cmd
import evl.util as util


class CommandTest(unittest.TestCase):
    def test_command_describe_default(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        desc = cmd.NAMES[command.command_type]

        self.assertEqual(desc, command.describe())

    def test_command_describe_override(self):
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        cmd_names = {cmd.CommandType.LOGIN: "LOGIN!"}
        cmd.NAMES = util.merge_dicts(cmd.NAMES, cmd_names)

        self.assertEqual("LOGIN!", command.describe())

    def test_command_with_unknown_number_should_be_unknown_type(self):
        command = cmd.Command("ABC")
        command_name = cmd.NAMES.get(cmd.CommandType.UNKNOWN)

        self.assertEqual(cmd.CommandType.UNKNOWN, command.command_type)
        self.assertEqual(command_name, command.describe())
