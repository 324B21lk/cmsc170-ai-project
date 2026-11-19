import unittest
from bfs import bfs


class BFSTests(unittest.TestCase):

    def check_path(self, grid, path, start, goal):
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        for position in path:
            self.assertIn(grid[position[0]][position[1]], {".", "G"})
        for first, second in zip(path, path[1:]):
            difference = abs(first[0] - second[0]) + abs(first[1] - second[1])
            self.assertEqual(difference, 1)

    def test_direct_path(self):
        grid = [list("..."), list("...")]
        result = bfs(grid, (0, 0), (0, 2))
        self.assertTrue(result["success"])
        self.assertEqual(result["path_length"], len(result["path"]) - 1)
        self.check_path(grid, result["path"], (0, 0), (0, 2))

    def test_obstacle_detour(self):
        grid = [list(".@."), list("..."), list("...")]
        result = bfs(grid, (0, 0), (0, 2))
        self.assertTrue(result["success"])
        self.check_path(grid, result["path"], (0, 0), (0, 2))

    def test_unreachable_goal(self):
        grid = [list(".@."), list("@@@"), list("...")]
        result = bfs(grid, (0, 0), (0, 2))
        self.assertFalse(result["success"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["path_length"])

    def test_start_equals_goal(self):
        result = bfs([list(".G")], (0, 0), (0, 0))
        self.assertTrue(result["success"])
        self.assertEqual(result["path"], [(0, 0)])
        self.assertEqual(result["path_length"], 0)
        self.assertEqual(result["nodes_explored"], 1)

    def test_no_diagonal_movement(self):
        grid = [list(".@"), list("@.")]
        result = bfs(grid, (0, 0), (1, 1))
        self.assertFalse(result["success"])

    def test_shortest_path(self):
        grid = [list("..."), list("..."), list("...")]
        result = bfs(grid, (0, 0), (2, 2))
        self.assertTrue(result["success"])
        self.assertEqual(result["path_length"], 4)

    def test_shortest_path_around_wall(self):
        grid = [list("..."), list(".@."), list("...")]
        result = bfs(grid, (1, 0), (1, 2))
        self.assertEqual(result["path_length"], 4)

    def test_blocked_start(self):
        with self.assertRaises(ValueError):
            bfs([list("@.")], (0, 0), (0, 1))

    def test_blocked_goal(self):
        with self.assertRaises(ValueError):
            bfs([list(".@")], (0, 0), (0, 1))

    def test_out_of_bounds(self):
        with self.assertRaises(ValueError):
            bfs([list(".")], (0, 0), (1, 0))

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            bfs([list(".."), list(".")], (0, 0), (0, 1))


if __name__ == "__main__":
    unittest.main()
