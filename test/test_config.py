import unittest

from evl.config import ConfigSchema


class ConfigTest(unittest.TestCase):
    def make_config(self, ip="127.0.0.1", partitions={}, zones={}):
        return {"ip": ip, "partitions": partitions, "zones": zones}

    def test_valid_config_validates(self):
        errors = ConfigSchema().validate(self.make_config())
        self.assertDictEqual(errors, {})

    def test_ip_is_present(self):
        errors = ConfigSchema().validate(self.make_config(ip=None))
        self.assertIn("ip", errors)

    def test_ip_is_valid_address(self):
        errors = ConfigSchema().validate(self.make_config(ip="123"))
        self.assertIn("ip", errors)

    def test_partitions_are_present(self):
        errors = ConfigSchema().validate(self.make_config(partitions=None))
        self.assertIn("partitions", errors)

    def test_partition_definitions_are_valid(self):
        partitions = {"001", "002"}
        errors = ConfigSchema().validate(self.make_config(partitions=partitions))
        self.assertIn("partitions", errors)

    def test_zones_are_present(self):
        errors = ConfigSchema().validate(self.make_config(zones=None))
        self.assertIn("zones", errors)

    def test_zone_definitions_are_valid(self):
        zones = {"1", "2"}
        errors = ConfigSchema().validate(self.make_config(zones=zones))
        self.assertIn("zones", errors)
