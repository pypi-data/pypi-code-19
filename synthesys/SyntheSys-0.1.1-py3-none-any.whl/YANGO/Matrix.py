
import logging

#======================================================================
# MATRIX PROCESSING
#======================================================================
class Matrix:
	#-----------------------------------------------------------
	def __init__(self, xSize=None, ySize=None, NbElement=None):
		"""
		Build the matrix structure (list of lists).
		"""
		self.Structure = [list(),]
		if NbElement==None:
			if xSize!=None and ySize!=None:
				self.NewMatrix(xSize, ySize)
			else:
				return
		else:
			self.BuildFromNbElement(NbElement)
		
	#-----------------------------------------------------------
	def NewMatrix(self, xSize, ySize):
		"""
		Create a empty matrix according to x,y dimensions.
		The matrix is filled with "None" values.
		"""
		if xSize<1 or ySize<1: return 
		self.Structure = [[None for x in range(0, xSize)] for y in range(0, ySize)]
	
	#-----------------------------------------------------------
	def BuildFromNbElement(self, NbElement):
		"""
		Build a new matrix from a number of element to add.
		It adds rows/column so as to respect near square size.
		"""
		if NbElement<1: 
			logging.error("Cannot build matrix for zero or negative elements.")
		self.NewMatrix(1, 1)
		DownCnt = NbElement
		while(DownCnt>0):
			self.AddToMatrix("")
			DownCnt-=1
		for RowIndice in range(len(self.Structure)):
			for ColumnIndice in range(len(self.Structure[RowIndice])):
				self.Structure[RowIndice][ColumnIndice]=None
				
		
	#-----------------------------------------------------------
	def AddAtPosition(self, Item, x, y):
		"""
		Add an item to a Matrix according position' function.
		Matrix is extendable.
		"""
		self.AddToMatrix(Item)
		self.MoveInMatrix(Item, x, y)
	
	#-----------------------------------------------------------
	def AddToMatrix(self, Item):
		"""
		Add an item to a Matrix according to rules defined in 'NextCoordinates()' function.
		Matrix is extendable.
		"""
		(x, y, xmax, ymax) = self.NextCoordinates()
#		print "(x, y, xmax, ymax)", x, y, xmax, ymax
#		self.Display()
	
		try: 
			if self.Structure[y][x]==None: 
				self.Structure[y][x] = Item # if previous item is None and good size. 
				return x, y
		except: pass
		
		if xmax<0:  # First item
			self.Structure[0].append(Item)
			return 0, 0
		elif y > ymax: self.Structure.append([Item,]) # This is the only case when we have to add a new row
		else: self.Structure[y].append(Item) # else add a new item to the found row

		return x, y

	#-----------------------------------------------------------
	def RemoveFromMatrix(self, Item):
		"""
		Add an item to a Matrix according to rules defined in 'NextCoordinates()' function.
		Matrix is extendable.
		"""
		# First find old coordinates
		Pos = self.PositionInMatrix(Item)
		if Pos == None: return False
		x, y = Pos
		# Replace item by 'None'
		self.Structure[y][x]=None
		# Resize each row to be of same lenght
		#xmax=0
		#for y in range(0, len(self.Structure)):
		#	for x in range(0, len(self.Structure[y])):
		#		if self.Structure[y][x]!=None: 
		#			if xmax<x: xmax=x
		# Fill each undersized row with Nones
		#for y in range(0, len(self.Structure)):
		#	for x in range(0, xmax):
		#		try:
		#			if self.Structure[y][x]!=None: pass
		#		except: self.Structure[y][x]=None
				
		self.Shrink() # Remove empty ending columns then remove empty lists.
		return True
	
	#-----------------------------------------------------------
	def ShrinkNones(self):
		"""
		Remove None nodes from matrix
		"""
		for RowIndice in reversed(range(len(self.Structure))):
			for ColumnIndice in reversed(range(len(self.Structure[RowIndice]))):
				if self.Structure[RowIndice][ColumnIndice]==None:
					self.Structure[RowIndice].pop(ColumnIndice)	
				
	#-----------------------------------------------------------
	def Shrink(self):
		"""
		Remove empty ending columns then remove empty lists.
		(Unable to remove None nodes)
		"""
		# Exit if empty matrix
		if len(self.Structure[0])==0: return True
		# Start by empty ending columns
		ScanEnd=False
		while(ScanEnd==False):
			EndColEmpty   = True
			StartColEmpty = True
			xMax, yMax = self.Dimensions() # Get dimensions for each new resized matrix
			if xMax<0: return # Do nothing if matrix is empty
			for y in range(0, len(self.Structure)):
				# Check first column
				if self.Structure[y][0]!=None:
					StartColEmpty=False
				# Check last column
				if xMax<len(self.Structure[y]):
					if self.Structure[y][xMax]!=None:
						EndColEmpty=False
					
				# If matrix scan finished, remove empty columns
				if y == yMax :
					# No ending/starting empty columns: end scan
					if EndColEmpty==False and StartColEmpty==False:
						ScanEnd=True
					else:
						# Found an empty ending column
						if EndColEmpty==True:
