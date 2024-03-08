import logging

from .evaluator import BaseEvaluator
from .testbed_evaluation.comparison_algorithm import comparison_algorithm


class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def load_crucial_states_by_episode(self, episode):
        pass

    def eval_impl(self, episode, task_description) -> bool:
        testbed_groudtruth_trace_path = (
            self.helper.load_testbed_goundtruth_trace_path_by_episode(episode)
        )
        task_exec_trace_path = self.agent.load_exec_trace_path_by_episode(episode)
        print(testbed_groudtruth_trace_path, task_exec_trace_path)

        completeness = comparison_algorithm(
            checkpoint_dir=testbed_groudtruth_trace_path,
            captured_dir=task_exec_trace_path,
        )
        return completeness, None
