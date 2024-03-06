import logging

from .agent import AppAgent
from .evaluator import BaseEvaluator
from .task_trace import TaskTrace
from .testbed_evaluator import comparison_algorithm

class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def load_crucial_states_by_episode(self, episode):
        pass

    def eval_impl(self, episode, task_description) -> bool:
        testbed_groudtruth_trace_path = self.helper.load_testbed_goundtruth_trace_path_by_episode(
            episode
        )
        task_exec_trace_path = self.agent.load_exec_trace_path_by_episode(
            episode
        )

        comparison_algorithm(checkpoint_dir=testbed_groudtruth_trace_path, captured_dir=task_exec_trace_path)

        # groundtruth_trace: TaskTrace = self.helper.load_groundtruth_trace_by_episode(
        #     episode
        # )
        # task_exec_trace: TaskTrace = self.agent.load_exec_trace_by_episode(episode)
        # for item in task_exec_trace:
        #     screenshot, vh, action = item
        #     # TODO: check whether all crucial states has been traversed


if __name__ == "__main__":
    agent = AppAgent()
    e = TestbedEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()
