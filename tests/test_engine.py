import unittest
from game.core.engine.engine import GameEngine
from game.core.engine.tile import Tile


class TestEngine(unittest.TestCase):

    def test_initial_state(self):
        engine = GameEngine(2, 3, 10) #Different values for row/col to make sure it's consistent.
        self.assertEqual(engine.gold, 10)
        self.assertEqual(len(engine.grid), 2)

        # Checks for each col too, not just the rows.
        for row in engine.grid:
            self.assertEqual(len(row), 3)

    def test_tick_increases(self):
        engine = GameEngine(2, 2, 10)
        # Checks ticks work correctly over multiple iterations
        self.assertEqual(engine.total_ticks, 0)
        engine.advance_time()
        engine.advance_time()
        engine.advance_time()
        self.assertEqual(engine.total_ticks, 3)

    def test_break_input_does_not_crash(self):
        engine = GameEngine(2, 2, 10)

        # malformed request (should not crash engine)
        try:
            engine.handle_engine_requests({"actions": None})
        except Exception as e:
            self.fail(f"Engine crashed on bad input: {e}")

    def test_successful_plantation(self):
        engine = GameEngine(5, 5, starting_gold=100)
        # Simulate a plant action request via coordinates [3, 4]

        product = {
            "product_name": "Cherry Tree",
            "price": 40,
            "product_reward": 38,
            "product_growth_time": 600,
            "product_remaining_harvests": 10
            }

        tile = engine.get_tile(3, 4)
        result = engine.handle_plantation_attempt(product, "tree", tile)
        self.assertTrue(result["planting_success"])
        self.assertTrue(engine.get_tile(3, 4).is_occupied())


    def test_engine_reset_and_fetch_product(self):
        """Tests the resetting mechanism and product catalog fetching."""
        engine = GameEngine()
        engine.reset_game()
        self.assertEqual(engine.total_ticks, 0)

        # Test fetch_product directly to clear its 0% status
        product = engine.fetch_product("plant", "1")
        self.assertIsNotNone(product)

    def test_handle_engine_requests_integration(self):
        """Feeds exact dictionary structures to execute handle_engine_requests paths."""
        engine = GameEngine(starting_gold=100)

        # Inject a mock catalog directly to guarantee a match and prevent disk issues
        engine.product_catalog = {
            "plant": {
                "id1": {
                    "price": 10,
                    "product_name": "Wheat",
                    "product_reward": 15,
                    "product_growth_time": 10,
                    "product_remaining_harvests": 2
                }
            }
        }

        mock_requests = {
            "actions": {
                "restart_game": False,
                "harvest_tile_contents": [[-1, 0]], # out of bounds attempt
                "delete_tile_contents": [],
                "plant_tile_contents": [
                    {"tile_location": [0, 0], "type": "plant", "id": 1}
                ]
            }
        }

        engine.handle_engine_requests(mock_requests)
        self.assertTrue(engine.get_tile(0, 0).is_occupied())

    def test_engine_reset_and_fetch_product(self):
        """
        Clears out reset and fetch product logic.
        """
        engine = GameEngine()
        engine.advance_time()
        engine.reset_game()
        self.assertEqual(engine.total_ticks, 0)

        product = engine.fetch_product("plant", 1)
        self.assertIsNotNone(product)


if __name__ == "__main__":
    unittest.main()