#!python3
__all__ = ["cson2dic", "loadcsonfile", "PrintDictContent"]
import ast

def indexall(mylist, searchiterms):
	ans =[]
	for iterm in searchiterms:
		ans += [mylist.index(iterm)]
	return ans
def removeall(string, whattoremove):
	while(whattoremove in string):
		string.remove(whattoremove)
	return string
def FindAll(String, Char):
	# The Python find Sucks.It only return first found result.
	# I need the following to find all.
	# But it turn out that, xxx.split() is much better.
	Index=[]
	n=0
	Check =  String.find(Char, 0)
	while Check !=-1:
		Index.append( Check )
		n += 1
		Check = String.find(Char, Index[n-1] +1)
	return Index
def OnlyOnePattternExist(string,where, test):
	#make sure there is only one pattern exists
	if string[where[0]:where[1]] == test:
		HowManyOtherSamePattern=\
			FindAll(string,test)
		if len(HowManyOtherSamePattern) == 1:
			return True
	return False
def DeteleItemsByIndex(FullItems, WhichOneToDelete):
	for n in range(len(WhichOneToDelete)):
		FullItems[WhichOneToDelete[n]]=""
	removeall(FullItems,"")
	return FullItems
def LargestTabNumber(S, TAB="\t", SEPARATOR=":",EOL="\n"):
	if (SEPARATOR+EOL+TAB) not in S:
		return 0
	n=1
	while (SEPARATOR + EOL+n*TAB) in S:
		n+=1
	return n-1
def IsThereEmptyTabColumn(S,TAB):
	S=S.split("\n")
	IsThereEmptyTabColumn = True
	for x in S:
		if len(x)>0:
			if x !=TAB:
				return False
	return True
def HowManyEmtpyTabColumn(S,TAB="\t"):
	S=S.split("\n")
	How=[]
	for x in S:
		How+=[x.rfind(TAB)]
		#How = -1 if no TAB found
	How = min(How) + 1
	return How
def RemoveEmptyTabColumn(S,TAB="\t"):
	N = HowManyEmtpyTabColumn(S)
	y=S.split("\n")
	S = ""
	for x in y:
		x=x[N:]
		S += x + "\n"
	return S
def RemoveTabOnlyContentLessItem(Y, TAB):
	ToBeDelete = []
	for n in range(len(Y)):
		x = Y[n].replace(TAB,"")
		#print (x)
		if len(x) == 0:
			ToBeDelete += [n]
	Y = DeteleItemsByIndex(Y, ToBeDelete)
	return Y

def ScanForHowManyEscapeBefore(x, j):
	#The the value is even, then \..\\" is a valid Open/Close quot
	#If the result is odd, then \..\" is not a valid quot
	n = 0
	while x[j-n] =="\\":
		n += 1
	return n

def ScanForQuotPair(x):
	# e.g. xxx"xxx"yy"yy"
	# return [[3,7],[10,13]]
	R = []
	r = []
	n = x.find("\"")
	while n != -1 :
		if ScanForHowManyEscapeBefore(x,n)%2 == 0:
			r += [n]
			if len(r) == 2:
				R += [r]
				r = []
		n += 1
		n = x.find("\"", n)

	# If successful, r should be []
	if len(r) != 0 :
		print ("String Error: Number of Quotation Mark Not Correct")
		return []
	return R

def IsNotWithinPairedValues(v, Pair):
	# for v = 4, Pair = [[0,3], [5,7]] => return True
	# for v = 4, Pair = [[0,5], [.. , ..]] => return False
	R = True
	for P in Pair:
		if (v > P[0]) and (v < P[1]):
			R = False
			return R
	return R

