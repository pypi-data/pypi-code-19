import numpy as np
import pandas as pd
import random
import itertools
from Bio import motifs

def topseq(filename):  
	"""Opens a PSSM file and generates the string corresponding to the highest probable LOG-odds score at each position"""
	dic = {0:"A",1:"C",2:"G",3:"T"}  # dictionary of indexes of each nucleotide for matrices
	tf1 = np.loadtxt(filename, skiprows=1)
	tf2 = tf1[:,1:].transpose()
	indexes = np.argmax(tf2,axis=0).tolist()  #generates a list of indexes of the highest probability base per position. 
	seqstring = ""
	for i in indexes: #generates a string nucleotide sequence corresponding top nucleotide for each position
		seqstring += dic[i]
	return seqstring # returns the top motif

def topseq_array(numpyarray):  
	"""Takes a PSSM as a numpy array and generates the string corresponding to the highest probable LOG-odds score at each position"""
	dic = {0:"A",1:"C",2:"G",3:"T"}  # dictionary of indexes of each nucleotide for matrices
	# tf1 = np.loadtxt(filename, skiprows=1)
	# tf2 = tf1[:,1:].transpose()
	indexes = np.argmax(numpyarray,axis=0).tolist()  #generates a list of indexes of the highest probability base per position. 
	seqstring = ""
	for i in indexes: #generates a string nucleotide sequence corresponding top nucleotide for each position
		seqstring += dic[i]
	return seqstring # returns the top motif
  
def reversecomp(rprimsequence): 
""" Make a complement version of the sequence, and reverse it so it has the proper orientation. Both input and output are strings"""
	a = ""
	tempzrev = rprimsequence
	tempzrev = tempzrev.replace("T","X")
	tempzrev = tempzrev.replace("A","T")
	tempzrev = tempzrev.replace("X","A")
	tempzrev = tempzrev.replace("C","Y")
	tempzrev = tempzrev.replace("G","C")
	tempzrev = tempzrev.replace("Y","G")
	templist = list(tempzrev)
	templist.reverse()
	for i in templist:
		a += i
	return a


def matrixmaker(dnastring):   
	""" Generates a numpy array from a DNA sequence string, made from ones and zeros. 2D representation of a DNA sequence. 
	Complements the matrixconverter function""" 
	lettersinv = {"A":0,"C":1,"G":2,"T":3}
	matrix = np.zeros( (4, len(dnastring)) ) # Make a matrix full of zeros of of the length of the DNA string
	index = []
	for i in range(len(dnastring)):    
		index.append([lettersinv[list(dnastring)[i]], i]) #convert the string into a list of indexes that correspond to those same bases from tge lettersinv dict
	a = np.array(index)  
	matrix[a[:,0], a[:,1]] = 1  # replace the zeros form empty matrix to 1 accordign to the sequence index list. 
	
	return matrix

def matrixconverter(seqmatrix): 
	"""Generates a DNA sequence string based on a NumPy matrix"""
	dic = {0:"A",1:"C",2:"G",3:"T"}  # dictionary of indexes of each nucleotide for matrices
	a = np.transpose(np.nonzero(np.transpose(seqmatrix))).tolist()
	seqstring = ""
	for i in a:
		seqstring += dic[i[1]]
	return seqstring



def regenerateseq(degeneratestring, format):
	""" Generates an iterable list of possible sequences in unambiguous IUPAC format based on a IUPACdegenerate sequence. Ex: ATN = [ATT, ATG, ATC, ATA]. 
	The Input is a IUPAC compatible string ; the output can either be a list of strings or a list of numpy arrays, depending on the options used."""
	##IUPAC dictionary
	lettersinv = {"A":0,"C":1,"G":2,"T":3}
	
	IUPAC1 = ["A", "T", "C", "G"]
	IUPAC2 = ["R", "Y","S","W","K","M"]
	IUPAC3 = ["B", "D", "H", "V"]
	IUPAC4 = "N"

	iupacdna2 = {"R":["A","G"],"Y":["C","T"],"S":["G","C"],"W":["A","T"],"K":["G","T"],"M":["A","C"]}
	iupacdna3 = {"B":["C","G","T"],"D":["A","G","T"],"H":["A","C","T"],"V":["C","G","T"]}


	seq = list(degeneratestring)

	seqcomb = []
	for i in seq: 
	# generate a list of lists, where the outer list corresponds to each position in the motif sequence, 
	# and the inner lists the possible letters at that position
		if i in IUPAC1:
			seqcomb.append([i])	
		elif i in IUPAC2: 
			seqcomb.append(iupacdna2[i])
		elif i in IUPAC3: 
			seqcomb.append(iupacdna3[i])	
		else:
			seqcomb.append(IUPAC1)
			

	seqcombbeta = list(itertools.product(*seqcomb)) # generate a list of all possible combinations 

	seqfinal = []

	if format == "numpy":
		for i in seqcombbeta:
			b = matrixmaker("".join(i))
			seqfinal.append(b)
		
	elif format == "string":
		for i in seqcombdbeta:
			b = "".join(i)
			seqfinal.append(b) 
		
	
	return seqfinal 


