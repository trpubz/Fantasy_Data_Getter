import os
from unittest.mock import patch

import pytest

from app.__main__ import main
from app.src.mtbl_globals import ETLType


class TestMain:
    @pytest.mark.parametrize("etl_type", [ETLType.PRE_SZN, ETLType.REG_SZN])
    def test_main_success(self, etl_type):
        def load_fixture(filename):
            fixture_dir = "tests/fixtures"
            with open(os.path.join(fixture_dir, filename), 'r') as f:
                return f.read()

        class MockScraper:
            def get_espn_plyr_universe(self, url):
                pass  # No-op for this test, we already have the content

            @property
            def bats(self):
                return load_fixture("temp_espn_bats_universe.html")

            @property
            def arms(self):
                return load_fixture("temp_espn_arms_universe.html")

            @property
            def combined_table(self):
                return load_fixture("temp_espn_player_universe.html")

        with patch('app.src.scrape.Scraper.get_espn_plyr_universe') as mock_get_universe:
            mock_get_universe.return_value = None
            mock_scraper = MockScraper()

            with patch('app.src.scrape.Scraper') as mock_scraper, \
                 patch('app.src.build.build_player_universe') as mock_build, \
                 patch('shutil.rmtree') as mock_rmtree:

                main(os.getenv("MTBL_LGID"), etl_type)
                if etl_type == ETLType.PRE_SZN:
                    assert mock_scraper.bats is not None
                    assert mock_scraper.arms is not None
                mock_build.assert_called_once()
                mock_rmtree.assert_called_once()
