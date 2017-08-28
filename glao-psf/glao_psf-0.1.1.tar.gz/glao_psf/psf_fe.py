"""Front end (test)
"""
import os
import sys
import time
flush = sys.stdout.flush
import ConfigParser as cp
import psf as p
import numpy as np
import infoArray
import warnings
if 'VIRTUAL_ENV' in os.environ:
    from matplotlib.backends.backend_pdf import PdfPages

def run(configFile=None,verbose=True):
    global a
    
    #------- default arguments --------
    defaults={
        'ngs':3,
        'geom':'circle',
        'rot': '45.',
        'radius':'6 arcmin',
        'profile':'MaunaKea 30 N',
        'outer_scale':'30 meters',
        'r0': '',
        'DM_conjugate': '-280 meters',
        'actuator_spacing': '0 cm',
        'wavelength':'0.5 microns',
        'field_points': '0., 2.5, 4., 5.',
        'filename':'psf.fits',
        'seeing_psf_filename':None
    }
    
    t0 = time.time()
    #-------- read arguments from config file ------
    if verbose:
        print 'reading config params...',; flush()
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    exampleConfigFile = os.path.join(dir_path,'example.cfg')

    if configFile is None:
        configFile = exampleConfigFile
    
    if not os.path.isfile(configFile):
        if configFile == 'example.cfg':
            configFile = exampleConfigFile
        else:
            raise IOError,'no file named %s'%configFile

    if configFile == exampleConfigFile:
        print ''
        print 'WARNING using example config file from code source directory'
        print '%s'%exampleConfigFile
            
    config  = cp.ConfigParser(defaults)
    config.read(configFile)
    
    ngs = config.get('constellation','ngs')
    geom = config.get('constellation','geom')
    radius = config.get('constellation','radius')
    rot = config.get('constellation','rot')
    profile = config.get('atmosphere','profile')
    outer_scale = config.get('atmosphere','outer_scale')
    r0 = config.get('atmosphere','r0')
    zc = config.get('AO','DM_conjugate')
    actSpacing = config.get('AO','actuator_spacing')
    wavelength = config.get('image','wavelength')
    fieldpts = config.get('image','field_points')
    filename = config.get('output','filename')
    seeing_psf_filename = config.get('output','seeing_psf_filename')
    
    #---------- parse and interpret arguments -------
    ngs = int(ngs)
    r= radius.split()
    radius = float(r[0])
    if len(r) > 1:
        ufac = {'arcmin':1,'arcsec':60}[r[1]]
        radius *= ufac
    r= outer_scale.split()
    outer_scale = float(r[0])
    if len(r) > 1:
        ufac = {'meter':1,'meters':1,'m':1,'cm':0.01}[r[1]]
        outer_scale *= ufac
    r= wavelength.split()
    wavelength = float(r[0])
    if len(r) > 1:
        ufac = {'micron':1,'microns':1,'angstrom':0.1,'angstroms':0.1}[r[1]]
        wavelength *= ufac
    r= zc.split()
    zc = float(r[0]) # only units of meters is allowed
    r= fieldpts.split(',')
    fieldpts = map(float,r)
    rot = float(rot)
    r= actSpacing.split()
    actSpacing= float(r[0])
    if len(r) > 1:
        ufac= {'m':1,'meter':1,'meters':1,'cm':0.01}[r[1]]
        actSpacing *= ufac
    if actSpacing < 0.01:
        actSpacing = None # spacing less than a centimeter => 'infinite' sampling
    
    valid_profiles = p.available(show=False)
    assert profile in valid_profiles, 'profile must be one of %r'%valid_profiles
    
    t1 = time.time()
    if verbose:
        print '(%.3f sec)'%(t1-t0); t0=t1
    #---------- do PSF calculation -------
        print 'doing PSF calculation...',; flush()
    N = ngs
    a = p.Cn2_Profile(profile,L0=outer_scale,lam=wavelength,sf_method='new')
    n = 256
    field_point = [fieldpts[0],0.]
    c = p.Constellation(N,radius,'circle',rot=rot,field_point = field_point)
    r_lim = a.r0*n/8.
    a.make_S(c,r_lim=r_lim,n=n,dm_conjugate=zc,wfs_conjugate=zc, act_spacing = actSpacing)
    w = np.zeros(N+1)
    w[0] = -1
    w[1:] = np.ones(N)/float(N)
    a.make_PSF(w)
    
    t1 = time.time()
    if verbose:
        print '(%.3f sec)'%(t1-t0); t0=t1
    #---------- save result --------
        print 'saving result...',; flush()
    keys_a = ['name','site','tile','Cn2','Cn2_units','Cn2_bar',
            'databaseFile','databaseMetadata',
            'r0','r0_units','r00','r00_units','spatialFilter',
            'theta0','theta0_units',
            'L0','L0_units',
            'dm_conjugate','dm_conjugate_units',
            'wfs_conjugate','wfs_conjugate_units']
    transkey = {'name':'profile','databaseFile':'dbFile','databaseMetadata':'dbMeta'}
    keys_c = ['N','field_point','geometry','radius','radius_units',
              'rotation','rotation_units']
    
    if a.spatialFilter is not False:
        keys_a += ['act_spacing']
    
    hdu = a.PSF._hdu()
    hdr = hdu.header
    hdr.append(('COMMENT','--- Guide Star Constellation ---'),end=True)
    d = a.constellation.__dict__
    for key in keys_c:
        if not key.endswith('_units'):
            kwd = key.upper()[:8]
            val = d[key]
            if isinstance(val,(tuple,list,np.ndarray)):
                val = str(str(val))
            if isinstance(val,dict):
                val = str(val)
            if isinstance(val,float):
                val = ['Infinity',val][np.isfinite(val)]
            card = (kwd,val)
            if key+'_units' in keys_c:
                cmt = d[key+'_units']
                card = card + (cmt,)
            hdr.append(card,end=True)
    d = a.__dict__
    hdr.append(('COMMENT','--- Atmosphere characteristics ---'),end=True)
    for key in keys_a:
        if not key.endswith('_units'):
            if key in transkey:
                kwd = transkey[key]
            else:
                kwd = key.upper()[:8]
            val = d[key]
            if isinstance(val,(tuple,list,np.ndarray)):
                val = str(list(val))
            if isinstance(val,dict):
                val = str(val)
            if isinstance(val,float):
                val = ['Infinity',val][np.isfinite(val)]
            card = (kwd,val)
            if key+'_units' in keys_a:
                cmt = d[key+'_units']
                card = card + (cmt,)
            hdr.append(card,end=True)
    
    
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',module='pyfits')
        hdu.writeto(filename,clobber=True)
    
    a.PSF_seeing.profile = a.profile
    a.PSF_seeing.Cn2 = str(list(a.Cn2))
    a.PSF_seeing.L0 = ['Infinity',a.L0][np.isfinite(a.L0)]
    a.PSF_seeing.L0_units = a.L0_units
    hdu = a.PSF_seeing._hdu()
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',module='pyfits')
        hdu.writeto(seeing_psf_filename,clobber=True)
    
    t1 = time.time()
    if verbose:
        print '(%.3f sec)'%(t1-t0); t0=t1
        print 'done'; flush()

