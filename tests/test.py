import unittest

from Globals import Savant
from app.main import getSavantData


class TestSavant(unittest.TestCase):
    def runSavant(self):
        getSavantData(statcastData=Savant.xStats)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
