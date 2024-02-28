import tempfile
import os
import shutil

import pytest
import app.src.scrape as scrape
from mtbl_driverkit.mtbl_driverkit import TempDirType


class TestScrape:
    temp_dir = ""
    ESPN_PLAYER_RATER_BASE_URL = "https://fantasy.espn.com/baseball/playerrater?leagueId="
    LGID = os.getenv("MTBL_LGID", 'default value')

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            yield

    def test_get_espn_plyr_universe(self):
        raw_html = scrape.get_espn_plyr_universe((TempDirType.TEMP, self.temp_dir),
                                                 self.ESPN_PLAYER_RATER_BASE_URL + self.LGID)
        assert raw_html is not None
        assert len(raw_html) > 0
        assert os.path.exists(os.path.join(self.temp_dir, "temp_espn_player_universe.html"))

    def test_get_espn_plyr_universe_app_root_not_temp(self):
        project_root = os.path.abspath(os.path.dirname(__file__))
        temp_path = os.path.join(project_root, "temp")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        raw_html = scrape.get_espn_plyr_universe((TempDirType.APP, temp_path),
                                                 self.ESPN_PLAYER_RATER_BASE_URL + self.LGID)
        assert raw_html is not None
        assert len(raw_html) > 0
        assert os.path.exists(os.path.join(temp_path, "temp_espn_player_universe.html"))

        shutil.rmtree("temp")
