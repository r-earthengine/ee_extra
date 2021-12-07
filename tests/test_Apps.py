import unittest

import ee

from ee_extra.Apps.core import apps

ee.Initialize()


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_apps(self):
        """Test the indices() method"""
        self.assertIsInstance(apps(), dict)
        self.assertIsInstance(apps(True), dict)


if __name__ == "__main__":
    unittest.main()