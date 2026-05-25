"""
This module is responsible for building and managing the GUI

This module creates an instance of the game engine, and via dict requests
allows communications between the game engine and GUI.
"""

import tkinter as tk
import math
from game.core.engine.engine import GameEngine


class GameGUI:
    """
    Main GUI controller for the farming game.

    This class builds and manages the entire Tkinter interface, including:
    a) The farm grid (interactive tiles)
    b) The shop interface (buy/select items)
    c) The info display (gold, time, weather)
    d) The game loop integration with GameEngine

    It acts as the bridge between:
    a= User input (button clicks)
    b) Game state (States class)
    c) Game simulation (GameEngine)
    """
    def __init__(self, root):
        """
        Initializes the full game UI and binds it to a GameEngine instance.

        Responsibilities:
        1 Creates main layout (farm grid + shop panel)
        2 Initializes UI frames and widgets
        3 Builds farm tiles and shop buttons
        4 Starts the game loop via tick()

        Args:
            root (tk.Tk): Root Tkinter window.
        """

        self.root = root
        self.game_engine = GameEngine(starting_gold=10)


        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.game_frame = tk.Frame(root, bg="tomato4")
        self.shop_frame = tk.Frame(root, bg="tomato4")



        self.game_frame.grid(row=0, column=0, sticky="nsew")
        self.shop_frame.grid(row=0, column=1, sticky="nsew")

        self.info_frame = tk.Frame(self.shop_frame, bg="tomato4")
        self.buttons_frame = tk.Frame(self.shop_frame, bg="tomato4")

        self.info_frame.pack(fill="x")
        self.buttons_frame.pack(expand=True, fill="both")

        self.is_running = True



        for r in range(self.game_engine.n_rows):
            self.game_frame.rowconfigure(r, weight=1)

        for c in range(self.game_engine.n_cols):
            self.game_frame.columnconfigure(c, weight=1)

        self._build_layout()

        info_label_text = f"Gold: {States.gold}"
        info_label_text += f", Game Age: {math.ceil(States.total_ticks/10)}"

        weather_mult = States.weather_multiplier

        if weather_mult == 1.2:
            info_label_text += ", weather: Very Good"
        elif weather_mult == 1.1:
            info_label_text += ", weather: Good"
        elif weather_mult == 1:
            info_label_text += ", weather: Normal"
        elif weather_mult == 0.9:
            info_label_text += ", weather: Bad"
        elif weather_mult == 0.8:
            info_label_text += ", weather: Very Bad"


        self.info_label = tk.Label(
            self.info_frame,
            text=info_label_text,
            bg="maroon",
            width=50
        )


        self.info_label.pack(side="right")

        self.reset_button = tk.Button(
            self.info_frame,
            text="Click here to reset game!",
            bg="red",
            command=lambda: setattr(States, "request_game_reset", True)
        )

        self.reset_button.pack(side="right")

        self.tick()

    def _build_layout(self):
        """
        Constructs the farm grid and shop UI.

        This method:
        1 Creates FarmTileButton instances for each grid cell
        2 Creates ShopButton instances based on the product catalog
        3 Assigns catalog data to shop buttons
        4 Configures grid layout weights for resizing behavior
        """
        cols = self.game_engine.n_cols
        rows = self.game_engine.n_rows

        for col in range(cols):
            for row in range(rows):
                created_btn = FarmTileButton(
                    self.game_frame,
                    col,
                    row,
                )
                States.farm_buttons.append(created_btn)

        catalog = self.game_engine.product_catalog

        product_plants = catalog.get("plant")
        product_trees = catalog.get("tree")
        product_animals = catalog.get("animal")

        total_entries = (
            len(product_plants)
            + len(product_trees)
            + len(product_animals)
            +1 #for the delete option
            )

        for r in range(math.ceil(total_entries/5)):
            self.buttons_frame.rowconfigure(r, weight=1)

        for c in range(5):
            self.buttons_frame.columnconfigure(c, weight=1)

        total_buttons_created = 0
        for col in range(math.ceil(total_entries/5)):

            for row in range(5):

                if total_buttons_created >= total_entries:
                    continue

                created_btn = ShopButton(
                    self.buttons_frame,
                    col,
                    row,
                )
                States.shop_buttons.append(created_btn)
                created_btn.insert_catalog_item(catalog, total_buttons_created)
                total_buttons_created += 1





    def redraw(self):
        """
        Updates all visual elements based on the latest game state.

        This includes:
        1 Updating the info label (gold, age, weather)
        2 Updating all farm tile buttons
        3 Refreshing the Tkinter frame display
        """

        info_label_text = f"Gold: {States.gold}"
        info_label_text += f", Game Age: {math.ceil(States.total_ticks/10)}"

        weather_mult = States.report.get("weather_multiplier")
        if weather_mult == 1.2:
            info_label_text += ", weather: Very Good"
        elif weather_mult == 1.1:
            info_label_text += ", weather: Good"
        elif weather_mult == 1:
            info_label_text += ", weather: Normal"
        elif weather_mult == 0.9:
            info_label_text += ", weather: Bad"
        elif weather_mult == 0.8:
            info_label_text += ", weather: Very Bad"


        self.info_label.configure(text=info_label_text)


        for btn in States.farm_buttons:
            btn.update_self()
        self.game_frame.update_idletasks()

    def build_action_request(self):
        """
        Collects all pending player actions into a structured request dictionary.

        Actions include:
        1 Planting crops
        2 Harvesting crops
        3 Deleting crops
        4 Resetting the game

        Returns:
            dict: Structured action request sent to GameEngine.
        """

        delete_requests = States.instructions_delete
        harvest_requests = States.instructions_harvest
        plant_requests = States.instructions_plant
        request_reset = States.request_game_reset

        requests = {
            "actions" : {
                "restart_game" : request_reset,
                "harvest_tile_contents" : harvest_requests,
                "delete_tile_contents" : delete_requests,
                "plant_tile_contents" : plant_requests
            }
        }
        if request_reset:
            States.request_game_reset = False
        return requests

    def tick(self):
        """
        Main game loop tick function.

        Flow:
        1. Build player action requests
        2. Advance game engine simulation
        3. Clear processed input instructions
        4. Update shared state (States.report, etc.)
        5. Redraw UI
        6. Schedule next tick using Tkinter after()

        Runs continuously while `self.is_running` is True.
        """

        # Can be turned off for debug
        if self.is_running:

            requests = self.build_action_request()
            States.report = self.game_engine.advance_time(requests)
            States.clear_instructions()
            States.update_info()
            self.redraw()
            self.root.after(100, self.tick)

