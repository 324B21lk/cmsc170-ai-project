
# P1 - A* Implementation and Testing
# Moving AI Pathfinding Benchmarks

import time
import heapq
from itertools import count

from dataset_loader import load_dataset, PASSABLE


# --------------------------------------------------
# 1. MANHATTAN DISTANCE
# --------------------------------------------------

def manhattan_distance(position, goal):

    row_distance = abs(position[0] - goal[0])
    col_distance = abs(position[1] - goal[1])

    return row_distance + col_distance


# --------------------------------------------------
# 2. RECONSTRUCT PATH
# --------------------------------------------------

def reconstruct_path(parents, goal):

    path = []
    position = goal

    while position is not None:
        path.append(position)
        position = parents[position]

    path.reverse()

    return path


# --------------------------------------------------
# 3. VALIDATE INPUT
# --------------------------------------------------

def validate_input(grid, start, goal):

    # Check if the map is empty
    if len(grid) == 0 or len(grid[0]) == 0:
        raise ValueError("The map cannot be empty.")

    height = len(grid)
    width = len(grid[0])

    # Check if all rows have the same width
    for row in grid:
        if len(row) != width:
            raise ValueError(
                "The map rows must have the same width."
            )

    # Check if the start and goal are valid
    for position in [start, goal]:

        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Invalid start or goal coordinates.")

        row, col = position

        if not isinstance(row, int) or not isinstance(col, int):
            raise ValueError("Coordinates must be integers.")

        if row < 0 or row >= height or col < 0 or col >= width:
            raise ValueError("Start or goal is outside the map.")

        if grid[row][col] not in PASSABLE:
            raise ValueError("Start or goal is not passable.")


# --------------------------------------------------
# 4. A* SEARCH
# --------------------------------------------------

def astar(grid, start, goal):

    validate_input(grid, start, goal)

    # Start measuring execution time
    start_time = time.perf_counter()

    # Initialize the priority queue
    priority_queue = []

    # Prevent positions from being compared when priorities tie
    tie_breaker = count()

    # Store the actual cost from the start to each position
    g_scores = {start: 0}

    # Store the parent of each position
    parents = {start: None}

    # Track explored positions
    visited = set()

    # Count explored nodes
    nodes_explored = 0

    # Calculate the starting heuristic
    start_h = manhattan_distance(start, goal)

    # Add the starting position to the priority queue
    heapq.heappush(
        priority_queue,
        (start_h, next(tie_breaker), 0, start)
    )

    # Same movement directions as BFS and DFS
    directions = [
        (0, 1),   # Right
        (0, -1),  # Left
        (1, 0),   # Down
        (-1, 0)   # Up
    ]

    # Continue while there are positions to explore
    while priority_queue:

        # Get the position with the lowest f-score
        f_score, _, current_g, current = heapq.heappop(
            priority_queue
        )

        # Skip outdated queue entries
        if current_g != g_scores[current]:
            continue

        # Skip positions that have already been explored
        if current in visited:
            continue

        visited.add(current)
        nodes_explored += 1

        # Check if the goal has been reached
        if current == goal:

            path = reconstruct_path(parents, goal)

            return {
                "success": True,
                "path": path,
                "path_length": len(path) - 1,
                "nodes_explored": nodes_explored,
                "execution_time": time.perf_counter() - start_time
            }

        # Explore neighboring positions
        for move in directions:

            new_row = current[0] + move[0]
            new_col = current[1] + move[1]

            neighbor = (new_row, new_col)

            # Check map boundaries
            if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]):

                # Check if the neighboring cell is passable
                if grid[new_row][new_col] in PASSABLE:

                    # Every movement has a cost of 1
                    tentative_g = current_g + 1

                    # Update if a better path is found
                    if tentative_g < g_scores.get(
                        neighbor, float("inf")
                    ):

                        g_scores[neighbor] = tentative_g
                        parents[neighbor] = current

                        # Calculate Manhattan heuristic
                        h_score = manhattan_distance(
                            neighbor,
                            goal
                        )

                        # Calculate total estimated cost
                        f_score = tentative_g + h_score

                        # Add neighbor to the priority queue
                        heapq.heappush(
                            priority_queue,
                            (
                                f_score,
                                next(tie_breaker),
                                tentative_g,
                                neighbor
                            )
                        )

    # Return if no path is found
    return {
        "success": False,
        "path": [],
        "path_length": None,
        "nodes_explored": nodes_explored,
        "execution_time": time.perf_counter() - start_time
    }


# --------------------------------------------------
# 5. RUN ALL BENCHMARK SCENARIOS
# --------------------------------------------------

def run_all_scenarios():

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

    total_scenarios = len(dataset["scenarios"])
    successful = 0
    unsuccessful = 0
    total_nodes = 0
    total_time = 0

    map_results = {}

    for scenario in dataset["scenarios"]:

        map_name = scenario["map_name"]
        map_data = dataset["maps"][map_name]

        result = astar(
            map_data["grid"],
            scenario["start"],
            scenario["goal"]
        )

        if map_name not in map_results:
            map_results[map_name] = {
                "total": 0,
                "successful": 0,
                "unsuccessful": 0,
                "nodes_explored": 0,
                "execution_time": 0
            }

        map_results[map_name]["total"] += 1
        map_results[map_name]["nodes_explored"] += result["nodes_explored"]
        map_results[map_name]["execution_time"] += result["execution_time"]

        total_nodes += result["nodes_explored"]
        total_time += result["execution_time"]

        if result["success"]:
            successful += 1
            map_results[map_name]["successful"] += 1
        else:
            unsuccessful += 1
            map_results[map_name]["unsuccessful"] += 1

    # Display overall results
    print("========== A* BENCHMARK RESULTS ==========")

    print("Total Scenarios:", total_scenarios)
    print("Successful Searches:", successful)
    print("Unsuccessful Searches:", unsuccessful)
    print("Total Nodes Explored:", total_nodes)
    print("Total Execution Time:", round(total_time, 6), "seconds")

    if total_scenarios > 0:
        print(
            "Average Nodes Explored:",
            round(total_nodes / total_scenarios, 2)
        )

        print(
            "Average Execution Time:",
            round(total_time / total_scenarios, 6),
            "seconds"
        )

    # Display results for each map
    print("\n========== RESULTS BY MAP ==========")

    for map_name, results in map_results.items():

        print("\nMap:", map_name)
        print("Total Scenarios:", results["total"])
        print("Successful:", results["successful"])
        print("Unsuccessful:", results["unsuccessful"])
        print("Nodes Explored:", results["nodes_explored"])
        print(
            "Execution Time:",
            round(results["execution_time"], 6),
            "seconds"
        )


# --------------------------------------------------
# 6. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":
    run_all_scenarios()
