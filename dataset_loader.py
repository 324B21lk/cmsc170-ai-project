
# P1 - Dataset Loading and Preprocessing
# Moving AI Pathfinding Benchmarks

from pathlib import Path


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

    with open(filename, "r") as file:
        lines = file.readlines()

    # Read map header
    if len(lines) < 4:
        raise ValueError("Invalid map file.")

    header = lines[0].split()
    height_header = lines[1].split()
    width_header = lines[2].split()

    if len(header) != 2 or len(height_header) != 2 or len(width_header) != 2:
        raise ValueError("Invalid map header.")

    map_type = header[1]
    height = int(height_header[1])
    width = int(width_header[1])

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
        "name": Path(filename).name,
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
# 2. RESIZE MAP TO SCENARIO DIMENSIONS
# --------------------------------------------------

def resize_map(map_data, new_width, new_height):

    old_grid = map_data["grid"]

    old_height = map_data["height"]
    old_width = map_data["width"]

    if new_width <= 0 or new_height <= 0:
        raise ValueError("Invalid scenario map dimensions.")
    if old_width == new_width and old_height == new_height:
        return map_data

    new_grid = []

    for y in range(new_height):
        row = []
        for x in range(new_width):
            old_y = int(y * old_height / new_height)
            old_x = int(x * old_width / new_width)

            old_y = min(old_y, old_height - 1)
            old_x = min(old_x, old_width - 1)

            row.append(old_grid[old_y][old_x])

        new_grid.append(row)

    # Recalculate cell classifications
    passable_cells = []
    blocked_cells = []
    special_cells = []

    for y in range(new_height):
        for x in range(new_width):
            cell = new_grid[y][x]
            if cell in PASSABLE:
                passable_cells.append((y, x))
            elif cell in BLOCKED:
                blocked_cells.append((y, x))
            elif cell in SPECIAL:
                special_cells.append((y, x))

    resized_data = map_data.copy()

    resized_data.update({
        "height": new_height,
        "width": new_width,
        "grid": new_grid,
        "passable_cells": passable_cells,
        "blocked_cells": blocked_cells,
        "special_cells": special_cells
    })

    return resized_data


# --------------------------------------------------
# 3. LOAD SCENARIO FILE
# --------------------------------------------------

def load_scenarios(filename):

    scenarios = []
    version_found = False

    with open(filename, "r") as file:

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

            fields = line.split()

            if len(fields) != 9:
                raise ValueError(
                    "Invalid scenario at line " + str(line_number)
                )

            scenario = {
                "bucket": int(fields[0]),
                "map_name": fields[1],
                "map_width": int(fields[2]),
                "map_height": int(fields[3]),

                # Convert x, y into row, column
                "start": (int(fields[5]), int(fields[4])),
                "goal": (int(fields[7]), int(fields[6])),

                "optimal_path_length": float(fields[8])
            }

            if scenario["map_width"] <= 0 or scenario["map_height"] <= 0:
                raise ValueError("Invalid scenario map dimensions.")

            if scenario["optimal_path_length"] < 0:
                raise ValueError("Invalid optimal path length.")

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
    if scenario["map_width"] != width:
        raise ValueError("Scenario width does not match map.")

    if scenario["map_height"] != height:
        raise ValueError("Scenario height does not match map.")

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
# 5. LOAD COMPLETE DATASET
# --------------------------------------------------

def load_dataset(map_directory, scen_filename):

    map_directory = Path(map_directory)

    scenarios = load_scenarios(scen_filename)

    maps = {}
    valid_scenarios = []

    for scenario in scenarios:
        map_name = scenario["map_name"]
        # Load each original map only once
        if map_name not in maps:
            map_file = map_directory / map_name
            if not map_file.exists():
                raise FileNotFoundError(
                    "Map file not found: " + str(map_file)
                )

            maps[map_name] = load_map(map_file)

        # Keep the original map unchanged
        original_map = maps[map_name]

        # Resize a copy if dimensions differ
        scenario_map = resize_map(
            original_map,
            scenario["map_width"],
            scenario["map_height"]
        )

        # Validate scenario coordinates
        validate_scenario(scenario_map, scenario)

        valid_scenarios.append(scenario)

    return {
        "maps": maps,
        "scenarios": valid_scenarios
    }


# --------------------------------------------------
# 6. DISPLAY DATASET INFORMATION
# --------------------------------------------------

def display_dataset(dataset):

    print("========== DATASET INFORMATION ==========")

    print("Total Maps:", len(dataset["maps"]))
    print("Total Scenarios:", len(dataset["scenarios"]))

    for map_name, map_data in dataset["maps"].items():

        print("\nMap Name:", map_name)
        print("Height:", map_data["height"])
        print("Width:", map_data["width"])

        print("Passable Cells:", len(map_data["passable_cells"]))
        print("Blocked Cells:", len(map_data["blocked_cells"]))
        print("Special Cells:", len(map_data["special_cells"]))

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
# 7. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    dataset = load_dataset(
        "dataset",
        "dataset/arena.map.scen"
    )

    display_dataset(dataset)