#							logging.debug("Remove column {0} of matrix.".format(xMax))
							# Remove last item from each column
							for Row in range(0, len(self.Structure)):
								if xMax<len(self.Structure[Row]):
									del self.Structure[Row][xMax]
							xMax-=1
						# Found an empty starting column
						if StartColEmpty==True:
#							logging.debug("Remove column {0} of matrix.".format(0))
							# Remove first item from each column
							for Row in range(0, len(self.Structure)):
								if len(self.Structure[Row])==0: continue
								del self.Structure[Row][0]
							xMax-=1
				
						
		# Now remove empty ending lists (rows)
		EmptyRows=[]
		for Row in range(0, len(self.Structure)):
			Shrinked = list(filter(lambda x: x!=None, self.Structure[Row]))
			if len(Shrinked)>0: pass
			else: EmptyRows.append(Row)
			
		for Row in sorted(EmptyRows, reverse=True):
			while(len(self.Structure[Row])): self.Structure[Row].pop() # Empty row
			
		# Now remove empty lists (rows)
		self.Structure = list(filter(lambda x: len(x)!=0, self.Structure))
		
		return	
		
	
	#-----------------------------------------------------------
	def MoveInMatrix(self, Item, xNew, yNew):
		"""
		Move item to new coordinates.
		Matrix is not extendable.
		"""
		# Test if new coordinates are within dimensions
		xmax, ymax = self.Dimensions()
		if xNew>xmax or yNew>ymax: return False
	
		# First find old coordinates
		Pos = self.PositionInMatrix(Item)
		if Pos!=None: xOld, yOld = Pos
		else: return False
		
		#logging.debug("Move item '{0}' from coordinates ({1},{2}) to coordinates ({3},{4}).".format(Item, xOld, yOld, xNew, yNew))
	
		# Find if there is a component already at xNew, yNew
		ReplacedItem = self.Get(xNew, yNew)
		#logging.debug("Found '{0}' at coordinates ({1},{2}).".format(ReplacedItem, xNew, yNew))
		
		if ReplacedItem!=None: 
			# Change replaced item coordinates
			self.Structure[yOld][xOld]=ReplacedItem
			# Move to new coordinates
			self.Structure[yNew][xNew]=Item
			return True
		else: # If it's a position not used
			try: 
				self.Structure[yOld][xOld]=None
				self.Structure[yNew][xNew]=Item # If None at new coordinates: Fill it !
				return True
			except:
				# We have to enlarge matrix
				for y in range(0, ymax+1):
					for x in range(0, xmax+1):
						if x==xNew and y==yNew:
							self.Structure[yNew].append(Item)
							self.Structure[yOld][xOld]=None
							return True
						else: 
							while(len(self.Structure[y])<(xmax+1)):
								# We must fill it with None Values
								self.Structure[y].append(None)
		return False
			
	#-----------------------------------------------------------
	def EnlargeMatrix(self, xSize, ySize):
		"""
		Fill extra lines/columns with None values.
		Item should be removed, return False.
		"""
		xmax, ymax = self.Dimensions()
		if xSize<(xmax+1) or ySize<(ymax+1): return True
	
		for y in range(0, ySize):
			try: 
				while len(self.Structure[y])<xSize: self.Structure[y].append(None)
			except: 
				self.Structure.append([None for x in range(0, xSize)])
		return True
		
	#-----------------------------------------------------------
	def PositionInMatrix(self, Item):
		"""
		Move item to new coordinates.
		"""
		for y in range(0,len(self.Structure)):
			for x in range(0,len(self.Structure[y])):
				if Item==self.Structure[y][x]:
					return x, y
		return self.FreeInMatrix() # Return a free coordinate in Matrix.
		
	#-----------------------------------------------------------
	def BrowseMatrix(self):
		"""
		Iter on each element. Return a 2 tuple of coordinate and item.
		"""
		for y in range(0,len(self.Structure)):
			for x in range(0,len(self.Structure[y])):
				yield (x, y), self.Structure[y][x]
				
	#----------------------------------------------------------------------
	def __getitem__(self, index):
		"""
		Return row (list) a given position.
		"""
		(xmax, ymax) = self.Dimensions()
		if isinstance(index, int):
			if index >= 0 and index<=ymax:
				if xmax==0: return []
				else: return self.Structure[index]
			else : return None
		elif isinstance(index, slice):
			logging.warning("Slicing interfaces not supported yet.")
			return None
		else:
			raise TypeError("index must be int or slice")
				
	#----------------------------------------------------------------------
	def Get(self, x=0, y=0):
		"""
		Return item found at position (x,y).
		Return None if no item is found.
		"""
		try: Item = self.Structure[y][x]
		except: Item = None
		return Item
			
	#----------------------------------------------------------------------
	def __len__(self):
		"""
		Return number of items in matrix.
		"""
		NbItem=0
		for Item in self.BrowseMatrix():
			if Item!=None: NbItem+=1
		return NbItem
	
	#-----------------------------------------------------------
	def FreeInMatrix(self):
		"""
		Return a free coordinate in Matrix.
		"""
		# Get next coordinate according to filling rules
		xnext, ynext, xmax, ymax = self.NextCoordinates()
		# Return those coordinates only if they are in the matrix dimensions.
		if xnext>xmax or ynext>ymax: return None
		return xnext, ynext

	#-----------------------------------------------------------
	def NextCoordinates(self):
		"Determine what is the next coordinates where en item should be added. Return Matrix dimension too with this coordinate."
		(xmax, ymax) = self.Dimensions()
		#----------------Rules for populating--------------------
		#--------------------------------------------------------
		# Find empty coordinate within the matrix dimensions
		# Perfect square ?
		xFullMax= 0
		for y in range(0, len(self.Structure)):
			for x in range(0, len(self.Structure[y])):
				if self.Structure[y][x]==None: 
					if x == 0:
						if y == 0 : 
							return 0, 0, xmax, ymax # First Item
						elif y>xFullMax: 
							return xFullMax+1, 0, xmax, ymax # When perfect square: add to first line
					if x<=xFullMax: 
						return x, y, xmax, ymax # Fill uncomplete lines
					else:
						return x, y, xmax, ymax # Fill uncomplete lines
						
					break
				elif x>xFullMax: xFullMax = x # Save last populated xmax coordinate
				
			
		#--------------------------------------------------------
		# If we must enlarge the matrix
		# Perfect square ?
		if xmax == ymax:
			for Rows in self.Structure:# browse y
				# All lines of same length ?
				if (len(Rows)-1)<xmax:# nope ! Fill the space !
					x = len(Rows)-1
					y = self.Structure.index(Rows)
					return (x, y, xmax, ymax)
			# Perfect Square => Append to first raw.
			x = xmax+1
			y = 0
			return (x, y, xmax, ymax)

		for Rows in self.Structure:# browse y
			# All lines of same length ?
			if (len(Rows)-1)< max(xmax, ymax):# nope ! Fill in the space !
				x = len(Rows)-1
				y = self.Structure.index(Rows)
				return (x, y, xmax, ymax)
		return (0, ymax+1, xmax, ymax)
			
	# -------------------------------------------------------
	def Dimensions(self):
		"""
		Return matrix dimensions in term of coordinates: xmax and ymax
		"""
		xSize, ySize = self.Size()
		return (xSize-1, ySize-1)
			
	# -------------------------------------------------------
	def Size(self):
		"""
		Return matrix size (a tuple).
		"""
		if len(self.Structure[0])==0: return (0,0)
		else:
			ySize = len(self.Structure) # Get matrix dimensions
			xSize = max(map(len, self.Structure))
		
			return xSize, ySize
			
	#-----------------------------------------------------------
	def Display(self):
		"""
		Display Matrix in terminal.
		"""
		for y in reversed(range(0, len(self.Structure))):
			print(y, end=" ")
			for x in range(0, len(self.Structure[y])):
				#if y == 0: 
				#	print ""
				#	for i in range(0, len(Matrix[y])):
				#		print "{0} ".format(i),
				print("[{0}] ".format(self.Structure[y][x]), end=" ")
			print("")

