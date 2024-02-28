import json
import tempfile
import os

import pytest

import app.src.build as build


class TestBuild:
    raw_html = ""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        with open("tests/fixtures/temp_espn_player_universe.html", "r") as f:
            self.raw_html = f.read()

    def test_build_player_universe_raw_html_bufferized(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            build.build_player_universe(raw_html=self.raw_html, output_dir=temp_dir)

            output_file = os.path.join(temp_dir, "espn_player_universe.json")
            assert os.path.exists(output_file)
            with open(output_file) as f:
                parsed_json = json.load(f)
                assert parsed_json[0]["name"] == "Mookie Betts"

    def test_build_player_universe_no_raw_html(self):
        # raw_html is "", must find the temp file
        with tempfile.TemporaryDirectory() as temp_dir:
            build.build_player_universe(temp_dir="tests/fixtures", output_dir=temp_dir)

            output_file = os.path.join(temp_dir, "espn_player_universe.json")
            assert os.path.exists(output_file)
            with open(output_file) as f:
                parsed_json = json.load(f)
                assert parsed_json[0]["name"] == "Mookie Betts"

    def test_stringify_raw_html(self):
        raw_html = build.stringify_raw_html("tests/fixtures")

        assert len(raw_html) > 0
        assert isinstance(raw_html, str)
