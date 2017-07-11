#!/usr/bin/env python
# -*- coding: ascii -*-
from __future__ import absolute_import
from __future__ import print_function

r"""
A tkinter code that helps users digitize curves from plot images.

If a 2D plot is available only on paper or an image file, but the user needs the x,y data pairs in digital form, DigiPlot will help to create those x,y data pairs.


DigiPlot
Copyright (C) 2017  Charlie Taylor

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

-----------------------

"""
import os
here = os.path.abspath(os.path.dirname(__file__))
import sys
if sys.version_info < (3,):
    from future import standard_library
    standard_library.install_aliases()
    import tkFileDialog
    import tkMessageBox
    import tkSimpleDialog
else:
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    import tkinter.simpledialog as tkSimpleDialog

#  Need to redefine object here
# pylint: disable=W0622, W0703, W0612, W0403, C0330
from builtins import object

from tkinter import Menu, StringVar, Label, SUNKEN, SW, X, BOTTOM, Frame, NE, NW,\
    BOTH, TOP, Button, LEFT, SE, Scrollbar, VERTICAL, Text, RIGHT, Y, END, Tk,\
    Canvas, Listbox, Entry, N, S, E, W, YES, Toplevel, ALL, Checkbutton

from PIL import Image, ImageTk
from digiplot.plot_area import PlotArea, HAS_IMAGEGRAB
from digiplot.realign_Dialog import _ReAlign

# for multi-file projects see LICENSE file for authorship info
# for single file projects, insert following information
__author__ = 'Charlie Taylor'
__copyright__ = 'Copyright (c) 2016 Charlie Taylor'
__license__ = 'GPL-3'
exec( open(os.path.join( here,'_version.py' )).read() )  # creates local __version__ variable
__email__ = "cet@appliedpython.com"
__status__ = "3 - Alpha" # "3 - Alpha", "4 - Beta", "5 - Production/Stable"


class Point( object ):
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        
    def get_str(self):
        return '%g, %g'%(self.x, self.y)
    
    def set_xy(self, x, y):
        self.x = x
        self.y = y
    
    def get_xy(self):
        return self.x, self.y