def summary():
    print 'GLAO PSF ENA = %0.4f %s'%(a.PSF.ena,a.PSF.ena_units)
    print 'Seeing PSF ENA = %0.4f %s'%(a.PSF_seeing.ena,a.PSF_seeing.ena_units)
    print 'GLAO PSF ENA_r = %0.4f %s'%(a.PSF.ena_r,'arcsec')
    print 'Seeing PSF ENA_r = %0.4f %s'%(a.PSF_seeing.ena_r,'arcsec')
    if 'VIRTUAL_ENV' in os.environ:
        gfile = 'glao_psf_summary.pdf'
        pp = PdfPages(gfile)
        a.constellation.graph()
        pp.savefig()
        a.PSF.graph()
        a.PSF_seeing.graph(oplot=True)
        pp.savefig()
        a.PSF.show()
        pp.savefig()
        a.PSF_seeing.show()
        pp.savefig()
        pp.close()
        print 'Graphs written to %s'%gfile
    else:
        a.constellation.graph()
        a.PSF.graph()
        a.PSF_seeing.graph(oplot=True)
        a.PSF.show()
        a.PSF_seeing.show()
        

if __name__ == 'main':
    if len(sys.argv >1):
        configFile = sys.argv[1]
    else:
        configFile = 'example.cfg'
    run(configFile)
