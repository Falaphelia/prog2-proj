import unittest
from game.utils.networking import get_soil_conditions


class TestNetworking(unittest.TestCase):

    def test_get_soil_conditions_returns_floats(self):
        soil_temp, soil_moisture = get_soil_conditions()

        self.assertIsInstance(soil_temp, float)
        self.assertIsInstance(soil_moisture, float)

        self.assertNotEqual(soil_temp, 0)
        self.assertNotEqual(soil_moisture, 0)


if __name__ == "__main__":
    unittest.main()