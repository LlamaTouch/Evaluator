import logging
from typing import Dict, List

from evaluator.agent import MobileAgent

from .common.action_type import Action
from .evaluator import BaseEvaluator
from .task_trace import (
    TaskTrace,
    get_all_actions,
    get_all_screenshot_paths,
    get_all_vh_paths,
)
from .testbed_evaluation.comparison_algorithm import comparison_algorithm
from .testbed_evaluation.get_crucial_states import CrucialState, CrucialStates


class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent: MobileAgent, options: Dict = None) -> None:
        super().__init__(agent, options)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def load_crucial_states_by_episode(self, episode):
        gt_trace = self.helper.load_groundtruth_trace_by_episode(episode)

    def eval_impl(self, episode, task_description) -> bool:
        # load crucial states
        # crucial_states: CrucialStates = self.load_crucial_states_by_episode(episode)

        # # load task execution trace of a specific mobile agent
        # task_exec_trace: TaskTrace = self.agent.load_exec_trace_by_episode(episode)
        # screenshot_paths: List[str] = get_all_screenshot_paths(task_exec_trace)
        # vh_paths: List[str] = get_all_vh_paths(task_exec_trace)
        # actions: List[Action] = get_all_actions(task_exec_trace)

        # # for each crucial states, find matching things

        testbed_groudtruth_trace_path = (
            self.helper.load_testbed_goundtruth_trace_path_by_episode(episode)
        )
        task_exec_trace_path = self.agent.load_exec_trace_path_by_episode(episode)

        completeness = comparison_algorithm(
            episode=episode,
            checkpoint_dir=testbed_groudtruth_trace_path,
            captured_dir=task_exec_trace_path,
        )
        return completeness, None
