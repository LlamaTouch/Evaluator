# Agent Execution

## Docs

The `DatasetHelper` class defined in [task_trace.py](./evaluator/task_trace.py) helps to retrieve the dataset and annotated essential states.

The following APIs are provided to build a mobile agent that ingests
- task description
- UI representation (screenshot and view hierarchy)
    - screenshot path: str
    - view hierarchy path: str

1. Retrieve all episodes of all tasks

```python
from config import CONFIG
from Evaluator.task_trace import DatasetHelper
from typing import List

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH)
episodes: List[str] = helper.get_all_episodes()
```

2. Retrieve task description and UI representation for a specific episode

```python
from config import CONFIG
from Evaluator.task_trace import (
    DatasetHelper, 
    TaskTrace, 
    get_all_screenshot_paths,
    get_all_vh_paths,
)
from typing import List

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH)
episodes: List[str] = helper.get_all_episodes()
epi = episodes[0]

task_description: str = helper.get_task_decsription_by_episode(epi)
trace: TaskTrace = helper.load_groundtruth_trace_by_episode(epi)

screenshot_paths: List[str] = get_all_screenshot_paths(trace)
vhs: List[str] = get_all_vh_paths(trace)
```

## Installation
Below are quick steps for installation:
```bash
conda create -n llamatouch python=3.9
conda activate llamatouch 
git clone https://github.com/LlamaTouch/Evaluator.git
cd Evaluator
pip install -v -e .
```