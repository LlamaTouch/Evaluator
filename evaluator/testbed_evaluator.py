import logging
from typing import Dict, List, Optional, Tuple

from evaluator.agent import MobileAgent

from .evaluator import BaseEvaluator, FailedReason
from .task_trace import TaskTrace, get_all_vh_paths
from .testbed_evaluation.get_essential_states import EssentialState, EssentialStates
from .testbed_evaluation.xml_exactly_match import exactly_match
from .testbed_evaluation.xml_fuzzy_match import get_xml_fuzzy_match


class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent: MobileAgent, options: Dict = None) -> None:
        super().__init__(agent, options)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)
        logging.getLogger().setLevel(logging.WARNING)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        # load the ground-truth trace and essential states
        gr_trace_path = self.helper.load_testbed_goundtruth_trace_path_by_episode(
            episode
        )
        gr_trace: TaskTrace = self.helper.load_groundtruth_trace_by_episode(episode)
        essential_states: EssentialStates = EssentialStates(episode, gr_trace_path)

        # load the task execution trace
        exec_trace: TaskTrace = self.agent.load_exec_trace_by_episode(episode)