def RemoveComment(text, comment="#"):
	#e.g. xxxx : "xx#xx" #comment
	#e.g. #xxx : "xx#xx" #coment
	lines = text.split("\n")
	S = ""
	for x in lines:
		m = x.find(comment)
		if  m != -1:
			QuotPair = ScanForQuotPair(x)
			if len(QuotPair) == 0:
				x = x[:m]
			else:
				while m != -1:
					if IsNotWithinPairedValues(m, QuotPair):
						x = x[:m]
						break
					m = x.find(comment, m+1)

		if len(x) != 0:
			S += x +"\n"
	return S

#print (RemoveComment("[\"#ss\",\"cc#dd\",#123"))

def RemoveUnwantedSpaceInEachLine(Y):
	RS =[]
	for x in Y:
		if "\"" in x:
			InBetweenColonAndQuot =\
			 	x[x.index(":"):x.index("\"")]
			InBetweenColonAndQuot =\
			 InBetweenColonAndQuot.replace(" ","")
			InBetweenColonAndQuot =\
			 InBetweenColonAndQuot.replace("\t","")
			AfterQuot = x[x.rindex("\"") :]
			AfterQuot = AfterQuot.replace(" ","")
			AfterQuot = AfterQuot.replace("\t","")
			BeforeFirstColon = x[: x.index(":")+1]
			BeforeFirstColon =\
			 BeforeFirstColon.replace(" ","")

			while "\t:" in BeforeFirstColon:
				BeforeFirstColon=\
				BeforeFirstColon.replace("\t:",":")
			RS += [
				BeforeFirstColon +
				InBetweenColonAndQuot[1:] +
				x[x.index("\""):x.rindex("\"")] +
				AfterQuot
			]
		else:
			BeforeFirstColon =	x[:x.index(":")+1]
			BeforeFirstColon =\
				BeforeFirstColon.replace(" ","")
			while "\t:" in BeforeFirstColon:
				BeforeFirstColon=\
				BeforeFirstColon.replace("\t:",":")
			AfterColon = x[x.index(":"):]
			AfterColon =\
				AfterColon.replace(" ","").\
				replace("\t","")
			RS += [BeforeFirstColon + AfterColon[1:]]
			#RS += [x.replace(" ","")]
	return RS
def str2val(value):
	if len(value) == 0:
		return value
	if isinstance(value, dict):
		#I have no idea how to handle this.
		#Just leave it as it is first.
		return value
	if (value[0] =="\"") &(value[-1] =="\""):
		if len(value[1:-1])==0:
			return ""
		else:
			value = value[1:-1] #get rid of " at both ends
							# e.g. "good" -> good
			return value
	if value == "true": return True
	if value == "false": return False
	value = ast.literal_eval(value)
	return value
def GetIndicesForBracketPair(S,Left="[",Right="]"):
	M1 = S.count(Left)
	M2 = S.count(Right)
	if M1 != M2:
		print ("Error: Bracket number not correct")
		return ""
	StartPoint = [0]*M1
	EndPoint = [0]*M1
	for m in range(M1):
		M=0
		Found = False
		Start = 0
		End =0
		SearchStart = 0 if m ==0 else\
					StartPoint[m-1]+1
		for n in range(SearchStart,len(S)):
			if S[n] == Left:
				if not Found :
					Found =True
					Start += n
				M += 1
			if Found == True:
				if S[n] == Right:
					M -= 1
				if M==0:
					End = n
					break
		StartPoint[m]=Start
		EndPoint[m]=End
	return list(zip(StartPoint, EndPoint))
def CleanUpStringWithinBracket(S,Left="[",Right="]"):
	M1 = S.count(Left)
	M2 = S.count(Right)
	if M1 != M2:
		print ("Error: Bracket number not correct")
		return ""
	for m in range(M1):
		BracketPosition = GetIndicesForBracketPair(S, "[","]")
		#Position=[(start, end),(start, end), ...]
		start=BracketPosition[m][0]
		end = BracketPosition[m][1]
		Y=S[start:end]
		Y=Y.replace("\t","")
		Y=Y.replace("\n","")
		Y=Y.replace(" ","")
		S=S[:start]+Y+S[end:]
	return S
