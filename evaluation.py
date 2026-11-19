import csv
import random
import time
from pathlib import Path

from dataset_loader import load_dataset, PASSABLE
from bfs import bfs
from dfs import dfs
from astar import astar


# the three maps and their selected number of scenarios
SCENARIO_FILES = [
    "dataset/arena.map.scen",
    "dataset/arena2.map.scen",
    "dataset/brc000d.map.scen"
]

SCENARIO_TARGETS = {
    "arena.map": 130,
    "arena2.map": 100,
    "brc000d.map": 100
}

SEED = 170
TEST_PERCENT = 30
TRIALS = 3

RESULT_FIELDS = [
    "algorithm", "map_name", "scenario_line", "split",
    "start_row", "start_col", "goal_row", "goal_col",
    "success", "path_length", "nodes_explored", "execution_time_seconds"
]

SUMMARY_FIELDS = [
    "algorithm", "map_name", "split", "scenarios", "successes",
    "success_rate", "average_path_length", "average_nodes_explored",
    "average_time_seconds"
]


# get the three algorithms that will be compared
def get_algorithms():

    return {
        "BFS": bfs,
        "DFS": dfs,
        "A*": astar
    }


# divide each map's scenarios into development and test sets
def split_scenarios(scenarios, seed=SEED, test_percent=TEST_PERCENT):

    if test_percent < 0 or test_percent > 100:
        raise ValueError("Test percentage must be between 0 and 100.")

    maps = {}

    for scenario in scenarios:
        map_name = scenario["map_name"]

        if map_name not in maps:
            maps[map_name] = []

        maps[map_name].append(scenario)

    random_generator = random.Random(seed)
    test_scenarios = set()

    # randomly select 30 percent from each map for testing
    for map_name in sorted(maps):
        map_scenarios = maps[map_name][:]
        random_generator.shuffle(map_scenarios)
        test_count = int(len(map_scenarios) * test_percent / 100)

        for scenario in map_scenarios[:test_count]:
            key = (map_name, scenario["start"], scenario["goal"])
            test_scenarios.add(key)

    splits = {}

    for scenario in scenarios:
        key = (scenario["map_name"], scenario["start"], scenario["goal"])

        if key in test_scenarios:
            splits[key] = "test"
        else:
            splits[key] = "development"

    return splits


# check if the algorithm returned a valid path and metrics
def check_result(grid, start, goal, result):

    if not isinstance(result, dict):
        raise ValueError("The algorithm must return a dictionary.")

    for field in ["success", "path", "path_length", "nodes_explored"]:
        if field not in result:
            raise ValueError("Missing result: " + field)

    success = result["success"]
    path = result["path"]
    path_length = result["path_length"]
    nodes_explored = result["nodes_explored"]

    if type(success) != bool or type(path) != list:
        raise ValueError("Invalid success or path result.")

    if type(nodes_explored) != int or nodes_explored < 0:
        raise ValueError("Invalid number of explored nodes.")

    if success:
        if len(path) == 0 or path[0] != start or path[-1] != goal:
            raise ValueError("Path does not start or end at the correct position.")

        # calculate the path length using the number of moves
        if type(path_length) != int or path_length != len(path) - 1:
            raise ValueError("Incorrect path length.")

        if nodes_explored == 0:
            raise ValueError("A successful search must explore a node.")

        # check that every cell is inside the map and passable
        for position in path:
            if not isinstance(position, tuple) or len(position) != 2:
                raise ValueError("Invalid position in path.")

            row, col = position

            if type(row) != int or type(col) != int:
                raise ValueError("Invalid path coordinates.")

            if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[0]):
                raise ValueError("Path goes outside the map.")

            if grid[row][col] not in PASSABLE:
                raise ValueError("Path passes through a blocked cell.")

        # check that no diagonal movements are made
        for index in range(1, len(path)):
            previous_row, previous_col = path[index - 1]
            current_row, current_col = path[index]
            distance = abs(current_row - previous_row) + abs(current_col - previous_col)

            if distance != 1:
                raise ValueError("Path contains an invalid movement.")

    else:
        if path != [] or path_length is not None:
            raise ValueError("Unsuccessful searches must return an empty path.")

    return True


