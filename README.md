# Stratton_Oakmont

This script analyzes the performance of different option strategies with weekly expirations. Any strategy (that expires the same week in which it is opened) can be tested by creating a class which derives from the ‘Day’ class and implements the ‘calc_profit()’ method. Data must be acquired from the option suite in the Wharton WRDS database. Heatmaps are produced by the script, with premium on one axis and day of the week (excluding Friday) on the other. The WRDS database provides the best bids and offers at close for a given strike, so strategies are limited by that. 
