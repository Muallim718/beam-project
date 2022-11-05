# Python Script for ENES220 Beam Project Group X
# Team Members: Jeremy Kuznetsov, Muallim Cekic

# English engineering units (lbs, in)

from math import pow, sqrt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Block:
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

## Change These Variables =====================================

# Measurements in in for:
web_width = 0.6875
web_height = 1.375
top_flange_height = 0.4375
top_flange_width = 1.125
bot_flange_height = 0.4375
bot_flange_width = 1.25

# Beam Force 
F = 0

## ============================================================

# Variables for Beam Under Loading
Ra = 0
Rb = 0
Vmax = 0
Mmax = 0
SigmaMax = 0
TauMax = 0
TauGlue = 0
xmax = 0
E = 1.5 * pow(10,6) #units in psi, pine is 1.8*10^6, oak is 1.5*10^6

def main():

    top = Block(top_flange_width, top_flange_height, area(top_flange_width, top_flange_height), centroid(top_flange_height, web_height + bot_flange_height))
    middle = Block(web_width, web_height, area(web_width, web_height), centroid(web_height, bot_flange_height))
    bottom = Block(bot_flange_width, bot_flange_height, area(bot_flange_width, bot_flange_height), centroid(bot_flange_height, 0))

    totalheight = (top.height + middle.height + bottom.height)

    # Check for Rule Violations
    if totalheight/max(top.width,bottom.width) > 2:
        print("You have violated the height to width ratio rule!")
        return
    if max(top.width, bottom.width) > 2:
        print("You have violated the maximum width rule!")
        return
    if max(top.width/top.height, bottom.width/bottom.height) > 8:
        print("You have violated the flange Width ratio rule!")
        return
    if (middle.height/middle.width) > 8:
        print("You have violated the flange thickness ratio rule!")
        return

    totalcentroid = totalcentroidfunc(top, middle, bottom)

    top.cdist = abs(totalcentroid - (bottom.height + middle.height + (0.5*top.height)))
    middle.cdist = abs(totalcentroid - (bottom.height + (0.5*middle.height)))
    bottom.cdist = abs(totalcentroid - (0.5*bottom.height))

    totalmoment = momentsquare(top) + parallel(top) + momentsquare(middle) + parallel(middle) + momentsquare(bottom) + parallel(bottom)
    Fvalues = list(range(1000, 3000, 10))
    SigmaMaxValues = [0]*200
    TauGlueValues = [0]*200
    TauMaxValues = [0]*200

    LimitNormal = np.full(200,14327)
    LimitShear = np.full(200,1495)
    LimitGlueShear = np.full(200,989)

    sigma_indicator = 0
    tau_wood_indicator = 0
    tau_glue_indicator = 0

    F_sigma = 0
    F_tauwood = 0
    F_tauglue = 0
    F_failure_modes = []

    for i in range(0, 200, 1):

        Ra = (2/5)*Fvalues[i]
        Rb = (3/5)*Fvalues[i]
        Vmax = abs(Rb)
        Mmax = 12*Ra # Specific to a 20in beam loaded 12in into its length

        # Calculating Sigma Max in the Beam
        if totalcentroid > (totalheight / 2):
            SigmaMax = (Mmax * totalcentroid) / totalmoment
        else:
            SigmaMax = (Mmax * (totalheight - totalcentroid) / totalmoment)

        # Calculating Tau Max in the Beam
        TauMax = (Vmax * qmax(top, middle, bottom, totalcentroid, totalheight)) / (totalmoment * web_width)

        # Calculating the Tau Max in the Glue Areas
        if q(top) > q(bottom):
            TauGlue = (Vmax * q(top)) / (totalmoment * web_width)
        else:
            TauGlue = (Vmax * q(bottom)) / (totalmoment * web_width)

        SigmaMaxValues[i] = SigmaMax
        TauGlueValues[i] = TauGlue
        TauMaxValues[i] = TauMax

        
        if SigmaMax > LimitNormal[1] and sigma_indicator == 0:
            sigma_indicator = 1
            F_sigma = Fvalues[i]
            print(f"The failure F for normal stress {F_sigma}")
        if TauMax > LimitShear[1] and tau_wood_indicator == 0:
            tau_wood_indicator = 1
            F_tauwood = Fvalues[i]
            print(f"The failire F for shear stress {F_tauwood}")
        if TauGlue > LimitGlueShear[1] and tau_glue_indicator == 0:
            tau_glue_indicator = 1
            F_tauglue = Fvalues[i]
            print(f"The failire F for glue shear stress {F_tauglue}")

    F_failure_modes.append(F_sigma)
    F_failure_modes.append(F_tauwood)
    F_failure_modes.append(F_tauglue)
    F_control = min(F_failure_modes)
    
    # Length measurements are in in
    beam_length = 20
    # b is the distance from F to the right roller
    b = 8

    xmax = max_deflection_location(beam_length, b)
    deflection_max = max_deflection(F_control, beam_length, b, totalmoment)
    print(f"Max deflection occurs at {xmax}")
    print(f"Max deflection is {deflection_max}")

    df = pd.DataFrame.from_dict({
        'Force'            : Fvalues,
        'Max Normal Stress': SigmaMaxValues,
        'Max Shear Stress' : TauMaxValues,
        'Max Glue Stress'  : TauGlueValues,
        'Yield Normal'       : LimitNormal,
        'Yield Shear'        : LimitShear,
        'Yield Glue Shear'   : LimitGlueShear
    })
    
    fig, ax = plt.subplots(1)
    ax.plot(df['Force'], df['Max Normal Stress'], 'blue')
    ax.plot(df['Force'], df['Max Shear Stress'], 'black')
    ax.plot(df['Force'], df['Max Glue Stress'], 'green')
    ax.plot(df['Force'], df['Yield Normal'], 'red')
    ax.plot(df['Force'], df['Yield Shear'], 'orange')
    ax.plot(df['Force'], df['Yield Glue Shear'], 'purple')
    ax.set_title('Stresses vs. Applied Load F')
    ax.set_xlabel('Force Units (lbs)')
    ax.set_ylabel('Stress Units (psi)?')
    ax.legend(['Max Normal Stress', 'Max Shear Stress', 'Max Glue Stress', 'Yield Normal', 'Yield Shear', 'Yield Glue Shear'])
    #plt.show()

    ## Deflection Calculations
    Fnew = 2400
    DeflectionValues = [0]*200
    Dist = [0]*200
    minimum = 0

    for i in range(0,200,1):
        Dist[i] = i*(12/200)
        DeflectionValues[i] = (-Fnew*8*Dist[i])/(6*20*totalmoment*E) * (pow(20,2)-pow(8,2)-pow(Dist[i],2))
        if DeflectionValues[i] < minimum:
            minimum = DeflectionValues[i]

    dg = pd.DataFrame.from_dict({
        'Distance'   : Dist,
        'Deflection' : DeflectionValues
    })

    fig, bx = plt.subplots()
    bx.plot(dg['Distance'], dg['Deflection'])
    bx.set_title('Deflection vs Distance')
    bx.set_xlabel('Distance from left pin (in)')
    bx.set_ylabel('Displacement (in)')
    bx.legend(['Displacement'])
    plt.show()

    return

