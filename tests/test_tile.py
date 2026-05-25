import unittest

from game.core.engine.tile import Tile
from game.core.engine.products import Product


class TestTile(unittest.TestCase):

    def test_plant_product(self):
        tile = Tile(0, 0)
        product = Product("Potato")

        result = tile.plant(product, 5)

        self.assertTrue(result["planting_success"])
        self.assertTrue(tile.is_occupied())

    def test_harvest_ready_product(self):
        tile = Tile(0, 0)

        product = Product("Potato", reward=10, growth_time=1)
        product.current_growth = 1

        tile.plant(product, 5)

        result = tile.harvest()

        self.assertTrue(result["product_harvest_is_success"])
        self.assertEqual(result["product_harvest_reward"], 10)

    def test_harvest_empty_tile_does_not_crash(self):
        tile = Tile(0, 0)
        result = tile.harvest()

        #Since no product has been planted, look for false.
        self.assertFalse(result.get("product_harvest_is_success"))

    def test_tile_template_report(self):
        tile = Tile(3, 4)

        report = tile._get_templated_report()

        self.assertEqual(report["tile_origin"], [4, 3])
        self.assertFalse(report["tile_has_contents"])

    def test_get_content_stat_empty_tile(self):
        tile = Tile(0, 0)
    
        result = tile.get_content_specific_stat("name")
    
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()