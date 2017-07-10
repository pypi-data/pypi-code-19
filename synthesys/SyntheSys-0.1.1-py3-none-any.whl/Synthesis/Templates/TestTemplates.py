#! /usr/bin/python

#====================================================================
#class Multiple_Conditional_Returns:
#	#-----------------------------------------
#	def __init__(self):
#		pass
#		
#	#-----------------------------------------
#	def BadImplementation(self):
#		"Has several problems that will prevent good QofR."
#		def acc(data):
#			int tmp = 0;
#			for i=0 in range(4):
#				tmp += data[i]
#				return tmp
#		def test(int a, int b, bool sel0, bool sel1):
#			if(sel0): return acc(a)
#			if(sel1): return acc(b)

#	#-----------------------------------------
#	def SingleReturn(self):
#		"Make the conditions mutually exclusive."
#		int acc(int data):
#			int tmp = 0
#			for(int i=0;i<4;i++):
#			tmp += data[i]
#			return tmp
#			
#		int test(int a, int b, bool sel0, bool sel1):
#			int tmp = 0
#			if(sel0): tmp = acc(a)
#			else if(sel1): tmp = acc(b)
#			return tmp
#	
#	#-----------------------------------------
#	def ConditionalReturnToBypassCode(self):
#		"Only adds “b” to “tmp” if “sel0” is false."
#		tmp = 0
#		tmp += a
#		if(sel0): return tmp
#		tmp += b
#		return tmp
#	
#	#-----------------------------------------
#	def UsingFlagsToBypassCode(self):
#		"Replaces the conditional return with a flag that is set conditionally."
#		bool flag = false
#		tmp = 0
#		tmp += a
#		if(sel0): flag = true;
#		if(flag): tmp += b;
#		return tmp
#		
##====================================================================
#class MappingArraysToMemories:
#	#-----------------------------------------
#	def __init__(self):
#		pass
#		
#	#-----------------------------------------
#	def SimpleLoopLeftRolled(self):
#		"""
#		Requires four clock cycles, or four 32-bit memory reads, to read the data from the memory and write the output to 'dout'.
#			> One memory read per iteration of ACCUM.
#		"""
#		def accumulate(int din, int &dout):
#			int acc=0
#			for(int i=0;i<4;i++):
#				acc += din[i]
#			dout = acc
#			
#	#-----------------------------------------
#	def AutomaticMemoryMergingNotConditional():
#		"""
#		Boucle déroulée d'un facteur 2:
#			Solution : Une seule lecture d'un vecteur deux fois plus large.
#		Si lecture conditionnelle (Non-Mutually Exclusive Memory Accesses) 
#			=> limite le pipeline et moins efficace que totalement enroulée.
#		"""
#		def accumulate(int din, int &dout):
#			int acc=0
#			for(int i=0;i<4;i++):
#				acc += din[i]
#			dout = acc
#		
#			
#	#-----------------------------------------
#	def AutoMergingMutExMemoryAccesses():
#		"""
#		Explicit mutual exclusivity by using an 'if-else' statement.
#		"""
#		def accumulate(int din, int &dout, bool &flag0, bool &flag1){
#			int acc=0
#			for(int i=0;i<4;i++):
#				if(flag0):      acc += din[i]
#				else if(flag1): acc -= din[i]/2
#			dout = acc
#			
#	#-----------------------------------------
#	def ManuallyMergingNonMutExMemoryAccesses():
#		"""
#		Explicit non mutual exclusivity by using an 'tmp' variable.
#		"""
#		def accumulate(int din[4], int &dout, bool &flag0, bool &flag1):
#			int acc=0
#			int tmp # 
#			ACCUM:for(int i=0;i<4;i++):
#				tmp = din[i]
#				if(flag0): acc += tmp
#				if(flag1): acc -= tmp/2
#			dout = acc
#	
#		
##====================================================================
#class ShiftRegisters:
#	#-----------------------------------------
#	def __init__(self):
#		pass
#		
#	#-----------------------------------------
#	def BasicShiftRegister(self):
#		"""
#		The “static” declaration is required so that the past values of “din” stored in “regs” persist between calls to the shift_reg
#function.
#		Problem: the function cannot be reused if multiple shift registers are needed.
#		"""	
#		# If multiple shift registers are required the user must either create a separate function for each shift register, or use C++ template functions or classes to uniqueify the implementation.	
#		def shift_reg(dType din, dType dout[N_REGS]):
#			"Note: There is no clock, reset, enable"
#			static dType regs[N_REGS]
#			SHIFT:for(int i=N_REGS-1;i>=0;i--):
#				if(i==0):
#					regs[i] = din
#				else:
#					regs[i] = regs[i-1]
#			WRITE:for(int i=0;i<N_REGS;i++):
#				dout[i] = regs[i]
#				
#		
#	#-----------------------------------------
#	def ShiftRegisterWithDataEnable():
#		"""
#		Added a data enable signal to control the shifting of 'regs'
#		
#		Boolean signal "en" is used to control whether or not the SHIFT loop body is executed. If "en" is true then the shift occurs, otherwise the values stored in "regs" are held. Figure 6-2 shows the hardware diagram for Example 6-2. The "en" signal that was added to the design causes a feedback MUX to be inserted at the input of each register to hold the output when "en" is false. This feedback MUX can then be transformed into a clock gate during the downstream RTL synthesis process.
#		"""
#		def shift_reg(dType din, dType dout[N_REGS],bool en):
#			static dType regs[N_REGS]
#			SHIFT:for(int i=N_REGS-1;i>=0;i--):
#				if(en):
#					if(i==0): regs[i] = din
#					else: regs[i] = regs[i-1]
#			WRITE:for(int i=0;i<N_REGS;i++):
#				dout[i] = regs[i]
#		
#	#-----------------------------------------
#	def ShiftRegisterWithSynchronousClear():
#		"""
#		Shift register can be enhanced to allow clearing of all registers based on a control signal
#		"""
#		def shift_reg(dType din, dType dout[N_REGS],bool srst){
#			static dType regs[N_REGS];
#			SHIFT:for(int i=N_REGS-1;i>=0;i--):
#				if(srst): regs[i] = 0;
#				else:
#					if(i==0): regs[i] = din;
#					else: regs[i] = regs[i-1]
#				
#			WRITE:for(int i=0;i<N_REGS;i++):
#				dout[i] = regs[i]
#		
#	#-----------------------------------------
#	def ShiftRegisterWithLoad():
#		"""
#		A synchronous load can be added to the shift register to load "regs" from the design interface.
#		"""
#		def shift_reg(dType din, dType load_data[N_REGS],dType dout[N_REGS], bool load)
#			static dType regs[N_REGS]
#			SHIFT:for(int i=N_REGS-1;i>=0;i--):
#				if(load): regs[i] = load_data[i]
#				else:
#					if(i==0): regs[i] = din
#					else:     regs[i] = regs[i-1]
#			
#			WRITE:for(int i=0;i<N_REGS;i++):
#				dout[i] = regs[i]
#		
#	#-----------------------------------------
#	def Shift Register Function Template():
#		"""
#		templatized version of the basic shift register.
#		"""
#		template<int ID, typename dataType, int NUM_REGS>
#		def shift_reg(dataType din, dataType dout[NUM_REGS]){
#			static dataType regs[NUM_REGS];
#			SHIFT:for(int i=NUM_REGS-1;i>=0;i--){
#			if(i==0)
#			regs[i] = din;
#			else
#			regs[i] = regs[i-1];
#			}
#			WRITE:for(int i=0;i<NUM_REGS;i++)
#			dout[i] = regs[i];
#		}
#		def shift_reg_instances(int din0, char din1, int dout0[N_REGS0],char
#			dout1[N_REGS1]){
#			shift_reg<1,int,N_REGS0>(din0,dout0);
#			shift_reg<2,char,N_REGS1>(din1,dout1);
#			}
#	
#		
##====================================================================
#class  FindingTheMaximumValueInArray:	
#		
#	
#		
##====================================================================
#class  MemoryInterleaving:
#		
#	#-----------------------------------------
#	def BasicAutoInterleaving():
#		"""
#		The memories are organized so that each one of the three reads occur from a separate memory, allowing the design to run with II=1.
#		"""	
#		void interleave(ac_int<8> x_in[NUM_WORDS], ac_int<8> y[NUM_WORDS/3],
#		bool load){
#		static ac_int<8> x[NUM_WORDS];
#		int idx = 0;
#		if(load)
#		for(int i=0;i<NUM_WORDS;i+=1)
#		x[i] = x_in[i];
#		else
#		for(int i=0;i<NUM_WORDS;i+=3)
#		y[idx++] = x[i]+x[i+1]+x[i+2];
#		}
#		
#	#-----------------------------------------
#	def BasicManualInterleaving():
#		"""
#		The memories are organized so that each one of the three reads occur from a separate memory, allowing the design to run with II=1.
#		"""
#		def interleave_manual(ac_int<8> x_in[NUM_WORDS],
#			ac_int<8> y[NUM_WORDS/3], bool load){
#			static interleave_mem<ac_int<8>,NUM_WORDS> x;
#			int idx = 0;
#			if(load)
#			for(int i=0;i<NUM_WORDS;i+=1)
#			x.write(i,x_in);
#			else
#			for(int i=0;i<NUM_WORDS;i+=3)
#			y[idx++] = x.read(i,0) + x.read(i,1) + x.read(i,2);
#			}	

#		
##====================================================================
#class  WideningWordWidthOfMemories:
#		
#	#-----------------------------------------
#	def ManualWidening():
#		"""
#		The memories are organized so that each one of the three reads occur from a separate memory, allowing the design to run with II=1.
#		"""
#		def word_width_manual(ac_int<8> x_in[NUM_WORDS],
#			ac_int<8> y[NUM_WORDS/3], bool load){
#			static word_width_mem<8,true,NUM_WORDS> x;
#			int idx = 0;
#			if(load)
#			for(int i=0;i<NUM_WORDS;i+=1)
#			x.write(i,x_in);
#			else
#			for(int i=0;i<NUM_WORDS/3;i+=1)
#			y[idx++] = x.read(i,0) + x.read(i,1) + x.read(i,2);
#			}











		
