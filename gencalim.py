import casatools as ct
from casatasks import exportfits

cl = ct.componentlist()
caldirection = "J2000 12h00m00.0s 50d00m00.0s"
cl.addcomponent(dir=caldirection, flux=1.0, fluxunit='Jy', freq='1.4GHz', shape="Gaussian", 
                majoraxis="1arcsec", minoraxis='1arcsec', positionangle='0deg')
#

ia = ct.image()
ia.fromshape("Gaussian.im", [256, 256, 1, 1], overwrite=True)
cs=ia.coordsys()
cs.setunits(['rad', 'rad', '', 'Hz'])
cell_rad=qa.convert(qa.quantity("1arcsec"), "rad")['value']
cs.setincrement([-cell_rad, cell_rad], 'direction')
cs.setreferencevalue([qa.convert("12h", 'rad')['value'], qa.convert("50deg", 'rad')['value']], type="direction")
cs.setreferencevalue("1.4GHz",'spectral')
cs.setincrement('0.5MHz','spectral')
ia.setcoordsys(cs.torecord())
ia.setbrightnessunit("Jy/pixel")
ia.modify(cl.torecord(), subtract=False)
exportfits(imagename='Gaussian.im', fitsimage='Gaussian.fits', overwrite=True)
