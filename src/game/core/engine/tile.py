"""
Tile module.

Contains the base Tile class, whilst integrating fluid
communication and working methods for the engine and debug tools to work with.
"""

# Module being run as package, and pylint is complaining
# when running the file, so here's to make it shut up
# pylint: disable=relative-beyond-top-level
from .products import Product

class Tile:
    """
    Represents a single grid tile in the game world.

    A Tile can optionally contain a Product instance and is responsible for
    handling interactions such as planting, harvesting, clearing, and
    forwarding time progression to its contents.

    Also enriches product reports with spatial metadata for the engine.
    """

    def __init__(self, row: int = None, col: int = None, product: Product = None):
        self.row: int = row
        self.col: int = col
        self.contents: Product = product

    def is_occupied(self):
        """
        Checks if the tile is occupied by a product or not

        Returns:
            bool: True if the tile has contents, otherwise False.
        """
        return self.contents is not None

    def plant(self, product: Product, cost: int):
        """
        Attempts planting a product in this tile's self.contents var. It automatically
        does not do so if the tile is occupied by different contents already.

        Returns:
            dict: report containing success and cost, example:
            {
            "planting_success" : True,
            "cost" : 30
            }
        """

        report = {
            "planting_success" : False,
            "cost" : 0
        }

        if not self.is_occupied():
            self.contents = product

            if not self.is_occupied():
                return report

            report["planting_success"] = True
            report["cost"] = cost

        return report

    def harvest(self):
        """
        If a product (contents) exists, an attempt at harvesting the product is made.

        Returns:
            dict: Returns a report as a dict with information on the harvest.
            The engine is to interpret this. Example output:
            {
            'product_name': 'Apple Tree',
            'product_harvest_is_success': True,
            'product_harvest_reward': 15,
            'product_request_content_deletion': False,
            'tile_origin': [3, 4],
            'tile_has_contents': True
            }
        """

        if not self.is_occupied():
            return self._get_templated_report()

        report = self.contents.harvest()
        report = self._get_templated_report(report)

        if report.get("product_request_content_deletion"):
            self.clear()

        return report

    def clear(self):
        """
        Clears the contents of the tile (self.contents=None)
        """
        self.contents = None

    def advance_time(self):
        """
        If a product (contents) exists,
        contents.advance_time() is called to advance the product's time.

        Returns:
            dict: If a product exists, returns the product's status report
            combined with the tile's location.
        """
        if self.is_occupied():
            product_report = self.contents.advance_time()

            #Adds tile-related information to the comprehensive informational import by the product
            report = self._get_templated_report(product_report)

            if report.get("product_request_content_deletion"):
                self.clear()
                return self._get_templated_report()

            return report

        return self._get_templated_report()

    def _get_templated_report(self, report: dict = None):
        """
        Creates a template report stating the tile's origins (location in format [row, col]),
        and whether it has contents or not.

        Args
            report: A report (dict) may be given as an argument,
            in which case the template report will be added to it

        Returns:
            dict: Returns a report returned as a dict, optionally combined with an existing report.
        """
        if report is None:
            report = {}

        #Coordinates in [x, y] (col, row) format, not [row, col]
        if "tile_origin" not in report:
            report["tile_origin"] = [self.col, self.row]
        if "tile_has_contents" not in report:
            report["tile_has_contents"] = bool(self.contents)

        return report


    def get_contents_status(self):
        """
        Returns:
            dict: contains key-value pairs, containing the information of
            the content's common stats: "name", "reward", "growth_time", "remaining_harvests",
            "current_growth", "current_age".
        """
        info = {
            "name" : self.contents.name,
            "reward" : self.contents.reward,
            "growth_time" : self.contents.growth_time,
            "remaining_harvests" : self.contents.remaining_harvests,
            "current_growth" : self.contents.current_growth,
            "current_age" : self.contents.current_age
        }

        if not self.is_occupied():
            return None

        return info

    def get_content_specific_stat(self, stat_name: str = "name"):
        """
        Attempts to get the specified stat of the contents (instance of Product).

        Returns:
            var: Returns the value of the specified attribute if it exists, otherwise returns None
        """
        if not self.is_occupied():
            return None

        return getattr(self.contents, stat_name, None)
