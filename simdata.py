import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import casatools as ct
import os.path
import shutil


def gensources(complist='src.cl', caldirection="J2000 12h00m00.0s 50d00m00.0s", calflux=1.0,
               srcdirection="J2000 12h30m00.0s 50d00m00.0s", srcflux=1.0,
               freq='1.4GHz'):
    """ Create component list
    """

    if os.path.exists(complist):
        logger.info("Removing existing file, {0}".format(complist))
        shutil.rmtree(complist)

    # assume compact sources
    cl = ct.componentlist()
    cl.addcomponent(dir=caldirection, flux=calflux, fluxunit='Jy', freq=freq, shape="Gaussian", 
                    majoraxis="1arcsec", minoraxis='1arcsec', positionangle='0deg')
    if srcdirection is not None:
        cl.addcomponent(dir=srcdirection, flux=srcflux, fluxunit='Jy', freq=freq, shape="Gaussian", 
                        majoraxis="1arcsec", minoraxis='1arcsec', positionangle='0deg')
    cl.rename(complist)
    cl.done()

# creating FIRST model image
# Note that header from FIRST archive only has two axes. Need to force definition on import.
# casatasks.importfits(fitsimage='first_12h+50d.fits', imagename='first_12h+50d.ms', beam=["5arcsec", "5arcsec", "0deg"], overwrite=True, defaultaxes=True, defaultaxesvalues=[180.0, 50.0, 1400000000.0, 'I'])

def simulate(imagename='', complist='', msname='dsa110-calsrc.ms', freq='1.4GHz', integrationtime='1s',
             diameter=5.0, noise='0Jy', gainnoise=0.,
             calobsdir = "J2000 12h00m00.0s 50d00m00.0s", srcobsdir="J2000 12h30m00.0s 50d00m00.0s"):
    """ Use source model to generate simulated ms for a few DSA antennas.
    """

    # outriggers
    x = [0, 400, 380, 370, 410, 420, 200, -200, -400, -980, -550, -1250, -1200, -1200, -1350]
    y = [-1050, -500, 350, 800, 975, 1120, 1100, 1050, 950, 775, 1000, 1120, 575, -800, -900]
    names = ['DSA-101', 'DSA-102', 'DSA-103', 'DSA-104', 'DSA-105', 'DSA-106', 'DSA-107', 'DSA-108', 'DSA-109', 'DSA-110', 'DSA-111', 'DSA-112', 'DSA-113', 'DSA-114', 'DSA-115']

    if os.path.exists(msname):
        logger.info("Removing existing file, {0}".format(msname))
        shutil.rmtree(msname)

    sm = ct.simulator()
    sm.open(msname)

    me = ct.measures()
    refpos = me.observatory('OVRO_MMA')                                                                                                                                                
    # TODO: confirm coordinates and set offsets from OVRO_MMA
    sm.setconfig(telescopename='DSA-110', x=x, y=y, dishdiameter=[diameter]*len(x), z=[0.]*len(x), offset=[0.0],
                 mount=['ALT-AZ'], antname=names, padname=names, coordsystem='local', referencelocation=refpos)

    sm.setspwindow(spwname='LBand', freq=freq, deltafreq='0.5MHz', freqresolution='0.5MHz', nchannels=1, stokes='XX YY')
    sm.settimes(integrationtime=integrationtime, usehourangle=True, referencetime=58722)
    sm.setfeed(mode='perfect X Y')
    sm.setauto(autocorrwt=0.0)

    vp = ct.vpmanager()
    vp.reset()
    vp.setpbairy(telescope="DSA-110", dishdiam="5m", maxrad="10deg", blockagediam="1m")
    sm.setvp(dovp=True, usedefaultvp=False)

    if calobsdir is not None:
        sm.setfield(sourcename='cal', sourcedirection=me.direction(*calobsdir.split()))
    if srcobsdir is not None:
        sm.setfield(sourcename='src', sourcedirection=me.direction(*srcobsdir.split()))

    if calobsdir is not None:
        sm.observe(sourcename='cal', spwname='LBand', starttime='-450s', stoptime='450s')  # times are in HA referenced to first source
    if srcobsdir is not None:
        sm.observe(sourcename='src', spwname='LBand', starttime='1350s', stoptime='2250s')  # 30min later

    sm.predict(complist=complist, imagename=imagename)
    sm.setnoise(mode='simplenoise', simplenoise=noise)
    sm.setgain(mode='fbm', amplitude=gainnoise)
    sm.corrupt()

    sm.summary()
    sm.done()


def read(msname='dsa110-calsrc.ms'):
    """ Read simulated ms and return data
    """

    ms = ct.ms()                                                                                                                                                    
    ms.open('dsa110-calsrc.ms')                                                                                                                                     
    dd = ms.getdata(items=['data', 'axis_info', 'uvw'], ifraxis=True)                                                                                               
    data = dd['data']                                                                                                                                               
#    times = dd['axis_info']['time_axis']['MJDseconds']                                                                                                              
#    plt.plot(data[...,0].flatten().real, data[...,0].flatten().imag, '.')  
    logger.info("Read data of shape: {0}".format(data.shape))

    return data


def solve(msname='dsa110-calsrc.ms', calname='cal.G', apply=False, show=True):
    cb = ct.calibrater()
    cb.open(msname)
    cb.setsolve(type='G', t=900., table=calname, phaseonly=True, refant=0)
    cb.solve()

    if show:
        cb.listcal(caltable=calname)

    if apply:
        cb.correct()


def image(msname='dsa110-calsrc.ms'):
    im = ct.imager() 
    im.open(msname)

    im.defineimage(nx=128, ny=128) 
    im.clean(image='test.im', complist='test.cl', niter=0)  # CRASH