def CleanUpTheScript(S):
	S=RemoveComment(S)
	S=S.strip("\n")
	#print([S])
	#print(HowManyEmtpyTabColumn(S))
	S=CleanUpStringWithinBracket(S, "[","]")
	S=CleanUpStringWithinBracket(S, "(",")")
	#S=S.replace(" ","")

	#while "\t:" in S:
	#	S=S.replace("\t:",":")

	while ":\t" in S:
		S=S.replace(":\t",":")
	while "\t\n" in S:
		S=S.replace("\t\n","\n")
	S=RemoveEmptyTabColumn(S)
	return S
def Print(S,echo=False):
	if echo:print(S)
	return
def PrintDictContent(D):
	if not isinstance(D, dict):
		return
	for x in D:
		if isinstance(D[x], dict):
			for y in D[x]:
				if isinstance(D[x][y], dict):
					for z in D[x][y]:
						print("[",x,"][",y,"][",z,"]=>",D[x][y][z])
				else:
					print ("[",x,"][",y,"]=>", D[x][y])
		else:
			print("[",x,"]=>",D[x])
def CreateDictArray(N):
	A = []
	for n in range(N):
		A += [{}]
	return A

def CreateNestedDictWithKeyArray(mydict, key, value):
	if not isinstance(mydict,dict):
		return
	if not isinstance(key, list):
		return mydict.update({key:value})
	dictarray=CreateDictArray(len(key))
	newdict = {key[-1]:value}
	for x in reversed(key[:-1]):
		temp = {}
		temp.update({x:newdict})
		#print ("temp: ", temp)
		newdict=temp
		#print ("newdict: ", newdict)
	mydict.update(newdict)
	return mydict

def __Obsolete_Bugged_cson2dic(S, TAB = "\t", SEPARATOR=":", echo=False):
	#echo=True
	S=CleanUpTheScript(S)
	N=LargestTabNumber(S)
	Y=S.split("\n")
	Y = RemoveTabOnlyContentLessItem(Y,TAB)
	Y = RemoveUnwantedSpaceInEachLine(Y)
	Identity = [[]]*len(Y)
	RootName="root"
	#Do the first round analysis
	for n in range(N+1):
		Mother = 0
		KidID = 0
		generation = n
		for i in range(len(Y)):
			if OnlyOnePattternExist(
					string=Y[i],
					where=[0,n],
					test = TAB*n):
				if Y[i-1][-1]==SEPARATOR:
					KidID=0
					Mother = i-1
					Identity[i] = [generation, Mother, KidID]
				else:
					Identity[i]=[generation, Mother, KidID]
				KidID += 1
			if Y[i][0]!=TAB:
				Identity[i]=[0,0,KidID]
				KidID += 1
	Print ("String Data:\n"+str([Y]), echo)
	Print ("ID :\n"+str(Identity), echo)
	MotherDict = []
	OffSpringIndex=0
	#Arrange into dict
	DictInEachGen = CreateDictArray(N+1)
	for n in reversed(range(N+1)):
		#n=N-m
		RootName="root"
		GodMother=0
		D={}

		for i in range(len(Y)):
			print (i,")",Identity[i][0], " ",Identity[i][1],[Y[i]])
			generationID = Identity[i][0]
			Mother = Identity[i][1]
			if generationID  == n:
				if (Mother == 0) & (n == 0):
					MotherName = RootName
					#this will avoid the identity crisis
				else:
					MotherName =\
					 Y[Mother][(n-1):-1]
				Print ("Mother's Name:	" + str([MotherName]),echo)
				Print(str(n)+") Y["+str(i)+"]=> " +str([Y[i]]),echo)
				#Get rid of the TAB
				X= Y[i][n:]
				#X=X.split(SEPARATOR)
				key=X[:X.index(":")]
				value = X[X.index(":")+1:]
				#key = X[0]
				#value=X[1]
				Print("key=>" +
							str(key) +
							"\tvalue=>" +
							str(value),echo)
				if Mother != GodMother:
					print("New Mother Found")
					GodMotherName =\
					 Y[GodMother][(n-1):-1]
					if n!=0 :
						D={GodMotherName:D}
					print ("D>>>> ",D)
					DictInEachGen[n].update(D)
					GodMother=Mother
					D={}
					if value =="":
						print("Got Kid")
						value = DictInEachGen[n-1][key]
					value=str2val(value)
					D.update({key:value})

				else:
					print("Same Mother")
					if value =="":
						print("Got Kid")
						value = DictInEachGen[n+1][key]
					value=str2val(value)
					D.update({key:value})
				#print ("D: ",D)
		GodMotherName = Y[GodMother][(n-1):-1]
		if n!=0 :
			D={GodMotherName:D}
		#print ("D>> ",D)
		DictInEachGen[n].update(D)
		#print(n," Gen:..> ",DictInEachGen[n])
	return D

