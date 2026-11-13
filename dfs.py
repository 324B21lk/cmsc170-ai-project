#dfs implementation

import time
from dataset_loader import load_dataset, PASSABLE


# find a path from the start to the goal using dfs
def dfs(grid, start, goal):

    # check if the map is empty
    if len(grid) == 0 or len(grid[0]) == 0:
        raise ValueError("The map cannot be empty.")

    height = len(grid)
    width = len(grid[0])

    # check if all rows have the same width
    for row in grid:
        if len(row) != width:
            raise ValueError("The map rows must have the same width.")

    # check if the start and goal are valid
    for position in [start, goal]:
        row, col = position

        if row < 0 or row >= height or col < 0 or col >= width:
            raise ValueError("Start or goal is outside the map.")

        if grid[row][col] not in PASSABLE:
            raise ValueError("Start or goal is not passable.")

    # start measuring the execution time
    start_time = time.perf_counter()

    # use a stack to keep track of cells to visit
    stack = [(start, None)]
    visited = set()
    parents = {}
    nodes_explored = 0

    # add neighbors in reverse order so dfs checks up, down, left, right
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while len(stack) > 0:
        current, previous = stack.pop()

        # skip cells that have already been visited
        if current in visited:
            continue

        visited.add(current)
        parents[current] = previous
        nodes_explored += 1

        # check if the goal was found
        if current == goal:
            path = []
            position = goal

            # trace the path from the goal back to the start
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

        # check the neighboring cells
        for move in directions:
            new_row = current[0] + move[0]
            new_col = current[1] + move[1]
            neighbor = (new_row, new_col)

            if 0 <= new_row < height and 0 <= new_col < width:
                if grid[new_row][new_col] in PASSABLE:
                    if neighbor not in visited:
                        stack.append((neighbor, current))

    # return the result if no path was found
    return {
        "success": False,
        "path": [],
        "path_length": None,
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time
    }


# run dfs on one scenario from the dataset
def run_example():

    dataset = load_dataset(
        "dataset",
        "dataset/arena.map.scen",
        {"arena.map": 130},
        seed=170
    )

    scenario = dataset["scenarios"][0]
    map_data = dataset["maps"][scenario["map_name"]]

    result = dfs(
        map_data["grid"],
        scenario["start"],
        scenario["goal"]
    )

    print("========== DFS RESULTS ==========")
    print("Map:", scenario["map_name"])
    print("Start:", scenario["start"])
    print("Goal:", scenario["goal"])
    print("Path found:", result["success"])
    print("Path:", result["path"])
    print("Path length:", result["path_length"])
    print("Nodes explored:", result["nodes_explored"])
    print("Execution time:", round(result["execution_time"], 6), "seconds")


# for running the program
if __name__ == "__main__":
    run_example()
