# LlamaTouch Evaluator


> [!TIP]
> More details of this project in our [project page](https://github.com/LlamaTouch/LlamaTouch) and [paper](https://arxiv.org).

- [Installation](#installation)
- [Using the Dataset](#using-the-dataset)
- [Agent Evaluation](#agent-evaluation)

## Installation

```
conda create -n llamatouch python=3.9
conda activate llamatouch 
git clone https://github.com/LlamaTouch/Evaluator.git && cd Evaluator
pip install -v -e .
```

## Using the Dataset

The `DatasetHelper` class defined in [evaluator/task_trace.py](./evaluator/task_trace.py) helps to retrieve the dataset and annotated essential states.

This class requires the file path of [task metadata](https://github.com/LlamaTouch/LlamaTouch/tree/main/dataset) for initialization:

```python
from config import CONFIG

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH)
```

We provide a list of examples to show how to use the dataset with LlamaTouch Evaluator for UI automation task execution (i.e., agent ingests task descriptions from the dataset) and evaluation (i.e., evaluator extracts UI representations, actions, and essential states from the dataset).

1. Retrieve all episodes or episodes by category

```python
from config import CONFIG
from evaluator.task_trace import DatasetHelper
from typing import List

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH)

# get all episodes
episodes: List[str] = helper.get_all_episodes()

# get episodes by category
# AITW categories: "general", "install", "googleapps", "webshopping"
# LlamaTouch category: "generaetd"
episodes_general: List[str] = helper.get_episodes_by_category('general')
```

2. Retrieve task description and UI representations for a specific episode

```python
from config import CONFIG
from evaluator.task_trace import (
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

## Agent Evaluation

`autoui.py`, `autodroid.py`, `appagent.py`, `cocoagent.py` are four exemplified implementations for agent evaluation.

Overall, the evaluation process requires two instances:
1. A `MobileAgent` instance representing the agent to be evaluated.
2. An `Evaluator` instance representing the evaluation approach.

### MobileAgent

A `MobileAgent` class represents the agent to be evaluated.
A mobile agent should inherit this class and implement its abstract method for loading agent execution traces (generated by [AgentEnv](https://github.com/LlamaTouch/AgentEnv)) for evaluation.

For example, the [`AutoUI` class](autoui.py) inherit `MobileAgent` and implements two following methods.
1. `load_exec_trace_by_episode` takes a string-format episode as the input, and returns a TaskTrace object containing all recorded information during executing the task on AgentEnv. 
Agents should have their own implementation for this method, such as specifying the path of agent execution traces.
2. `load_predicted_action_by_episode` extracts the action sequence from an agent execution trace.
This is used for the two baseline evaluation approaches involving only action match.

```python
class AutoUI(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTOUI
        self.agent_exec_trace_path = CONFIG.AUTOUI_EXEC_TRACE_PATH

    def load_exec_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        pass

    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Action]]:
        pass
```

### Evaluator

An `Evaluator` class represents an evaluation implementation.
Currently, LlamaTouch has three evaluator implementations that inherit the [BaseEvaluator](evaluator/evaluator.py) class:
1. [TestbedEvaluator](evaluator/testbed_evaluator.py): the essential state-powered evaluator introduced in our paper.
2. [ExactMatchEvaluator](evaluator/exactmatch_evaluator.py): a baseline evaluation method that compares whether two action sequences are exactly matched.
3. [LCSMatchEvaluator](evaluator/lcsmatch_evaluator.py): a baseline evaluation method that compares whether the action sequence of a task execution trace is a subsequence of the ground-truth action sequence.

To use one evaluator to evaluate agent execution results, it requires
1. An agent instance is initialized.
2. An evaluator instance is initialized and takes the initialized agent instance as the input.
3. Call the `evaluator.run_evaluation()` method and `evaluator.report_stats()` to get evaluation results.
Evaluation result will be dumped in the `dumped_stats/` folder.

For example:
```python
from config import CONFIG

# this class is defined in the above section
agent = AutoUI()

te = TestbedEvaluator(
    agent=agent,
    # pass the metadata path defined in config.py
    epi_metadata_path=CONFIG.EPI_METADATA_PATH,  
    # this field is optional.
    # by default, all tasks in the metadata file will be evaluated
    options={
        # only tasks of their categories in this list will be evaluated
        "categories": [
            TaskCategory.GENERAL,
            TaskCategory.INSTALL,
            TaskCategory.WEBSHOPPING,
            TaskCategory.GOOGLEAPPS,
            TaskCategory.GENERATED,
        ],
        # only evaluate selected tasks with the following episodes
        "episodes": [
            "epi1",
            "epi2",
            "..."
        ],
    }
)
te.run_evaluation()
te.report_stats()
```
