import pytest


class TestScrape:
    def runSavant(self):
        getSavantData(statcastData=Savant.xStats)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
