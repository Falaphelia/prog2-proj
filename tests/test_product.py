import unittest
from unittest.mock import patch

from game.core.engine.tile import Tile
from game.core.engine.products import Product, Plant, Tree, Animal


class TestProduct(unittest.TestCase):

    def test_growth_increases(self):
        product = Product("Potato", growth_time=5)

        self.assertEqual(product.current_growth, 0)

        product.advance_time()

        self.assertEqual(product.current_growth, 1)

    def test_harvest_ready_product(self):
        product = Product("Potato", reward=15, growth_time=1)

        product.current_growth = 1

        result = product.harvest()

        self.assertTrue(result["product_harvest_is_success"])
        self.assertEqual(result["product_harvest_reward"], 15)

    def test_harvest_not_ready_product(self):
        product = Product("Potato", growth_time=10)

        result = product.harvest()

        self.assertFalse(result["product_harvest_is_success"])

    def test_is_ready(self):
        product = Product("Potato", growth_time=2)

        self.assertFalse(product.is_ready())

        product.current_growth = 2

        self.assertTrue(product.is_ready())


    #PLANT type

    def test_tile_contents_status_and_time(self):
        """Clears out remaining logic paths in Tile status tracking and time advancement."""
        product = Product("Wheat", growth_time=10)
        tile = Tile(0, 0, product)

        status = tile.get_contents_status()
        self.assertEqual(status["name"], "Wheat")

        report = tile.advance_time()
        self.assertIn("tile_origin", report)

    def test_plant_has_disease_resistance(self):
        plant = Plant()

        self.assertIsInstance(plant.disease_resistance, float)

    def test_plant_disease_resistance_bounds(self):

        # 100 000 times *should* be enough times to guarantee the randomness
        # never exceeds bounds and stays within expectations
        for _ in range(100000):
            plant = Plant()

            #Makes sure the resistance never causes a plant to be immune or to vulnerable
            self.assertGreaterEqual(plant.disease_resistance, 0.2)
            self.assertLessEqual(plant.disease_resistance, 0.8)

    def test_plant_event_and_infect(self):

        for _ in range(1000):
            plant = Plant()
            tile = Tile(1, 1, plant)
            for tick in range(100000):
                tile.advance_time()
                if not tile.is_occupied():
                    break
            self.assertEqual(False, tile.is_occupied())

    #TREE type

    def test_tree_perch_anti_abuse(self):
        """
        Ensures trees cannot gain extra harvests if they are already fully grown.
        """
        tree = Tree(growth_time=100, remaining_harvests=5)
        tree.current_growth = 100  # Fully grown

        # Even with a guaranteed 100% chance, it should exit early
        with patch("random.random", return_value=0.0):
            tree.perch()
            self.assertEqual(tree.remaining_harvests, 5)

    def test_simulated_tree_looped_event(self):
        tree = Tree(growth_time=100, remaining_harvests=10)
        tree.n_ticks_full_lifetime = 1 #makes the chance of harvest stupidly high
        tile = Tile(1, 1, tree)
        n_original_remaining_harvests = tree.remaining_harvests
        n_harvests = 0
        while True:
            tile.advance_time()
            if not tile.is_occupied():
                break

            # makes it so it cant loop too many times
            if n_harvests > (n_original_remaining_harvests + 10):
                break

            if tree.growth_time <= tree.current_growth:
                report: dict = tile.harvest()
                if report.get("product_harvest_is_success"):
                    n_harvests += 1

        self.assertGreater(n_harvests, n_original_remaining_harvests)





    def test_tree_harvest_mechanics(self):
        """
        Checks that harvesting a tree scales reward and updates growth time dynamically.
        """
        # 100 000 times *should* be enough times to guarantee the randomness
        # never exceeds bounds and stays within expectations
        for tree in range(1000000):
            tree = Tree(reward=100, growth_time=100, remaining_harvests=2)
            tree.current_growth = 100  # harvestable now

            result = tree.harvest()

            self.assertTrue(result["product_harvest_is_success"])
            # Reward should be 0.5 to 1.5 because of random,uniform
            self.assertTrue(50 <= result["product_harvest_reward"] <= 150)
            # Next growth_time should change within 80 to 130
            self.assertTrue(80 <= tree.growth_time <= 130)
            self.assertEqual(tree.remaining_harvests, 1)


    #ANIMAL type

    def test_animal_reproduction_success(self):
        """
        Forces the random event to succeed to verify the reward increases.
        """
        animal = Animal(reward=100, growth_time=50, remaining_harvests=2)
        animal.current_growth = 10  # Not fully grown, allowed to reproduce

        # Mock random to force the probability check to pass
        with patch("random.random", return_value=0.0):
            animal.reproduce()
            self.assertEqual(animal.reward, 150)  # Base 100 + 50 bonus

if __name__ == "__main__":
    unittest.main()