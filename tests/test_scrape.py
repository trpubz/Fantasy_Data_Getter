import tempfile
import os
import shutil

import pytest
from mtbl_driverkit.mtbl_driverkit import TempDirType
from app.src.scrape import Scraper
from app.src.mtbl_globals import ETLType

ESPN_PLAYER_RATER_BASE_URL = "https://fantasy.espn.com/baseball/playerrater?leagueId="
ESPN_PROJECTIONS_BASE_URL = "https://fantasy.espn.com/baseball/players/projections?leagueId="


class TestScrape:
    temp_dir: tuple[TempDirType,str]
    LGID = os.getenv("MTBL_LGID", 'default value')

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # self.temp_dir = (TempDirType.TEMP, temp_dir)
            self.temp_dir = (TempDirType.TEMP, "./tests/fixtures")
            yield

    def test_get_espn_plyr_universe_reg_szn(self):
        # scraper = Scraper(self.temp_dir, ETLType.REG_SZN)
        scraper = Scraper(self.temp_dir, ETLType.REG_SZN)
        scraper.get_espn_plyr_universe(ESPN_PLAYER_RATER_BASE_URL + self.LGID)
        assert scraper.combined_table is not None
        assert len(scraper.combined_table) > 0
        assert os.path.exists(os.path.join(self.temp_dir[1], "temp_espn_player_universe_dep.html"))

    @pytest.mark.skip(reason="2024 REG SZN")
    def test_get_espn_plyr_universe_pre_szn(self):
        # scraper = Scraper(self.temp_dir, ETLType.PRE_SZN)
        scraper = Scraper(self.temp_dir, ETLType.PRE_SZN)
        scraper.get_espn_plyr_universe(ESPN_PROJECTIONS_BASE_URL + self.LGID)
        assert scraper.bats is not None
        assert scraper.arms is not None
        assert os.path.exists(os.path.join(self.temp_dir[1], "temp_espn_bats_universe.html"))
        assert os.path.exists(os.path.join(self.temp_dir[1], "temp_espn_arms_universe.html"))

    @pytest.mark.skip
    def test_get_espn_plyr_universe_app_root_not_tempfile(self):
        project_root = os.path.abspath(os.path.dirname(__file__))
        temp_path = os.path.join(project_root, "temp")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        scraper = Scraper((TempDirType.APP, temp_path), ETLType.REG_SZN)

        scraper.get_espn_plyr_universe(ESPN_PLAYER_RATER_BASE_URL + self.LGID)
        assert scraper.combined_table is not None
        assert len(scraper.combined_table) > 0
        assert os.path.exists(os.path.join(temp_path, "temp_espn_player_universe.html"))

        shutil.rmtree("./tests/temp")
