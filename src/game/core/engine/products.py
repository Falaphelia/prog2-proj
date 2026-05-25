"""
Product module.

Contains the base Product class and specific subclasses
for different types of plantable products in the game.
"""

import random

class Product():
    """
    Base class for all plantable products in the game.

    Handles growth, harvesting logic, and lifecycle state.
    """

    def __init__(self,
                 name: str,
                 reward: int = 5,
                 growth_time: int = 5,
                 remaining_harvests: int = 1):

        """
        Initializes a Product instance.

        Args:
            name (str): Name of the product.
            reward (int): Reward value when harvested.
            growth_time (int): Ticks required to grow.
            remaining_harvests (int): Number of times it can be harvested.
        """

        self.name = name
        self.reward = reward
        self.growth_time = growth_time
        self.remaining_harvests = remaining_harvests
        self.current_growth = 0
        self.current_age = 0


        self.n_ticks_full_lifetime = self.growth_time * self.remaining_harvests

    def harvest(self):
        """
        Harvests the contents of the tile.

        Will increment down (-=) self.remaining_harvests.

        Returns:
            dict: a mini status-report of the result of the action. Example:
            {
            "product_name" : "Potato",
            "product_harvest_is_success" : True,
            "product_harvest_reward" : 5
            }
        """

        #Report failure template
        report: dict = {
                "product_name" : self.name,
                "product_harvest_is_success" : False,
                "product_harvest_reward" : 0,
                "product_request_content_deletion" : False
            }

        #Harvest Success situation
        if self.is_ready() and self.remaining_harvests >= 1:

            self.remaining_harvests -= 1
            self.current_growth = 0

            report = {
                "product_name" : self.name,
                "product_harvest_is_success" : True,
                "product_harvest_reward" : self.reward,
                "product_request_content_deletion" : self.remaining_harvests == 0
            }

        return report


    def is_ready(self):
        """
        Checks if the product is ready to be harvested.

        Returns:
            bool: True if the product is ready to be harvested, otherwise False.
        """
        return self.current_growth >= self.growth_time


    def advance_time(self):
        """
        Increments the age of the product and advances the product's time.

        Affects for example harvestability and may trigger a random event.

        Returns:
            Dict: A static object containing the updated state of the Product,
            is to normally be forwarded to the Tile and Game Engine.
        """
        self.current_age += 1

        #Affect growth and product's harvest if not harvestable
        if not self.is_ready() and self.remaining_harvests >= 1:
            self.current_growth += 1

        #Triggers the random even method, with a chance of producing a random event
        # unique to the Product subclass
        result = self._trigger_random_event()
        report = self._get_report()

        if not result:
            result = {}

        # merge reports in case the random event triggers a tile-level instruction,
        # for example clear.
        merged_report = report | result

        return merged_report


    def _trigger_random_event(self):
        """
        Triggers a random event. This is a placeholder later
        to be defined with properitery logic in the subclass.

        If you can see this then you may have forgotten to define the
        random events method in the subclass!
        """
        return {}

    def _get_report(self):
        """
        Creates a report based on the current state of the Product.

        This status report is to be sent to the Tile and later Game Engine to update the game state.

        Returns:
            dict: A static object containing the state of the Product
        """

        product_report = {
            "product_name" : self.name,
            "product_reward" : self.reward,
            "product_growth_time" : self.growth_time,
            "product_remaining_harvests" : self.remaining_harvests,
            "product_current_growth" : self.current_growth,
            "product_current_age" : self.current_age,
            "product_is_harvestable" : self.current_growth >= self.growth_time and
                                        self.remaining_harvests >= 1,
            "product_is_dead" : self.remaining_harvests <= 0
        }

        return product_report

class Plant(Product):
    """
    Represents a plantable crop product.

    Plants can become infected by random events and require timely harvesting
    before they are destroyed.
    """

    def __init__(self, name="Potato", reward=5, growth_time=20, remaining_harvests=1):
        super().__init__(name, reward, growth_time, remaining_harvests)

        self.disease_resistance = random.uniform(0.2, 0.8)

    def _trigger_random_event(self):
        """
        Triggers plant-specific random events (e.g. disease/infection).

        Returns:
            dict or None: Event result affecting the tile or plant state.
        """

        infect_result = self.infect()

        return infect_result

    def infect(self):
        """
        Applies a disease/infection check to the plant.

        Has a probability of killing the plant by requesting tile deletion.

        Returns:
            dict or None: Contains deletion request if infection triggers.
        """

        #Note this event is still valid when the the crop is ready to be harvested
        #The "Plant" type of product requires the player actively making sure to harvest it in time
        #before something bad happens to it
        average_n_per_lifetime = 0.2
        chance = (average_n_per_lifetime / self.n_ticks_full_lifetime) * self.disease_resistance
        if random.random() < chance:
            return {
                "product_request_content_deletion" : True
            }

        return None

