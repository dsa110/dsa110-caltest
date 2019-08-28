import casatools as ct

x = [0, 400, 380, 370, 410, 420, 200, -200, -400, -980, -550, -1250, -1200, -1200, -1350]
y = [-1050, -500, 350, 800, 975, 1120, 1100, 1050, 950, 775, 1000, 1120, 575, -800, -900]
names = ['DSA-101', 'DSA-102', 'DSA-103', 'DSA-104', 'DSA-105', 'DSA-106', 'DSA-107', 'DSA-108', 'DSA-109', 'DSA-110', 'DSA-111', 'DSA-112', 'DSA-113', 'DSA-114', 'DSA-115']

sm = ct.simulator()
sm.open('dsa110.ms')

me = ct.measures()
refpos = me.observatory('OVRO_MMA')                                                                                                                                                
sm.setconfig(telescopename='DSA-110', x=x, y=y, dishdiameter=[5.0]*len(x), z=[0.]*len(x), offset=[0.0],
             mount=['ALT-AZ'], antname=names, padname=names, coordsystem='local', referencelocation=refpos)

sm.setspwindow(spwname='LBand', freq='1.4GHz', deltafreq='0.5MHz', freqresolution='0.5MHz', nchannels=1, stokes='XX YY')
sm.settimes(integrationtime='1s', usehourangle=True)
#sm.setnoise(simplenoise='0.1Jy')
sm.setfeed(mode='perfect X Y')
#sm.setgain(mode='fbm', amplitude=0.1)
sm.setauto(autocorrwt=0.0)

caldir = me.direction('J2000',  '12h00m0.0', '50d0m0.000')
sm.setfield(sourcename='cal', sourcedirection=caldir)
#sourcedir = me.direction('J2000',  '12h30m0.0', '50d0m0.000')
#sm.setfield(sourcename='src', sourcedirection=sourcedir)
sm.observe(sourcename='cal', spwname='LBand', starttime='-450s', stoptime='450s')
#sm.observe(sourcename='src', spwname='LBand', starttime='900s', stoptime='1800s')  # should separate more in time

sm.predict(complist='Gauss_point.cl')

#sm.corrupt()

sm.summary()
sm.done()