class GridButton(tk.Button):
    """
    Base class for all grid-based buttons in the game.

    Provides:
    1 Grid position tracking (row, column)
    2 Default sizing and padding
    3 Automatic placement in Tkinter grid system
    """
    def __init__(self, parent, col, row, **kwargs):
        """
        Initializes a button placed in a grid cell.

        Args:
            parent (tk.Widget): Parent container.
            col (int): Column position in grid.
            row (int): Row position in grid.
            **kwargs: Additional Tkinter Button arguments.
        """
        super().__init__(
            parent,
            width=15,
            height=5,
            padx=30,
            pady=30,
            **kwargs
        )

        self.row = row
        self.col = col
        self.grid(row=row, column=col)

class FarmTileButton(GridButton):
    """
    Represents a single farm tile in the grid.

    Handles:
    1 Visual tile state (empty, growing, harvestable)
    2 Interaction logic (planting, harvesting, deleting)
    3 Syncing UI state with GameEngine report data
    """

    def __init__(self, parent, col, row, **kwargs):
        super().__init__(
            parent,
            row,
            col,
            command = lambda: self.farm_tile_on_click(),
            **kwargs
        )


        self.state = "empty" #Options: "empty", "growing", "harvestable"

        #Variables for showing information - are not to be used for decisions
        self.show_product_name = ""

    def _find_tile_report(self, report_grid):
        target = [self.col, self.row]

        for row in report_grid:
            for tile in row:
                if tile.get("tile_origin") == target:
                    return tile

        return None



    def update_bg_colour_by_state(self):
        """
        Updates the tile background color based on its current state:
        - empty -> brown
        - growing -> dark orange
        - harvestable -> dark green
        - unknown -> black
        """
        #Note the fg is default
        if self.state == "empty":
            self.config(bg="saddle brown")
        elif self.state == "growing":
            self.config(bg="darkorange3")
        elif self.state == "harvestable":
            self.config(bg="dark olive green")
        else:
            self.config(bg="black")

    def update_self(self):
        """
        Synchronizes the tile UI with the latest GameEngine report.

        Responsibilities:
        - Finds corresponding tile in report grid
        - Updates state (empty / growing / harvestable)
        - Updates displayed text (crop info, growth, reward)
        - Updates background color accordingly
        """

        report_grid = States.report.get("report_grid")
        correct_tile = self._find_tile_report(report_grid)

        if not correct_tile:
            return

        if correct_tile.get("tile_has_contents"):

            if correct_tile.get("product_is_harvestable"):
                self.state = "harvestable"
            else:
                self.state = "growing"

            self.show_product_name = correct_tile.get("product_name")

            reward = correct_tile.get("product_reward")

            remaining_harvests = correct_tile.get("product_remaining_harvests")

            description = f"Product: {self.show_product_name}\nReward: {reward} Gold"

            if remaining_harvests == 1:
                description += "\nOne remaining harvest!"
            elif remaining_harvests >= 2:
                description += f"\n{remaining_harvests} Remaining harvests!"

            growth_time = correct_tile.get("product_growth_time")
            product_current_growth = correct_tile.get("product_current_growth")

            remaining = growth_time - product_current_growth
            remaining = math.ceil(remaining/10) #convert to seconds
            if growth_time != product_current_growth:
                description = description + f"\nTime Remaining: {remaining}"

            self.configure(text=description)


        else:
            self.state = "empty"
            self.configure(text="Plant Something Here!")

        self.update_bg_colour_by_state()


    def farm_tile_on_click(self):
        """
        Handles user interaction when a farm tile is clicked.

        Behavior depends on:
        - Whether the tile has content
        - Whether the content is harvestable
        - Which shop item is currently selected

        Possible actions:
        - Plant a new crop
        - Harvest existing crop
        - Delete crop (if selected tool is delete mode)
        - Do nothing if no valid action exists
        """
        report_grid = States.report.get("report_grid")
        correct_tile = self._find_tile_report(report_grid)

        if not correct_tile:
            return

        tile_origins = correct_tile.get("tile_origin")

        #If the tile does not have contents, plant.
        if not correct_tile.get("tile_has_contents"):

            if States.selected_button_id > 0:
                cmd = {"tile_location" : tile_origins,
                                                 "type" : States.selected_button_type,
                                                 "id" : States.selected_button_id}
                if cmd not in States.instructions_plant:
                    States.instructions_plant.append(cmd)

        #If the tile has contents, either delete them or harvest them
        if correct_tile.get("tile_has_contents"):
            if correct_tile.get("product_is_harvestable"):
                if not tile_origins in States.instructions_harvest:
                    States.instructions_harvest.append(tile_origins)


            elif States.selected_button_id == 0:
                if tile_origins not in States.instructions_delete:
                    States.instructions_delete.append(tile_origins)


