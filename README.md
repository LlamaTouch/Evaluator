# Agent Execution

## Docs

The `DatasetHelper` class defined in [task_trace.py](./task_trace.py) helps to retrieve the ground-truth dataset and testbed-generated dataset.

The following APIs are provided to build a mobile agent that ingests
- task description
- UI representation (screenshot and view hierarchy)
    - screenshot path: str
    - text-format view hierarchy: str

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

## Usages

Clone this repo as a submodule to the agent, then import it?

```
git submodule add https://github.com/MATestbed/Evaluator.git
```
