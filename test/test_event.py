import unittest

import evl.command as cmd
import evl.event as ev
import evl.util as util


class TestEventManager(unittest.TestCase):

    def test_led_state_describe(self):
        state = "83"
        state_str = "Backlight, Armed, Ready"
        mgr = ev.EventManager(None)

        self.assertEqual(state_str, mgr._describe_led_state(state))

    def test_event_priority_override(self):
        cmd_priorities = {cmd.CommandType.LOGIN: cmd.Priority.CRITICAL}
        cmd.PRIORITIES = util.merge_dicts(cmd.PRIORITIES, cmd_priorities)
        command = cmd.Command(cmd.CommandType.LOGIN.value)
        event = ev.Event(command, {})

        self.assertEqual(cmd.Priority.CRITICAL, event.priority)
