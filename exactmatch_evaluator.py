import logging
import random

from agent import AppAgent
from evaluator import BaseEvaluator
from task_trace import load_groundtruth_trace_by_episode


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def eval_impl(self, episode, task_description) -> bool:
        groundtruth_trace = load_groundtruth_trace_by_episode(episode)
        task_exec_trace = self.agent.load_exec_trace_by_episode(episode)
        for i, item in enumerate(groundtruth_trace):
            gr_screenshot, gr_vh, gr_action = item
            exec_screenshot, exec_vh, exec_action = task_exec_trace[i]
            if not self.check_action_match(gr_action, exec_action):
                return False
        return True

    def check_action_match(self, gr_action, exec_action) -> bool:
        """TODO"""
        return random.choice([True, False])


if __name__ == "__main__":
    agent = AppAgent()
    e = ExactMatchEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()
