# ReGrowth

A Python-based simulation game featuring dynamic plant growth, weather integration, and random event mechanics.

## Prerequisites
* **Python Version:** Python 3.14.5

## Installation & Setup
1. Clone or download the repository.
2. Navigate to the project root directory (`C:.`).
3. Install the required dependencies:
   ```bash
   pip install -e .
   ```

4. python main.py

## Credits & Assets

- App Icon: Designed using assets sourced from Unsplash.
  Wolfgang Hasselmann on unsplash at https://unsplash.com/@wolfgang_hasselmann

## Code Coverage and Tests

    88% coverage, with 484 statements and 58 missing.

    Unzip coverage_files.zip to view the local HTML report breakdown.

## How to Play

    1. You start out with a total of 10 gold.

    2. On the right-hand side, you can choose the product you wish to plant.

    3. The product can either be a plant, tree, or animal.

    4. The price, reward per harvest (market price), and name are all listed in the catalog/shop.

    5. If using a small screen, it is recommended to enter settings and make sure you don't have a high zoom-rate, as having a high zoom or overall large screen can result in not being able to see all the text properly.

    6. Pressing F11 toggles fullscreen. Pressing Esc forces you out of fullscreen.

    7. All tiles on the left side of the screen can be planted on. Clicking on an empty tile with the required capital for your selected product in the store results in the product being planted.

    8. An orange tile indicates that the Product is currently Growing. At the bottom of the tile, you can see how long it is until the product has finished growing in seconds.

    9. When a product has finished growing, it turns green. By clicking on it, it gets harvested, and you earn the market value back. Some products, for example strawberries, have multiple harvest cycles.

    10. You may face some difficulties or for some reason need to reset the game. There is a reset button towards the top-right corner of the screen. Here, you can also see how much gold you have, how many seconds it has been since you started playing, and the weather rating.

    11. The weather rating is a calculation based on the weather in Stockholm, accounting for soil moisture and soil temperature. Ideal temperature and moisture results in a slight boost to the market price (up to +20%!), whilst very bad weather which is not ideal for plants can result in a decreased market price (down to -20%).

    12. As mentioned earlier, there are different types of Products: Plants, Trees, and lastly Animals. All of these have some notable differences:

    Plants: Plants grow decently fast, have a shorter amount of life cycles, and give a small-medium income. These are "active" products, meaning you need to as a rule be actively playing when using them. This is because as time goes on, plants have a chance of being "infected", which results in them quite literally disappearing. You do not get compensated for this. Always harvest as fast as possible, especially early game! If you lose your first plants due to bad luck, the only thing you can do is reset!

    Trees: Trees are more often than not somewhere in the middle. Trees have more harvest cycles than plants, but on average take longer to grow. They are slightly more passive. Whilst a tree is growing, there is a chance for a bird to perch on it. When this happens, the tree silently earns one additional harvest cycle and can thus earn more money for slightly longer. An additional consideration to have when planting trees is that upon harvest, their yield may vary. This means that in your earlier farming, trees can be a bit of a gamble, and may result in earning less than expected!

    Animals: Animals are more late-game and overall take a long time to grow. These are the perfect products to have if you wish to go for a coffee mid-playthrough. Animals aren't anything too special, but compared to more active playstyles such as with Plants, they may earn you less coin on average per minute. However, that doesn't mean they are a bad choice—it all depends on your playstyle. Animals can be expensive, and on harvest, a portion of their original reward will be deducted for the cost of feed. The portion is small, but will vary per harvest.