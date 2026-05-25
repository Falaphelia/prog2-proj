"""
Game engine module.

Handles the main simulation loop, grid updates, time progression,
and processing of player action requests.
"""

# Module being run as package, and pylint is complaining
# when running the file, so here's to make it shut up

import json
from pathlib import Path
from game.core.engine.tile import Tile
from game.core.engine.products import Plant, Tree, Animal
from game.utils.networking import get_soil_conditions

class GameEngine():
    """
    Core game engine responsible for running the simulation.

    Maintains the grid state, game time, player resources, and
    processes actions such as planting, harvesting, and resetting.
    """

    #I'm not altering instances vars for no reason.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, rows: int = 5, columns: int = 5, starting_gold: int = 5):
        """
        Initializes a game engine. Automatically creates a grid (self.grid) with empty Tiles
        instances, the size of the grid is dependant on the two integer args 'rows' and 'columns'.
        """

        self.catalog_path = Path(__file__).parent.parent / "data" / "product_catalog.json"

        self.grid: list[list[Tile]] = [] #object is a Tile instance

        self.weather_multiplier: int = 1
        self.total_ticks = 0
        self.product_catalog = {}
        self.starting_gold = starting_gold
        self.n_rows: int = rows
        self.n_cols: int = columns
        self.gold: int = self.starting_gold

        self.fetch_weather_data()
        self.fetch_product_catalog()
        self.create_grid(self.n_rows, self.n_cols)

    def reset_game(self):
        """
        Resets the game state to initial values, including grid,
        gold, tick counter, product catalog, and weather data.
        """
        self.fetch_weather_data()
        self.fetch_product_catalog()
        self.gold: int = self.starting_gold
        self.total_ticks = 0
        self.create_grid()

    def fetch_weather_data(self):
        """
        Retrieves and formats weather data for use in the game.

        This function calls the Open-Meteo API via a client wrapper,
        extracts the latest soil temperature and moisture values,
        and returns them in a simplified dictionary format for gameplay.

        Returns:
            dict: Dictionary containing:
                - "temp" (int): Soil temperature at 6 cm depth
                - "moisture" (int): Soil moisture (9–27 cm depth)
        """
        soil_temp, soil_moisture = get_soil_conditions()
        moisture_ok = 0.18 <= soil_moisture <= 0.32
        moisture_bad = 0.15 >= soil_moisture or soil_moisture >= 0.35
        temp_ok = 15 <= soil_temp <= 28
        temp_bad = 12 >= soil_temp or soil_temp >= 28

        if moisture_ok and temp_ok:
            self.weather_multiplier = 1.2
        elif moisture_ok or temp_ok:
            self.weather_multiplier = 1.1
        elif moisture_bad and temp_bad:
            self.weather_multiplier = 0.8
        elif moisture_bad or temp_bad:
            self.weather_multiplier = 0.9
        else:
            self.weather_multiplier = 1


    def fetch_product_catalog(self):
        """
        Loads the product catalog from disk into memory.
        """
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.product_catalog = json.load(f)


    def fetch_product(self, product_type, product_id):
        """
        Retrieves a product from the catalog.

        Args:
            product_type (str): Type/category of product, e.g., pla nt / tree / animal
            product_id (int): ID of the product.

        Returns:
            dict or None: Product data if found.
        """
        category_items = self.product_catalog.get(product_type)
        if category_items:
            product = category_items.get(f"id{product_id}")
            if product:
                return product
        return None

    def handle_engine_requests(self, requests: dict):
        """
        Processes incoming game engine requests such as:
        1. restarting the game
        2. harvesting tiles
        3. deleting tile contents
        4. planting new products
        """

        requests = requests.get("actions")
        if not requests:
            return

        if requests.get("restart_game"):
            self.reset_game()

        harvest_entries = requests.get("harvest_tile_contents")
        if harvest_entries:
            for tile_coordinates in harvest_entries:

                x, y = tile_coordinates

                if x < 0 or x >= self.n_cols:
                    continue

                if y < 0 or y >= self.n_rows:
                    continue

                tile = self.get_tile(tile_coordinates[0], tile_coordinates[1])
                report = tile.harvest()
                harvest_reward = report.get("product_harvest_reward")
                if harvest_reward:
                    self.gold += round(harvest_reward * self.weather_multiplier)

        deletion_entries = requests.get("delete_tile_contents")
        if deletion_entries:
            for tile_coordinates in deletion_entries:
                tile = self.get_tile(tile_coordinates[0], tile_coordinates[1])
                if not tile:
                    continue
                tile.clear()


        plantation_entries = requests.get("plant_tile_contents")
        if plantation_entries:
            for entry in plantation_entries:
                tile_coordinates = entry.get("tile_location")
                tile = self.get_tile(tile_coordinates[0], tile_coordinates[1])

                product_type = entry.get("type")
                product_id = entry.get("id")
                product = self.fetch_product(product_type, product_id)

                self.handle_plantation_attempt(product, product_type, tile)

    def handle_plantation_attempt(self, product: dict, product_type: str, tile: Tile):
        """
        Attempts to plant a product on a tile.

        Validates resources, creates product instances, and applies cost
        if planting succeeds.
        """
        product_price = product.get("price")
        product_name = product.get("product_name")
        product_reward = product.get("product_reward")
        product_growth_time = product.get("product_growth_time")
        product_remaining_harvests = product.get("product_remaining_harvests")

        all_variables_fetched_successfully = bool(
            product_price
            and product_name
            and product_reward
            and product_growth_time
            and product_remaining_harvests
        )

        #guard clauses
        if not all_variables_fetched_successfully:
            return {}

        if not self.gold >= product_price:
            return {}

        if product_type == "plant":
            #create product instance
            product_instance = Plant(
                product_name,
                product_reward,
                product_growth_time,
                product_remaining_harvests)
            #attempt plantation
            report = tile.plant(product_instance, product_price)

        elif product_type == "tree":
            product_instance = Tree(
                product_name,
                product_reward,
                product_growth_time,
                product_remaining_harvests)

            report = tile.plant(product_instance, product_price)

        elif product_type == "animal":
            product_instance = Animal(
                product_name,
                product_reward,
                product_growth_time,
                product_remaining_harvests)
            report = tile.plant(product_instance, product_price)
        else:
            return {}

        #deduct expenses if successful
        if report.get("planting_success") and report.get("cost"):
            self.gold -= report.get("cost")
            return report
        return {}

    def advance_time(self, action_requests: dict = None):
        """
        The main tick function of the game engine. Calling this advances the time by one tick.
        The game engine does not simulate ticks when this function isn't being called.

        Args:
            dict: action_requests is an optional argument that can contain instructions for
            the engine, attempting harvest a product, delete a product,
            plant a product or to reset the game.

        Returns:
            dict: a status report containing the full state of the game
            after the tick has been completed.
        """

        if isinstance(action_requests, dict):
            self.handle_engine_requests(action_requests)

        self.total_ticks += 1

        master_report = {
            "report_grid" : [],
            "gold" : self.gold,
            "total_ticks" : self.total_ticks,
            "weather_multiplier" : float(self.weather_multiplier)
        }
        for r_index, row in enumerate(self.grid):
            master_report["report_grid"].append([])
            for tile in row:
                tile_status_report = tile.advance_time()
                master_report["report_grid"][r_index].append(tile_status_report)

        return master_report

    def create_grid(self, n_rows: int = 0, n_columns: int = 0):
        """
        Creates the main grid of the GameEngine instance (self.grid).

        Args:
            n_rows: the number of rows the grid should have; minimum: 1 (positive int)
            n_columns: the number of columns the grid should have; minimum: 1 (positive int)
        """
        self.grid = []

        if not n_rows:
            n_rows = self.n_rows
        if not n_columns:
            n_columns = self.n_cols

        for row in range(n_rows):
            self.grid.append([])
            for col in range(n_columns):
                self.grid[row].append(Tile(row, col))

    def get_tile(self, x: int, y: int):
        """
        Helper function for returning the Tile instance at a specific [x, y]
        coordinate on the Game Engine's grid.

        If the coordinates are out of bounds, returns None.

        Returns:
            Tile: an instance of Tile from the specified grid coordinates.
        """

        if x < 0 or x >= self.n_cols:
            return None

        if y < 0 or y >= self.n_rows:
            return None

        return self.grid[y][x]
