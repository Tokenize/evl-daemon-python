import unittest

import evl.command as cmd
import evl.data as dt


class TestData(unittest.TestCase):
    def test_led_state_describe(self):
        state = "83"
        state_str = "Backlight, Armed, Ready"

        self.assertEqual(state_str, dt.describe_led_state(state))

    def test_zone_data_parse(self):
        command = cmd.Command("609")
        data = "001"
        parsed = dt.parse(command, data)

        self.assertEqual(parsed, {'zone': '001', 'data': ''})

    def test_zone_partition_data_parse(self):
        command = cmd.Command("601")
        data = "1001"
        parsed = dt.parse(command, data)

        self.assertEqual(parsed, {'partition': '1', 'zone': '001', 'data': ''})

    def test_data_parse(self):
        command = cmd.Command("510")
        data = "83"
        parsed = dt.parse(command, data)

        self.assertEqual(parsed, {'data': data})