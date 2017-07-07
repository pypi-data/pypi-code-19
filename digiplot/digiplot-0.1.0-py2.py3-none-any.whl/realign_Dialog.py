#!/usr/bin/env python
# -*- coding: ascii -*-
from __future__ import absolute_import
from __future__ import print_function

import sys, os

if sys.version_info < (3,):
    from future import standard_library
    standard_library.install_aliases()
    from tkSimpleDialog import Dialog
    import tkMessageBox
else:
    # this is only called incorrectly by pylint using python2
    from tkinter.simpledialog import Dialog
    import tkinter.messagebox as tkMessageBox


from tkinter import *

# Import Pillow:
from PIL import Image, ImageTk

from digiplot.fix_distortion import fix_plot_img
from digiplot.plot_area import PlotArea        

class _Dialog(Dialog):
    # use dialogOptions dictionary to set any values in the dialog
    def __init__(self, parent, title = None, dialogOptions=None):
        self.initComplete = 0
        self.dialogOptions = dialogOptions
        Dialog.__init__(self, parent, title)
        
        
class _ReAlign(_Dialog):

    def body(self, body):
        
        body.pack(padx=5, pady=5, fill=BOTH, expand=True) 
        
        dialogframe = Frame(body, width=663, height=627)
        dialogframe.pack(fill=BOTH, expand=YES, side=TOP)
        self.dialogframe = dialogframe

        lbframe = Frame( dialogframe )
        self.Canvas_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Canvas_1 = Canvas(lbframe, width="600", height="600", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Canvas_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Canvas_1.pack(side=LEFT, fill=BOTH, expand=YES)
        lbframe.pack(fill=BOTH, expand=YES, side=TOP)

        self.Canvas_1.bind("<ButtonRelease-1>", self.Canvas_1_Click)

        
        # Mouse Wheel for Zooming in and out
        self.Canvas_1.bind("<MouseWheel>",self.MouseWheelHandler) # Windows Binding
        self.Canvas_1.bind("<Button-4>",self.MouseWheelHandler) # Linux Binding
        self.Canvas_1.bind("<Button-5>",self.MouseWheelHandler) # Linux Binding   

        self.Canvas_1.bind('<Up>', self.MakeBigger)
        self.Canvas_1.bind('<Down>', self.MakeSmaller)
        
        #body.unbind_all('<Escape>')
        self.Canvas_1.bind_all('<Key-1>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-2>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-3>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-4>', self.Key_Actions)

        
        self.Canvas_1.bind("<Button-3>", self.Canvas_Begin_End_Drag)
        self.Canvas_1.bind("<B3-Motion>", self.Canvas_Drag_Axes)
        self.Canvas_1.bind("<Motion>", self.Canvas_Hover)
        self.Canvas_1.bind("<Enter>", self.Canvas_Enter)
        self.Canvas_1.bind("<Leave>", self.Canvas_Leave)
        
        self.Canvas_1.bind("<Configure>", self.Canvas_1_Resize)
        
        self.resizable(1,1) # Linux may not respect this
        # >>>>>>insert any user code below this comment for section "top_of_init"
        
        self.Canvas_1.focus_set()

        self.PA = PlotArea(w_canv=600, h_canv=600) # will hold PlotArea() when it is opened
        
        # use a copy of submitted image
        self.PA.set_img( self.dialogOptions['img'].copy() )
        
        self.is_dragging = False
        self.last_right_click_pos = (0,0) # any action calling Canvas_Find_Closest will set

        self.last_hover_pos = (0,0)
        self.in_canvas = False

        self.canvas_tooltip_num = 0
        self.canvas_tooltip_inc = 1 # set > 1 to skip some options
        self.canvas_tooltip_strL = ['Left Click Upper Left.', 'Left Click Upper Right',
                                    'Left Click Lower Right.', 'Left Click Lower Left']
        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None] # only useful if all None's replaced
        
        self.is_first_display = True
        self.all_done = False
        

    def Key_Actions(self, event):
        #print('event.char =',event.char)
        if event.char=='1':
            self.PA.zoom_to_quadrant(qname='UL')
        elif event.char=='2':
            self.PA.zoom_to_quadrant(qname='UR')
        elif event.char=='3':
            self.PA.zoom_to_quadrant(qname='LR')
        elif event.char=='4':
            self.PA.zoom_to_quadrant(qname='LL')
            
        self.fill_canvas()

    def MakeBigger(self, event):
        #print('MakeBigger')
        self.PA.zoom_in(zoom_factor=0.1)
        self.fill_canvas()
        
    def MakeSmaller(self, event):
        #print('MakeSmaller')
        self.PA.zoom_out(zoom_factor=0.1)
        self.fill_canvas()

    def fill_canvas(self):
        if self.all_done:
            return
        
        if self.is_first_display:
            self.PA.zoom_to_quadrant(qname='UL')
            self.is_first_display = False
        
        # make coordinate axes
        try:
            self.Canvas_1.delete("all")
        except:
            pass
        
        # Place click directions onto canvas
        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
        else:
            tt_str = ''
        
        self.photo_image = self.PA.get_tk_photoimage(greyscale=True, text=tt_str)
        self.Canvas_1.create_image(0,0, anchor=NW, image=self.photo_image )
        

        # Show cross-hairs for picking axis points
        if self.in_canvas:
            x,y = self.last_hover_pos
            self.Canvas_1.create_line(x, 0, x, self.PA.h_canv, fill="magenta", width=3, dash=(5,) )
            self.Canvas_1.create_line(0, y, self.PA.w_canv, y, fill="magenta", width=3, dash=(5,) )

        

    def Canvas_1_Resize(self, event):
        #w_canv = int( self.Canvas_1.winfo_width() )
        #h_canv = int( self.Canvas_1.winfo_height() )
        #if w_canv>0 and h_canv>0:
            
        self.PA.set_canvas_wh(event.width, event.height)
        self.fill_canvas()

    def MouseWheelHandler(self, event):
        #print('MouseWheelHandler event.num =', event.num)

        if event.num == 5 or event.delta < 0:
            result = -1 
            #self.PA.zoom_in(zoom_factor=0.1)
            self.PA.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1 
            #self.PA.zoom_out(zoom_factor=0.1)
            self.PA.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)
            
        self.fill_canvas()

    def Canvas_Begin_End_Drag(self, event):
        
        self.is_dragging = not self.is_dragging
        ix = int(event.x)
        iy = int(event.y)
        
        self.last_right_click_pos = (ix, iy)
        

    def Canvas_Drag_Axes(self, event):
        
        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA.adjust_offset(di, dj)
        
        self.last_right_click_pos = (event.x, event.y)
        
        self.fill_canvas()

    def Canvas_Enter(self, event):
        self.in_canvas = True
        self.fill_canvas()
                
        
    def Canvas_Leave(self, event):
        self.in_canvas = False
        self.fill_canvas()


    def Canvas_Hover(self, event):
            
        self.last_hover_pos = (event.x, event.y)
        self.fill_canvas()
            

    # tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "compID=2"
    def Canvas_1_Click(self, event): #click method for component ID=2
        pass
        # >>>>>>insert any user code below this comment for section "compID=2"
        # replace, delete, or comment-out the following
        #print("executed method Canvas_1_Click")
        #print("clicked in canvas at x,y =",event.x,event.y)
        #w = int(self.Canvas_1.cget("width"))
        #h = int(self.Canvas_1.cget("height"))
        
        w = int(self.Canvas_1.winfo_width())
        h = int(self.Canvas_1.winfo_height())

        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
            
            # For Now, units are fi,fj
            fi, fj = self.PA.get_fifj_at_ij(event.x, event.y)
            self.canvas_click_posL[self.canvas_tooltip_num] = \
                        (self.PA.get_img_i_from_img_fi(fi),  \
                         self.PA.get_img_j_from_img_fj(fj) )
            
            if self.canvas_tooltip_num==0:
                self.title("Upper Left = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==1:
                self.title("Upper Right = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==2:
                self.title("Lower Right = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==3:
                self.title("Lower Left = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                    
                
            
            self.canvas_tooltip_inc = 1 # Just in case it is >1 for single options

        
            if self.canvas_tooltip_num==0:
                self.PA.zoom_to_quadrant(qname='UL')
            elif self.canvas_tooltip_num==1:
                self.PA.zoom_to_quadrant(qname='UR')
            elif self.canvas_tooltip_num==2:
                self.PA.zoom_to_quadrant(qname='LR')
            elif self.canvas_tooltip_num==3:
                self.PA.zoom_to_quadrant(qname='LL')
            else:
                self.PA.fit_img_on_canvas()


            if not None in self.canvas_click_posL:
                UL, UR, LR, LL = self.canvas_click_posL
                #print('UL, UR, LR, LL =',UL, UR, LR, LL)
                self.img_fixed = fix_plot_img( UL, UR, LR, LL, self.PA.img)
                self.PA.set_img( self.img_fixed )
                
                self.ShowInfo( title='Image Is Realigned', message='''Use Cross-Hairs to examine orthogonality
                If satisfied, hit "OK" button on main screen.''')
                
            
            self.fill_canvas()
                

    # standard message dialogs... showinfo, showwarning, showerror
    def ShowInfo(self, title='Title', message='your message here.'):
        tkMessageBox.showinfo( title, message )
        return
        

    # tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "dialog_validate"
    def validate(self):
        self.result = {} # return a dictionary of results
        
        #self.Canvas_1.unbind_all('<Key>')
        self.all_done = True
        
        self.result["img_fixed"] = self.img_fixed.copy()
        return 1
# tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "end"


    def apply(self):
        #print('apply called')
        pass

class _Testdialog:
    def __init__(self, master):
        frame = Frame(master, width=300, height=300)
        frame.pack()
        self.master = master
        self.x, self.y, self.w, self.h = -1,-1,-1,-1
        
        self.Button_1 = Button(text="Test Dialog", relief="raised", width="15")
        self.Button_1.place(x=84, y=36)
        self.Button_1.bind("<ButtonRelease-1>", self.Button_1_Click)

    def Button_1_Click(self, event): #click method for component ID=1

        # Load the original image:
        img = Image.open("rot_poly_m3.jpg")
        dialogOptions = {'img':img}
        
        dialog = _ReAlign(self.master, "Test Dialog",dialogOptions=dialogOptions)
        print('===============Result from Dialog====================')
        print(dialog.result)
        print('=====================================================')

def main():
    root = Tk()
    app = _Testdialog(root)
    root.mainloop()

if __name__ == '__main__':
    main()
