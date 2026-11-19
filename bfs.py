import time
from collections import deque
from dataset_loader import load_dataset, PASSABLE


def bfs(grid, start, goal):

    if len(grid) == 0 or len(grid[0]) == 0:
        raise ValueError("The map cannot be empty.")

    height = len(grid)
    width = len(grid[0])

    for row in grid:
        if len(row) != width:
            raise ValueError("The map rows must have the same width.")

    for position in [start, goal]:
        row, col = position

        if row < 0 or row >= height or col < 0 or col >= width:
            raise ValueError("Start or goal is outside the map.")

        if grid[row][col] not in PASSABLE:
            raise ValueError("Start or goal is not passable.")

    start_time = time.perf_counter()

    # a queue gives first in, first out, so cells are explored level by level
    queue = deque([start])
    visited = {start}
    parents = {start: None}
    nodes_explored = 0

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while len(queue) > 0:
        current = queue.popleft()
        nodes_explored += 1

        if current == goal:
            path = []
            position = goal

            while position is not None:
                path.append(position)
                position = parents[position]

            path.reverse()

            return {
                "success": True,
                "path": path,
                "path_length": len(path) - 1,
                "nodes_explored": nodes_explored,
                "execution_time": time.perf_counter() - start_time
            }

        for move in directions:
            new_row = current[0] + move[0]
            new_col = current[1] + move[1]
            neighbor = (new_row, new_col)

            if 0 <= new_row < height and 0 <= new_col < width:
                if grid[new_row][new_col] in PASSABLE:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parents[neighbor] = current
                        queue.append(neighbor)

    return {
        "success": False,
        "path": [],
        "path_length": None,
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time
    }


def run_example():

    dataset = load_dataset(
        "dataset",
        "dataset/arena.map.scen",
        {"arena.map": 130},
        seed=170
    )

    scenario = dataset["scenarios"][0]
    map_data = dataset["maps"][scenario["map_name"]]

    result = bfs(
        map_data["grid"],
        scenario["start"],
        scenario["goal"]
    )

    print("========== BFS RESULTS ==========")
    print("Map:", scenario["map_name"])
    print("Start:", scenario["start"])
    print("Goal:", scenario["goal"])
    print("Path found:", result["success"])
    print("Path:", result["path"])
    print("Path length:", result["path_length"])
    print("Nodes explored:", result["nodes_explored"])
    print("Execution time:", round(result["execution_time"], 6), "seconds")


if __name__ == "__main__":
    run_example()
