
# P1 - Tests for A* Implementation

import unittest
from pathlib import Path

from astar import astar, manhattan_distance
from dataset_loader import load_dataset


class TestAStar(unittest.TestCase):

    def setUp(self):

        # Simple map without obstacles
        self.simple_grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", ".", "."]
        ]

        # Map with an obstacle in the center
        self.obstacle_grid = [
            [".", ".", "."],
            [".", "T", "."],
            [".", ".", "."]
        ]

        # Map with an unreachable goal
        self.blocked_grid = [
            [".", "T", "."],
            [".", "T", "."],
            [".", "T", "."]
        ]

    # Test Manhattan distance
    def test_manhattan_distance(self):

        distance = manhattan_distance(
            (0, 0),
            (3, 4)
        )

        self.assertEqual(distance, 7)

    # Test if A* finds a path
    def test_path_found(self):

        result = astar(
            self.simple_grid,
            (0, 0),
            (2, 2)
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["path"][0], (0, 0))
        self.assertEqual(result["path"][-1], (2, 2))

    # Test the shortest path length
    def test_path_length(self):

        result = astar(
            self.simple_grid,
            (0, 0),
            (2, 2)
        )

        self.assertEqual(result["path_length"], 4)

    # Test pathfinding with an obstacle
    def test_obstacle_path(self):

        result = astar(
            self.obstacle_grid,
            (0, 0),
            (2, 2)
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["path_length"], 4)

    # Test if every movement in the path is valid
    def test_valid_path(self):

        result = astar(
            self.obstacle_grid,
            (0, 0),
            (2, 2)
        )

        path = result["path"]

        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))

        for index in range(len(path) - 1):

            current = path[index]
            next_position = path[index + 1]

            row_difference = abs(
                current[0] - next_position[0]
            )

            col_difference = abs(
                current[1] - next_position[1]
            )

            # Only horizontal or vertical movement is allowed
            self.assertEqual(
                row_difference + col_difference,
                1
            )

            # The next cell must be passable
            self.assertIn(
                self.obstacle_grid[next_position[0]][next_position[1]],
                {".", "G"}
            )

    # Test if A* handles unreachable goals
    def test_no_path_found(self):

        result = astar(
            self.blocked_grid,
            (0, 0),
            (0, 2)
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["path_length"])

    # Test when start and goal are the same
    def test_start_equals_goal(self):

        result = astar(
            self.simple_grid,
            (1, 1),
            (1, 1)
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["path"], [(1, 1)])
        self.assertEqual(result["path_length"], 0)

    # Test an empty map
    def test_empty_map(self):

        with self.assertRaises(ValueError):
            astar([], (0, 0), (1, 1))

    # Test maps with inconsistent row widths
    def test_inconsistent_map_width(self):

        invalid_grid = [
            [".", "."],
            ["."]
        ]

        with self.assertRaises(ValueError):
            astar(invalid_grid, (0, 0), (1, 0))

    # Test coordinates outside the map
    def test_invalid_coordinates(self):

        with self.assertRaises(ValueError):
            astar(self.simple_grid, (0, 0), (5, 5))

    # Test a blocked starting position
    def test_blocked_start(self):

        with self.assertRaises(ValueError):
            astar(self.obstacle_grid, (1, 1), (2, 2))

    # Test a blocked goal
    def test_blocked_goal(self):

        with self.assertRaises(ValueError):
            astar(self.obstacle_grid, (0, 0), (1, 1))

    # Test invalid map row width
    def test_invalid_coordinate_format(self):

        with self.assertRaises(ValueError):
            astar(self.simple_grid, [0, 0], (2, 2))

    # Test all 330 selected benchmark scenarios
    def test_all_benchmark_scenarios(self):

        required_files = [
            "dataset/arena.map",
            "dataset/arena.map.scen",
            "dataset/arena2.map",
            "dataset/arena2.map.scen",
            "dataset/brc000d.map",
            "dataset/brc000d.map.scen"
        ]

        if not all(Path(filename).exists() for filename in required_files):
            self.skipTest("DAO benchmark files are not available.")

        dataset = load_dataset(
            "dataset",
            [
                "dataset/arena.map.scen",
                "dataset/arena2.map.scen",
                "dataset/brc000d.map.scen"
            ],
            {
                "arena.map": 130,
                "arena2.map": 100,
                "brc000d.map": 100
            },
            seed=170
        )

        self.assertEqual(len(dataset["scenarios"]), 330)

        for scenario in dataset["scenarios"]:

            map_data = dataset["maps"][scenario["map_name"]]

            result = astar(
                map_data["grid"],
                scenario["start"],
                scenario["goal"]
            )

            # Check the common result structure
            self.assertIn("success", result)
            self.assertIn("path", result)
            self.assertIn("path_length", result)
            self.assertIn("nodes_explored", result)
            self.assertIn("execution_time", result)

            self.assertGreaterEqual(result["nodes_explored"], 0)
            self.assertGreaterEqual(result["execution_time"], 0)

            if result["success"]:

                self.assertEqual(
                    result["path"][0],
                    scenario["start"]
                )

                self.assertEqual(
                    result["path"][-1],
                    scenario["goal"]
                )

                self.assertEqual(
                    result["path_length"],
                    len(result["path"]) - 1
                )

            else:

                self.assertEqual(result["path"], [])
                self.assertIsNone(result["path_length"])


if __name__ == "__main__":
    unittest.main()