class ShopButton(GridButton):
    """
    Represents a shop UI button used to select items for planting.

    Each button corresponds to:
    - A plant, tree, or animal from the catalog
    - Or a special "delete tool" button

    Selecting a button updates global selection state.

    - Note: id0 is always the "delete" option.
    """

    def __init__(self, parent, col, row):
        super().__init__(
            parent,
            row,
            col,
            command = lambda: self.shop_onclick(),
            bg="lightsalmon4"
        )

        self.state: str = "unselected" #Options: unselected, selected
        self.catalog_type: str = "" #Options: "plant", "tree", "animal"
        self.catalog_id: int = 0


    def update_bg_colour_by_state(self):
        """
        Updates button highlight state based on global selection.

        Selected button is visually highlighted,
        others revert to default color.
        """
        if not States.selected_button_id == self.catalog_id:
            self.configure(bg="lightsalmon4")
            return
        if not States.selected_button_type == self.catalog_type:
            self.configure(bg="lightsalmon4")
            return
        self.configure(bg="lightsalmon2")



    def shop_onclick(self):
        """
        When a button a shop button is pressed, update the state to persist
        the newly selected option in the shop (product).

        Also updates the visuals of every shop button, to correctly visually select
        the newly picked option.
        """
        States.selected_button_type = self.catalog_type
        States.selected_button_id = self.catalog_id

        for button in States.shop_buttons:
            button.update_bg_colour_by_state()

    def insert_catalog_item(self, catalog: dict, n: int):
        """
        Determines self.type and self.catalog_id based on the catalog.

        If n==0, this button will be labeled a delete button. Otherwise it will
        take the n:th catalog item determined of its category as its id.

        Also updates:
        - Button label
        - Displayed item stats (price, growth time, reward, etc.)

        Args:
            catalog (dict): Full product catalog.
            n (int): Global index across all categories.
        """
        if n == 0:
            self.catalog_id = 0
            self.configure(text="Delete Crop")
            self.update_bg_colour_by_state()
            return

        n_plants = len(catalog.get("plant"))
        n_trees = len(catalog.get("tree"))
        n_animals = len(catalog.get("animal"))
        if n <= n_plants:
            self.catalog_id = n
            self.catalog_type = "plant"
            self.config(text=f"{self.catalog_type}{self.catalog_id}")


        elif n_plants < n <= (n_plants + n_trees):
            n -= n_plants
            self.catalog_id = n
            self.catalog_type = "tree"
            self.config(text=f"{self.catalog_type}{self.catalog_id}")

        elif n_trees < n <= (n_plants + n_trees + n_animals):
            n -= (n_plants + n_trees)
            self.catalog_id = n
            self.catalog_type = "animal"
            self.config(text=f"{self.catalog_type}{self.catalog_id}")

        category = catalog.get(self.catalog_type)
        item = category.get(f"id{self.catalog_id}")
        name = item.get("product_name")
        price = item.get("price")
        reward_per_harvest = item.get("product_reward")
        growth_time = item.get("product_growth_time") / 10 #convert to seconds
        lifespan = item.get("product_remaining_harvests")

        description = f"{name}\nPrice: {price} Gold"
        description += f"\n Avg. Sell Price: {reward_per_harvest}"
        description += f"\nGrowth Time: {growth_time}"
        description += f"\nAmount of Harvests: {lifespan}"
        self.configure(text=description)





class States:
    """
    Unified class for keeping track of, and managing,
    the state of the game, UI and
    """
    gold = 0
    total_ticks = 0
    weather_multiplier = 1
    request_game_reset = False

    report = {}
    farm_buttons: list[FarmTileButton] = []

    shop_buttons: list[ShopButton] = []
    selected_button_type: str = ""
    selected_button_id: int = 0

    instructions_harvest = [] # format: [ [x, y], [x, y]]
    instructions_delete = [] # format: [ [x, y], [x, y]]
    instructions_plant = [] # format: [ [[x, y], type, id] [[x, y], type, id] ]

    @staticmethod
    def clear_instructions():
        """
        Clears all queued player action instructions.

        Called after each GameEngine tick to prevent duplicate execution.
        """
        States.instructions_harvest = []
        States.instructions_delete = []
        States.instructions_plant = []

    @staticmethod
    def update_info():
        """
        Updates global UI-related state variables from the latest engine report.

        Syncs:
        - gold
        - total_ticks
        - weather_multiplier

        These values are used for UI display updates.
        """
        States.gold = States.report.get("gold")
        States.total_ticks = States.report.get("total_ticks")
        States.weather_multiplier = States.report.get("weather_multiplier")
