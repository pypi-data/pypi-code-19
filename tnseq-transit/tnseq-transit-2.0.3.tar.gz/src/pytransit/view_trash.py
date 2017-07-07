# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import sys

try:
    import wx
    import wx.xrc
    hasWx = True
except Exception as e:
    hasWx = False


###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Trash View", pos = wx.DefaultPosition, size = wx.Size( 1117,439 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.m_bitmap1, 1, wx.ALL|wx.EXPAND, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		sbSizer41 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Canvas" ), wx.HORIZONTAL )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.updateButton = wx.Button( self, wx.ID_ANY, u"Update", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		bSizer9.Add( self.updateButton, 0, wx.ALL, 5 )
		
		self.resetButton = wx.Button( self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer9.Add( self.resetButton, 0, wx.ALL, 5 )
		
		
		sbSizer41.Add( bSizer9, 0, 0, 5 )
		
		bSizer111 = wx.BoxSizer( wx.VERTICAL )
		
		self.saveButton = wx.Button( self, wx.ID_ANY, u"Save Img", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer111.Add( self.saveButton, 0, wx.ALL, 5 )
		
		self.featureButton = wx.Button( self, wx.ID_ANY, u"Add Feature", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer111.Add( self.featureButton, 0, wx.ALL, 5 )
		
		
		sbSizer41.Add( bSizer111, 0, 0, 5 )
		
		
		bSizer5.Add( sbSizer41, 0, 0, 5 )
		
		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Position" ), wx.VERTICAL )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.moveLeftButton = wx.Button( self, wx.ID_ANY, u"<-", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.moveLeftButton, 0, wx.ALL, 5 )
		
		self.moveRightButton = wx.Button( self, wx.ID_ANY, u"->", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.moveRightButton, 0, wx.ALL, 5 )
		
		self.startText = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer10.Add( self.startText, 0, wx.ALL, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Search:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer10.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.searchText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer10.Add( self.searchText, 0, wx.ALL, 5 )
		
		self.searchButton = wx.Button( self, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.searchButton, 0, wx.ALL, 5 )
		
		
		sbSizer4.Add( bSizer10, 0, wx.EXPAND, 5 )
		
		bSizer11 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.zoomOutButton = wx.Button( self, wx.ID_ANY, u"Zoom Out", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.zoomOutButton, 0, wx.ALL, 5 )
		
		self.zoomInButton = wx.Button( self, wx.ID_ANY, u"Zoom In", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.zoomInButton, 0, wx.ALL, 5 )
		
		self.endText = wx.TextCtrl( self, wx.ID_ANY, u"10000", wx.Point( 400,350 ), wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer11.Add( self.endText, 0, wx.ALL, 5 )
		
		self.normCheck = wx.CheckBox( self, wx.ID_ANY, u"Normalize Data", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.normCheck.SetValue(True) 
		bSizer11.Add( self.normCheck, 0, wx.ALL, 5 )
		
		
		sbSizer4.Add( bSizer11, 0, wx.EXPAND, 5 )
		
		
		bSizer5.Add( sbSizer4, 1, 0, 5 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Scale" ), wx.VERTICAL )
		
		bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.minLabel = wx.StaticText( self, wx.ID_ANY, u"Min Read", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.minLabel.Wrap( -1 )
		bSizer12.Add( self.minLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.minText = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.minText.Enable( False )
		
		bSizer12.Add( self.minText, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer3.Add( bSizer12, 1, wx.EXPAND, 5 )
		
		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.maxLabel = wx.StaticText( self, wx.ID_ANY, u"Max Read", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxLabel.Wrap( -1 )
		bSizer13.Add( self.maxLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.maxText = wx.TextCtrl( self, wx.ID_ANY, u"150", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer13.Add( self.maxText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer3.Add( bSizer13, 1, wx.EXPAND, 5 )
		
		
		bSizer5.Add( sbSizer3, 0, wx.EXPAND, 5 )
		
		
		bSizer2.Add( bSizer5, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.updateButton.Bind( wx.EVT_BUTTON, self.updateFunc )
		self.resetButton.Bind( wx.EVT_BUTTON, self.resetFunc )
		self.saveButton.Bind( wx.EVT_BUTTON, self.saveImageFunc )
		self.featureButton.Bind( wx.EVT_BUTTON, self.addFeatureFunc )
		self.moveLeftButton.Bind( wx.EVT_BUTTON, self.leftFunc )
		self.moveRightButton.Bind( wx.EVT_BUTTON, self.rightFunc )
		self.startText.Bind( wx.EVT_TEXT_ENTER, self.updateFunc )
		self.searchText.Bind( wx.EVT_TEXT_ENTER, self.searchFunc )
		self.searchButton.Bind( wx.EVT_BUTTON, self.searchFunc )
		self.zoomOutButton.Bind( wx.EVT_BUTTON, self.zoomOutFunc )
		self.zoomInButton.Bind( wx.EVT_BUTTON, self.zoomInFunc )
		self.endText.Bind( wx.EVT_TEXT_ENTER, self.updateFunc )
		self.normCheck.Bind( wx.EVT_CHECKBOX, self.updateFunc )
		self.maxText.Bind( wx.EVT_TEXT, self.updateFunc )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def updateFunc( self, event ):
		event.Skip()
	
	def resetFunc( self, event ):
		event.Skip()
	
	def saveImageFunc( self, event ):
		event.Skip()
	
	def addFeatureFunc( self, event ):
		event.Skip()
	
	def leftFunc( self, event ):
		event.Skip()
	
	def rightFunc( self, event ):
		event.Skip()
	
	
	def searchFunc( self, event ):
		event.Skip()
	
	
	def zoomOutFunc( self, event ):
		event.Skip()
	
	def zoomInFunc( self, event ):
		event.Skip()
	
	
	
	

