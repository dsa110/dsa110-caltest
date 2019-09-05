import casatools as ct

x = [0, 400, 380, 370, 410, 420, 200, -200, -400, -980, -550, -1250, -1200, -1200, -1350]
y = [-1050, -500, 350, 800, 975, 1120, 1100, 1050, 950, 775, 1000, 1120, 575, -800, -900]
names = ['DSA-101', 'DSA-102', 'DSA-103', 'DSA-104', 'DSA-105', 'DSA-106', 'DSA-107', 'DSA-108', 'DSA-109', 'DSA-110', 'DSA-111', 'DSA-112', 'DSA-113', 'DSA-114', 'DSA-115']

sm = ct.simulator()
sm.open('dsa110-calsrc.ms')

me = ct.measures()
refpos = me.observatory('OVRO_MMA')                                                                                                                                                

# TODO: confirm coordinates and set offsets from OVRO_MMA
sm.setconfig(telescopename='DSA-110', x=x, y=y, dishdiameter=[5.0]*len(x), z=[0.]*len(x), offset=[0.0],
             mount=['ALT-AZ'], antname=names, padname=names, coordsystem='local', referencelocation=refpos)

sm.setspwindow(spwname='LBand', freq='1.4GHz', deltafreq='0.5MHz', freqresolution='0.5MHz', nchannels=1, stokes='XX YY')
sm.settimes(integrationtime='1s', usehourangle=True, referencetime=58722)
#sm.setnoise(simplenoise='0.1Jy')
sm.setfeed(mode='perfect X Y')
#sm.setgain(mode='fbm', amplitude=0.1)
sm.setauto(autocorrwt=0.0)

vp = ct.vpmanager()
vp.reset()
vp.setpbairy(telescope="DSA-110", dishdiam="5m", maxrad="10deg", blockagediam="1m")
sm.setvp(dovp=True, usedefaultvp=False)

caldirstr = "J2000 12h00m00.0s 50d00m00.0s"
caldir = me.direction(*caldirstr.split())
sm.setfield(sourcename='cal', sourcedirection=caldir)
srcdirstr = "J2000 12h30m00.0s 50d00m00.0s"
sourcedir = me.direction(*srcdirstr.split())
sm.setfield(sourcename='src', sourcedirection=sourcedir)
sm.observe(sourcename='cal', spwname='LBand', starttime='-450s', stoptime='450s')  # times are in HA referenced to first source
sm.observe(sourcename='src', spwname='LBand', starttime='1350s', stoptime='2250s')

sm.predict(complist='srcs.cl')

#sm.corrupt()

sm.summary()
sm.done()
