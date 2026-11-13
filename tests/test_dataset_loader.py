import tempfile
import unittest
from pathlib import Path

from dataset_loader import load_map, load_scenarios, validate_scenario, load_dataset


class DatasetLoaderTests(unittest.TestCase):

    def setUp(self):
        self.temp_folder = tempfile.TemporaryDirectory()
        self.dataset_folder = Path(self.temp_folder.name)

        # create a small map for testing
        map_text = (
            "type octile\n"
            "height 3\n"
            "width 3\n"
            "map\n"
            "...\n"
            ".T.\n"
            "...\n"
        )

        (self.dataset_folder / "sample.map").write_text(map_text, encoding="utf-8")

    def tearDown(self):
        self.temp_folder.cleanup()

    # create a scenario file for testing
    def write_scenarios(self, lines):
        filename = self.dataset_folder / "sample.map.scen"
        filename.write_text("version 1\n" + "\n".join(lines) + "\n", encoding="utf-8")
        return filename

    # check the map dimensions and cell types
    def test_load_map(self):
        map_data = load_map(self.dataset_folder / "sample.map")
        self.assertEqual(map_data["height"], 3)
        self.assertEqual(map_data["width"], 3)
        self.assertEqual(len(map_data["passable_cells"]), 8)
        self.assertEqual(len(map_data["blocked_cells"]), 1)
        self.assertEqual(map_data["grid"][1][1], "T")

    # check if the map dimensions are wrong
    def test_wrong_map_dimensions(self):
        filename = self.dataset_folder / "wrong.map"
        filename.write_text("type octile\nheight 2\nwidth 3\nmap\n...\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_map(filename)

    # check if there is an unknown terrain symbol
    def test_unknown_terrain(self):
        filename = self.dataset_folder / "unknown.map"
        filename.write_text("type octile\nheight 1\nwidth 2\nmap\n.?\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_map(filename)

    # check the scenario coordinates
    def test_load_scenarios(self):
        filename = self.write_scenarios(["0 sample.map 3 3 0 2 2 0 2.828427"])
        scenarios = load_scenarios(filename)
        self.assertEqual(len(scenarios), 1)
        self.assertEqual(scenarios[0]["start"], (2, 0))
        self.assertEqual(scenarios[0]["goal"], (0, 2))

    # check if the scenario version is missing
    def test_missing_version(self):
        filename = self.dataset_folder / "sample.map.scen"
        filename.write_text("0 sample.map 3 3 0 0 2 2 2.828427\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_scenarios(filename)

    # check if the scenario version is unsupported
    def test_invalid_version(self):
        filename = self.dataset_folder / "sample.map.scen"
        filename.write_text("version 2\n0 sample.map 3 3 0 0 2 2 2.828427\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_scenarios(filename)

    # check if the start or goal is blocked
    def test_blocked_position(self):
        map_data = load_map(self.dataset_folder / "sample.map")
        scenario = {"map_name": "sample.map", "map_width": 3, "map_height": 3,
                    "start": (1, 1), "goal": (2, 2)}
        with self.assertRaises(ValueError):
            validate_scenario(map_data, scenario)

    # check if the start or goal is outside the map
    def test_outside_position(self):
        map_data = load_map(self.dataset_folder / "sample.map")
        scenario = {"map_name": "sample.map", "map_width": 3, "map_height": 3,
                    "start": (3, 0), "goal": (2, 2)}
        with self.assertRaises(ValueError):
            validate_scenario(map_data, scenario)

    # check if the scenario dimensions do not match
    def test_scenario_dimensions(self):
        map_data = load_map(self.dataset_folder / "sample.map")
        scenario = {"map_name": "sample.map", "map_width": 4, "map_height": 3,
                    "start": (0, 0), "goal": (2, 2)}
        with self.assertRaises(ValueError):
            validate_scenario(map_data, scenario)

    # check if duplicate and invalid scenarios are removed
    def test_remove_duplicates_and_invalid(self):
        filename = self.write_scenarios([
            "0 sample.map 3 3 0 0 2 2 2.828427",
            "0 sample.map 3 3 0 0 2 2 2.828427",
            "0 sample.map 3 3 1 1 2 2 1.414214",
            "0 sample.map 3 3 4 0 2 2 2.828427",
            "1 sample.map 3 3 0 1 2 1 2.0"
        ])
        dataset = load_dataset(self.dataset_folder, filename)
        counts = dataset["scenario_counts"]["sample.map"]
        self.assertEqual(counts["invalid"], 2)
        self.assertEqual(counts["duplicates"], 1)
        self.assertEqual(counts["available"], 2)
        self.assertEqual(counts["selected"], 2)

    # check if the fixed seed gives the same scenarios
    def test_repeatable_selection(self):
        filename = self.write_scenarios([
            "0 sample.map 3 3 0 0 2 2 2.828427",
            "1 sample.map 3 3 0 1 2 1 2.0",
            "2 sample.map 3 3 0 2 2 0 2.828427"
        ])
        first = load_dataset(self.dataset_folder, filename, {"sample.map": 2}, seed=170)
        second = load_dataset(self.dataset_folder, filename, {"sample.map": 2}, seed=170)
        self.assertEqual(first["scenarios"], second["scenarios"])
        self.assertEqual(len(first["scenarios"]), 2)

    # check if the requested number is too large
    def test_too_many_scenarios(self):
        filename = self.write_scenarios(["0 sample.map 3 3 0 0 2 2 2.828427"])
        with self.assertRaises(ValueError):
            load_dataset(self.dataset_folder, filename, {"sample.map": 3})

    # check the full dataset if all six dao files are available
    def test_real_dao_dataset(self):
        dataset_folder = Path(__file__).resolve().parent.parent / "dataset"
        filenames = [dataset_folder / "arena.map.scen",
                     dataset_folder / "arena2.map.scen",
                     dataset_folder / "brc000d.map.scen"]

        if not all(filename.exists() for filename in filenames):
            self.skipTest("The full DAO dataset is not in this project folder.")

        dataset = load_dataset(dataset_folder, filenames,
                               {"arena.map": 130, "arena2.map": 100, "brc000d.map": 100},
                               seed=170)
        self.assertEqual(len(dataset["maps"]), 3)
        self.assertEqual(len(dataset["scenarios"]), 330)
        self.assertEqual(sum(counts["invalid"] for counts in dataset["scenario_counts"].values()), 0)
        self.assertEqual(sum(counts["duplicates"] for counts in dataset["scenario_counts"].values()), 0)


if __name__ == "__main__":
    unittest.main()
