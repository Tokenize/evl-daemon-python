import unittest

from evl import tpi


class TestTpi(unittest.TestCase):
    def test_checksum_is_correct(self):
        checksum = tpi.calculate_checksum("6543")
        self.assertEqual(checksum, "D2")

    def test_checksum_truncates(self):
        checksum = tpi.calculate_checksum("005123456")
        self.assertEqual(checksum, "CA")

    def test_checksum_adds_leading_zero(self):
        checksum = tpi.calculate_checksum("5108A")
        self.assertEqual(checksum, "0F")

    def test_get_checksum(self):
        checksum = tpi.parse_checksum("005user54")
        self.assertEqual(checksum, "54")

    def test_get_command(self):
        command = tpi.parse_command("005user54")
        self.assertEqual(command, "005")

    def test_get_data(self):
        data = tpi.parse_data("005user54")
        self.assertEqual(data, "user")

    def test_get_data_with_no_data(self):
        data = tpi.parse_data("501" + tpi.calculate_checksum("501"))
        self.assertEqual(data, "")

    def test_validate_checksum_valid(self):
        valid = tpi.validate_checksum("005user54")
        self.assertTrue(valid)

    def test_validate_checksum_invalid(self):
        valid = tpi.validate_checksum("005userAB")
        self.assertFalse(valid)