class DigiPlot(object):
    """A tkinter code that helps users digitize curves from plot images."""

    def __init__(self, master):
        
        self.initComplete = 0
        
        self.frame = Frame(master, width=555, height=546)
        self.frame.pack(fill=BOTH, expand=YES)
        self.master = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1

        # bind master to <Configure> in order to handle any resizing, etc.
        # postpone self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Enter>', self.bindConfigure)
        #self.master.bind('<Button-1>', self.bindConfigure)
        master.bind('<Escape>', self.Clear_Pending_Actions)
        
        
        self.master.title("DigiPlot")
        
        # ======================  Make a Widget Frame =============
        
        # ------------ left_frame -----------------
        left_frame = Frame(self.frame)
        left_frame.pack(fill=Y,  side=LEFT, anchor=NW)

        #self.Defined_Points_Label = Label(left_frame,text="Defined Points", width="15")
        #self.Defined_Points_Label.pack(anchor=NW, side=TOP)
        
        left_frame_ch1 = Frame(left_frame)
        left_frame_ch1.pack(fill=Y,  side=TOP, anchor=NW)
        
        self.Del_Button = Button(left_frame_ch1,text="Delete Point", width="10")
        self.Del_Button.pack(side=LEFT, anchor=NW)
        self.Del_Button.bind("<ButtonRelease-1>", self.Del_Button_Click)
        
        self.Sort_Button = Button(left_frame_ch1,text="Sort By X", width="10")
        self.Sort_Button.pack(side=LEFT, anchor=NW)
        self.Sort_Button.bind("<ButtonRelease-1>", self.Sort_Button_Click)
        
        # Listbox for points
        lbframe = Frame( left_frame )
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Defined_Points_Listbox = Listbox(lbframe, width="40", selectmode="single", 
                                              yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Defined_Points_Listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y, expand=YES)
        self.Defined_Points_Listbox.pack(side=LEFT, fill=Y, expand=YES)
        lbframe.pack(fill=Y, anchor=W, side=TOP, expand=YES)
        self.Defined_Points_Listbox_frame = lbframe
        self.Defined_Points_Listbox.bind("<ButtonRelease-1>", self.Defined_Points_Listbox_Click)
        

        # -------------------- right_frame -------------------
        # Canvas for plot
        right_frame = Frame(self.frame)
        right_frame.pack(fill=BOTH, expand=YES, side=LEFT, anchor=NE)
        
        right_frame_ch1 = Frame(right_frame)
        right_frame_ch1.pack(fill=Y,  side=TOP, anchor=NW)

        self.GreyScale_Checkbutton = Checkbutton(right_frame_ch1,text="Grey Scale Plot", width="15")
        self.GreyScale_Checkbutton.pack(side=LEFT, anchor=W)
        self.GreyScale_Checkbutton_StringVar = StringVar()
        self.GreyScale_Checkbutton_StringVar.set('yes')        
        self.GreyScale_Checkbutton.configure(variable=self.GreyScale_Checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.GreyScale_Checkbutton_StringVar_traceName = self.GreyScale_Checkbutton_StringVar.trace_variable("w", self.GreyScale_Checkbutton_StringVar_Callback)

        self.LogX_Checkbutton = Checkbutton(right_frame_ch1,text="Log X Scale", width="15")
        self.LogX_Checkbutton.pack(side=LEFT, anchor=W)
        self.LogX_Checkbutton_StringVar = StringVar()
        self.LogX_Checkbutton_StringVar.set('no')        
        self.LogX_Checkbutton.configure(variable=self.LogX_Checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.LogX_Checkbutton_StringVar_traceName = self.LogX_Checkbutton_StringVar.trace_variable("w", self.LogX_Checkbutton_StringVar_Callback)

        self.LogY_Checkbutton = Checkbutton(right_frame_ch1,text="Log Y Scale", width="15")
        self.LogY_Checkbutton.pack(side=LEFT, anchor=W)
        self.LogY_Checkbutton_StringVar = StringVar()
        self.LogY_Checkbutton_StringVar.set('no')        
        self.LogY_Checkbutton.configure(variable=self.LogY_Checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.LogY_Checkbutton_StringVar_traceName = self.LogY_Checkbutton_StringVar.trace_variable("w", self.LogY_Checkbutton_StringVar_Callback)

        
        self.MakeBigger_Button = Button(right_frame_ch1,text="+", width="5")
        self.MakeBigger_Button.pack(side=LEFT)
        self.MakeBigger_Button.bind("<ButtonRelease-1>", self.MakeBigger_Button_Click)

        self.MakeSmaller_Button = Button(right_frame_ch1,text="-", width="5")
        self.MakeSmaller_Button.pack(side=LEFT)
        self.MakeSmaller_Button.bind("<ButtonRelease-1>", self.MakeSmaller_Button_Click)

        self.MakeFit_Button = Button(right_frame_ch1,text="Fit", width="5")
        self.MakeFit_Button.pack(side=LEFT)
        self.MakeFit_Button.bind("<ButtonRelease-1>", self.MakeFit_Button_Click)

        self.Plot_Canvas = Canvas(right_frame,width="600", height="600")
        self.Plot_Canvas.pack(fill=BOTH, expand=YES, side=TOP)
        self.Plot_Canvas.bind("<ButtonRelease-1>", self.Plot_Canvas_Click)
        self.Plot_Canvas.bind("<Configure>", self.Plot_Canvas_Resize)

        
        # Mouse Wheel for Zooming in and out
        self.master.bind("<MouseWheel>",self.MouseWheelHandler) # Windows Binding
        self.master.bind("<Button-4>",self.MouseWheelHandler) # Linux Binding
        self.master.bind("<Button-5>",self.MouseWheelHandler) # Linux Binding        
        self.Plot_Canvas.bind("<Button-3>", self.Canvas_Begin_End_Drag)
        self.Plot_Canvas.bind("<B3-Motion>", self.Canvas_Drag_Axes)
        self.Plot_Canvas.bind("<Motion>", self.Canvas_Hover)
        self.Plot_Canvas.bind("<Enter>", self.Canvas_Enter)
        self.Plot_Canvas.bind("<Leave>", self.Canvas_Leave)
        
        if HAS_IMAGEGRAB:
            self.Plot_Canvas.bind('<Control-v>', self.menu_Paste_Clipboard_Image_event)

        # ======================  End of Widget Frame =============
        # make a Status Bar
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(self.master, textvariable=self.statusMessage, bd=1, relief=SUNKEN)
        self.statusbar.pack(anchor=SW, fill=X, side=BOTTOM)
        
        self.statusMessage.set("Welcome to temp")
        
        self.menuBar = Menu(self.master, relief = "raised", bd=2)

        top_File = Menu(self.menuBar, tearoff=0)

        top_File.add("command", label = "Read Image File", command = self.menu_File_Import_Image)
        if HAS_IMAGEGRAB:
            top_File.add("command", label = "Paste Clipboard Image", command = self.menu_Paste_Clipboard_Image)
        top_File.add("command", label = "Save Points to CSV", command = self.menu_File_Save_CSV)
        self.menuBar.add("cascade", label="File", menu=top_File)


        top_Clipboard = Menu(self.menuBar, tearoff=0)
        top_Clipboard.add("command", label = "Comma Separated (CSV)", command = self.menu_Clipboard_Comma)
        top_Clipboard.add("command", label = "Tab Separated (Excel)", command = self.menu_Clipboard_Tab)
        self.menuBar.add("cascade", label="Data-To-Clipboard", menu=top_Clipboard)

        top_Anchor_Plot = Menu(self.menuBar, tearoff=0)
        top_Anchor_Plot.add("command", label = "Set Xmin", command = self.menu_Anchor_Plot_Set_Xmin)
        top_Anchor_Plot.add("command", label = "Set Xmax", command = self.menu_Anchor_Plot_Set_Xmax)
        top_Anchor_Plot.add("command", label = "Set Ymin", command = self.menu_Anchor_Plot_Set_Ymin)
        top_Anchor_Plot.add("command", label = "Set Ymax", command = self.menu_Anchor_Plot_Set_Ymax)
        top_Anchor_Plot.add("command", label = "Set All", command = self.menu_Anchor_Plot_Set_All)
        self.menuBar.add("cascade", label="Anchor-Plot", menu=top_Anchor_Plot)


        top_Fix = Menu(self.menuBar, tearoff=0)
        top_Fix.add("command", label = "4 Point Axes Align", command = self.menu_Fix_Image_4Pt)
        top_Fix.add("command", label = "3 Point Axes Align", command = self.menu_Fix_Image_3Pt)
        self.menuBar.add("cascade", label="Fix-Image-Alignment", menu=top_Fix)


        top_View = Menu(self.menuBar, tearoff=0)
        top_View.add("command", label = "Fit Image", command = self.menu_Fit_Image)
        self.menuBar.add("cascade", label="View", menu=top_View)

        
        self.menuBar.add("command", label = "Help", command = self.menu_Help)

        top_Exit = Menu(self.menuBar, tearoff=0)
        top_Exit.add("command", label = "Quit", command = self.menu_Exit_Quit)
        self.menuBar.add("cascade", label="Exit", menu=top_Exit)

        self.master.config(menu=self.menuBar)
        
        self.master.sizefrom(who='program')
        self.master.resizable(True, True) # Linux may not respect this

        self.Plot_Canvas.focus_set()
            
        self.PA = PlotArea(w_canv=600, h_canv=600) # will hold PlotArea() when it is opened
        self.pointL = []
        self.has_some_new_data = False
        
        self.is_dragging = False
        self.last_right_click_pos = (0,0) # any action calling Canvas_Find_Closest will set

        self.last_hover_pos = (0,0)
        self.in_canvas = False

        self.canvas_tooltip_num = 0
        self.canvas_tooltip_inc = 1 # set > 1 to skip some options
        self.canvas_tooltip_strL = ['Left Click on X minimum.', 'Left Click on X maximum',
                                    'Left Click on Y minimum.', 'Left Click on Y maximum']
                                    
        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None] # only useful if all None's replaced
        self.distortion_flag = False

        master.protocol('WM_DELETE_WINDOW', self.cleanupOnQuit)
        
        # if image file given, then import it.
        if len( sys.argv ) == 2:
            fName = sys.argv[1]
            flo = fName.lower()
            if flo.endswith('.png') or flo.endswith('.jpg') or flo.endswith('.jpeg') or flo.endswith('.gif'):
                if os.path.isfile( fName ): # if file exists, read it as a definition file
                    if self.PA.open_img_file( fName ):
                        self.Initialize_Image_State()
                        self.statusMessage.set('file "%s" opened'%fName)
                        self.master.title("DigiPlot: %s"%fName)
                    else:
                        self.statusMessage.set('file "%s" failed to open'%fName)
                        
                else:
                    self.statusMessage.set('file "%s" not found'%fName)
        
        
        
        # give a few milliseconds before calling bindConfigure
        self.master.after(100, lambda: self.bindConfigure(None))
            
    def Initialize_Image_State(self):
        
        # Clear entries in Listbox
        self.Defined_Points_Listbox.delete(0, END)
        self.LogX_Checkbutton_StringVar.set('no')        
        self.LogY_Checkbutton_StringVar.set('no')        
        
        self.pointL = []
        self.has_some_new_data = False
        
        self.is_dragging = False
        self.last_right_click_pos = (0,0) # any action calling Canvas_Find_Closest will set
        
        self.canvas_tooltip_num = 0
        self.canvas_tooltip_inc = 1 # set > 1 to skip some options
        
                                    
        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None] # only useful if all None's replaced
        self.distortion_flag = False
        
        self.PA.zoom_to_quadrant(qname='LL')
        self.plot_points()
        
    def Clear_Pending_Actions(self, event):
        self.statusMessage.set("Cleared pending actions.")
        self.is_dragging = False
        self.last_right_click_pos = (0,0) # any action calling Canvas_Find_Closest will set
        
        self.canvas_tooltip_num = 1000
        self.canvas_tooltip_inc = 1 
        
        self.plot_points()
        
        
    def cleanupOnQuit(self):
        
        if (len(self.pointL)>0) and self.has_some_new_data:
            if self.AskYesNo( title='Exit WITHOUT Saving Data?', \
                              message='Exit WITHOUT Saving Data??\n'+\
                              '(Hit "Yes" to DISCARD your data.)'):
                try:
                    self.master.destroy()
                except:
                    pass
                sys.exit(1)
        else:
            try:
                self.master.destroy()
            except:
                pass
            sys.exit(1)

    def bindConfigure(self, event):
        if not self.initComplete:
            self.initComplete = 1
            #self.Plot_Canvas.config(width=600, height=500)
            self.master.bind("<Configure>", self.Master_Configure)
            
            self.PA.zoom_to_quadrant(qname='LL')
            self.plot_points()


    def Master_Configure(self, event):
        
        if event.widget != self.master:
            if self.w > -1:
                return
        self.master.unbind('<Enter>')
            
        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        
        if (self.x, self.y, self.w, self.h) == (-1,-1,-1,-1):
            self.x, self.y, self.w, self.h = x,y,w,h
            self.lb_init_width  = int(self.Defined_Points_Listbox_frame.winfo_width() )
            self.lb_init_height = int(self.Defined_Points_Listbox_frame.winfo_height())
            self.w_init = w
            self.h_init = h
            self.w_canv_init = int( self.Plot_Canvas.winfo_width() )

        if self.w!=w or self.h!=h:
            #print( "Master reconfigured... make resize adjustments")
            self.w=w
            self.h=h
        
        #print('self.frame.w =', self.frame.winfo_width())
        self.frame.update()
        #try:
        #    self.frame.update_idletasks()
        #except:
        #    pass
        
        #dw = max(100, self.w - self.w_init + self.w_canv_init - 1)
        #dh = max(100, self.h - self.h_init + self.lb_init_height)
        
        #self.Plot_Canvas.config(width=dw, height=dh)
        
        #self.PA.set_canvas_wh(dw, dh)
        #self.plot_points()

    def Plot_Canvas_Resize(self, event):
        self.PA.set_canvas_wh(event.width, event.height)
        self.plot_points()
        
    def eval_distortion(self):
        if None in self.canvas_click_posL:
            self.distortion_flag = False
            return
        
        # evaluate any distortion in img 
        pos_xmin, pos_xmax, pos_ymin, pos_ymax = self.canvas_click_posL
        
        xy_xmin = self.PA.get_xy_at_fifj( *pos_xmin )
        xy_xmax = self.PA.get_xy_at_fifj( *pos_xmax )
        xy_ymin = self.PA.get_xy_at_fifj( *pos_ymin )
        xy_ymax = self.PA.get_xy_at_fifj( *pos_ymax )
        
        #for pos, xy in zip([pos_xmin, pos_xmax, pos_ymin, pos_ymax], [xy_xmin, xy_xmax, xy_ymin, xy_ymax]):
        #    print( 'pos=(%g,%g)'%pos,'  xy=(%g,%g)'%xy )
        
        x_err = xy_ymax[0] - xy_ymin[0]
        y_err = xy_xmax[1] - xy_xmin[1]
        
        pcent_x_err = abs(x_err) * 100.0 / max( abs(self.PA.x_origin), abs(self.PA.xmax) )
        pcent_y_err = abs(y_err) * 100.0 / max( abs(self.PA.y_origin), abs(self.PA.ymax) )
        
        self.statusMessage.set("Distortion Error: Xerr=%g%%, Yerr=%g%%"%(pcent_x_err, pcent_y_err))
        #self.ShowWarning( title='Distortion Error', message="Xerr=%g%%, Yerr=%g%%"%(pcent_x_err, pcent_y_err))
        
        
    def plot_points(self):
        s = 3
        s2 = s+3
        s3 = s+5
        
        # make coordinate axes
        self.Plot_Canvas.delete("all")
        
        # Place click directions onto canvas
        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
        else:
            tt_str = ''
        
        greyscale = str(self.GreyScale_Checkbutton_StringVar.get())=='yes'
        self.photo_image = self.PA.get_tk_photoimage(greyscale=greyscale, text=tt_str, 
                                                     show_linlog_text=True)
        self.Plot_Canvas.create_image(0,0, anchor=NW, image=self.photo_image )
                    
        iL = [i for i in self.Defined_Points_Listbox.curselection()]
        if (len(iL)>0):
            isel = iL[0]
        else:
            isel = -1
        
        # show x and y axes if they are visible
        if (self.canvas_tooltip_num>0) and self.PA.x_is_visible( self.PA.x_origin ):
            i = self.PA.get_canvas_i( self.PA.x_origin )
            j1, j2 = 0, self.PA.h_canv
            self.Plot_Canvas.create_line(i, j1, i, j2, fill="purple", dash=(1,5,1,1), width=3)
        if (self.canvas_tooltip_num>2) and self.PA.y_is_visible( self.PA.y_origin ):
            j = self.PA.get_canvas_j( self.PA.y_origin )
            i1, i2 = 0, self.PA.w_canv
            self.Plot_Canvas.create_line(i1, j, i2, j, fill="purple", dash=(1,5,1,1), width=3)
            
        # Show max click points if available
        pos_xmin, pos_xmax, pos_ymin, pos_ymax = self.canvas_click_posL
        if pos_xmax is not None:
            i = self.PA.get_canvas_i_from_img_fi( pos_xmax[0] )
            j = self.PA.get_canvas_j_from_img_fj( pos_xmax[1] )
            self.Plot_Canvas.create_line(i, j-s2, i, j+s2, fill="purple", width=3)
            self.Plot_Canvas.create_line(i-s2, j, i+s2, j, fill="purple", width=3)

        if pos_ymax is not None:
            i = self.PA.get_canvas_i_from_img_fi( pos_ymax[0] )
            j = self.PA.get_canvas_j_from_img_fj( pos_ymax[1] )
            self.Plot_Canvas.create_line(i, j-s2, i, j+s2, fill="purple", width=3)
            self.Plot_Canvas.create_line(i-s2, j, i+s2, j, fill="purple", width=3)

        # Show points
        for ip,P in enumerate(self.pointL):
            x,y = P.get_xy()
            i,j = self.PA.get_ij_at_xy( x,y )
            
            if min(i,j)>=0:
                if (isel>=0) and (ip==isel):
                    self.Plot_Canvas.create_rectangle((i-s2, j-s2, i+s2, j+s2), outline="blue", fill="blue")
                else:
                    self.Plot_Canvas.create_rectangle((i-s2, j-s2, i+s2, j+s2), outline="blue", fill="cyan")

        # Show cross-hairs for picking axis points
        if self.in_canvas:
            if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
                x,y = self.last_hover_pos
                self.Plot_Canvas.create_line(x, 0, x, self.PA.h_canv, fill="magenta", width=3, dash=(5,) )
                self.Plot_Canvas.create_line(0, y, self.PA.w_canv, y, fill="magenta", width=3, dash=(5,) )
            else:
                x,y = self.last_hover_pos
                self.Plot_Canvas.create_line(x, 0, x, self.PA.h_canv, fill="cyan", width=3, dash=(5,) )
                self.Plot_Canvas.create_line(0, y, self.PA.w_canv, y, fill="cyan", width=3, dash=(5,) )
        
    
    def add_point(self, x_float, y_float):
        
        self.has_some_new_data = True
        
        itemL = list(self.Defined_Points_Listbox.get(0, END))
        iL = [i for i in self.Defined_Points_Listbox.curselection()]
        
        if len(itemL)==0:
            self.pointL.append( Point(x_float, y_float) )
            self.Defined_Points_Listbox.insert(END, self.pointL[-1].get_str() )
            self.select_pointL(0)
        else:
            
            if len(iL)==0:
                self.pointL.append( Point(x_float, y_float) )
                self.Defined_Points_Listbox.insert(END, self.pointL[-1].get_str() )
                self.select_pointL(END)
            else:
                self.pointL.insert(iL[0]+1, Point(x_float, y_float) )
                self.Defined_Points_Listbox.insert(iL[0]+1, self.pointL[iL[0]+1].get_str() )
                self.select_pointL(iL[0]+1)
                
                #print( 'self.pointL =',self.pointL)
                
        self.statusMessage.set("added point x,y=%g, %g"%(x_float, y_float))

    def Canvas_Enter(self, event):
        self.in_canvas = True
        self.plot_points()
    def Canvas_Leave(self, event):
        self.in_canvas = False
        self.plot_points()


    def Canvas_Hover(self, event):
        
        if self.canvas_tooltip_num >= len(self.canvas_tooltip_strL):
        
            x = int(event.x)
            y = int(event.y)
            
            x_move, y_move = self.PA.get_xy_at_ij(x,y)
            
            try:
                x_str = '%g'%x_move
                y_str = '%g'%y_move
            except:
                x_str = '%s'%x_move
                y_str = '%s'%y_move
            
            self.statusMessage.set(x_str + ', ' + y_str)
            
        self.last_hover_pos = (event.x, event.y)
        self.plot_points()
            

    def Canvas_Begin_End_Drag(self, event):
        
        self.is_dragging = not self.is_dragging
        ix = int(event.x)
        iy = int(event.y)
        
        self.last_right_click_pos = (ix, iy)
        
        if self.is_dragging:
            self.statusMessage.set("Dragging Selected Point")
        else:
            self.statusMessage.set("END Dragging Selected Point")
        

    def Canvas_Drag_Axes(self, event):
        
        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA.adjust_offset(di, dj)
        
        self.last_right_click_pos = (event.x, event.y)
        
        self.plot_points()

    def MouseWheelHandler(self, event):

        if event.num == 5 or event.delta < 0:
            result = -1 
            #self.PA.zoom_in(zoom_factor=0.1)
            self.PA.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1 
            #self.PA.zoom_out(zoom_factor=0.1)
            self.PA.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)
            
        self.plot_points()
    
    def Sort_Button_Click(self, event):
        self.statusMessage.set("Sorting Points by Increasing X")
        
        self.pointL.sort( key=lambda P: (P.x,P.y) )
        
        # Clear entries in Listbox
        self.Defined_Points_Listbox.delete(0, END)
        
        for P in self.pointL:
            self.Defined_Points_Listbox.insert(END, P.get_str() )
            #print(P.get_str())
        
        self.Defined_Points_Listbox.select_set( END )
        self.plot_points()
    
    def Del_Button_Click(self, event):
        
        iL = [i for i in self.Defined_Points_Listbox.curselection()]
        if len(iL)>0:
            #print 'Deleting item %i'%iL[0]
            self.statusMessage.set("Deleting Pt: %s"%self.Defined_Points_Listbox.get( iL[0] ))
            
            self.Defined_Points_Listbox.delete( iL[0] )
            self.pointL.pop( iL[0] )
            
            isel = iL[0]-1
            if isel < 0:
                isel = 0
            if len(self.pointL)>0:
                self.select_pointL(isel)
            
        self.plot_points()


    def MakeBigger_Button_Click(self, event):
        self.PA.zoom_in(zoom_factor=0.1)
        self.plot_points()
        
    def MakeSmaller_Button_Click(self, event):
        self.PA.zoom_out(zoom_factor=0.1)
        self.plot_points()
        
    def MakeFit_Button_Click(self, event):
        self.menu_Fit_Image()
        self.plot_points()


    def select_pointL(self, i ):
        
        self.Defined_Points_Listbox.selection_clear(0, END)
        if i==END:
            self.Defined_Points_Listbox.select_set( END )
            i = len(self.pointL)-1
        else:
            self.Defined_Points_Listbox.select_set( i )
            
        self.plot_points()

    def menu_Paste_Clipboard_Image_event(self, event):
        self.menu_Paste_Clipboard_Image()

    def menu_Paste_Clipboard_Image(self):
        self.statusMessage.set("Pasting Image from Clipboard")
        
        if self.PA.set_img_from_clipboard():
            self.master.title("DigiPlot: Pasted Clipboard Image")
            self.Initialize_Image_State()
            
            self.statusMessage.set("SUCCESS... Pasted Image from Clipboard")
        else:
            self.statusMessage.set("FAILED... Pasting Image from Clipboard")
            self.ShowWarning(title='Clipboard Image Paste Failed', message='Clipboard Image Paste Failed.')
        

    def menu_File_Import_Image(self):
        self.statusMessage.set("called menu_File_Import_Image")
        
        if (len(self.pointL)>0) and self.has_some_new_data:
            if not self.AskYesNo( title='Current Data NOT Saved.', \
                              message='Import New Image?\n'+\
                              '(Hit "Yes" to DISCARD your current data.)'):
                return
        
        
        filetypes = [
            ('Images','*.png;*.jpg;*.gif;*.jpeg'),
            ('Any File','*.*')]
        img_path = tkFileDialog.askopenfilename(parent=self.master,title='Open Image file', 
            filetypes=filetypes)
            
        if img_path:
            if self.PA.open_img_file( img_path ):
                head,fName = os.path.split( img_path )
                self.master.title("DigiPlot: %s"%fName)
                self.Initialize_Image_State()
                self.statusMessage.set('file "%s" opened'%fName)
            


    def menu_File_Save_CSV(self):
        self.statusMessage.set("called menu_File_Save_CSV")
        self.saveFile('*.csv')
        
        
    def saveFile(self, fileDesc='*.csv'):
        
        fsave = tkFileDialog.asksaveasfilename(parent=self.master, title='Saving CSV file', 
            initialfile=fileDesc)
        
        if fsave:
            if fsave.find('.')<0:
                fsave += '.csv'
            
            
            self.statusMessage.set( 'Saving to:' + fsave )
            
            self.master.title("DigiPlot: %s"%fsave)
            
            fOut = open( fsave, 'w' )
            
            for P in self.pointL:
                fOut.write( '%s\n'%P.get_str() )
            fOut.close()
            
            self.has_some_new_data = False # after successful save
    
    def menu_Clipboard_Comma(self):
        if len(self.pointL)==0:
            self.ShowWarning( title='No Data Warning', message='No Data to put on Clipboard.')
            return
        
        self.frame.clipboard_clear()
        for P in self.pointL:
            self.frame.clipboard_append( P.get_str() + '\n' )
        self.statusMessage.set( "====== Comma-Separated on Clipboard =========")
        
    def menu_Clipboard_Tab(self):
        if len(self.pointL)==0:
            self.ShowWarning( title='No Data Warning', message='No Data to put on Clipboard.')
            return
        
        self.frame.clipboard_clear()
        for P in self.pointL:
            self.frame.clipboard_append( P.get_str().replace(', ','\t') + '\n' )
        self.statusMessage.set( "====== Tab-Separated on Clipboard =========")

    def set_xy_min_max(self, tt_num):
        
        if tt_num==0:
            self.PA.zoom_to_quadrant(qname='LL')
        elif tt_num==1:
            self.PA.zoom_to_quadrant(qname='LR')
        elif tt_num==2:
            self.PA.zoom_to_quadrant(qname='LL')
        elif tt_num==3:
            self.PA.zoom_to_quadrant(qname='UL')
        
        self.canvas_tooltip_num = tt_num
        self.canvas_tooltip_inc = 10
        self.plot_points()

    def menu_Anchor_Plot_Set_Xmin(self):
        self.statusMessage.set("Set Axis Point Xmin")
        self.set_xy_min_max(0)


    def menu_Anchor_Plot_Set_Xmax(self):
        self.statusMessage.set("Set Axis Point Xmax")
        self.set_xy_min_max(1)


    def menu_Anchor_Plot_Set_Ymin(self):
        self.statusMessage.set("Set Axis Point Ymin")
        self.set_xy_min_max(2)


    def menu_Anchor_Plot_Set_Ymax(self):
        self.statusMessage.set("Set Axis Point Ymax")
        self.set_xy_min_max(3)

    def menu_Anchor_Plot_Set_All(self):
        self.statusMessage.set("Set All 4 Axis Points (Xmin, Xmax, Ymin, Ymax)")
        self.set_xy_min_max(0)
        self.canvas_tooltip_inc = 1

    def menu_Fit_Image(self):
        self.PA.fit_img_on_canvas()
        self.plot_points()

    def menu_Fix_Image_4Pt(self):
        dialog = _ReAlign(self.master, "4 Point Re-Align Plot Axes (Make Orthogonal)",\
                          dialogOptions={'img':self.PA.img})
        if dialog.result is not None:
            self.PA.set_img( dialog.result["img_fixed"] )
            
            self.master.title("DigiPlot: Re-Aligned Image")
            self.Initialize_Image_State()
            self.statusMessage.set('Re-Aligned Image')
            
        dialog.destroy()

    def menu_Fix_Image_3Pt(self):
        dialog = _ReAlign(self.master, "3 Point Re-Align Plot Axes (Make Orthogonal)",\
                          dialogOptions={'img':self.PA.img, 'use_3_point':True})
        if dialog.result is not None:
            self.PA.set_img( dialog.result["img_fixed"] )
            
            self.master.title("DigiPlot: Re-Aligned Image")
            self.Initialize_Image_State()
            self.statusMessage.set('Re-Aligned Image')
            
        dialog.destroy()

    def menu_Help(self):
        self.statusMessage.set("called menu_Help")
        help_msg = """
        
Left Click = Add Point or Define Axes
Right Drag = Pan Zoomed Plot
Mouse Wheel = Zoom

Esc Key = Clear Pending Actions
"""
        self.ShowInfo( title='Help', message='Mouse/Keyboard Options\r' + help_msg)


    def menu_Exit_Quit(self):
        self.statusMessage.set("called menu_Exit_Quit")
        print( "called menu_Exit_Quit")
        self.cleanupOnQuit()

    def Plot_Canvas_Click(self, event): #click method for component ID=1

        x,y = self.PA.get_xy_at_ij(event.x, event.y)

        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
            
            self.canvas_click_posL[self.canvas_tooltip_num] = self.PA.get_fifj_at_ij(event.x, event.y) # can detect img distortion
            
            if self.canvas_tooltip_num==0:
                result = tkSimpleDialog.askfloat(tt_str, 'Enter Xmin')
                if result is not None:
                    self.statusMessage.set("Xmin = %g"%result)
                    self.PA.set_ix_origin(event.x, result)
                    self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==1:
                result = tkSimpleDialog.askfloat(tt_str, 'Enter Xmax')
                if result is not None:
                    self.statusMessage.set("Xmax = %g"%result)
                    self.PA.set_imax_xmax(event.x, result)
                    self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==2:
                result = tkSimpleDialog.askfloat(tt_str, 'Enter Ymin')
                if result is not None:
                    self.statusMessage.set("Ymin = %g"%result)
                    self.PA.set_jy_origin(event.y, result)
                    self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==3:
                result = tkSimpleDialog.askfloat(tt_str, 'Enter Ymax')
                if result is not None:
                    self.statusMessage.set("Ymax = %g"%result)
                    self.PA.set_jmax_ymax(event.y, result)
                    self.canvas_tooltip_num += self.canvas_tooltip_inc
                    
                    self.PA.fit_img_on_canvas()
            
            self.canvas_tooltip_inc = 1 # Just in case it is >1 for single options

        
            if self.canvas_tooltip_num==0:
                self.PA.zoom_to_quadrant(qname='LL')
            elif self.canvas_tooltip_num==1:
                self.PA.zoom_to_quadrant(qname='LR')
            elif self.canvas_tooltip_num==2:
                self.PA.zoom_to_quadrant(qname='LL')
            elif self.canvas_tooltip_num==3:
                self.PA.zoom_to_quadrant(qname='UL')


            if not None in self.canvas_click_posL:
                self.eval_distortion()
            
            self.plot_points()
                
        else:
        
            #print( "executed method Plot_Canvas_Click")
            #self.statusMessage.set("executed method Plot_Canvas_Click")
            #print( "clicked in canvas at i,j =",event.x,event.y)
            
            #print('x=%g, y=%g'%(x,y))
            self.add_point(x,y)

    def Defined_Points_Listbox_Click(self, event): #click method for component ID=2
        #print( "current selection(s) =",self.Defined_Points_Listbox.curselection())
        labelL = []
        for i in self.Defined_Points_Listbox.curselection():
            labelL.append( self.Defined_Points_Listbox.get(i))
        
        if labelL:
            self.statusMessage.set("Selected Pt: %s"%labelL[0])
        self.plot_points()

    def GreyScale_Checkbutton_StringVar_Callback(self, varName, index, mode):
        self.statusMessage.set("    GreyScale_Checkbutton_StringVar = "+self.GreyScale_Checkbutton_StringVar.get())
        #print "    new StringVar value =",self.GreyScale_Checkbutton_StringVar.get()
        self.plot_points()

    def LogX_Checkbutton_StringVar_Callback(self, varName, index, mode):
        self.statusMessage.set("    LogX_Checkbutton_StringVar = "+self.LogX_Checkbutton_StringVar.get())
        
        is_log = str(self.LogX_Checkbutton_StringVar.get())=='yes'
        if is_log:
            self.PA.set_log_x()
        else:
            self.PA.set_linear_x()
            
        self.plot_points()

    def LogY_Checkbutton_StringVar_Callback(self, varName, index, mode):
        self.statusMessage.set("    LogY_Checkbutton_StringVar = "+self.LogY_Checkbutton_StringVar.get())
        
        is_log = str(self.LogY_Checkbutton_StringVar.get())=='yes'
        if is_log:
            self.PA.set_log_y()
        else:
            self.PA.set_linear_y()
            
        self.plot_points()


    # standard message dialogs... showinfo, showwarning, showerror
    def ShowInfo(self, title='Title', message='your message here.'):
        tkMessageBox.showinfo( title, message )
        return
    def ShowWarning(self, title='Title', message='your message here.'):
        tkMessageBox.showwarning( title, message )
        return
    def ShowError(self, title='Title', message='your message here.'):
        tkMessageBox.showerror( title, message )
        return
        
    # standard question dialogs... askquestion, askokcancel, askyesno, or askretrycancel
    # return True for OK, Yes, Retry, False for Cancel or No
    def AskYesNo(self, title='Title', message='your question here.'):
        return tkMessageBox.askyesno( title, message )
    def AskOK_Cancel(self, title='Title', message='your question here.'):
        return tkMessageBox.askokcancel( title, message )
    def AskRetryCancel(self, title='Title', message='your question here.'):
        return tkMessageBox.askretrycancel( title, message )
        
    # return "yes" for Yes, "no" for No
    def AskQuestion(self, title='Title', message='your question here.'):
        return tkMessageBox.askquestion( title, message )
    # END of standard message dialogs

    # >>>>>>insert any user code below this comment for section "standard_message_dialogs"


    # standard file dialogs... askdirectory, askopenfile, asksaveasfilename

    # return a string containing directory name
    def AskDirectory(self, title='Choose Directory', initialdir="."):
        dirname = tkFileDialog.askdirectory(parent=self.master,initialdir=initialdir,title=title)
        return dirname # <-- string
        
    # return an OPEN file type object OR None (opened using mode, 'r','rb','w','wb')
    # WARNING... opening file with mode 'w' or 'wb' will erase contents
    def AskOpenFile(self, title='Choose File', mode='rb', initialdir='.', filetypes=None):
        if filetypes==None:
            filetypes = [
                ('Text File','*.txt'),
                ('Data File','*.dat'),
                ('Output File','*.out'),
                ('Any File','*.*')]
        fileobj = tkFileDialog.askopenfile(parent=self.master,mode=mode,title=title,
            initialdir=initialdir, filetypes=filetypes)
        
        # if opened, then fileobj.name contains the name string
        return fileobj # <-- an opened file, or the value None
        
    # return a string containing file name (the calling routine will need to open the file)
    def AskSaveasFilename(self, title='Save File', filetypes=None, initialfile=''):
        if filetypes==None:
            filetypes = [
                ('Text File','*.txt'),
                ('Data File','*.dat'),
                ('Output File','*.out'),
                ('Any File','*.*')]

        fileName = tkFileDialog.asksaveasfilename(parent=self.master,filetypes=filetypes, initialfile=initialfile ,title=title)
        return fileName # <-- string
        
    # END of standard file dialogs

    # >>>>>>insert any user code below this comment for section "standard_file_dialogs"



def main():
    root = Tk()
    app = DigiPlot(root)
    root.mainloop()

if __name__ == '__main__':
    main()
