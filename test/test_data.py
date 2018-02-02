import unittest

import evl.data as dt


class TestData(unittest.TestCase):
    def test_led_state_describe(self):
        state = "83"
        state_str = "Backlight, Armed, Ready"

        self.assertEqual(state_str, dt.describe_led_state(state))
