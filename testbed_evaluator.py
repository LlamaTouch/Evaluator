import logging
import random

from evaluator import BaseEvaluator
from task_trace import (
    Agents,
    load_agent_exec_trace_by_episode,
    load_groundtruth_trace_by_episode,
)


class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent_name) -> None:
        super().__init__(agent_name)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def load_crucial_states_by_episode(self, episode):
        pass

    def eval_impl(self, episode, task_description) -> bool:

        groundtruth_trace = load_groundtruth_trace_by_episode(episode)
        task_exec_trace = load_agent_exec_trace_by_episode(self.agent_name, episode)
        for item in task_exec_trace:
            screenshot, vh, action = item
            # TODO: check whether all crucial states has been traversed


if __name__ == "__main__":
    e = TestbedEvaluator(agent_name=Agents.APPAGENT)
    e.run_evaluation()
    e.report_stats()
