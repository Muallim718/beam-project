# Python Script for ENES220 Beam Project Group X
# Team Members: Jeremy Kuznetsov, Moocow

# English engineering units (lbs, in)

import math


class block:
    width = 0
    height = 0
    area = 0
    centroid = 0
    cdist = 0
def __init__(self, width, height, area, centroid):
    self.width = width
    self.height = height
    self.area = area
    self.centroid = centroid


# Measurements in mm for:
web_width = 0
web_height = 0
top_flange_height = 0
top_flange_width = 0
bot_flange_height = 0
bot_flange_width = 0


# Variables for Beam Under Loading
F = 0
Ra = 0
Rb = 0
Vmax = 0
Mmax = 0
SigmaMax = 0
TauMax = 0

def main():
    top = block(top_flange_width, top_flange_height, area(top_flange_width, top_flange_height), centroid(top_flange_height, web_height + bot_flange_height))
    middle = block(web_width, web_height, area(web_width, web_height), centroid(web_height, bot_flange_height))
    bottom = block(bot_flange_width, bot_flange_height, area(bot_flange_width, bot_flange_height), centroid(bot_flange_height, 0))

    totalcentroid = totalcentroidfunc(top, middle, bottom)

    top.cdist = totalcentroid - (bottom.height + middle.height + (0.5*top.height))
    middle.cdist = totalcentroid - (bottom.height + (0.5*middle.height))
    bottom.cdist = totalcentroid - (0.5*bottom.height)

    totalmoment = momentsquare(top) + parallel(top) + momentsquare(middle) + parallel(middle) + momentsquare(bottom) + parallel(bottom)

    Ra = (2/5)*F
    Rb = (3/5)*F
    Vmax = abs(Rb)
    Mmax = 12*Ra # Specific to a 20in beam loaded 12in in


    totalheight = (top.height + middle.height + bottom.height)
    if totalcentroid > (totalheight / 2):
        SigmaMax = (Mmax * totalcentroid) / totalmoment
    else:
        SigmaMax = (Mmax * (totalheight - totalcentroid) / totalmoment)

    if q(top) > q(bottom):
        TauMax = (Vmax * q(top)) / (totalmoment * web_width)
    else:
        TauMax = (Vmax * q(bottom)) / (totalmoment * web_width)

    

    return

    


def area(L1, L2):
    return L1*L2

def centroid(hgt, Offset):
    return Offset + (hgt/2)

def totalcentroidfunc(top, middle, bottom):
    atotal = top.area + bottom.area + middle.area
    return ((top.area*top.centroid) + (middle.area*middle.centroid) + (bottom.area*bottom.centroid))/atotal
    
def momentsquare(block):
    return (1/12)*block.width*math.pow(block.height, 2)

def parallel(block):
    return block.area * math.pow(block.cdist, 2)

def q(block):
    return block.area * block.cdist



if __name__ == "__main__":
    main()