# Functions ============================================

def max_deflection_location(L, b):
    return sqrt((pow(L, 2) - pow(b, 2)) / 3)

def max_deflection(F, L, b, Iz):
    term1 = - (F * b * sqrt((pow(L, 2) - pow(b, 2)) / 3)) / (6 * E * L * Iz)
    term2 = pow(20, 2) - pow(8, 2) - ((pow(L, 2) - pow(b, 2)) / 3)
    return term1 * term2

def area(L1, L2):
    return L1*L2

def centroid(hgt, Offset):
    return Offset + (hgt/2)

def totalcentroidfunc(top, middle, bottom):
    atotal = top.area + bottom.area + middle.area
    return ((top.area*top.centroid) + (middle.area*middle.centroid) + (bottom.area*bottom.centroid))/atotal
    
def momentsquare(block):
    return (1/12)*block.width*pow(block.height, 3)

def parallel(block):
    return block.area * pow(block.cdist, 2)

def q(block):
    return block.area * block.cdist

def qmax(top, middle, bottom, totalcentroid, totalheight):
    q1= q(bottom) + (((totalcentroid - bottom.height) * middle.width) * (0.5*(totalcentroid - bottom.height)))
    q2 = q(top) + ((totalheight - totalcentroid - top.height) * middle.width) * (0.5 * (totalheight - totalcentroid - top.height))
    return max(q1,q2)

if __name__ == "__main__":
    main()