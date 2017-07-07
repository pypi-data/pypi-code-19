import sys
import wx
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


############# Description ##################

short_name = "example"
long_name = "Example method that calculates mean read-counts per gene."
description = "A method made to serve as an example to implementing other methods."
transposons = ["himar1", "tn5"]
columns = ["Orf","Name","Desc","k","n","mean","nzmean"]

############# Analysis Method ##############

class ExampleAnalysis(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, description, transposons, ExampleMethod, ExampleGUI, [ExampleFile])


################## FILE ###################

class ExampleFile(base.TransitFile):

    def __init__(self):
        base.TransitFile.__init__(self, "#Example", columns)

    def getHeader(self, path):
        text = """This is file contains mean counts for each gene. Nzmean is mean accross non-zero sites."""
        return text


################# GUI ##################

class ExampleGUI(base.AnalysisGUI):

    def __init__(self):
        base.AnalysisGUI.__init__(self)

########## METHOD #######################

class ExampleMethod(base.SingleConditionMethod):
    """   
    Example
 
    """
    def __init__(self,
                ctrldata,
                annotation_path,
                output_file,
                replicates="Sum",
                normalization=None,
                LOESS=False,
                ignoreCodon=True,
                NTerminus=0.0,
                CTerminus=0.0, wxobj=None):

        base.SingleConditionMethod.__init__(self, short_name, long_name, description, ctrldata, annotation_path, output_file, replicates=replicates, normalization=normalization, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)




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
        ignoreCodon = True
        NTerminus = float(wxobj.globalNTerminusText.GetValue())
        CTerminus = float(wxobj.globalCTerminusText.GetValue())
        replicates="Sum"
        normalization = None
        LOESS = False

        #Get output path
        defaultFileName = "example_output.dat"
        defaultDir = os.getcwd()
        output_path = wxobj.SaveFile(defaultDir, defaultFileName)
        if not output_path: return None
        output_file = open(output_path, "w")



        return self(ctrldata,
                annotationPath,
                output_file,
                replicates,
                normalization,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus, wxobj)

    @classmethod
    def fromargs(self, rawargs): 
        (args, kwargs) = transit_tools.cleanargs(rawargs)

        print "ARGS:", args
        print "KWARGS:", kwargs

        ctrldata = args[0].split(",")
        annotationPath = args[1]
        outpath = args[2]
        output_file = open(outpath, "w")

        replicates = "Sum"
        normalization = None
        LOESS = False
        ignoreCodon = True
        NTerminus = 0.0
        CTerminus = 0.0

        return self(ctrldata,
                annotationPath,
                output_file,
                replicates,
                normalization,
                LOESS,
                ignoreCodon,
                NTerminus,
                CTerminus)

    def Run(self):

        self.transit_message("Starting Example Method")
        start_time = time.time()
        
        #Get orf data
        self.transit_message("Getting Data")
        G = tnseq_tools.Genes(self.ctrldata, self.annotation_path, ignoreCodon=self.ignoreCodon, nterm=self.NTerminus, cterm=self.CTerminus)

        data = []
        N = len(G)
        count = 0
        self.progress_range(N)
        for gene in G:
            count+=1
            mean = numpy.mean(gene.reads)
            if gene.k == 0:
                nzmean = 0.0
            else:
                nzmean = numpy.sum(gene.reads)/float(gene.k)

            data.append("%s\t%s\t%s\t%s\t%s\t%1.2f\t%1.2f\n" % (gene.orf, gene.name, gene.desc, gene.k, gene.n, mean, nzmean))

            
            self.progress_update("gumbel", count)
            self.transit_message_inplace("Running Example Method... %1.1f%%" % (100.0*count/N))
            
        
        self.output.write("#Example\n")
        if self.wxobj:
            members = sorted([attr for attr in dir(self) if not callable(getattr(self,attr)) and not attr.startswith("__")])
            memberstr = ""
            for m in members:
                memberstr += "%s = %s, " % (m, getattr(self, m))
            self.output.write("#GUI with: ctrldata=%s, annotation=%s, output=%s\n" % (",".join(self.ctrldata), self.annotation_path, self.output))
        else:
            self.output.write("#Console: python %s\n" % " ".join(sys.argv))

        self.output.write("#Data: %s\n" % (",".join(self.ctrldata))) 
        self.output.write("#Annotation path: %s\n" % (",".join(self.ctrldata))) 
        self.output.write("#Time: %s\n" % (time.time() - start_time))
        self.output.write("#%s\n" % "\t".join(columns))

        data.sort()
        for line in data:
            self.output.write(line)
        self.output.close()

        self.transit_message("") # Printing empty line to flush stdout 
        self.transit_message("Adding File: %s" % (self.output.name))
        self.add_file(filetype="Example")
        self.finish()
        self.transit_message("Finished Example Method") 

    @classmethod
    def usage_string(self):
        return """python %s example <comma-separated .wig files> <annotation .prot_table> <output file>""" % (sys.argv[0])


if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv[1:])

    print "ARGS:", args
    print "KWARGS:", kwargs

    G = Example.fromargs(sys.argv[1:])

    print G
    G.console_message("Printing the member variables:")   
    G.print_members()

    print ""
    print "Running:"

    G.Run()