# evaluate one algorithm on one scenario
def evaluate_scenario(algorithm_name, algorithm, map_data, scenario, split, trials=TRIALS):

    if trials <= 0:
        raise ValueError("Number of trials must be positive.")

    grid = map_data["grid"]
    start = scenario["start"]
    goal = scenario["goal"]
    total_time = 0
    first_result = None

    # repeat the search and calculate the average time
    for trial in range(trials):
        start_time = time.perf_counter()
        result = algorithm(grid, start, goal)
        execution_time = time.perf_counter() - start_time

        check_result(grid, start, goal, result)

        if first_result is None:
            first_result = result
        else:
            if result["success"] != first_result["success"]:
                raise ValueError("Search success changed between trials.")

            if result["path_length"] != first_result["path_length"]:
                raise ValueError("Path length changed between trials.")

            if result["nodes_explored"] != first_result["nodes_explored"]:
                raise ValueError("Explored nodes changed between trials.")

        total_time += execution_time

    # count the moves in the returned path
    path_length = None

    if first_result["success"]:
        path_length = len(first_result["path"]) - 1

    start_row, start_col = start
    goal_row, goal_col = goal

    return {
        "algorithm": algorithm_name,
        "map_name": scenario["map_name"],
        "scenario_line": scenario.get("line_number", ""),
        "split": split,
        "start_row": start_row,
        "start_col": start_col,
        "goal_row": goal_row,
        "goal_col": goal_col,
        "success": first_result["success"],
        "path_length": path_length,
        "nodes_explored": first_result["nodes_explored"],
        "execution_time_seconds": round(total_time / trials, 9)
    }


# calculate averages and success rates for the comparison
def summarize_results(results):

    groups = {}

    for result in results:
        algorithm = result["algorithm"]
        map_name = result["map_name"]
        split = result["split"]

        keys = [
            (algorithm, map_name, split),
            (algorithm, map_name, "ALL"),
            (algorithm, "ALL", split),
            (algorithm, "ALL", "ALL")
        ]

        for key in keys:
            if key not in groups:
                groups[key] = []

            groups[key].append(result)

    summaries = []

    for key in sorted(groups):
        algorithm, map_name, split = key
        group = groups[key]
        successes = 0
        total_length = 0
        total_nodes = 0
        total_time = 0

        for result in group:
            if result["success"]:
                successes += 1
                total_length += result["path_length"]

            total_nodes += result["nodes_explored"]
            total_time += result["execution_time_seconds"]

        average_length = ""

        if successes > 0:
            average_length = round(total_length / successes, 3)

        summaries.append({
            "algorithm": algorithm,
            "map_name": map_name,
            "split": split,
            "scenarios": len(group),
            "successes": successes,
            "success_rate": round(successes * 100 / len(group), 2),
            "average_path_length": average_length,
            "average_nodes_explored": round(total_nodes / len(group), 3),
            "average_time_seconds": round(total_time / len(group), 9)
        })

    return summaries


# save the evaluation results
def save_csv(filename, results, fields):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for result in results:
            writer.writerow(result)


# evaluate bfs, dfs, and astar on the same 330 scenarios
def run_evaluation():

    dataset = load_dataset(
        "dataset",
        SCENARIO_FILES,
        SCENARIO_TARGETS,
        seed=SEED
    )

    algorithms = get_algorithms()
    scenarios = dataset["scenarios"]
    splits = split_scenarios(scenarios)
    results = []

    print("========== EVALUATION ==========")
    print("Selected scenarios:", len(scenarios))
    print("Random seed:", SEED)
    print("Development/Test:", 100 - TEST_PERCENT, "/", TEST_PERCENT)
    print("Timing trials:", TRIALS)

    for algorithm_name, algorithm in algorithms.items():
        print("\nEvaluating:", algorithm_name)

        for scenario in scenarios:
            map_data = dataset["maps"][scenario["map_name"]]
            key = (scenario["map_name"], scenario["start"], scenario["goal"])

            result = evaluate_scenario(
                algorithm_name,
                algorithm,
                map_data,
                scenario,
                splits[key]
            )

            results.append(result)

        print("Scenarios completed:", len(scenarios))

    summaries = summarize_results(results)

    save_csv("results/results.csv", results, RESULT_FIELDS)
    save_csv("results/summary.csv", summaries, SUMMARY_FIELDS)

    print("\n========== SUMMARY ==========")

    for summary in summaries:
        if summary["map_name"] == "ALL" and summary["split"] == "ALL":
            print("\nAlgorithm:", summary["algorithm"])
            print("Success rate:", summary["success_rate"], "%")
            print("Average path length:", summary["average_path_length"])
            print("Average nodes explored:", summary["average_nodes_explored"])
            print("Average execution time:", summary["average_time_seconds"], "seconds")

    print("\nSaved: results/results.csv")
    print("Saved: results/summary.csv")

    return results, summaries


# for running the program
if __name__ == "__main__":
    run_evaluation()
