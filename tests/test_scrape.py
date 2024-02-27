import tempfile
import os

import pytest
import app.src.scrape as scrape


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
        raw_html = scrape.get_espn_plyr_universe(self.temp_dir,
                                                 self.ESPN_PLAYER_RATER_BASE_URL + self.LGID)
        assert raw_html is not None
        assert len(raw_html) > 0
        assert os.path.exists(os.path.join(self.temp_dir, "temp_espn_player_universe.html"))
