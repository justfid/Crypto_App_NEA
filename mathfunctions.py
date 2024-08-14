import math

def round_to_sf(x, sf=3):
    if x == 0:
        return 0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (sf - 1))