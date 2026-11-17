# CMSC 170 - AI Project

## Table of Contents

1. [Project Overview](#project-overview)
2. [Group Members](#group-members)
3. [Chosen Dataset](#chosen-dataset)
4. [Proposed Methods](#proposed-methods)
5. [Evaluation Plan](#evaluation-plan)
6. [Project Structure](#project-structure)
7. [Setup and Running](#setup-and-running)
8. [Integration and Handoffs](#integration-and-handoffs)
9. [Collaboration Guidelines](#collaboration-guidelines)
10. [Testing](#testing)
11. [Results](#results)
12. [References](#references)

---

## Project Overview

This project compares three search algorithms for **2D grid-based pathfinding** using the Moving AI Pathfinding Benchmarks.

The goal is to find a valid path from a starting position to a goal position while avoiding obstacles. The algorithms will be compared based on execution time, nodes explored, path length, and success rate.

## Group Members

**Group Name:** AOA

- Alde, Mark Kennard
- Omamalin, Dexter
- Austria, Lakeisha Mae

## Chosen Dataset

**Dataset:** Moving AI Pathfinding Benchmarks - Dragon Age: Origins (2D)

**Source:** [Moving AI - 2D Pathfinding Benchmarks](https://www.movingai.com/benchmarks/grids.html)

The group selected the Dragon Age: Origins (DAO) collection. Three maps will be used for the pathfinding experiments.

### Selected Maps and Scenario Files

| Map File      | Scenario File      | Planned Scenarios |
| ------------- | ------------------ | ----------------: |
| `arena.map`   | `arena.map.scen`   |               130 |
| `arena2.map`  | `arena2.map.scen`  |               100 |
| `brc000d.map` | `brc000d.map.scen` |               100 |
| **Total**     |                    |           **330** |

The scenario counts for the additional maps are target selection sizes and will be verified during dataset preparation.

### Dataset Information

| Description             | Details               |
| ----------------------- | --------------------- |
| Dataset Collection      | Dragon Age: Origins   |
| Map Type                | Octile                |
| Current Map             | 49 × 49 (`arena.map`) |
| Current Scenarios       | 130                   |
| Target Scenarios        | Approximately 330     |
| Number of Selected Maps | 3                     |

### Data Preparation

The `dataset_loader.py` file handles map loading and scenario preprocessing.

It will be updated to:

- Read multiple `.map` files and their corresponding `.scen` files.
- Convert maps into two-dimensional grid representations.
- Identify walkable and blocked cells.
- Extract starting and goal coordinates.
- Validate coordinates against the corresponding map.
- Count valid scenarios and remove duplicates.

The final dataset will contain approximately 300–400 valid pathfinding scenarios from the three selected maps.

## Proposed Methods

The group will implement and compare three search algorithms from scratch.

### 1. Breadth-First Search (BFS)

Uses a queue to explore neighboring cells level by level. It finds the shortest path when all movements have equal costs.

### 2. Depth-First Search (DFS)

Uses a stack to explore one path as deeply as possible before backtracking. It can find a valid path but does not guarantee the shortest path.

### 3. A\* Search

Uses the actual cost of reaching a cell and an estimated distance to the goal to guide its search. Manhattan distance will be used as the heuristic for four-directional movement.

## Evaluation Plan

All algorithms will use the same maps, scenarios, and movement rules to ensure a fair comparison.

| Metric         | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| Execution Time | Time required to find a path or determine that no path exists. |
| Nodes Explored | Number of nodes expanded during the search.                    |
| Path Length    | Number of movement steps in the resulting path.                |
| Success Rate   | Percentage of scenarios where a valid path is found.           |

### Movement Rules

All algorithms will follow four-directional movement:

- Up
- Down
- Left
- Right

Each movement has a cost of 1. Diagonal movement is not allowed, and blocked cells cannot be traversed.

A\* will use Manhattan distance as its heuristic.

**Note:** The original Moving AI scenarios use octile movement and may contain diagonal-based optimal path lengths. The group will calculate path lengths using its own four-directional movement rules.

### Scenario Testing

The group will use the same development and test scenarios for all algorithms. The splitting method and random seed will be documented to ensure reproducibility.

## Project Structure

### Planned Repository Structure

```text
cmsc170-ai-project/
│
├── dataset/
│   ├── arena.map
│   ├── arena.map.scen
│   ├── arena2.map
│   ├── arena2.map.scen
│   ├── brc000d.map
│   └── brc000d.map.scen
│
├── dataset_loader.py
├── bfs.py
├── dfs.py
├── astar.py
├── metrics.py
├── experiment.py
│
├── tests/
│   ├── test_dataset_loader.py
│   ├── test_bfs.py
│   ├── test_dfs.py
│   ├── test_astar.py
│   └── test_metrics.py
│
├── results/
│   ├── initial_results.csv
│   └── figures/
│
├── docs/
│   ├── progress_reports/
│   └── task_log.md
│
├── .gitignore
└── README.md
```

The structure will be updated as additional files are implemented. Member assignments and contributions are recorded separately in `docs/task_log.md`.

## Setup and Running

### Requirements

- Python 3
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/324B21lk/cmsc170-ai-project.git
cd cmsc170-ai-project
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Run the Dataset Loader

```bash
python dataset_loader.py
```

The program loads the map and scenario files and displays the dataset information.

After multiple-map support is implemented, it should display the number of maps, dimensions, passable cells, blocked cells, and valid scenarios for each map.

No additional packages are currently required for the dataset loader.

### 4. Run the Search Algorithms

Execution commands for BFS, DFS, and A\* will be added once the algorithms and experiment runner are integrated.

## Integration and Handoffs

The group will follow this workflow:

1. **Dataset Preparation:** Prepare the maps and validated starting and goal positions.
2. **Algorithm Implementation:** Use the same grid representation, coordinate format, and movement rules.
3. **Integration:** Connect the algorithms with the dataset loader and experiment runner.
4. **Evaluation:** Run all algorithms using the same scenarios and record their performance.

All algorithms must follow a consistent input and output format.

## Collaboration Guidelines

The group will use GitHub for version control and collaboration.

### Branching

- Keep `main` as the stable branch.
- Create a separate branch for each feature, fix, or documentation update.
- Do not commit directly to `main`.
- Merge changes through pull requests.

**Example:**

```bash
git checkout main
git pull origin main
git checkout -b feature/bfs-implementation
```

### Branch Naming

Use the following format:

```text
<type>/<short-description>
```

Examples:

- `feature/bfs-implementation`
- `feature/astar-implementation`
- `fix/map-parser`
- `test/search-algorithms`
- `docs/update-readme`

### Commit Messages

Follow the Conventional Commits format:

```text
<type>(<scope>): <short description>
```

Examples:

```text
feat(dataset): add map loader
feat(bfs): implement breadth-first search
feat(dfs): implement depth-first search
feat(astar): implement manhattan heuristic
fix(dataset): correct coordinate validation
test(bfs): add pathfinding test cases
docs: update readme
```

### Pull Requests and Code Review

- Submit changes through pull requests.
- Describe the changes and how they were tested.
- Request at least one teammate to review the changes.
- Address review comments before merging.
- Make sure relevant tests pass before merging into `main`.

### Python Style and Code Rules

- Follow PEP 8 conventions.
- Use `snake_case` for functions and variables.
- Use uppercase names for constants.
- Use four-space indentation.
- Write clear and simple comments.
- Implement all required algorithms and evaluation metrics from scratch.
- Use only permitted libraries:
  - Python standard library.
  - NumPy for basic arrays and linear algebra.
  - Matplotlib for plots and figures.
- Do not use Pandas, scikit-learn, TensorFlow, PyTorch, Keras, or other libraries that provide ready-made implementations of the required methods.

## Testing

The group will test the dataset loader, search algorithms, and evaluation metrics.

### Dataset Tests

- Verify that all selected maps and scenario files load correctly.
- Check map dimensions and terrain classifications.
- Validate starting and goal coordinates.
- Reject invalid or blocked positions.
- Check the total number of valid scenarios.

### Algorithm Tests

Each algorithm will be tested using:

- A grid with a direct path.
- A grid with obstacles.
- A grid with no possible path.
- A starting position equal to the goal.
- Invalid starting or goal positions.
- A grid with multiple possible paths.

Successful paths must begin at the starting position, end at the goal, avoid blocked cells, and follow the movement rules.

BFS and A\* should find shortest paths under the selected movement costs and heuristic assumptions. DFS is not expected to guarantee the shortest path.

### Running the Test Suite

Once the test files are available, run:

```bash
python -m unittest discover -s tests
```

## Results

Experimental results will be saved in the `results/` directory.

Comparison tables and graphs will show the performance of BFS, DFS, and A\* using the selected evaluation metrics.

Results and conclusions will be added after the experiments are completed.

## References

- Moving AI Lab. (n.d.). [2D Pathfinding Benchmarks](https://www.movingai.com/benchmarks/grids.html).
