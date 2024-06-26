import json
import tempfile
import os

import pytest
from bs4 import BeautifulSoup, Tag

from app.src.mtbl_globals import ETLType
import app.src.build as build


# noinspection DuplicatedCode
class TestBuild:
    raw_html = []

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def setup_reg_szn(self):
        self.raw_html = []
        with open("./tests/fixtures/temp_espn_player_universe.html", "r") as f:
            self.raw_html.append(f.read())

    def setup_pre_szn(self):
        self.raw_html = []
        with open("./tests/fixtures/temp_espn_bats_universe.html", "r") as f:
            self.raw_html.append(f.read())
        with open("./tests/fixtures/temp_espn_arms_universe.html", "r") as f:
            self.raw_html.append(f.read())

    def test_build_player_universe_bs4_tag_element(self, temp_dir):
        html = ""
        with open("./tests/fixtures/single_player_row.html", "r") as f:
            html = f.read()

        html = [BeautifulSoup(html, "lxml")]
        assert isinstance(html, list)

        build.build_player_universe(etl_type=ETLType.REG_SZN,
                                    raw_html=html,
                                    output_dir=temp_dir)

        output_file = os.path.join(temp_dir, "espn_player_universe.json")
        assert os.path.exists(output_file)
        with open(output_file) as f:
            parsed_json = json.load(f)
            assert len(parsed_json[0]["name"]) > 0

    def test_build_player_universe_raw_html_bufferized_reg_szn(self, temp_dir):
        self.setup_reg_szn()

        build.build_player_universe(etl_type=ETLType.REG_SZN,
                                    raw_html=self.raw_html,
                                    output_dir=temp_dir)

        output_file = os.path.join(temp_dir, "espn_player_universe.json")
        assert os.path.exists(output_file)
        with open(output_file) as f:
            parsed_json = json.load(f)
            assert len(parsed_json[0]["name"]) > 0

    def test_build_player_universe_raw_html_bufferized_pre_szn(self, temp_dir):
        self.setup_pre_szn()

        build.build_player_universe(etl_type=ETLType.PRE_SZN,
                                    raw_html=self.raw_html,
                                    output_dir=temp_dir)

        output_file = os.path.join(temp_dir, "espn_player_universe.json")
        assert os.path.exists(output_file)
        with open(output_file) as f:
            parsed_json = json.load(f)
            assert len(parsed_json[0]["name"]) > 0

    def test_build_player_universe_no_raw_html(self, temp_dir):
        # raw_html is "", must find the temp file
        build.build_player_universe(etl_type=ETLType.REG_SZN,
                                    temp_dir="./tests/fixtures",
                                    output_dir=temp_dir)

        output_file = os.path.join(temp_dir, "espn_player_universe.json")
        assert os.path.exists(output_file)
        with open(output_file) as f:
            parsed_json = json.load(f)
            assert len(parsed_json[0]["name"]) > 0

    def test_stringify_raw_html(self):
        raw_html = build.stringify_raw_html("./tests/fixtures", ETLType.REG_SZN)

        assert len(raw_html) > 0
        assert isinstance(raw_html[0], str)

        raw_html = build.stringify_raw_html("./tests/fixtures", ETLType.PRE_SZN)

        assert len(raw_html) == 2
        assert isinstance(raw_html[0], str)

    def test_raise_load_error(self):
        with pytest.raises(build.RawHtmlLoadError) as e:
            build.stringify_raw_html(None, ETLType.PRE_SZN)
            assert str(e.value) == "raw_html cannot be empty and temp_dir None"

    def test_exit_code_load_error(self):
        with pytest.raises(SystemExit) as excinfo:
            build.build_player_universe(ETLType.PRE_SZN)
            assert excinfo.value.code == 1