def GetNumberOfForeTab(S, TAB = "\t"):
	n = 0
	while n < len(S):
		if S[n] != TAB:
			break
		n += 1
	return n
def IsEndOfSameKids(StringList, CurrentIteration,
		CurrentGeneration):

	#If it is the last line
	if CurrentIteration == (len(StringList) -1):
		return True
	# If Not the last line
	if CurrentIteration < (len(StringList) - 1):
		#print ("."*10,CurrentIteration, "..", CurrentGeneration,
		#"..", GetNumberOfForeTab(
		#StringList[CurrentIteration + 1]))
		if GetNumberOfForeTab(
		StringList[CurrentIteration + 1]) !=\
		 CurrentGeneration:
			return True
	return False


def cson2dic(S, TAB = "\t", SEPARATOR=":", echo=False):
	#echo=True
	S=CleanUpTheScript(S)
	G=LargestTabNumber(S)
	Y=S.split("\n")
	Y = RemoveTabOnlyContentLessItem(Y,TAB)
	Y = RemoveUnwantedSpaceInEachLine(Y)

	#To store the dictinary kids starting from
	#the last generation
	Bank =[]
	for g in reversed(range(G+1)):
		#A line up of Kids in the same generation
		# Kids from the same mother is stored in a same dict
		# Kids from different mothers are in the same list
		#[ {kids of same mother}, {Kids of another mother}]
		Block = []

		# Temporary Dict to store the kids of same mother
		TD = {}
		Mother = 0
		PreviousKidPlace = 0
		S = []
		for n in range(len(Y)):
			Gen = GetNumberOfForeTab(Y[n])
			if Gen == g:
				#print (g,")",[Y[n]],"[%d, %d]"%(n,PreviousKidPlace))
				# If not the same Mother
				if (n-PreviousKidPlace != 1):
					TD = {}
				X = Y[n]
				key=X[:X.index(":")][g:]
				value = X[X.index(":")+1:]

				if value=="":
					#print("This is mother")
					value = Bank[g-1][Mother]
					Mother += 1
				value=str2val(value)
				TD.update({key:value})
				#print("TD :",TD)
				if IsEndOfSameKids(Y, n, g):
					#print("This is the last kid")
					Block += [TD]
					TD = {}
				PreviousKidPlace = n
			else:
				#Make a new list to get rid of the last generation
				S += [Y[n]]
		Y = S
		#print (Y)
		#print ("...",Block)
		Bank += [Block]

	result ={}
	for x in Block:
		result.update(x)
	#print (result)
	return result

def _cson2dic(S, echo=False):
	return cson.loads(S)

def loadcsonfile(filename):
	with open(filename) as f:
		S=f.read()
		S = cson2dic(S)
	return S


#with open("attrib.cson") as f:
#with open("killme.cson") as f:
#	S=f.read()
#D=(cson2dic(S,echo=True))
#print (D)
#PrintDictContent(D)
