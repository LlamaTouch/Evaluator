# Agent Execution

## Docs

The `DatasetHelper` class defined in [task_trace.py](./task_trace.py) helps to retrieve the dataset and annotated crucial states.

The following APIs are provided to build a mobile agent that ingests
- task description
- UI representation (screenshot and view hierarchy)
    - screenshot path: str
    - view hierarchy path: str

1. Retrieve all episodes of all tasks

```python
from Evaluator.task_trace import DatasetHelper
from typing import List

helper = DatasetHelper()
episodes: List[str] = helper.get_all_episodes()
```

2. Retrieve task description and UI representation for a specific episode

```python
from Evaluator.task_trace import DatasetHelper, TaskTrace
from typing import List

helper = DatasetHelper()
episodes: List[str] = helper.get_all_episodes()
epi = episodes[0]

task_description: str = helper.get_task_decsription_by_episode(epi)
trace: TaskTrace = helper.load_groundtruth_trace_by_episode(epi)

screenshot_paths: List[str] = [ui_state[0] for ui_state in trace]
vhs: List[str] = [ui_state[1] for ui_state in trace]
```

## Installation
Below are quick steps for installation:
```bash
conda create -n matestbed python=3.9
conda activate matestbed
git clone https://github.com/MATestbed/Evaluator.git
cd Evaluator
pip install -v -e .
```

# Evaluation

To evaluate the mobile agents, the following traces should be prepared:

- **The ground-truth trace with annotated crucial states.**
It contains screenshot, view hierarchy, and actions on each UI representation.
For each task (episode), it includes crucial states that a agent should go through to finish the task.
This is used as the ground-truth trace for evaluating mobile agents using <ins>*exact match evaluator*</ins> and our <ins>*testbed evaluator*</ins>.
- **The agent-predicted action trace.**
This is used by the <ins>*exact match evaluator*</ins>.
It includes agent-predicted actions on each UI as a lot of traditional work do (e.g., AITW).
These predicted actions can be compared with the actions in the ground-truth trace to show the single-step match accuracy.
- **The task execution trace.**
This is used by the <ins>*testbed evaluator*</ins>.
This is recorded during a mobile agent operating on a real device.
It will be compared with the crucial stats in the ground-truth trace, aiming to revealing the real capability of mobile agents operating on a real environment.

## Usages

Implement the specific trace loading logic for each agent, and then call `Evaluator.run_evaluation()` method!

# Code Development

## Run tests

Use the `pytest` library.

```python
pytest test/test_agent.py
```