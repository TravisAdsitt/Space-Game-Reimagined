# -*- coding: utf-8 -*-
"""
Author: Travis Adsitt

This is the beginnings of the space game idea, more documentation and planning
to come.
"""

import random

"""
A console progress bar taken from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
"""
def printProgressBar (iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

"""
Intended for the management of a sector of a planets resource space
"""
class Planet_Sector:
    
    def __init__(self, gen_random = True):
        if(gen_random):
            self.land                 = bool((random.getrandbits(1)))
            if(self.land):
                rock_ratio           = random.randint(0,100)
                metal_ratio          = random.randint(0,100)
                wood_ratio           = random.randint(0,rock_ratio)
                water_ratio          = 100 - (wood_ratio + rock_ratio)
                self.wood_resource_count  = 100 * wood_ratio  #How much wood do we see in this sector?
                self.rock_resource_count  = 100 * rock_ratio  #How much stone do we see in this sector?
                self.water_resource_count = 100 * water_ratio #How much water in this sector?
                self.metal_resource_count = self.rock_resource_count * metal_ratio #How much metal do we see in the rock?
                self.rock_resource_count -= self.metal_resource_count
            else:
                self.wood_resource_count  = 0
                self.metal_resource_count = 0
                self.rock_resource_count  = 0
                self.water_resource_count = 100

"""
Intended to manage the planet object
"""
class Planet:
    
    def __init__(self):
        self.atmosphere_radius   = 0
        self.atmosphere_volume   = 0
        self.oxygen_level        = 0
        self.nitrogen_level      = 0
        self.co2_level           = 0
        self.planet_surface_area = 0
        self.sectors             = None
        self.initialized         = False
        
    def initialize_random(self):
        #ATMOSPHERE SETUP START
        self.planet_surface_area = random.randint(100000000,1000000000)   #In km^2
        self.atmosphere_radius   = random.randint(50,10000) #In km
        self.atmosphere_volume   = self.atmosphere_radius * self.planet_surface_area
        oxygen_ratio             = random.randint(15,23)
        nitrogen_ratio           = random.randint(75,82)
        
        if(nitrogen_ratio + oxygen_ratio > 100):
            nitrogen_ratio = 100 - oxygen_ratio
            co2_ratio      = 0
        else:
            co2_ratio      = 100 - (nitrogen_ratio + oxygen_ratio)
        
        self.oxygen_level        = self.atmosphere_volume * oxygen_ratio
        self.nitrogen_level      = self.atmosphere_volume * nitrogen_ratio
        self.co2_level           = self.atmosphere_radius * co2_ratio
        #ATMOSPHERE SETUP END
        
        #SECTOR SETUP START
        total_sectors = int(self.planet_surface_area / 10) #Each sector represents 10x10 km
        self.sectors  = []
        for i in range(total_sectors):                     #TODO: Thread this out -- takes waaay too long atm
            printProgressBar(i,total_sectors)
            self.sectors.append(Planet_Sector())
        #SECTOR SETUP END
        
        
        self.initialized = True

"""
Intended for the managment of a ship object
"""
class Ship:
    
    def __init__(self):
        self.fuel_level   = 0
        self.oxygen_level = 0
        self.ore_level    = 0
    

"""
Intended for the managment of a player object
"""
class Player:
    
    def __init__(self):
        self.ships       = None
        self.bases       = None
        self.home_planet = None
        