import casatools as ct

cl = ct.componentlist()
caldirection = "J2000 12h00m00.0s 50d00m00.0s"
cl.addcomponent(dir=caldirection, flux=1.0, fluxunit='Jy', freq='1.4GHz', shape="Gaussian", 
                majoraxis="1arcsec", minoraxis='1arcsec', positionangle='0deg')
cl.rename('Gauss_point.cl')
cl.done()
