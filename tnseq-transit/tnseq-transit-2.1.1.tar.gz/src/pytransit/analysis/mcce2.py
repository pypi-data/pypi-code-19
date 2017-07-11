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
import ntpath
import math
import random
import numpy
import scipy.stats
import datetime

import matplotlib.pyplot as plt

import base
import pytransit
import pytransit.transit_tools as transit_tools
import pytransit.tnseq_tools as tnseq_tools
import pytransit.norm_tools as norm_tools
import pytransit.stat_tools as stat_tools



############# GUI ELEMENTS ##################

short_name = "mcce2"
long_name = "MCCE2 test of conditional essentiality between two conditions"
description = """Method for determining conditional essentiality based on mcce2 (i.e. permutation test). Identifies significant changes in mean read-counts for each gene after normalization."""

transposons = ["himar1", "tn5"]
columns = ["Orf","Name","Desc", "Num. of Sites","Obs Mean Ctrl","Obs Mean Exp", "Post Mean Ctrl", "Post Mean Exp", "log2FC", "Std. Dev.", "DE", "prob-L", "prob-0", "prob-R"]

class MCCE2Analysis(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, description, transposons, MCCE2Method, MCCE2GUI, [MCCE2File])



############# FILE ##################

class MCCE2File(base.TransitFile):

    def __init__(self):
        base.TransitFile.__init__(self, "#MCCE2", columns)

    def getHeader(self, path):
        DE=0; poslogfc=0; neglogfc=0;
        for line in open(path):
            if line.startswith("#"): continue
            tmp = line.strip().split("\t")
            if tmp[-1] == "True":
                DE +=1
                if float(tmp[-2]) > 0:
                    poslogfc+=1
                else:
                    neglogfc+=1

        text = """Results:
    Conditionally Essential: %s
        More Essential in Experimental datasets: %s
        Less Essential in Experimental datasets: %s
            """ % (DE, poslogfc, neglogfc)
        return text


    def getMenus(self):
        menus = []
        menus.append(("Display in Track View", self.displayInTrackView))
        menus.append(("Display Histogram", self.displayHistogram))
        return menus

    def displayHistogram(self, displayFrame, event):
            gene = displayFrame.grid.GetCellValue(displayFrame.row, 0)
            filepath = os.path.join(ntpath.dirname(displayFrame.path), transit_tools.fetch_name(displayFrame.path))
            filename = os.path.join(filepath, gene+".png")
            if os.path.exists(filename):
                imgWindow = pytransit.fileDisplay.ImgFrame(None, filename)
                imgWindow.Show()
            else:
                transit_tools.ShowError(MSG="Error Displaying File. Histogram image not found. Make sure results were obtained with the histogram option turned on.")
                print "Error Displaying File. Histogram image does not exist."


        

############# GUI ##################

