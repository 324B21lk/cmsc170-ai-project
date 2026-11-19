import csv
import tempfile
import unittest
from pathlib import Path

from dataset_loader import load_dataset
from bfs import bfs
from dfs import dfs
from astar import astar
from evaluation import (
    get_algorithms,
    split_scenarios,
    check_result,
    evaluate_scenario,
    summarize_results,
    save_csv
)


class EvaluationTests(unittest.TestCase):

    def setUp(self):
        self.grid = [
            [".", ".", "."],
            ["@", "@", "."],
            [".", ".", "."]
        ]

        self.scenario = {
            "map_name": "sample.map",
            "line_number": 2,
            "start": (0, 0),
            "goal": (2, 2)
        }

    # check that bfs, dfs, and astar are included
    def test_algorithms(self):
        algorithms = get_algorithms()

        self.assertEqual(algorithms["BFS"], bfs)
        self.assertEqual(algorithms["DFS"], dfs)
        self.assertEqual(algorithms["A*"], astar)

    # check that each algorithm can be evaluated
    def test_three_algorithms(self):
        for name, algorithm in get_algorithms().items():
            result = evaluate_scenario(
                name, algorithm, {"grid": self.grid}, self.scenario, "test", 1
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["path_length"], 4)
            self.assertGreaterEqual(result["nodes_explored"], 1)
            self.assertGreaterEqual(result["execution_time_seconds"], 0)

    # check that one step in a path is valid
    def test_valid_path(self):
        result = bfs(self.grid, (0, 0), (2, 2))
        self.assertTrue(check_result(self.grid, (0, 0), (2, 2), result))

    # check that diagonal movement is rejected
    def test_diagonal_path(self):
        result = {
            "success": True,
            "path": [(0, 0), (1, 1)],
            "path_length": 1,
            "nodes_explored": 2
        }

        with self.assertRaises(ValueError):
            check_result([[".", "."], [".", "."]], (0, 0), (1, 1), result)

    # check that blocked cells are rejected
    def test_blocked_path(self):
        result = {
            "success": True,
            "path": [(0, 0), (1, 0), (2, 0)],
            "path_length": 2,
            "nodes_explored": 3
        }

        with self.assertRaises(ValueError):
            check_result(self.grid, (0, 0), (2, 0), result)

    # check that an incorrect path length is rejected
    def test_wrong_length(self):
        result = {
            "success": True,
            "path": [(0, 0), (0, 1)],
            "path_length": 2,
            "nodes_explored": 2
        }

        with self.assertRaises(ValueError):
            check_result(self.grid, (0, 0), (0, 1), result)

    # check that no path is represented correctly
    def test_no_path(self):
        result = {
            "success": False,
            "path": [],
            "path_length": None,
            "nodes_explored": 3
        }

        self.assertTrue(check_result(self.grid, (0, 0), (2, 0), result))

    # check that the same random seed makes the same split
    def test_repeatable_split(self):
        scenarios = []

        for index in range(10):
            scenarios.append({
                "map_name": "sample.map",
                "start": (0, index),
                "goal": (1, index)
            })

        first = split_scenarios(scenarios)
        second = split_scenarios(scenarios)

        self.assertEqual(first, second)
        self.assertEqual(list(first.values()).count("test"), 3)

    # check that all 330 scenarios have a split
    def test_real_dataset_split(self):
        dataset = load_dataset(
            "dataset",
            ["dataset/arena.map.scen", "dataset/arena2.map.scen", "dataset/brc000d.map.scen"],
            {"arena.map": 130, "arena2.map": 100, "brc000d.map": 100},
            seed=170
        )

        splits = split_scenarios(dataset["scenarios"])

        self.assertEqual(len(splits), 330)
        self.assertEqual(list(splits.values()).count("development"), 231)
        self.assertEqual(list(splits.values()).count("test"), 99)

    # check the average values and success rate
    def test_summary(self):
        rows = [
            {"algorithm": "BFS", "map_name": "sample.map", "split": "test",
             "success": True, "path_length": 4, "nodes_explored": 5,
             "execution_time_seconds": 0.1},
            {"algorithm": "BFS", "map_name": "sample.map", "split": "test",
             "success": False, "path_length": None, "nodes_explored": 3,
             "execution_time_seconds": 0.3}
        ]

        summaries = summarize_results(rows)
        total = [row for row in summaries if row["map_name"] == "ALL" and row["split"] == "ALL"][0]

        self.assertEqual(total["success_rate"], 50)
        self.assertEqual(total["average_path_length"], 4)
        self.assertEqual(total["average_nodes_explored"], 4)
        self.assertEqual(total["average_time_seconds"], 0.2)

    # check that csv files save the results correctly
    def test_save_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "results.csv"
            save_csv(path, [{"algorithm": "DFS", "success": True}], ["algorithm", "success"])

            with open(path, newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["algorithm"], "DFS")
            self.assertEqual(rows[0]["success"], "True")

    # check that the number of trials is valid
    def test_invalid_trials(self):
        with self.assertRaises(ValueError):
            evaluate_scenario("BFS", bfs, {"grid": self.grid}, self.scenario, "test", 0)

    # check that the test percentage is valid
    def test_invalid_percentage(self):
        with self.assertRaises(ValueError):
            split_scenarios([], test_percent=110)


if __name__ == "__main__":
    unittest.main()
