from pathlib import Path
import math
import random


# --------------------------------------------------
# TERRAIN CLASSIFICATIONS
# --------------------------------------------------

PASSABLE = {".", "G"}
BLOCKED = {"@", "O", "T"}
SPECIAL = {"S", "W"}


# --------------------------------------------------
# 1. LOAD MAP FILE
# --------------------------------------------------

def load_map(filename):

    filename = Path(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Read map header
    if len(lines) < 4:
        raise ValueError("Invalid map file.")

    header = lines[0].split()
    height_header = lines[1].split()
    width_header = lines[2].split()

    if len(header) != 2 or len(height_header) != 2 or len(width_header) != 2:
        raise ValueError("Invalid map header.")

    if header[0] != "type" or height_header[0] != "height" or width_header[0] != "width":
        raise ValueError("Invalid map header labels.")

    map_type = header[1]

    try:
        height = int(height_header[1])
        width = int(width_header[1])
    except ValueError as error:
        raise ValueError("Invalid map dimensions.") from error

    if height <= 0 or width <= 0:
        raise ValueError("Map dimensions must be positive.")

    # Find the map data header
    map_index = None

    for i, line in enumerate(lines):
        if line.strip() == "map":
            map_index = i
            break

    if map_index is None:
        raise ValueError("Map data header not found.")

    # Read the ASCII grid
    map_rows = [
        line.rstrip("\r\n")
        for line in lines[map_index + 1:]
    ]

    # Validate map dimensions
    if len(map_rows) != height:
        raise ValueError("Map height does not match header.")

    for row in map_rows:
        if len(row) != width:
            raise ValueError("Map width does not match header.")

    grid = [list(row) for row in map_rows]

    # Identify cell types
    passable_cells = []
    blocked_cells = []
    special_cells = []

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if cell in PASSABLE:
                passable_cells.append((y, x))
            elif cell in BLOCKED:
                blocked_cells.append((y, x))
            elif cell in SPECIAL:
                special_cells.append((y, x))
            else:
                raise ValueError("Unknown terrain symbol: " + cell)

    return {
        "name": filename.name,
        "path": str(filename),
        "type": map_type,
        "height": height,
        "width": width,
        "grid": grid,
        "passable_cells": passable_cells,
        "blocked_cells": blocked_cells,
        "special_cells": special_cells
    }


# --------------------------------------------------
# 2. CHECK MAP DIMENSIONS AGAINST SCENARIO
# --------------------------------------------------

def check_map_dimensions(map_data, scenario):

    # Check map dimensions
    if scenario["map_width"] != map_data["width"]:
        raise ValueError("Scenario width does not match map.")

    if scenario["map_height"] != map_data["height"]:
        raise ValueError("Scenario height does not match map.")

    return True


# --------------------------------------------------
# 3. LOAD SCENARIO FILE
# --------------------------------------------------

def load_scenarios(filename):

    scenarios = []
    version_found = False

    with open(filename, "r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            # Read version header
            if line.startswith("version"):
                if version_found:
                    raise ValueError("Duplicate scenario version header.")

                fields = line.split()

                if len(fields) != 2:
                    raise ValueError("Invalid scenario version header.")

                version = fields[1]

                if version not in {"1.0", "1"}:
                    raise ValueError("Unsupported scenario version.")

                version_found = True
                continue

            if not version_found:
                raise ValueError("Scenario data found before version header.")

            fields = line.split()

            if len(fields) != 9:
                raise ValueError(
                    "Invalid scenario at line " + str(line_number)
                )

            try:
                scenario = {
                    "bucket": int(fields[0]),
                    "map_name": fields[1],
                    "map_width": int(fields[2]),
                    "map_height": int(fields[3]),

                    # Convert x, y into row, column
                    "start": (int(fields[5]), int(fields[4])),
                    "goal": (int(fields[7]), int(fields[6])),

                    "optimal_path_length": float(fields[8]),
                    "line_number": line_number
                }
            except ValueError as error:
                raise ValueError(
                    "Invalid scenario values at line " + str(line_number)
                ) from error

            if scenario["bucket"] < 0:
                raise ValueError("Invalid scenario bucket.")

            if scenario["map_width"] <= 0 or scenario["map_height"] <= 0:
                raise ValueError("Invalid scenario map dimensions.")

            if (
                not math.isfinite(scenario["optimal_path_length"])
                or scenario["optimal_path_length"] < 0
            ):
                raise ValueError("Invalid optimal path length.")

            if Path(scenario["map_name"]).name != scenario["map_name"]:
                raise ValueError("Invalid map name in scenario.")

            scenarios.append(scenario)

    if not version_found:
        raise ValueError("Scenario version header not found.")

    return scenarios


# --------------------------------------------------
# 4. VALIDATE SCENARIO
# --------------------------------------------------

def validate_scenario(map_data, scenario):

    height = map_data["height"]
    width = map_data["width"]
    grid = map_data["grid"]

    # Check map dimensions
    check_map_dimensions(map_data, scenario)

    if scenario["map_name"] != map_data["name"]:
        raise ValueError("Scenario map name does not match loaded map.")

    start_y, start_x = scenario["start"]
    goal_y, goal_x = scenario["goal"]

    # Check coordinate boundaries
    for y, x in [scenario["start"], scenario["goal"]]:
        if not (0 <= y < height and 0 <= x < width):
            raise ValueError("Start or goal is outside the map.")

        # Check if the coordinate is blocked
        if grid[y][x] in BLOCKED:
            raise ValueError("Start or goal is blocked.")

    return True


# --------------------------------------------------
# 5. SELECT SCENARIOS BY BUCKET
# --------------------------------------------------

def select_scenarios(scenarios, target_count, seed):

    if target_count < 0:
        raise ValueError("Scenario target cannot be negative.")

    if target_count > len(scenarios):
        raise ValueError(
            "Not enough valid scenarios. Requested "
            + str(target_count)
            + ", but only "
            + str(len(scenarios))
            + " are available."
        )

    if target_count == len(scenarios):
        return list(scenarios)

    # Group scenarios by bucket
    buckets = {}

    for scenario in scenarios:
        bucket = scenario["bucket"]

        if bucket not in buckets:
            buckets[bucket] = []

        buckets[bucket].append(scenario)

    # Shuffle scenarios within each bucket using a fixed seed
    rng = random.Random(seed)

    for bucket_scenarios in buckets.values():
        rng.shuffle(bucket_scenarios)

    # Select scenarios across buckets
    selected = []
    bucket_numbers = sorted(buckets.keys())
    rng.shuffle(bucket_numbers)

    while len(selected) < target_count:
        added_scenario = False

        for bucket in bucket_numbers:
            if buckets[bucket]:
                selected.append(buckets[bucket].pop())
                added_scenario = True

                if len(selected) == target_count:
                    break

        if not added_scenario:
            break

    return selected


# --------------------------------------------------
# 6. LOAD COMPLETE DATASET
# --------------------------------------------------

def load_dataset(
    map_directory,
    scen_filenames,
    scenario_targets=None,
    seed=170
):

    map_directory = Path(map_directory)

    if isinstance(scen_filenames, (str, Path)):
        scen_filenames = [scen_filenames]

    if not scen_filenames:
        raise ValueError("No scenario files were provided.")

    if scenario_targets is None:
        scenario_targets = {}

    maps = {}
    scenarios_by_map = {}
    scenario_counts = {}

    # Load each scenario file and its corresponding map
    for scen_filename in scen_filenames:

        scen_path = Path(scen_filename)

        if not scen_path.exists():
            raise FileNotFoundError(
                "Scenario file not found: " + str(scen_path)
            )

        if not scen_path.name.endswith(".scen"):
            raise ValueError("Scenario file must have a .scen extension.")

        expected_map_name = scen_path.name[:-5]

        scenarios = load_scenarios(scen_path)

        for scenario in scenarios:

            map_name = scenario["map_name"]

            if map_name != expected_map_name:
                raise ValueError(
                    "Scenario map name does not match scenario filename: "
                    + str(scen_path)
                )

            # Load each original map only once
            if map_name not in maps:

                map_file = map_directory / map_name

                if not map_file.exists():
                    raise FileNotFoundError(
                        "Map file not found: " + str(map_file)
                    )

                maps[map_name] = load_map(map_file)
                scenarios_by_map[map_name] = []
                scenario_counts[map_name] = {
                    "invalid": 0,
                    "duplicates": 0
                }

            # Validate scenario coordinates
            try:
                validate_scenario(maps[map_name], scenario)
            except ValueError:
                scenario_counts[map_name]["invalid"] += 1
                continue

            scenarios_by_map[map_name].append(scenario)

    # Remove duplicate scenarios
    for map_name in scenarios_by_map:

        unique_scenarios = []
        seen_scenarios = set()

        for scenario in scenarios_by_map[map_name]:

            scenario_key = (
                scenario["map_name"],
                scenario["start"],
                scenario["goal"]
            )

            if scenario_key in seen_scenarios:
                scenario_counts[map_name]["duplicates"] += 1
                continue

            seen_scenarios.add(scenario_key)
            unique_scenarios.append(scenario)

        scenarios_by_map[map_name] = unique_scenarios

    # Select the requested number of scenarios for each map
    selected_scenarios = []

    for map_name, map_scenarios in scenarios_by_map.items():

        available_count = len(map_scenarios)
        target_count = scenario_targets.get(map_name, available_count)

        # Use a separate, repeatable seed for each map
        map_seed = seed + sum(
            (index + 1) * ord(character)
            for index, character in enumerate(map_name)
        )

        selected = select_scenarios(
            map_scenarios,
            target_count,
            map_seed
        )

        scenario_counts[map_name]["available"] = available_count
        scenario_counts[map_name]["selected"] = len(selected)

        selected_scenarios.extend(selected)

    return {
        "maps": maps,
        "scenarios": selected_scenarios,
        "scenario_counts": scenario_counts,
        "seed": seed
    }


# --------------------------------------------------
# 7. DISPLAY DATASET INFORMATION
# --------------------------------------------------

def display_dataset(dataset):

    print("========== DATASET INFORMATION ==========")

    print("Total Maps:", len(dataset["maps"]))
    print("Total Selected Scenarios:", len(dataset["scenarios"]))
    print("Random Seed:", dataset["seed"])

    for map_name, map_data in dataset["maps"].items():

        counts = dataset["scenario_counts"][map_name]

        print("\nMap Name:", map_name)
        print("Height:", map_data["height"])
        print("Width:", map_data["width"])

        print("Passable Cells:", len(map_data["passable_cells"]))
        print("Blocked Cells:", len(map_data["blocked_cells"]))
        print("Special Cells:", len(map_data["special_cells"]))

        print("Available Valid Scenarios:", counts["available"])
        print("Selected Scenarios:", counts["selected"])
        print("Invalid Scenarios:", counts["invalid"])
        print("Duplicate Scenarios Removed:", counts["duplicates"])

    print("\n========== SCENARIO INFORMATION ==========")

    # Display only the first five scenarios
    for index, scenario in enumerate(dataset["scenarios"][:5]):

        print("\nScenario", index + 1)
        print("Map:", scenario["map_name"])
        print("Bucket:", scenario["bucket"])
        print("Start:", scenario["start"])
        print("Goal:", scenario["goal"])
        print("Optimal Path Length:", scenario["optimal_path_length"])

    if len(dataset["scenarios"]) > 5:
        print("\nShowing 5 of", len(dataset["scenarios"]), "scenarios.")


# --------------------------------------------------
# 8. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

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

    display_dataset(dataset)