class MCCE2GUI(base.AnalysisGUI):

    def definePanel(self, wxobj):
        self.wxobj = wxobj
        mcce2Panel = wx.Panel( self.wxobj.optionsWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )

        mcce2Sizer = wx.BoxSizer( wx.VERTICAL )

        mcce2Label = wx.StaticText( mcce2Panel, wx.ID_ANY, u"mcce2 Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcce2Label.Wrap( -1 )
        mcce2Sizer.Add( mcce2Label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        mcce2TopSizer = wx.BoxSizer( wx.HORIZONTAL )

        mcce2TopSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        mcce2LabelSizer = wx.BoxSizer( wx.VERTICAL )

        # Samples Label
        mcce2SampleLabel = wx.StaticText( mcce2Panel, wx.ID_ANY, u"Samples", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcce2SampleLabel.Wrap( -1 )
        mcce2LabelSizer.Add( mcce2SampleLabel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        # Pseudocount Label
        mcce2PseudocountLabel = wx.StaticText(mcce2Panel, wx.ID_ANY, u"Pseudocount", wx.DefaultPosition, wx.DefaultSize, 0)
        mcce2PseudocountLabel.Wrap( -1 )
        mcce2LabelSizer.Add( mcce2PseudocountLabel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        # Norm Label
        mcce2NormLabel = wx.StaticText( mcce2Panel, wx.ID_ANY, u"Normalization", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcce2NormLabel.Wrap( -1 )
        mcce2LabelSizer.Add( mcce2NormLabel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        mcce2TopSizer2.Add( mcce2LabelSizer, 1, wx.EXPAND, 5 )

        mcce2ControlSizer = wx.BoxSizer( wx.VERTICAL )

        # Samples Text
        self.wxobj.mcce2SampleText = wx.TextCtrl( mcce2Panel, wx.ID_ANY, u"10000", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcce2ControlSizer.Add( self.wxobj.mcce2SampleText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        # Pseudocounts
        self.wxobj.mcce2PseudocountText = wx.TextCtrl(mcce2Panel, wx.ID_ANY, u"0.0", wx.DefaultPosition, wx.DefaultSize, 0)
        mcce2ControlSizer.Add( self.wxobj.mcce2PseudocountText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        # Norm Choices
        mcce2NormChoiceChoices = [ u"TTR", u"nzmean", u"totreads", u'zinfnb', u'quantile', u"betageom", u"nonorm" ]
        self.wxobj.mcce2NormChoice = wx.Choice( mcce2Panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, mcce2NormChoiceChoices, 0 )
        self.wxobj.mcce2NormChoice.SetSelection( 0 )
        mcce2ControlSizer.Add( self.wxobj.mcce2NormChoice, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


        # Adaptive Check
        self.wxobj.mcce2AdaptiveCheckBox = wx.CheckBox(mcce2Panel, label = 'Adaptive MCCE2 (Faster)')

        # Histogram Check
        self.wxobj.mcce2HistogramCheckBox = wx.CheckBox(mcce2Panel, label = 'Generate MCCE2 Histograms')

        # Zeros Check
        self.wxobj.mcce2ZeroCheckBox = wx.CheckBox(mcce2Panel, label = 'Include sites with all zeros')


        mcce2TopSizer2.Add( mcce2ControlSizer, 1, wx.EXPAND, 5 )

        mcce2TopSizer.Add( mcce2TopSizer2, 1, wx.EXPAND, 5 )

        

        mcce2Sizer.Add( mcce2TopSizer, 1, wx.EXPAND, 5 )
        mcce2Sizer.Add( self.wxobj.mcce2AdaptiveCheckBox, 0, wx.EXPAND, 5 )
        mcce2Sizer.Add( self.wxobj.mcce2HistogramCheckBox, 0, wx.EXPAND, 5 )
        mcce2Sizer.Add( self.wxobj.mcce2ZeroCheckBox, 0, wx.EXPAND, 5 )

        mcce2Button = wx.Button( mcce2Panel, wx.ID_ANY, u"Run mcce2", wx.DefaultPosition, wx.DefaultSize, 0 )
        mcce2Sizer.Add( mcce2Button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

 
        mcce2Panel.SetSizer( mcce2Sizer )
        mcce2Panel.Layout()
        mcce2Sizer.Fit( mcce2Panel )

        #Connect events
        mcce2Button.Bind( wx.EVT_BUTTON, self.wxobj.RunMethod )

        self.panel = mcce2Panel



########## CLASS #######################

class MCCE2Method(base.DualConditionMethod):
    """   
    mcce2
 
    """
    def __init__(self,
                ctrldata,
                expdata,
                annotation_path,
                output_file,
                normalization="TTR",
                samples=10000,
                adaptive=False,
                doHistogram=False,
                includeZeros=False,
                pseudocount=0.0,
                replicates="Sum",
                LOESS=False,
                ignoreCodon=True,
                NTerminus=0.0,
                CTerminus=0.0, wxobj=None):

        base.DualConditionMethod.__init__(self, short_name, long_name, description, ctrldata, expdata, annotation_path, output_file, normalization=normalization, replicates=replicates, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)

        self.samples = samples
        self.adaptive = adaptive
        self.doHistogram = doHistogram
        self.includeZeros = includeZeros
        self.pseudocount = pseudocount

        self.mu_pi = 50.0
        self.s2_pi = 20
        self.k_pi = 1
        self.nu_pi = 1
        self.mu0 = 0.0
        self.std0 = 1.0
        self.alpha = 0.95

    @classmethod
    def fromGUI(self, wxobj):
        """ """
        #Get Annotation file
        annotationPath = wxobj.annotation
        if not transit_tools.validate_annotation(annotationPath):
            return None

        #Get selected files
        ctrldata = wxobj.ctrlSelected()
        expdata = wxobj.expSelected()
        if not transit_tools.validate_both_datasets(ctrldata, expdata):
            return None

        #Validate transposon types
        if not transit_tools.validate_filetypes(ctrldata+expdata, transposons):
            return None


        #Read the parameters from the wxPython widgets
        ignoreCodon = True
        samples = int(wxobj.mcce2SampleText.GetValue())
        normalization = wxobj.mcce2NormChoice.GetString(wxobj.mcce2NormChoice.GetCurrentSelection())
        replicates="Sum"
        adaptive = wxobj.mcce2AdaptiveCheckBox.GetValue()
        doHistogram = wxobj.mcce2HistogramCheckBox.GetValue()

        includeZeros = wxobj.mcce2ZeroCheckBox.GetValue()
        pseudocount = float(wxobj.mcce2PseudocountText.GetValue())

        NTerminus = float(wxobj.globalNTerminusText.GetValue())
        CTerminus = float(wxobj.globalCTerminusText.GetValue())
        LOESS = False

        #Get output path
        defaultFileName = "mcce2_output_s%d_pc%1.2f" % (samples, pseudocount)
        if adaptive: defaultFileName+= "_adaptive"
        if includeZeros: defaultFileName+= "_iz"
        defaultFileName+=".dat"
    
        defaultDir = os.getcwd()
        output_path = wxobj.SaveFile(defaultDir, defaultFileName)
        if not output_path: return None
        output_file = open(output_path, "w")


        return self(ctrldata,
                expdata,
                annotationPath,
                output_file,
                normalization,
                samples,
                adaptive,
                doHistogram,
                includeZeros,
                pseudocount,
                replicates,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus, wxobj)

    @classmethod
    def fromargs(self, rawargs):

        (args, kwargs) = transit_tools.cleanargs(rawargs)

        ctrldata = args[0].split(",")
        expdata = args[1].split(",")
        annotationPath = args[2]
        output_path = args[3]
        output_file = open(output_path, "w")

        normalization = kwargs.get("n", "TTR")
        samples = int(kwargs.get("s", 10000))
        adaptive = kwargs.get("a", False)
        doHistogram = kwargs.get("h", False)
        replicates = kwargs.get("r", "Sum")
        includeZeros = kwargs.get("iz", False)
        pseudocount = float(kwargs.get("pc", 0.00))
    
        
        LOESS = kwargs.get("l", False)
        ignoreCodon = True
        NTerminus = float(kwargs.get("iN", 0.00))
        CTerminus = float(kwargs.get("iC", 0.00))

        return self(ctrldata,
                expdata,
                annotationPath,
                output_file,
                normalization,
                samples,
                adaptive,
                doHistogram,
                includeZeros,
                pseudocount,
                replicates,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus)



    def Run(self):

        self.transit_message("Starting mcce2 Method")
        start_time = time.time()
       

        if self.doHistogram:
            histPath = os.path.join(os.path.dirname(self.output.name), transit_tools.fetch_name(self.output.name)+"_histograms")
            if not os.path.isdir(histPath):
                os.makedirs(histPath)
        else:
            histPath = ""
 


        Kctrl = len(self.ctrldata)
        Kexp = len(self.expdata)
        #Get orf data
        self.transit_message("Getting Data")
        if self.normalization != "nonorm":
            self.transit_message("Normalizing using: %s" % self.normalization)


        (data, position) = tnseq_tools.get_data(self.ctrldata + self.expdata)
        (normdata, factors) = norm_tools.normalize_data(data, self.normalization, self.ctrldata + self.expdata, self.annotation_path)

        G_A = tnseq_tools.Genes([], self.annotation_path, ignoreCodon=self.ignoreCodon, nterm=self.NTerminus, cterm=self.CTerminus, data=normdata[:Kctrl], position=position)
        G_B = tnseq_tools.Genes([], self.annotation_path, ignoreCodon=self.ignoreCodon, nterm=self.NTerminus, cterm=self.CTerminus, data=normdata[Kctrl:], position=position)



        #MCCE2
        data = []
        N = len(G_A)
        count = 0
        self.progress_range(N)
        for i in range(N):
            count+=1
            if G_A[i].n > 0:
                A_data = G_A[i].reads.flatten()
                B_data = G_B[i].reads.flatten()
            else:
                A_data = numpy.array([0])
                B_data = numpy.array([0])
        

            muA_post, varA_post = self.sample_post(A_data, self.samples, self.mu_pi, self.s2_pi, self.k_pi, self.nu_pi)
            muB_post, varB_post = self.sample_post(B_data, self.samples, self.mu_pi, self.s2_pi, self.k_pi, self.nu_pi)

            varBA_post = varB_post + varA_post
            muA_post[muA_post<=0] = 0.001
            muB_post[muB_post<=0] = 0.001

            logFC_BA_post = numpy.log2(muB_post/muA_post)


            delta_logFC = logFC_BA_post #- scipy.stats.norm.rvs(self.mu0, self.std0, size=self.samples)
            
            #l_BA, u_BA = self.HDI_from_MCMC(logFC_BA_post, self.alpha)
            l_BA, u_BA = self.HDI_from_MCMC(delta_logFC, self.alpha)


            hL = scipy.stats.norm.pdf(delta_logFC, -2, 0.5)
            h0 = scipy.stats.norm.pdf(delta_logFC, 0, 0.5)
            hR = scipy.stats.norm.pdf(delta_logFC, 2, 0.5)

            pL = numpy.mean(hL/(hL+h0+hR))
            p0 = numpy.mean(h0/(hL+h0+hR))
            pR = numpy.mean(hR/(hL+h0+hR))


            bit_BA = not (l_BA <= 0.0 <= u_BA)
 
            if self.doHistogram:
                if len(delta_logFC) > 0:
                    n, bins, patches = plt.hist(delta_logFC, normed=1, facecolor='c', alpha=0.75, bins=100)
                else:
                    n, bins, patches = plt.hist([0], normed=1, facecolor='c', alpha=0.75, bins=100)
                plt.xlabel('Delta Sum')
                plt.ylabel('Probability')
                plt.title('%s - Histogram of Delta Sum' % G_A[i].orf)
                plt.axvline(l_BA, color='r', linestyle='dashed', linewidth=3)
                plt.axvline(u_BA, color='r', linestyle='dashed', linewidth=3)
                plt.axvline(0.00, color='g', linestyle='dashed', linewidth=3)
                plt.grid(True)
                genePath = os.path.join(histPath, G_A[i].orf +".png")
                plt.savefig(genePath)
                plt.clf()


            meanlogFC_BA = numpy.mean(logFC_BA_post)
            stddevlogFC_BA = numpy.std(logFC_BA_post)
            post_meanA = numpy.mean(muA_post)
            post_meanB = numpy.mean(muB_post)
            obs_meanA = numpy.mean(A_data)
            obs_meanB = numpy.mean(B_data)
            sumA = numpy.sum(A_data)
            sumB = numpy.sum(B_data)
            obsdiff = obs_meanB - obs_meanA 
            #data.append([G_A[i].orf, G_A[i].name, G_A[i].desc, G_A[i].n, obs_meanA, obs_meanB, post_meanA, post_meanB, meanlogFC_BA, bit_BA])
            data.append([G_A[i].orf, G_A[i].name, G_A[i].desc, G_A[i].n, obs_meanA, obs_meanB, post_meanA, post_meanB, meanlogFC_BA, stddevlogFC_BA, bit_BA, pL, p0, pR])
            self.progress_update("mcce2", count)
            self.transit_message_inplace("Running MCCE2 Method... %1.1f%%" % (100.0*count/N))


        #
        self.transit_message("") # Printing empty line to flush stdout 
        #self.transit_message("Performing Benjamini-Hochberg Correction")
        data.sort() 
        #qval = stat_tools.BH_fdr_correction([row[-1] for row in data])
       
 
        self.output.write("#MCCE2\n")
        if self.wxobj:
            members = sorted([attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")])
            memberstr = ""
            for m in members:
                memberstr += "%s = %s, " % (m, getattr(self, m))
            self.output.write("#GUI with: norm=%s, samples=%s, pseudocounts=%1.2f, adaptive=%s, histogram=%s, includeZeros=%s, output=%s\n" % (self.normalization, self.samples, self.pseudocount, self.adaptive, self.doHistogram, self.includeZeros, self.output.name))
        else:
            self.output.write("#Console: python %s\n" % " ".join(sys.argv))
        self.output.write("#Control Data: %s\n" % (",".join(self.ctrldata))) 
        self.output.write("#Experimental Data: %s\n" % (",".join(self.expdata))) 
        self.output.write("#Annotation path: %s\n" % (self.annotation_path))
        self.output.write("#Time: %s\n" % (time.time() - start_time))
        self.output.write("#%s\n" % "\t".join(columns))

        for i,row in enumerate(data):
            (orf, name, desc, n, obs_meanA, obs_meanB, meanA, meanB, log2FC, stddev, bit_BA, pL, p0, pR) = row
            self.output.write("%s\t%s\t%s\t%d\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%2.2f\t%5f\t%s\t%1.5f\t%1.5f\t%1.5f\n" % (orf, name, desc, n, obs_meanA, obs_meanB, meanA, meanB, log2FC, stddev, bit_BA, pL, p0, pR))
        self.output.close()

        self.transit_message("Adding File: %s" % (self.output.name))
        self.add_file(filetype="MCCE2")
        self.finish()
        self.transit_message("Finished mcce2 Method") 


    def sample_post(self, data, S, mu0, s20, k0, nu0):
        n = len(data)
        if n > 1:
            s2 = numpy.var(data,ddof=1)
        else:
            s2 = s20
        ybar = numpy.mean(data)
        
        kn = k0+n
        nun = nu0+n
        mun = (k0*mu0 + n*ybar)/float(kn)
        s2n = (1.0/nun) * (nu0*s20 + (n-1)*s2 + (k0*n/float(kn))*numpy.power(ybar-mu0,2))
        
        #s2_post = 1.0/scipy.stats.gamma.rvs(nun/2, scale=s2n*nun/2.0, size=S)
        s2_post = 1.0/scipy.stats.gamma.rvs(nun/2.0, scale=2.0/(s2n*nun), size=S)
        mu_post = scipy.stats.norm.rvs(mun, numpy.sqrt(s2_post/float(kn)), size=S)
        
        #print S, mu0, s20, k0, nu0
        #print n, s2, ybar, kn, nun, mun, s2n
        #print ""
        #for i in range(S):
        #    #print mu_post[i], s2_post[i]
        #    print mu_post[i]
        
        return (mu_post, s2_post)


    def HDI_from_MCMC(self, posterior_samples, credible_mass=0.95):
        # Computes highest density interval from a sample of representative values,
        # estimated as the shortest credible interval
        # Takes Arguments posterior_samples (samples from posterior) and credible mass (normally .95)
        sorted_points = sorted(posterior_samples)
        ciIdxInc = numpy.ceil(credible_mass * len(sorted_points)).astype('int')
        nCIs = len(sorted_points) - ciIdxInc
        ciWidth = [0]*nCIs
        for i in range(0, nCIs):
            ciWidth[i] = sorted_points[i + ciIdxInc] - sorted_points[i]
        HDImin = sorted_points[ciWidth.index(min(ciWidth))]
        HDImax = sorted_points[ciWidth.index(min(ciWidth))+ciIdxInc]
        return(HDImin, HDImax)



    @classmethod
    def usage_string(self):
        return """python %s mcce2 <comma-separated .wig control files> <comma-separated .wig experimental files> <annotation .prot_table or GFF3> <output file> [Optional Arguments]
    
        Optional Arguments:
        -s <integer>    :=  Number of samples. Default: -s 10000
        -n <string>     :=  Normalization method. Default: -n TTR
        -h              :=  Output histogram of the permutations for each gene. Default: Turned Off.
        -a              :=  Perform adaptive mcce2. Default: Turned Off.
        -iz             :=  Include rows with zero accross conditions.
        -pc             :=  Pseudocounts to be added at each site.
        -l              :=  Perform LOESS Correction; Helps remove possible genomic position bias. Default: Turned Off.
        -iN <float>     :=  Ignore TAs occuring at given fraction of the N terminus. Default: -iN 0.0
        -iC <float>     :=  Ignore TAs occuring at given fraction of the C terminus. Default: -iC 0.0
        """ % (sys.argv[0])




if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv)

    #TODO: Figure out issue with inputs (transit requires initial method name, running as script does not !!!!)

    G = MCCE2Method.fromargs(sys.argv[1:])

    G.console_message("Printing the member variables:")   
    G.print_members()

    print ""
    print "Running:"

    G.Run()