def randomseq(length, format):   
	""" Generate a random n length DNA sequence as a matrix"""
	matrix = np.zeros( (4, length) )
	index = []
	for i in range (length):    
	    index.append([random.randrange(0,4,1), i]) 
	a = np.array(index)  
	matrix[a[:,0], a[:,1]] = 1

	if format == "numpy":
		return matrix
	elif format == "string":
		return matrixmaker(matrix)
	return matrix




def read_pfm(filename):
	"""Facilitates readings a Bio.motif object with set parameters. The output is a motif object that can quickly be trasnformed to a 
	PWM, or a PSSM using the associated arguments (.pwm , .pssm).  """
	with open(filename, "r") as handle:
		motif = motifs.read(handle, "pfm")
	motif.pseudocounts = .25
	motif.background = {'A':0.3,'C':0.2,'G':0.2,'T':0.3}

	return motif    

def pearson_pssm(pfm1,pfm2):
	""" takes 2 motif objects and performs a pearson correlation to obtain their offset, their distance, along with the length of each separate motif"""
	motif1 = pfm1.pssm
	motif2 = pfm2.pssm

	distance, offset = motif1.dist_pearson(motif2)
	length1, length2 = motif1.length , motif2.length

	return [1 - distance, offset,length1, length2]


def pssmwalk(motif, sequence, pos, inputformat): 
	""" Tests each position of a SHORT DNA sequence as a numpy array against a pssm array. Returns the best alignment score. 
	The Pos argument lets you define over which portion of the pwm you want to align. Add 0 for the whole thing. 
	Useful when you add buffer random sequences on the site to align earlier than the 0 position for both array and sequence, or further than the length of the array"""
	if inputformat == "numpy": # accepts both numpy PSSM matrices or Bio.motifs PFMs as input. both are then stored as a numpy array
		pssm = motif

	elif inputformat == "pfm":
		pssm = np.array(pd.DataFrame(motif)).transpose()
		
	# make a buffer array of 0.25 probability accross the board. This will flank the real PWM and both sides. This will allow the 
	# alignment of the PSSM a little before and after the CORE sequence, giving flexibility to the process without giving these buffer 
	# sequences a strong probability to be the best alignment position. a log-odds of -1 is unprobable, without being 0. 
	mat =  np.ones((4, 20)) * -1 

	iterpssm = np.concatenate((mat, pssm, mat), axis=1) 

	alphapos = 0
	alphascore = -1000		
	for i in xrange(pos,len(iterpssm.transpose())-pos):
		try:
			betapos = i 
			betascore = np.sum(sequence * iterpssm[:,betapos:(betapos + sequence.shape[1])])

			if betascore > alphascore:
				alphascore = betascore
				alphapos = betapos
		except ValueError:
			pass
	prox = np.zeros((4,alphapos))
	dist = np.zeros((4,(iterpssm.shape[1]-(sequence.shape[1]+alphapos))))
	coreiter = np.transpose(np.concatenate((prox, sequence, dist), axis=1))


	
	return [alphascore,alphapos,iterpssm,coreiter]   


def save_pssm(pfm_file, outfile):
	""" Takes a motif object and saves it to a specified file in PSSM format, with the appropriate header and formatting"""
	motif = read_pfm(pfm_file)

	df_motif = pd.DataFrame(motif.pssm)
	df_motif["Pos"] = df_motif.index.values +1
	df_motif = df_motif.set_index("Pos")
	df_motif.to_csv(outfile, sep="\t")



def corescan(filename, core):
    """ Takes a core consensus motif and scans a numpy PSSM for the best alignment site, then returns the score. """
    
    pssm = np.loadtxt(filename, skiprows=1)
    pssmf = pssm[:,1:].transpose()

    # iterpssm = np.concatenate((matlog, pssmf, matlog), axis=1) #iterable PSSM , flanked by buffer arrays

    lenpssm = len(pssmf.transpose())

    score = -1000
    pos = 0
    for j in regenerateseq(core, "numpy"):
        beta = pssmwalk(pssmf,j, 0, "numpy")
        

        betascore = beta[0]

        betapos = beta[1]
        
        if betascore > score :
            score = betascore
            pos = betapos
        else:
            pass

    return [score,pos,pssmf]