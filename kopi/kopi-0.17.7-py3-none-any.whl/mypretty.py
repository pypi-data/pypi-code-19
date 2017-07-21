__all__=["logpretty", "mpretty"]
import math
import numpy as np
def logpretty(x = [],VerbalEcho=False):
	xmin = 10.0** np.floor(np.log10( min(x) ) )
	xmax = 10.0** np.ceil(np.log10( max(x)))
	print (xmin)
	print (xmax)
	NumberOfChoice = int(np.log10(xmax/xmin)) + 1
	Output = np.zeros(NumberOfChoice)
	for n in range(NumberOfChoice):
		Output[n] = xmin*10**n
	return Output

def mpretty(x=[], n=6, font_pt=10, xWidth = 100, VerbalEcho=False):
    """
    To generate a set a pretty value for assigning x or y ticks
    A Near equivalent to R pretty function.
    But I allow the xmax to be not always covered by the last tick,
    so the plotted area is actually larger and, in my taste, prettier.
    There is a number of existing non-trivial algorithm for this.
    Should take a read a have some comparison in the future.
    So far, may not be able to handle Log axis.
    Use [1, 2, 5] as the pretty base candidate for Spacing
    n is the number of desired tick number
    preliminary one. xmin->hard fixed, xmax-> flexibly tuned
    """
    n = round(n)
    xmin = min(x)
    xmax = max(x)
    deltax=xmax-xmin
    MindlessSpacing = deltax/n
    order = ( round(math.log10(MindlessSpacing)) )
    #PrettyCandidates = np.array([0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5]) * (10**order)
    PrettyCandidates = np.array([0.1, 0.2, 0.5, 1, 2, 5]) * (10**order)
    NumOfChoice = len(PrettyCandidates)
    PossibleN = np.ceil( deltax/PrettyCandidates )
    OverNumber = abs(n-PossibleN)
    Overshoot = PossibleN * PrettyCandidates - deltax
    FontDigits =  abs(order) + 1
    weight_OverNumber =  font_pt*FontDigits
    weight_Overshoot = 2* xWidth/deltax
    OvershootPenalty= Overshoot*weight_Overshoot
    OverNumberPenalty = OverNumber * weight_OverNumber
    TotalPenalty = OverNumberPenalty + OvershootPenalty
    CandidateID = np.argmin(TotalPenalty) 	#what if more than one ?
    					#Dont worry, .index will take care of it.
    					#It only returns One value :)
    PrettySpacing =  PrettyCandidates[CandidateID]
    N=int(PossibleN[CandidateID])

    # My taste is that: the xmin must be covered by the first tick
    PrettyStarting = math.floor( xmin/PrettySpacing ) * PrettySpacing
    PrettyEnding = PrettyStarting + N*PrettySpacing
    #After flooring for the pretty starting value, the Last tick will be left shifted,
    # and in the worse case, sway much away from the xmax.
    #Just in case, lets see if it is neccesary to compensate the End Value
    if (xmax - PrettyEnding) > (PrettySpacing/2) :
    	N += 1
    	PrettyEnding = PrettyStarting + N*PrettySpacing
    Output= np.zeros(N+1)
    for i in range(N+1):
    	Output[i] = PrettyStarting + i*PrettySpacing
    if VerbalEcho == True:
    	print (x)
    	print ("n : " , n)
    	print ("Mindless Spacing d : " , MindlessSpacing)
    	print (("Candidates : " , PrettyCandidates))
    	print (("Possible N : "  , PossibleN))
    	print (("Font Digits : " ,  FontDigits))
    	print (("OverNumber : " , OverNumber))
    	print ("OverNumberPenalty : " , OverNumberPenalty)
    	print (("Overshoot : " , Overshoot))
    	print ("Overshoot Penalty : " , OvershootPenalty)
    	print (("Penalty : " , TotalPenalty))
    	print ("PrettySpacing : ", PrettySpacing)
    	print ("N : " , N)
    	print ("PrettyStarting : " , PrettyStarting)
    	print ("PrettyEnding : " , PrettyEnding)
    	print ("xmax-PrettyEnding : " , xmax - PrettyEnding)
    	print ("Pretty Output : " , Output)
    return Output
