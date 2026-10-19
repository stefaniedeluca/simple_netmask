import unittest

from simple_netmask import NetworkError, find_host_bits, validate_network


class TestValidateNetwork(unittest.TestCase):
    def test_legal_network_24(self):
        self.assertTrue(validate_network("10.0.0.0", 24))

    def test_legal_network_32(self):
        self.assertTrue(validate_network("192.168.1.5", 32))

    def test_legal_network_0(self):
        self.assertTrue(validate_network("0.0.0.0", 0))

    def test_host_bits_set_24(self):
        self.assertFalse(validate_network("10.0.0.5", 24))

    def test_host_bits_set_16(self):
        self.assertFalse(validate_network("172.16.1.0", 16))

    def test_prefix_out_of_range_high(self):
        with self.assertRaises(NetworkError):
            validate_network("10.0.0.0", 33)

    def test_prefix_out_of_range_negative(self):
        with self.assertRaises(NetworkError):
            validate_network("10.0.0.0", -1)

    def test_prefix_bool_rejected(self):
        with self.assertRaises(NetworkError):
            validate_network("10.0.0.0", True)

    def test_malformed_address_too_few_octets(self):
        with self.assertRaises(NetworkError):
            validate_network("10.0.0", 24)

    def test_malformed_address_leading_zero(self):
        with self.assertRaises(NetworkError):
            validate_network("010.0.0.0", 24)

    def test_malformed_address_octet_out_of_range(self):
        with self.assertRaises(NetworkError):
            validate_network("10.0.0.256", 24)


class TestFindHostBits(unittest.TestCase):
    def test_host_bits_24(self):
        self.assertEqual(find_host_bits("10.0.0.5", 24), "0.0.0.5")

    def test_no_host_bits(self):
        self.assertEqual(find_host_bits("10.0.0.0", 24), "0.0.0.0")

    def test_host_bits_16(self):
        self.assertEqual(find_host_bits("172.16.1.5", 16), "0.0.1.5")

    def test_host_bits_0(self):
        self.assertEqual(find_host_bits("192.168.1.1", 0), "192.168.1.1")

    def test_host_bits_32(self):
        self.assertEqual(find_host_bits("192.168.1.1", 32), "0.0.0.0")

    def test_host_bits_bad_prefix(self):
        with self.assertRaises(NetworkError):
            find_host_bits("10.0.0.0", 50)


if __name__ == "__main__":
    unittest.main()
