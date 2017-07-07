import sys

try:
    import wx
    hasWx = True
    #Check if wx is the newest 3.0+ version:
    try:
        from wx.lib.pubsub import pub
        pub.subscribe
        newWx = True
    except AttributeError as e:
        from wx.lib.pubsub import Publisher as pub
        newWx = False
except Exception as e:
    hasWx = False
    newWx = False

import os
import time
import math
import random
import numpy
import scipy.stats
import datetime

import base
import pytransit.transit_tools as transit_tools
import pytransit.tnseq_tools as tnseq_tools
import pytransit.norm_tools as norm_tools
import pytransit.stat_tools as stat_tools

import re


############# GUI ELEMENTS ##################

short_name = "motifhmm"
long_name = "Analysis of genomic regions using a Hidden Markov Model"
description = """Analysis of essentiality in the entire genome using a Hidden Markov Model. Capable of determining regions with different levels of essentiality representing Essential, Growth-Defect, Non-Essential and Growth-Advantage regions.

Reference: DeJesus et al. (2013; BMC Bioinformatics)
"""
transposons = ["himar1"]
columns_sites = ["Location","Read Count", "NP Site", "Probability - ES","Probability - GD","Probability - NE","Probability - GA","State","Gene"]
columns_genes = ["Orf","Name","Description","Total Sites","Num. ES","Num. GD","Num. NE","Num. GA", "Avg. Insertions", "Avg. Reads", "State Call"] 


############# Analysis Method ##############

class MotifHMMAnalysis(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, description, transposons, MotifHMMMethod, MotifHMMGUI, [MotifHMMSitesFile, MotifHMMGenesFile])


################## FILE ###################

class MotifHMMSitesFile(base.TransitFile):

    def __init__(self):
        base.TransitFile.__init__(self, "#MotifHMM - Sites", columns_sites)

    def getHeader(self, path):
        es=0; gd=0; ne=0; ga=0; T=0;
        for line in open(path):
            if line.startswith("#"): continue
            tmp = line.strip().split("\t")
            if len(tmp) == 7:
                col = -1
            else:
                col = -2
            if tmp[col] == "ES": es+=1
            elif tmp[col] == "GD": gd+=1
            elif tmp[col] == "NE": ne+=1
            elif tmp[col] == "GA": ga+=1
            else: print tmp
            T+=1

        text = """Results:
    Essential: %1.1f%%
    Growth-Defect: %1.1f%%
    Non-Essential: %1.1f%%
    Growth-Advantage: %1.1f%%
            """ % (100.0*es/T, 100.0*gd/T, 100.0*ne/T, 100.0*ga/T)
        return text



class MotifHMMGenesFile(base.TransitFile):

    def __init__(self):
        base.TransitFile.__init__(self, "#MotifHMM - Genes", columns_genes)

    def getHeader(self, path):
        es=0; gd=0; ne=0; ga=0; T=0;
        for line in open(path):
            if line.startswith("#"): continue
            tmp = line.strip().split("\t")
            if len(tmp) < 5: continue
            if tmp[-1] == "ES": es+=1
            if tmp[-1] == "GD": gd+=1
            if tmp[-1] == "NE": ne+=1
            if tmp[-1] == "GA": ga+=1

        text = """Results:
    Essential: %s
    Growth-Defect: %s
    Non-Essential: %s
    Growth-Advantage: %s
            """ % (es, gd, ne, ga)

        return text


############# GUI ##################

