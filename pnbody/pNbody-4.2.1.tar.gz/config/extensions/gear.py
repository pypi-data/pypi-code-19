import os
import sys
import types

import numpy as np

from pNbody import parameters, units, ctes, cosmo
from pNbody import thermodyn

class Gear:
  def isComovingIntegrationOn(self):
    """
    return true if the file has been runned using
    the comoving integration scheme
    """
    return self.comovingintegration


  def setComovingIntegrationOn(self):
    self.comovingintegration = True

  def setComovingIntegrationOff(self):
    self.comovingintegration = False

  def ComovingIntegrationInfo(self):
    if self.isComovingIntegrationOn():
      print "ComovingIntegration"
      print "  on  (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
    else:
      print "ComovingIntegration"
      print " off"

  def spec_info(self):
    """
    Write spec info
    """	
    infolist = []
    infolist.append("")
    #infolist.append("nzero               : %s"%self.nzero)	
    #infolist.append("npart               : %s"%self.npart)		
    #infolist.append("massarr             : %s"%self.massarr)       
    infolist.append("atime               : %s"%self.atime)		
    infolist.append("redshift            : %s"%self.redshift)       
    infolist.append("flag_sfr            : %s"%self.flag_sfr)       
    infolist.append("flag_feedback       : %s"%self.flag_feedback)  
    infolist.append("nall                : %s"%self.nall)		
    infolist.append("flag_cooling        : %s"%self.flag_cooling)   
    infolist.append("num_files           : %s"%self.num_files)      
    infolist.append("boxsize             : %s"%self.boxsize)        
    infolist.append("omega0              : %s"%self.omega0)  	
    infolist.append("omegalambda         : %s"%self.omegalambda)    
    infolist.append("hubbleparam         : %s"%self.hubbleparam)   
    infolist.append("flag_age            : %s"%self.flag_age)
    infolist.append("flag_metals         : %s"%self.flag_metals)
    infolist.append("nallhw              : %s"%self.nallhw)
    infolist.append("flag_entr_ic        : %s"%self.flag_entr_ic) 
    infolist.append("critical_energy_spec: %s"%self.critical_energy_spec) 


    infolist.append("")
    if self.has_array('u'):
      infolist.append("len u               : %s"%len(self.u))
      infolist.append("u[0]                : %s"%self.u[0])
      infolist.append("u[-1]               : %s"%self.u[-1])
    if self.has_array('rho'):  
      infolist.append("len rho             : %s"%len(self.rho))
      infolist.append("rho[0]              : %s"%self.rho[0])
      infolist.append("rho[-1]             : %s"%self.rho[-1])  
    if self.has_array('rsp'):  
      infolist.append("len rsp             : %s"%len(self.rsp))
      infolist.append("rsp[0]              : %s"%self.rsp[0])
      infolist.append("rsp[-1]             : %s"%self.rsp[-1]) 
    if self.has_array('opt'):  
      infolist.append("len opt             : %s"%len(self.opt))
      infolist.append("opt[0]              : %s"%self.opt[0])
      infolist.append("opt[-1]             : %s"%self.opt[-1])     
    if self.has_array('opt2'):  
      infolist.append("len opt2            : %s"%len(self.opt2))
      infolist.append("opt2[0]             : %s"%self.opt2[0])
      infolist.append("opt2[-1]            : %s"%self.opt2[-1])     
    if self.has_array('erd'):  
      infolist.append("len erd             : %s"%len(self.erd))
      infolist.append("erd[0]              : %s"%self.erd[0])
      infolist.append("erd[-1]             : %s"%self.erd[-1]) 
    if self.has_array('dte'):  
      infolist.append("len dte             : %s"%len(self.dte))
      infolist.append("dte[0]              : %s"%self.dte[0])
      infolist.append("dte[-1]             : %s"%self.dte[-1]) 

    if self.has_array('tstar'):  
      infolist.append("len tstar           : %s"%len(self.tstar))
      infolist.append("tstar[0]            : %s"%self.tstar[0])
      infolist.append("tstar[-1]           : %s"%self.tstar[-1])

    if self.has_array('idp'):
      infolist.append("len idp             : %s"%len(self.idp))
      infolist.append("idp[0]              : %s"%self.idp[0])
      infolist.append("idp[-1]             : %s"%self.idp[-1])
      
    return infolist  

  #def select(self,tpe='gas'):
  def select(self,*arg,**kw):
    """
    Return an N-body object that contain only particles of a
    certain type, defined by in gadget:

    gas		:       gas particles
    halo	:       halo particles
    disk	:	disk particles
    bulge	:	bulge particles
    stars	:	stars particles
    bndry	:	bndry particles

    sph         :       gas with u > u_c
    sticky      :       gas with u < u_c

    """

    index = {'gas':0,'halo':1,'disk':2,'bulge':3,'stars':4,'bndry':5,'stars1':1,'halo1':2}

    # this allows to write nb.select(('gas','disk'))
    if len(arg)==1:
      if type(arg[0])==types.TupleType:
        arg = arg[0]

    tpes = arg



    # create the selection vector
    c = np.zeros(self.nbody)

    for tpe in tpes:
      if type(tpe) == types.StringType:

        if   (tpe=='sph'):
          c = c+(self.u>self.critical_energy_spec)*(self.tpe==0)

        elif (tpe=='sticky'):
          c = c+(self.u<self.critical_energy_spec)*(self.tpe==0)

        elif (tpe=='diskbulge'):
          c = c+(self.tpe==2)+(self.tpe==3)


        elif (tpe=='wg'):
          c = c+(self.u>0)*(self.tpe==0)

        elif (tpe=='cg'):
          c = c+(self.u<0)*(self.tpe==0)
        elif (tpe=='all'):
          return self



        elif not index.has_key(tpe):
          print "unknown type, do nothing %s"%(tpe)
          return self



        else:
          i = index[tpe]
          c = c+(self.tpe==i)

      elif type(tpe) == types.IntType:

        c = c+(self.tpe==tpe)


    return self.selectc(c)


    '''


    elif type(tpe) == types.StringType:

      if (tpe=='sph'):
        nb = self.select('gas')
        return nb.selectc((self.u>self.critical_energy_spec))

      if (tpe=='sticky'):
        nb = self.select('gas')
        return nb.selectc((nb.u<=nb.critical_energy_spec))



      if not index.has_key(tpe):
        print "unknown type %s"%(tpe)
        return self

      i = index[tpe]

    else:
      i = tpe


    if self.npart[i]==0:
      #print "no particle of type %s"%(tpe)
      return self.selectc(np.zeros(self.nbody))

    n1 = sum(self.npart[:i])
    n2 = n1 + self.npart[i]-1

    return self.sub(n1,n2)

    '''


  def subdis(self,mode='dd',val=None):
    """
    Equivalent of select
    """
    return self.select(mode)




  def Z(self):
    """
    total metallicity
    """
    elt = "Metals"
    idx = self.ChimieElements.index(elt)
    return np.log10(self.metals[:,idx] / self.ChimieSolarMassAbundances[elt] + 1.0e-20)


  def Fe(self):
    """
    metallicity Fe
    """
    elt = "Fe"
    idx = self.ChimieElements.index(elt)
    return np.log10(self.metals[:,idx] / self.ChimieSolarMassAbundances[elt] + 1.0e-20)



  def Mg(self):
    """
    magnesium
    """
    elt = "Mg"
    idx = self.ChimieElements.index(elt)
    return np.log10(self.metals[:,idx] / self.ChimieSolarMassAbundances[elt] + 1.0e-20)



  def O(self):
    """
    Oxygen
    """
    elt = "O"
    idx = self.ChimieElements.index(elt)
    return np.log10(self.metals[:,idx] / self.ChimieSolarMassAbundances[elt] + 1.0e-20)


  def Ba(self):
    """
    Barium
    """
    elt = "Ba"
    idx = self.ChimieElements.index(elt)
    return np.log10(self.metals[:,idx] / self.ChimieSolarMassAbundances[elt] + 1.0e-20)


  def MgFe(self):
    elt1 = "Mg"
    elt2 = "Fe"
    idx1 = self.ChimieElements.index(elt1)
    idx2 = self.ChimieElements.index(elt2)
    eps = 1e-20
    return np.log10((self.metals[:,idx1]+eps)/(self.metals[:,idx2]+eps) / self.ChimieSolarMassAbundances[elt1] * self.ChimieSolarMassAbundances[elt2])

  def BaFe(self):
    elt1 = "Ba"
    elt2 = "Fe"
    idx1 = self.ChimieElements.index(elt1)
    idx2 = self.ChimieElements.index(elt2)
    eps = 1e-20
    return np.log10((self.metals[:,idx1]+eps)/(self.metals[:,idx2]+eps) / self.ChimieSolarMassAbundances[elt1] * self.ChimieSolarMassAbundances[elt2])


  def SiFe(self):
    elt1 = "Si"
    elt2 = "Fe"
    idx1 = self.ChimieElements.index(elt1)
    idx2 = self.ChimieElements.index(elt2)
    eps = 1e-20
    return np.log10((self.metals[:,idx1]+eps)/(self.metals[:,idx2]+eps) / self.ChimieSolarMassAbundances[elt1] * self.ChimieSolarMassAbundances[elt2])



  def AbRatio(self,elt1,elt2):
    """
    return [X/Y]
    """

    if elt2=="H":
      idx1 = self.ChimieElements.index(elt1)
      return np.log10(self.metals[:,idx1] / self.ChimieSolarMassAbundances[elt1] + 1.0e-20)
    else:
      idx1 = self.ChimieElements.index(elt1)
      idx2 = self.ChimieElements.index(elt2)
      eps = 1e-20
      return np.log10((self.metals[:,idx1]+eps)/(self.metals[:,idx2]+eps) / self.ChimieSolarMassAbundances[elt1] * self.ChimieSolarMassAbundances[elt2])




  def LuminositySpec(self,tnow=None):
    """
    compute specific luminosity, per unit of Msol
    This is the new version, using units correctly

    tnow is given in code units
    """


    # initialize SSP
    from pNbody.SSP import libvazdekis
    # vazdekis_kb_mu1.3.txt : krupa 01 revisited
    self.LObj = libvazdekis.VazdekisLuminosities(os.path.join(parameters.OPTDIR,'SSP','vazdekis_kb_mu1.3.txt'))
    self.LObj.ExtrapolateMatrix(order=1,s=0)
    self.LObj.CreateInterpolator()
    self.LObj.Extrapolate2DMatrix()


    if self.tstar is None:
      return np.array([],np.float32)


    out_units = units.UnitSystem('local',[units.Unit_kpc,units.Unit_Ms,units.Unit_Gyr,units.Unit_K])



    Ages = self.StellarAge(units=out_units.UnitTime)


    if tnow is not None:
      atime = float(self.atime)

      tnow =  self.CosmicTime(units=out_units.UnitTime,age=tnow)
      atime=  self.CosmicTime(units=out_units.UnitTime,age=atime)
      AgeOffset = tnow-atime
      print "    AgeOffset %g [Gyr]"%AgeOffset


      # apply offset
      Ages = Ages + AgeOffset



    Zs   = self.Z()

    # compute luminosities using LObj
    L  = self.LObj.Luminosities(Zs,Ages)

    return L




  def Luminosity(self,tnow=None):
    '''
    Luminosity per particle in solar luminosity unit
    '''

    out_units = units.UnitSystem('local',[units.Unit_kpc,units.Unit_Ms,units.Unit_Gyr,units.Unit_K])


    # set factor unit
    funit=1.0
    if out_units.UnitMass is not None:
      funit = self.localsystem_of_units.convertionFactorTo(out_units.UnitMass)
      print "... mass factor units = %g"%funit

    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      mass = self.mass/self.hubbleparam *funit
    else:
      mass = self.mass*funit

    return self.LuminositySpec(tnow)*mass





  def Age(self):
    '''in Gyrs (for treeasph units)'''

    print "!!! please, no longer use that !!!"

    u_time = 4.7287e6
    age = (self.atime-self.tstar)*u_time*1.0e-9
    return age


  def age(self):
    '''in CU '''
    return (self.atime-self.tstar)


  def RGB(self,tnow=None,u_mass=1.e10,u_time=4.7287e6):
    """
    Compute the number of stars in each particle which are climbing the red giant branch, assuming a Kroupa IMF.
    """
    from pNbody.SSP import libbastitime

    self.NRGB = libbastitime.BastiRGB(os.path.join(parameters.OPTDIR,'SSP','basti'))

    if self.tstar is None:
      return np.array([],np.float32)
    if tnow is None:
      tnow = self.atime

    Ages = (tnow-self.tstar)*u_time*1.0e-9
    Zs   = self.Fe()
    N = self.mass*u_mass*self.NRGB.RGBs(Zs,Ages)

    return(N)




  #################################################################
  # physical values (with correct unit conversion)
  #################################################################


  def Rxyz(self,a=None,h=None,units=None,center=None):
    """
    return the radius of each particles in physical units, i.e.
    correct it from the scaling factor and h if necessary (i.e. comoving integration is on)
    """

    print "... compute Rxyz()"


    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit


    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.rxyz()*self.atime/self.hubbleparam * funit
    else:
      return self.rxyz(center=center) * funit


  def Rxy(self,a=None,h=None,units=None):
    """
    return the radius of each particles in physical units, i.e.
    correct it from the scaling factor and h if necessary (i.e. comoving integration is on)
    """

    print "... compute Rxy()"


    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit


    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.rxy()*self.atime/self.hubbleparam * funit
    else:
      return self.rxy() * funit

  def SphRadius(self,a=None,h=None,units=None):
    """
    return the sph radius of each particles in physical units, i.e.
    correct it from the scaling factor and h if necessary (i.e. comoving integration is on)
    """

    print "... compute Hsml()"


    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit


    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.rsp*self.atime/self.hubbleparam * funit
    else:
      return self.rsp * funit


  def TotalMass(self,a=None,h=None,units=None):
    '''
    return the total mass of the system

    a : scaling factor
    h : hubble parameter
    units : output units


    different cases :

      comoving integration      (self.comovingintegration==True)

        1) convert into physical coorinates
        2) if a=1 -> stay in comoving (in this case, we can also use nb.rho)

      non comoving integration (self.comovingintegration==False)

        1) do not convert
        2) if I want to force a behavior : put a=0.1 ->

    '''

    print "... compute TotalMass()"

    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit

    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.mass_tot/self.hubbleparam *funit
    else:
      return self.mass_tot*funit

  def Mass(self,a=None,h=None,units=None):
    '''
    return the mass of the particles

    a : scaling factor
    h : hubble parameter
    units : output units


    different cases :

      comoving integration      (self.comovingintegration==True)

        1) convert into physical coorinates
        2) if a=1 -> stay in comoving (in this case, we can also use nb.rho)

      non comoving integration (self.comovingintegration==False)

        1) do not convert
        2) if I want to force a behavior : put a=0.1 ->

    '''

    print "... compute Mass()"

    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit

    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.mass/self.hubbleparam *funit
    else:
      return self.mass*funit




  def Rho(self,a=None,h=None,units=None):
    '''
    return the density of particles.

    a : scaling factor
    h : hubble parameter
    units : output units


    different cases :

      comoving integration      (self.comovingintegration==True)

        1) convert into physical coorinates
        2) if a=1 -> stay in comoving (in this case, we can also use nb.rho)

      non comoving integration (self.comovingintegration==False)

        1) do not convert
        2) if I want to force a behavior : put a=0.1 ->

    '''

    print "... compute Rho()"

    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit

    if self.isComovingIntegrationOn():
      print "    converting to physical units (a=%5.3f h=%5.3f)"%(self.atime,self.hubbleparam)
      return self.rho/self.atime**3*self.hubbleparam**2 *funit
    else:
      return self.rho*funit



  def T(self):
    '''
    u does not depends on a nor h
    '''

    print "... compute T()"

    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)


    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}

    # this is the old implementation, avoid the computation of the ionization state
    #T = where((self.u>0),(gamma-1.)* (mu*mh)/k * self.u,0)

    # this is the new implementation, but may take much more time
    T = np.where((self.u>0),thermodyn.Tru(None,self.u,thermopars),0)

    return T


  def TJeans(self,Hsml=None,Softening=None,SofteningMaxPhys=None):
    '''
    Jeans temperature for a given density and Hsml.
    The Jean temperature is the temperature corresponding to
    the Jeans pressure floor for a given density and resolution (Hsml).

    '''

    print "... compute TJeans()"

    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)
    G  = ctes.GRAVITY.into(self.localsystem_of_units)
    print "Gravity constant = %g"%G

    NJ = 10	# Jeans Mass factor

    rho    = self.Rho()

    if Hsml==None and Softening==None and SofteningMaxPhys==None:
      Hsml   = self.SphRadius()
    else:

      print
      print "Hsml in TJeans:"

      if Softening!=None and SofteningMaxPhys!=None:
        print "     using Softening = %g and  SofteningMaxPhys = %g"%(Softening,SofteningMaxPhys)
        Hsml = self.ComputeSofteningCosmo(Softening,SofteningMaxPhys)

      else:
        Hsml = Hsml

      print "     using Hsml = %g (in physical units)"%Hsml
      print





    '''
    uJeans = 4./pi * NJ**(2./3.) * Hsml**2 * rho * G * (gamma-1)**(-1) * gamma**(-1)



    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}

    # this is the old implementation, avoid the computation of the ionization state
    #T = where((self.u>0),(gamma-1.)* (mu*mh)/k * self.u,0)

    # this is the new implementation, but may take much more time
    #TJeans = where((uJeans>0),thermodyn.Tru(None,uJeans,thermopars),0)
    '''

    TJeans = (mu*mh)/k * 4./np.pi * G/gamma * NJ**(2./3.) * Hsml**(2) * rho





    return TJeans







  def Told(self):
    '''
    u does not depends on a nor h
    ...> old implementation, see below
    '''

    print "... compute T()"

    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)


    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}

    # this is the old implementation, avoid the computation of the ionization state
    T = np.where((self.u>0),(gamma-1.)* (mu*mh)/k * self.u,0)

    # this is the new implementation, but may take much more time
    #T = where((self.u>0),thermodyn.Tru(None,self.u,thermopars),0)


    return T

  def Tmu(self):

    '''
    u does not depends on a nor h
    '''

    print "... compute Tmu()"

    gamma      = self.unitsparameters.get('gamma')
    xi         = self.unitsparameters.get('xi')
    ionisation = self.unitsparameters.get('ionisation')
    mu         = thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)

    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}


    # this is the new implementation, but may take much more time
    T = np.where((self.u>0),thermodyn.Tmuru(None,self.u,thermopars),0)

    return T



  def Tcool(self,units=None):
    from pNbody import cooling

    print "... compute Tcool()"

    if self.metals is None:
      FeH = np.zeros(self.nbody).astype(np.float32)
    else:
      FeH = self.metals[:,self.ChimieElements.index('Fe')]

    #l = cooling.get_lambda_from_Density_EnergyInt_FeH(self.rho,self.u,FeH)
    #dudt = l/self.rho
    #tcool   = self.u/dudt

    # parameters for the cooling

    from pNbody import cooling
    cooling_params =  self.localsystem_of_units.getparam()
    cooling_params['CoolingFile'] = "/home/epfl/revaz/.pNbody/cooling_with_metals.dat"
    cooling.init_cooling(cooling_params)

    tcool = cooling.get_cooling_time_from_Density_EnergyInt_FeH(self.Rho(),self.u,FeH)

    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit
      tcool = tcool*funit

    if self.isComovingIntegrationOn():
      print "Tcool : isComovingIntegrationOn not implemented"
      sys.exit()

    return tcool.astype(np.float32)




  def Tff(self,units=None):

    print "... compute Tff()"
    G = ctes.GRAVITY.into(self.localsystem_of_units)

    Tff   = np.sqrt(3*np.pi/(32*G*self.Rho()))

    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit
      Tff = Tff*funit

    if self.isComovingIntegrationOn():
      print "in Tff isComovingIntegrationOn is not implemented"
      sys.exit()


    return Tff.astype(np.float32)




  def Pressure(self,units=None):

    print "... compute Pressure()"

    gamma      = self.unitsparameters.get('gamma')
    mu         = 1. # not needed here : thermodyn.MeanWeight(xi,ionisation)
    mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    k          = ctes.BOLTZMANN.into(self.localsystem_of_units)

    thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}
    rho = self.Rho()

    P =	thermodyn.Pru(rho,self.u,thermopars)

    return P.astype(np.float32)




  def SoundSpeed(self,units=None):

    print "... compute SoundSpeed()"

    gamma      = self.unitsparameters.get('gamma')
    #mu         = 1. # not needed here : thermodyn.MeanWeight(xi,ionisation)
    #mh         = ctes.PROTONMASS.into(self.localsystem_of_units)
    #k          = ctes.BOLTZMANN.into(self.localsystem_of_units)

    #thermopars = {"k":k,"mh":mh,"mu":mu,"gamma":gamma}
    #rho = self.Rho()

    #P =	thermodyn.Pru(rho,self.u,thermopars)
    #C = np.sqrt(gamma*P/rho)

    C = np.sqrt(gamma*(gamma-1)*self.u)


    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit
      C = C*funit

    return C.astype(np.float32)


  def CourantTimeStep(self,units=None):

    print "... compute CourantTimeStep()"

    C = self.SoundSpeed()
    dt = self.SphRadius()/C

    return dt






  def StellarAge(self,units=None):
    '''
    stellar age
    '''
    print "... compute StellarAge()"

    age = (self.atime-self.tstar)


    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)


      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit

    if self.isComovingIntegrationOn():

      Hubble = ctes.HUBBLE.into(self.localsystem_of_units)
      pars = {"Hubble":Hubble,"HubbleParam":self.hubbleparam,"OmegaLambda":self.omegalambda,"Omega0":self.omega0}

      t1 = cosmo.CosmicTime_a(self.atime,pars) / self.hubbleparam * funit
      t2 = cosmo.CosmicTime_a(self.tstar,pars) / self.hubbleparam * funit

      age = t1-t2

      return age

    else:
      return age*funit




  def CosmicTime(self,units=None,age=None):
    """
    return cosmic time in Gyrs
    """

    print "... compute CosmicTime()"

    if age==None:
      age = self.tstar


    # set factor unit
    funit=1.0
    if units is not None:

      if (type(units)==types.StringType):
        from pNbody import units as u
        units = u.GetUnitsFromString(units)

      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit

    if self.isComovingIntegrationOn():

      Hubble = ctes.HUBBLE.into(self.localsystem_of_units)
      pars = {"Hubble":Hubble,"HubbleParam":self.hubbleparam,"OmegaLambda":self.omegalambda,"Omega0":self.omega0}
      age = cosmo.CosmicTime_a(age,pars) / self.hubbleparam * funit

      return age

    else:
      return age*funit



  def Time(self,units="Gyr"):
    """
    return time in Gyrs
    """

    print "... compute CosmicTime()"
    
    age = self.atime
	
	
    # set factor unit    
    funit=1.0
    if units is not None:
    
      if (type(units)==types.StringType):	  
        from pNbody import units as u
      	units = u.GetUnitsFromString(units)  
    
      funit = self.localsystem_of_units.convertionFactorTo(units)
      print "... factor units = %g"%funit
        
    if self.isComovingIntegrationOn():
      
      Hubble = ctes.HUBBLE.into(self.localsystem_of_units)
      pars = {"Hubble":Hubble,"HubbleParam":self.hubbleparam,"OmegaLambda":self.omegalambda,"Omega0":self.omega0}            
      age = cosmo.CosmicTime_a(age,pars) / self.hubbleparam * funit
            
      return age[0]
      
    else:
      return age[0]*funit



  def Redshift(self,age=None):
    """
    return redshift
    """
    from pNbody import cosmo

    if age==None:
      age = self.tstar


    if self.isComovingIntegrationOn():

      redshift= cosmo.Z_a(age)
    else:
      print "this is not implemented yet"
      sys.exit()

    return   redshift




  def sfr(self,dt):
    """
    star formation rate per particle

    all units are in code units
    """

    sfr = np.where( (self.atime-self.tstar) < dt, self.mass/dt ,0 )

    return sfr






  def toPhysicalUnits(self,a=None,h=None):
     """
     convert from comobile units to physical units
     correct from the scaling factor and
     from the hubble parameter
     """

     if self.isComovingIntegrationOn():

       if a is None:
         a = self.atime
       if h is None:
         h = self.hubbleparam

       print "    converting to physical units (a=%5.3f h=%5.3f)"%(a,h)

       Hubble     = ctes.HUBBLE.into(self.localsystem_of_units)
       OmegaLambda= self.omegalambda
       Omega0     = self.omega0

       print "                                 (HubbleCte  =%5.3f)"%Hubble
       print "                                 (OmegaLambda=%5.3f)"%OmegaLambda
       print "                                 (Omega0     =%5.3f)"%Omega0


       pars = {"Hubble":Hubble,"OmegaLambda":OmegaLambda,"Omega0":Omega0}

       Ha =  cosmo.Hubble_a(a,pars=pars)

       self.vel = self.pos*Ha*a + self.vel*np.sqrt(a)
       self.pos = self.pos*a/h
       self.mass= self.mass/h

       if self.has_array('u'):
         self.u   = self.u
       if self.has_array('rho'):
         self.rho = self.rho/a**2 * h**2



  def TimeStepLevel(self):
    """
    return the timestep level in log2
    """

    return (np.log10(self.opt1)/np.log10(2)).astype(int)



  def dLdt(self):
    from pNbody import cooling

    if self.metals is None:
      FeH = np.zeros(self.nbody).astype(np.float32)
    else:
      FeH = self.metals[:,self.ChimieElements.index('Fe')]

    l = cooling.get_lambda_from_Density_EnergyInt_FeH(self.rho,self.u,FeH)
    dLdt = self.mass * l/self.rho

    return dLdt.astype(np.float32)

  def GetVirialRadius(self,X=200,Rmin=0.5,Rmax=100.,center=None,omega0=None,inCodeUnits=False):

    from scipy.optimize import bisect as bisection


    # define local units
    system_of_units = self.localsystem_of_units

    if omega0==None:
      omega0 = self.omega0


    G=ctes.GRAVITY.into(system_of_units)
    H = ctes.HUBBLE.into(system_of_units)
    HubbleParam = self.hubbleparam

    rhoc = pow(H,2)*3/(8*np.pi*G)
    rhoX = rhoc*X * omega0

    print "rhoX      (code units, dX=%g)"%X,rhoX



    # output system of units (the mass units is the hydrogen mass)
    Unit_atom = ctes.PROTONMASS.into(units.cgs)*units.Unit_g
    Unit_atom.set_symbol('atom')
    out_units = units.UnitSystem('local',[units.Unit_cm,Unit_atom,units.Unit_s,units.Unit_K])

    funit = system_of_units.convertionFactorTo(out_units.UnitDensity)

    if self.isComovingIntegrationOn():
      atime = self.atime
    else:
      atime = 1.0

    print "rhoX      (code unit)",rhoX


    print "    converting to physical units (a=%5.3f h=%5.3f)"%(atime,HubbleParam)
    rhoXu = rhoX/HubbleParam**2 *funit
    print "rhoX      (atom/cm^3)",rhoXu
    print "log10rhoX (atom/cm^3)",np.log10(rhoXu)

    ############################
    # find rX using bissectrice
    ############################

    #if center!=None:
    #  self.translate(-center)
    #self.histocenter()


    rs = self.rxyz(center=center)

    def getRes(r):

      nb_s = self.selectc(rs<r)
      M    = sum(nb_s.mass)
      V    = 4/3.*np.pi*r**3

      # move to physical units
      M = M/HubbleParam
      V = V*( atime/HubbleParam )**3
      
      return M/V - rhoX


    rX = bisection(getRes, Rmin, Rmax, args = (), xtol = 0.001, maxiter = 400)


    nb_s = self.selectc(self.rxyz(center=center)<rX)
    MX    = sum(nb_s.mass)
    V    = 4/3.*np.pi*rX**3


    out_units = units.UnitSystem('local',[units.Unit_kpc,units.Unit_Msol,units.Unit_s,units.Unit_K])
    fL = system_of_units.convertionFactorTo(out_units.UnitLength)
    fM = system_of_units.convertionFactorTo(out_units.UnitMass)

    print
    print "Virial radius : r%d = %g [kpc/h comobile]"%(X,rX*fL)
    print "Virial mass   : M%d = %g [Msol/h]"%(X,MX*fM)

    print
    print "Virial radius : r%d = %g [kpc]"%(X,rX*fL/HubbleParam*atime)
    print "Virial mass   : M%d = %g [Msol]"%(X,MX*fM/HubbleParam)


    if inCodeUnits:
      return rX,MX
    else:
      return rX*fL/HubbleParam*atime,MX*fM/HubbleParam
