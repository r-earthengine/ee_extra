# from ee_extra.JavaScript.merge import require
# from ee_extra.JavaScript.install import install
import unittest

import ee

from ee_extra import install, require

ee.Initialize()


class Test(unittest.TestCase):
    def test_module_01(self):
        """Testing Temperature modules"""
        jsmodule = "users/sofiaermida/landsat_smw_lst:modules/Landsat_LST.js"
        install(jsmodule)
        pymodule = require(jsmodule)
        self.assertTrue(pymodule)


# def test_module_02(self):
#    """Testing Temperature modules"""
#    jsmodule = "users/joselucassafanelli/TAGEE:TAGEE-functions"
#    install(jsmodule)
#    pymodule = require(jsmodule)
#    self.assertIsInstance(pymodule, dict)
#
#
# def test_module_03(self):
#    """Testing Temperature modules"""
#    jsmodule = "users/andreasvollrath/radar:slope_correction_lib.js"
#    install(jsmodule)
#    pymodule = require(jsmodule)
#    self.assertIsInstance(pymodule, dict)
#
#
# def test_module_04(self):
#    """Testing Temperature modules"""
#    jsmodule = "https://raw.githubusercontent.com/eMapR/LT-GEE/master/LandTrendr.js"
#    install(jsmodule, update=True)
#    pymodule = require(jsmodule)
#    self.assertIsInstance(pymodule, dict)

if __name__ == "__main__":
    unittest.main()
