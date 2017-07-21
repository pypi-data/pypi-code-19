#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from ..pkg.constant2 import Constant
except:
    from crawl_redfin.pkg.constant2 import Constant


class HouseType(Constant):
    class SingleHouse:
        id = 1
        name = "Single House"

    class Condo:
        id = 2
        name = "Condo"

    class TownHouse:
        id = 3
        name = "Town House"

    class MultiFamily:
        id = 4
        name = "Multi Family"

    class Land:
        id = 5
        name = "Land"

    class OtherType:
        id = 6
        name = "Other Type"