class MotifHMMGUI(base.AnalysisGUI):

    def definePanel(self, wxobj):
        self.wxobj = wxobj
        motifhmmPanel = wx.Panel( self.wxobj.optionsWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        motifhmmSection = wx.BoxSizer( wx.VERTICAL )

        motifhmmLabel = wx.StaticText( motifhmmPanel, wx.ID_ANY, u"MotifHMM Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        motifhmmLabel.Wrap( -1 )
        motifhmmSection.Add( motifhmmLabel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        motifhmmSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        motifhmmSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        motifhmmLabelSizer = wx.BoxSizer( wx.VERTICAL )
        motifhmmControlSizer = wx.BoxSizer( wx.VERTICAL )


        motifhmmRepLabel = wx.StaticText( motifhmmPanel, wx.ID_ANY, u"Replicates", wx.DefaultPosition, wx.DefaultSize, 0 )
        motifhmmRepLabel.Wrap(-1)
        motifhmmLabelSizer.Add(motifhmmRepLabel, 1, wx.ALL, 5)


        motifhmmRepChoiceChoices = [ u"Sum", u"Mean", "TTRMean" ]
        self.wxobj.motifhmmRepChoice = wx.Choice( motifhmmPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, motifhmmRepChoiceChoices, 0 )
        self.wxobj.motifhmmRepChoice.SetSelection( 2 )

        motifhmmControlSizer.Add(self.wxobj.motifhmmRepChoice, 0, wx.ALL|wx.EXPAND, 5)


        motifhmmSizer2.Add(motifhmmLabelSizer, 1, wx.EXPAND, 5)
        motifhmmSizer2.Add(motifhmmControlSizer, 1, wx.EXPAND, 5)
            
        motifhmmSizer1.Add(motifhmmSizer2, 1, wx.EXPAND, 5 )


        motifhmmSection.Add( motifhmmSizer1, 1, wx.EXPAND, 5 )

        motifhmmButton = wx.Button( motifhmmPanel, wx.ID_ANY, u"Run MotifHMM", wx.DefaultPosition, wx.DefaultSize, 0 )
        motifhmmSection.Add( motifhmmButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        motifhmmPanel.SetSizer( motifhmmSection )
        motifhmmPanel.Layout()
        motifhmmSection.Fit( motifhmmPanel )

        #Connect events
        motifhmmButton.Bind( wx.EVT_BUTTON, self.wxobj.RunMethod )

        self.panel =  motifhmmPanel



########## CLASS #######################

class MotifHMMMethod(base.SingleConditionMethod):
    """   
    MotifHMM
 
    """
    def __init__(self,
                ctrldata,
                annotation_path,
                seq_path,
                output_file,
                estimateA=False,
                replicates="TTRMean",
                normalization=None,
                LOESS=False,
                ignoreCodon=True,
                NTerminus=0.0,
                CTerminus=0.0, wxobj=None):

        base.SingleConditionMethod.__init__(self, short_name, long_name, description, ctrldata, annotation_path, output_file, replicates=replicates, normalization=normalization, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)

        try:
            T = len([1 for line in open(ctrldata[0]).readlines() if not line.startswith("#")])
            self.maxiterations = T*4 + 1
        except:
            self.maxiterations = 100
        self.count = 1
        self.seq_path = seq_path
        self.estimateA = estimateA


    @classmethod
    def fromGUI(self, wxobj):
        """ """

        #Get Annotation file
        annotationPath = wxobj.annotation
        if not transit_tools.validate_annotation(annotationPath):
            return None

        #Get selected files
        ctrldata = wxobj.ctrlSelected()
        if not transit_tools.validate_control_datasets(ctrldata):
            return None

        #Validate transposon types
        if not transit_tools.validate_filetypes(ctrldata, transposons):
            return None


        #Read the parameters from the wxPython widgets
        replicates = wxobj.motifhmmRepChoice.GetString(wxobj.motifhmmRepChoice.GetCurrentSelection()) 
        ignoreCodon = True
        NTerminus = float(wxobj.globalNTerminusText.GetValue())
        CTerminus = float(wxobj.globalCTerminusText.GetValue())
        normalization = None
        LOESS = False

        #Get output path
        name = transit_tools.basename(ctrldata[0])
        defaultFileName = "motifhmm_output.dat"
        defaultDir = os.getcwd()
        output_path = wxobj.SaveFile(defaultDir, defaultFileName)
        if not output_path: return None
        output_file = open(output_path, "w")

        
        seq_path = annotationPath.replace(".prot_table", ".fna")

        estimateA = False

        return self(ctrldata,
                annotationPath,
                seq_path,
                output_file,
                estimateA,
                replicates,
                normalization,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus, wxobj)

    @classmethod
    def fromargs(self, rawargs): 
        (args, kwargs) = transit_tools.cleanargs(rawargs)

        ctrldata = args[0].split(",")
        annotationPath = args[1]
        seq_path = args[2]
        outpath = args[3]
        output_file = open(outpath, "w")

        estimateA = kwargs.get("a", False)
        replicates = kwargs.get("r", "TTRMean")
        normalization = None
        LOESS = kwargs.get("l", False)
        ignoreCodon = True
        NTerminus = float(kwargs.get("iN", 0.0))
        CTerminus = float(kwargs.get("iC", 0.0))

        return self(ctrldata,
                annotationPath,
                seq_path,
                output_file,
                estimateA,
                replicates,
                normalization,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus)

    def Run(self):

        self.transit_message("Starting MotifHMM Method")
        start_time = time.time()
        
        #Get orf data
        self.transit_message("Getting Data")
        (data, position) = tnseq_tools.get_data(self.ctrldata)
        hash = tnseq_tools.get_pos_hash(self.annotation_path)
        rv2info = tnseq_tools.get_gene_info(self.annotation_path)

        ##########
        self.transit_message("Reading Sequence")
        nucseq = tnseq_tools.read_genome(self.seq_path)

        npsite = numpy.zeros(len(position), dtype=int)
        seq_window = 3
        pattern = "[CG]G[CGTA]TA[CGTA]C[CG]"
        for j,pos in enumerate(position):
            ii = pos-1
            seq = nucseq[(ii-seq_window):(ii+2+seq_window)]
            if re.search(pattern, seq):
                npsite[j] = 1
            else:
                npsite[j] = 0
        ##########

        self.transit_message("Combining Replicates as '%s'" % self.replicates)

        O = tnseq_tools.combine_replicates(data, method=self.replicates) + 1 # Adding 1 to because of shifted geometric in scipy

        


        #Parameters
        Nstates = 4
        label = {0:"ES", 1:"GD", 2:"NE",3:"GA"}

        reads = O-1
        reads_nz = sorted(reads[numpy.logical_and(reads !=0, npsite==0)])
        size = len(reads_nz)
        mean_r = numpy.average(reads_nz[:int(0.95 * size)])

        reads_nz_np = sorted(reads[numpy.logical_and(reads !=0, npsite==1) ])
        size_np = len(reads_nz_np)
        mean_r_np = numpy.average(reads_nz_np[:int(0.95 * size_np)])

        mu = numpy.array([1/0.99, 0.01 * mean_r + 2,  mean_r, mean_r*5.0])
        
        #mu = numpy.array([1/0.99, 0.1 * mean_r + 2,  mean_r, mean_r*5.0])
        L = 1.0/mu
        B = [] # Emission Probability Distributions
        #           0    1    2    3    4    5    6
        motif_factors = [1.0, mean_r_np/float(mean_r)]
        for i in range(Nstates):
            B.append([])
            for j,w in enumerate(motif_factors):
                new_mean = max(mu[i]*w, 1.001)
                print "# %d\t%d\t%1.3f\t%1.3f" % (i, j, mu[i], new_mean)
                B[i].append(scipy.stats.geom(1.0/new_mean).pmf)

        pins = self.calculate_pins(O-1)
        pins_obs = sum([1 for rd in O if rd >=2])/float(len(O))
        pnon = 1.0 - pins
        pnon_obs = 1.0 - pins_obs

        for r in range(100):
            if pnon ** r < 0.01: break

       
        PI = numpy.zeros(Nstates) # Initial state distribution
        #PI[0] = 0.7; PI[1:] = 0.3/(Nstates-1);
        PI = numpy.array([0.13, 0.01, 0.85, 0.01])
 
        A = numpy.zeros((Nstates,Nstates))
        a = math.log1p(-B[int(Nstates/2)][0](1)**r)
        b = r*math.log(B[int(Nstates/2)][0](1)) + math.log(1.0/3) # change to Nstates-1?
        for i in range(Nstates):
            A[i] = [b]*Nstates
            A[i][i] = a

        A = numpy.exp(A) * PI
        A = A/A.sum(1)[:,numpy.newaxis]
        A = numpy.log(A)

        self.progress_range(self.maxiterations)
       
        #print npsite 
        self.output.write("#MotifHMM - Sites\n")
        self.output.write("# Tn-MotifHMM\n")
        self.output.write("# State Emission Parameters:\n")
        for np in range(2):
            self.output.write("# %d    %s\n" % (np, "   ".join(["%s: %1.4f" % (label[i], 1.0/B[i][np](1)) for i in range(Nstates)])))
        
        ##################
        ### BAUM WELCH ###
        #(A, B, PI, L, iternum) = self.baum_welch(numpy.exp(A), B, PI, O, npsite, max_iterations = 50)
        ##################

        ###############
        ### VITERBI ###
        (Q_opt, delta, Q) = self.viterbi(A, B, PI, O, npsite)
        ###############

        ##################
        ### ALPHA PASS ###
        (log_Prob_Obs, alpha, C) = self.forward_procedure(numpy.exp(A), B, PI, O, npsite)
        ##################

        #################
        ### BETA PASS ###
        beta = self.backward_procedure(numpy.exp(A), B, PI, O, npsite, C)
        #################



        T = len(O); total=0; state2count = dict.fromkeys(range(Nstates),0)
        for t in xrange(T):
            state = Q_opt[t]
            state2count[state] +=1
            total+=1
 
            
       
        self.output.write("#MotifHMM - Sites\n")
        self.output.write("# Tn-MotifHMM\n")
 
        if self.wxobj:
            members = sorted([attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")])
            memberstr = ""
            for m in members:
                memberstr += "%s = %s, " % (m, getattr(self, m))
            self.output.write("#GUI with: ctrldata=%s, annotation=%s, output=%s\n" % (",".join(self.ctrldata), self.annotation_path, self.output))
        else:
            self.output.write("#Console: python %s\n" % " ".join(sys.argv))
       
        self.output.write("# \n")
        self.output.write("# Mean:\t%2.2f\n" % (numpy.average(reads_nz)))
        self.output.write("# Median:\t%2.2f\n" % numpy.median(reads_nz))
        self.output.write("# pins (obs):\t%f\n" % pins_obs)
        self.output.write("# pins (est):\t%f\n" % pins)
        self.output.write("# Run length (r):\t%d\n" % r)
        self.output.write("# State means:\n")
        self.output.write("#    %s\n" % "   ".join(["%s: %8.4f" % (label[i], mu[i]) for i in range(Nstates)]))
        self.output.write("# Self-Transition Prob:\n")
        self.output.write("#    %s\n" % "   ".join(["%s: %2.4e" % (label[i], A[i][i]) for i in range(Nstates)]))
        self.output.write("# State Emission Parameters (theta):\n")
        #self.output.write("#    %s\n" % "   ".join(["%s: %1.4f" % (label[i], L[i]*(1.0/motif_factors[1])) for i in range(Nstates)]))
        for np in range(2):
            self.output.write("# %d    %s\n" % (np, "   ".join(["%s: %1.4f" % (label[i], 1.0/B[i][np](1)) for i in range(Nstates)])))
        self.output.write("# State Distributions:\n")
        self.output.write("#    %s\n" % "   ".join(["%s: %2.2f%%" % (label[i], state2count[i]*100.0/total) for i in range(Nstates)]))
        self.output.write("# Motif Factor:")
        self.output.write("#    %s\n" % "   ".join(["%s: %1.2f" % (i,w) for (i,w) in enumerate(motif_factors)]))

        states = [int(Q_opt[t]) for t in range(T)]
        last_orf = ""
        for t in xrange(T):
            s_lab = label.get(states[t], "Unknown State")
            gamma_t = (alpha[:,t] * beta[:,t])/numpy.sum(alpha[:,t] * beta[:,t])
            genes_at_site = hash.get(position[t], [""])
            genestr = ""
            if not (len(genes_at_site) == 1 and not genes_at_site[0]):
                genestr = ",".join(["%s_(%s)" % (g,rv2info.get(g, "-")[0]) for g in genes_at_site])

            self.output.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (int(position[t]), int(O[t])-1, npsite[t], "\t".join(["%-9.2e" % g for g in gamma_t]), s_lab, genestr))

        self.output.close()

        self.transit_message("") # Printing empty line to flush stdout 
        self.transit_message("Finished MotifHMM - Sites Method")
        self.transit_message("Adding File: %s" % (self.output.name))
        self.add_file(filetype="MotifHMM - Sites")
        
        #Gene Files
        self.transit_message("Creating MotifHMM Genes Level Output")
        genes_path = ".".join(self.output.name.split(".")[:-1]) + "_genes." + self.output.name.split(".")[-1] 

        tempObs = numpy.zeros((1,len(O)))
        tempObs[0,:] = O - 1
        self.post_process_genes(tempObs, position, numpy.array(states), genes_path)


        self.transit_message("Adding File: %s" % (genes_path))
        self.add_file(path=genes_path, filetype="MotifHMM - Genes")
        self.finish()
        self.transit_message("Finished MotifHMM Method") 


    @classmethod
    def usage_string(self):
        return """python %s motifhmm <comma-separated .wig files> <annotation .prot_table> <sequence .fna> <output file>

        Optional Arguments:
            -r <string>     :=  How to handle replicates. Sum, Mean, TTRMean. Default: -r TTRMean
            -a              :=  Estimate the transition probability.
            -l              :=  Perform LOESS Correction; Helps remove possible genomic position bias. Default: Off.
            -iN <float>     :=  Ignore TAs occuring at given fraction of the N terminus. Default: -iN 0.0
            -iC <float>     :=  Ignore TAs occuring at given fraction of the C terminus. Default: -iC 0.0
        """ % (sys.argv[0])



    def forward_procedure(self, A, B, PI, O, NP):
        T = len(O)
        N = len(B)
        alpha = numpy.zeros((N,  T))
        C = numpy.zeros(T)

        alpha[:,0] = PI * [B[i][NP[0]](O[0]) for i in range(N)]

        C[0] = 1.0/numpy.sum(alpha[:,0])
        alpha[:,0] = C[0] * alpha[:,0]

        for t in xrange(1, T):
            #B[i](O[:,t])  =>  numpy.prod(B[i](O[:,t]))
            #b_o = numpy.array([numpy.prod(B[i](O[:,t])) for i in range(N)])
            b_o = [B[i][NP[t]](O[t]) for i in range(N)]
        
            alpha[:,t] = numpy.dot(alpha[:,t-1], A) * b_o
            
            C[t] = numpy.nan_to_num(1.0/numpy.sum(alpha[:,t]))
            alpha[:,t] = numpy.nan_to_num(alpha[:,t] * C[t])

            if numpy.sum(alpha[:,t]) == 0:
                alpha[:,t] = 0.0000000000001
           
            self.progress_update("motifhmm", self.count)
            self.transit_message_inplace("Running MotifHMM Method... %1.1f%%" % (100.0*self.count/self.maxiterations))
            self.count+=1
            #print t, O[:,t], alpha[:,t]

        log_Prob_Obs = - (numpy.sum(numpy.log(C)))
        return(( log_Prob_Obs, alpha, C ))

    def backward_procedure(self, A, B, PI, O, NP, C=None):

        N = len(B)
        T = len(O)
        beta = numpy.zeros((N,T))

        beta[:,T-1] = 1.0
        if C!=None: beta[:,T-1] = beta[:,T-1] * C[T-1]

        for t in xrange(T-2, -1, -1):
            #B[i](O[:,t])  =>  numpy.prod(B[i](O[:,t]))
            #b_o = numpy.array([numpy.prod(B[i](O[:,t])) for i in range(N)])
            b_o = [B[i][NP[t]](O[t]) for i in range(N)]

            beta[:,t] = numpy.nan_to_num(numpy.dot(A, (b_o * beta[:,t+1] ) ))

            if sum(beta[:,t]) == 0:
                beta[:,t] = 0.0000000000001

            if C!=None:
                beta[:,t] = beta[:,t] * C[t]

            self.progress_update("motifhmm", self.count)
            self.transit_message_inplace("Running MotifHMM Method... %1.1f%%" % (100.0*self.count/self.maxiterations))
            self.count+=1

        return(beta)



    def viterbi(self, A, B, PI, O, NP):
        N=len(B)
        T = len(O)
        delta = numpy.zeros((N, T))

        b_o = [B[i][NP[0]](O[0]) for i in range(N)]
        delta[:,0] = numpy.log(PI) + numpy.log(b_o)

        Q = numpy.zeros((N, T))

        for t in xrange(1, T):
            b_o = [B[i][NP[t]](O[t]) for i in range(N)]
            #nus = delta[:, t-1] + numpy.log(A)
            nus = delta[:, t-1] + A
            delta[:,t] = nus.max(1) + numpy.log(b_o)
            Q[:,t] = nus.argmax(1)
            self.progress_update("motifhmm", self.count)
            self.transit_message_inplace("Running MotifHMM Method... %1.1f%%" % (100.0*self.count/self.maxiterations))
            self.count+=1

        Q_opt = [numpy.argmax(delta[:,T-1])]
        for t in xrange(T-2, -1, -1):
            Q_opt.insert(0, Q[Q_opt[0],t+1])
            self.progress_update("motifhmm", self.count)
            self.transit_message_inplace("Running MotifHMM Method... %1.1f%%" % (100.0*self.count/self.maxiterations))
            self.count+=1

        self.progress_update("motifhmm", self.count)
        self.transit_message_inplace("Running MotifHMM Method... %1.1f%%" % (100.0*self.count/self.maxiterations))

        return((Q_opt, delta, Q))



    def baum_welch(self, A, B, PI, O, NP, max_iterations = 20):

        Nstates = 4
        label = {0:"ES", 1:"GD", 2:"NE",3:"GA"}
        N = len(B)
        T = len(O)
        alpha = numpy.zeros((N, T))
        beta = numpy.zeros((N, T))
        G_i = numpy.zeros((N,T))
        E_ij = numpy.zeros((N,N,T))
    
        logProb = 100
        oldLogProb = float('-inf')
        iternum = 0
        while True:
    
            G_i = numpy.zeros((N,T))
            E_ij = numpy.zeros((N,N,T))
    
            #alpha pass
            log_Prob_Obs, alpha, C = self.forward_procedure(A, B, PI, O, NP)
            #beta pass
            beta = self.backward_procedure(A, B, PI, O, NP, C)

            # Calculate the Gammas
            for t in xrange(T-1):
                denom = numpy.sum([numpy.sum([alpha[i,t] * A[i,j] * B[j][NP[t+1]](O[t+1]) * beta[j,t+1] for j in range(N)]) for i in range(N)])

                for i in xrange(N):
                    E_ij[i,:,t] = [(alpha[i,t] * A[i,j] * B[j][NP[t+1]](O[t+1]) * beta[j,t+1])/denom for j in range(N)]
                    G_i[i,t] = sum(E_ij[i,:,t])



            logProb = 0
            for t in xrange(T):
                logProb = logProb + numpy.log(C[t])
            logProb = -1*logProb
    
    
            if (iternum < max_iterations) and (logProb > oldLogProb):
                oldLogProb = logProb
            else:
                return(A,B,PI, L, iternum)
    
    
            #Re-estimate PI
            PI = G_i[:,0]
    
            #Re-estimate A
            if self.estimateA:
                for i in xrange(N):
                    for j in xrange(N):
                        #numer = 0; denom = 0;
                        #for t in xrange(0, T-1):
                        #    numer = numer + E_ij[i,j,t]
                        #    denom = denom + G_i[i,t]
                        numer = sum(E_ij[i,j,0:T-1])
                        denom = sum(G_i[i,0:T-1])
                        A[i,j] = numer/denom
    
    
            #Re-estimate B
            for s in range(N):
                for np in range(2):
                    ii = NP == np
                    L = 1.0/(numpy.sum(G_i[s,ii]*O[ii])/float(numpy.sum(G_i[s,ii])))
                    B[s][np] = scipy.stats.geom(L).pmf

                #L[1] = 1.0/(numpy.sum(G_i[1,0:T]*O[0:T])/float(numpy.sum(G_i[1,0:T])))
                #B[1] = scipy.stats.geom(L[1]).pmf
                #L[0] = 1.0/(sum(G_i[0,0:T]*O[0:T])/float(sum(G_i[0,0:T])))
                #B[0] = scipy.stats.geom(L[0]).pmf
    
    
            logProb = 0
            for t in xrange(T):
                logProb = logProb + numpy.log(C[t])
            logProb = -1*logProb
    
            iternum +=1
            print "Iteration", iternum
            print "#i=%d   logProb=%f" % (iternum, logProb)
            print "A:"
            print A
            print "PI:", PI
            print ""
            for np in range(2):
                print "# %d    %s" % (np, "   ".join(["%s: %1.4f" % (label[i], 1.0/B[i][np](1)) for i in range(Nstates)]))



        return(None)




    def calculate_pins(self, reads):
        non_ess_reads = []
        temp = []
        for rd in reads:

            if rd >=1:
                if len(temp) < 10: non_ess_reads.extend(temp)
                non_ess_reads.append(rd)
                temp = []
            else:
                temp.append(rd)

        return(sum([1 for rd in non_ess_reads if rd >= 1])/float(len(non_ess_reads)) )



    def post_process_genes(self, data, position, states, output_path):

        output = open(output_path, "w")
        pos2state = dict([(position[t],states[t]) for t in range(len(states))])
        #theta = numpy.mean(data > 0)
        pnon = numpy.mean(states == 0)
        pins = 1.0 - pnon
        theta = numpy.mean(data > 0)
        G = tnseq_tools.Genes(self.ctrldata, self.annotation_path, data=data, position=position, ignoreCodon=False)

        num2label = {0:"ES", 1:"GD", 2:"NE", 3:"GA"}
        output.write("#MotifHMM - Genes\n")        
        for gene in G:
            
            reads_nz = [c for c in gene.reads.flatten() if c > 0]
            avg_read_nz = 0
            if len(reads_nz) > 0:
                avg_read_nz = numpy.average(reads_nz)

            # State
            genestates = [pos2state[p] for p in gene.position]
            statedist = {}
            for st in genestates:
                if st not in statedist: statedist[st] = 0
                statedist[st] +=1

            genestates = numpy.array(genestates)
            # State counts
            n0 = statedist.get(0, 0); n1 = statedist.get(1, 0);
            n2 = statedist.get(2, 0); n3 = statedist.get(3, 0);

            esrun = tnseq_tools.maxrun(genestates, item=0)
            #print gene, esrun, pnon, pins
            if gene.n > 0:
                E = tnseq_tools.ExpectedRuns(gene.n,   1.0 - pins)
                V = tnseq_tools.VarR(gene.n,   1.0 - pins)
                B = 1.0/math.log(1.0/pnon)
                u = math.log(gene.n*pins, 1.0/pnon)
                gumbel_pval = 1.0 - tnseq_tools.GumbelCDF(esrun, u, B)
                binom_pval =  scipy.stats.binom.cdf(gene.k, gene.n, theta)
                #
                maxstate = max([(statedist.get(s, 0), num2label[s]) for s in [0, 1, 2, 3]])[1]

                temp = numpy.ones(gene.n)
                temp[genestates == 1] = 0
                temp[genestates == 2] = 0
                temp[genestates == 3] = 0
                NEruns =  tnseq_tools.runs(temp)
                NEruns_index = tnseq_tools.runindex(NEruns)
                goodSpan = False
                for r,ii in zip(NEruns, NEruns_index):
                    if r ==0: continue
                    if gene.position[ii+r-1] + 2 - gene.position[ii] >= 200:
                        goodSpan = True

                if gene.t < 15:
                    S = "Uncertain"
                elif gumbel_pval < 0.05 and goodSpan:
                    S = "ESD"
                elif gene.n < 4 and binom_pval < 0.05:
                    S = "ES"
                elif gene.n < 4 and gene.k == 0:
                    S = "Uncertain"
                else:
                    S = maxstate
            else:
                E = 0.0
                V = 0.0
                S = "Uncertain"
            output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%1.4f\t%1.2f\t%s\n" % (gene.orf, gene.name, gene.desc, gene.n, n0, n1, n2, n3, gene.theta(), avg_read_nz, S))

        output.close()



    




if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv)

    print "ARGS:", args
    print "KWARGS:", kwargs

    G = MotifHMMMethod.fromargs(sys.argv[1:])

    G.console_message("Printing the member variables:")   
    G.print_members()

    print ""
    print "Running:"

    G.Run()


