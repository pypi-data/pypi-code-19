
import sys
import wx
#Check if wx is the newest 3.0+ version:
try:
    from wx.lib.pubsub import pub
    pub.subscribe
    newWx = True
except AttributeError as e:
    from wx.lib.pubsub import Publisher as pub
    newWx = False

import pytransit
import pytransit.transit_tools as transit_tools
import pytransit.transit_gui as transit_gui
import pytransit.analysis

method_wrap_width = 250
methods = pytransit.analysis.methods


wildcard = "Python source (*.py)|*.py|" \
            "All files (*.*)|*.*"
transit_prefix = "[TRANSIT]"


def main(args=None):
    #If no arguments, show GUI:
    if len(sys.argv) == 1:

        transit_tools.transit_message("Running in GUI Mode")

        app = wx.App(False)

        #create an object of CalcFrame
        frame = transit_gui.TnSeekFrame(None)
        #show the frame
        frame.Show(True)
        #start the applications
        app.MainLoop()

    else:
        method_name = sys.argv[1]
        if method_name not in methods:
            print "Error: The '%s' method is unknown." % method_name
            print "Please use one of the known methods (or see documentation to add a new one):"
            for m in methods:
                print "\t - %s" % m
            print "Usage: python %s <method>" % sys.argv[0]
        else:
            methodobj = methods[method_name].method.fromconsole()
            methodobj.Run()



if __name__ == "__main__":
    main()


