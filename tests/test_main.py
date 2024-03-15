import importlib
import os

import pytest

from app.__main__ import main


class TestMain:
    raw_html = ""

    @pytest.fixture
    def mock_scrape(self, monkeypatch):
        def mock_get_espn_plyr_universe(*args, **kwargs):
            with open("tests/fixtures/temp_espn_player_universe.html", "r") as f:
                return f.read()

        monkeypatch.setattr("app.src.scrape.get_espn_plyr_universe",
                            mock_get_espn_plyr_universe)

    def test_main_success(self, mock_scrape):
        # importlib.reload(scrape)
        main(os.getenv("MTBL_LGID"))