class Tree(Product):
    """
    Represents a tree-based product.

    Trees have variable yield, evolving growth times, and may gain additional
    harvests over time.
    """

    def __init__(
            self,
            name="Apple Tree",
            reward=52,
            growth_time=900,
            remaining_harvests=10
        ):
        """
        Initializes a Tree product.

        Args:
            name (str): Name of the tree.
            reward (int): Base reward per harvest.
            growth_time (int): Growth time before harvest.
            remaining_harvests (int): Number of harvest cycles.
        """

        super().__init__(name, reward, growth_time, remaining_harvests)



        self.original_growth_time = growth_time


    def _trigger_random_event(self):
        """
        Triggers tree-specific random events such as bonus growth (perching).

        May increase remaining harvests under certain conditions.
        """

        return self.perch()

    def perch(self):
        """
        Handles random bonus growth behavior for trees.

        Can increase remaining harvests based on probability.
        """

        #Stops abuse by not harvesting
        if self.current_growth == self.growth_time:
            return

        average_n_per_lifetime = 0.5
        chance = average_n_per_lifetime / self.n_ticks_full_lifetime
        if random.random() <= chance:
            self.remaining_harvests += 1

    def harvest(self):
        """"
        Harvests the tree and applies random yield and growth variation.

        Returns:
            dict: Status report of harvest result.
        """

        #Report failure template
        report: dict = {
                "product_name" : self.name,
                "product_harvest_is_success" : False,
                "product_harvest_reward" : 0,
                "product_request_content_deletion" : False
            }

        #Harvest Success situation
        if self.is_ready() and self.remaining_harvests >= 1:

            #Trees have a chance to have a bad/good harvest
            yield_multiplier  = random.uniform(0.5, 1.5)

            self.remaining_harvests -= 1
            self.current_growth = 0

            # Trees have a chance to grow to take more or less time to grow
            # as they get older after harvests
            self.growth_time *= random.uniform(0.8, 1.3)

            # implement max cap so it doesn't drift too much,
            # 1,2**8 is roughly 4,3x the original growth time
            max_growth_time = self.original_growth_time * (1.2 ** 8)
            self.growth_time = min(self.growth_time, max_growth_time)


            report = {
                "product_name" : self.name,
                "product_harvest_is_success" : True,
                "product_harvest_reward" : round(self.reward * yield_multiplier),
                "product_request_content_deletion" : self.remaining_harvests == 0
            }


        return report

class Animal(Product):
    """
    Represents an animal-based product.

    Animals can reproduce over time, increasing their value,
    and incur feed costs when harvested.
    """

    def __init__(
        self,
        name: str = "Sheep",
        reward: int = 65,
        growth_time: int = 60,
        remaining_harvests: int = 8
        ):

        """
        Initializes an Animal product.

        Args:
            name (str): Name of the animal.
            reward (int): Base reward value.
            growth_time (int): Growth time before harvest.
            remaining_harvests (int): Number of harvest cycles.
        """

        super().__init__(name, reward, growth_time, remaining_harvests)

    def _trigger_random_event(self):
        """
        Triggers animal-specific random events such as reproduction.

        May increase reward value over time.
        """

        self.reproduce()

    def reproduce(self):
        """
        Handles reproduction event for animals.

        May increase the animal's reward value based on probability.
        """

        #Can't reproduce when harvestable - prevents players from
        # waiting/cheating to keep expensive products on their plot
        if self.current_growth == self.growth_time:
            return None

        average_n_per_lifetime = 3
        chance = average_n_per_lifetime / self.n_ticks_full_lifetime
        if random.random() <= chance:
            self.reward += 50

        return None


    def harvest(self):
        """
        Harvests the animal and applies feed cost deduction.

        Returns:
            dict: Status report of harvest result.
        """

        #Report failure template
        report: dict = {
                "product_name" : self.name,
                "product_harvest_is_success" : False,
                "product_harvest_reward" : 0,
                "product_request_content_deletion" : False
            }

        #Harvest Success situation
        if self.is_ready() and self.remaining_harvests >= 1:

            #animals deduct a random amount for feed cost on harvest.
            feed_cost_multiplier = random.uniform(0.001, 0.05)
            feed_deduction = feed_cost_multiplier * self.growth_time

            self.remaining_harvests -= 1
            self.current_growth = 0

            report = {
                "product_name" : self.name,
                "product_harvest_is_success" : True,
                "product_harvest_reward" : round(self.reward - feed_deduction),
                "product_request_content_deletion" : self.remaining_harvests == 0
            }

        return report
