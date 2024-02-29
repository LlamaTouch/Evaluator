import logging

from evaluator import BaseEvaluator
from task_trace import Agents, load_agent_exec_trace_by_episode


class LLMEvaluator(BaseEvaluator):
    """
    LLMEvaluator implements the evaluation process in paper:
        - AXNav: Replaying Accessibility Tests from Natural Language (https://arxiv.org/pdf/2310.02424v2.pdf)

    Inputs:
        - User prompt for the evaluation process
        - The overall task instruction
        - The plan for the current step
        - UI detections before the action
        - UI detections after the action
        - The action itself (the function call and thought)
    Output:
        - A result: success, fail, or task complete
        - An explanation: why the result is what it is
    Brain:
        - GPT-4
    """

    def __init__(self, agent_name) -> None:
        super().__init__(agent_name)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)

    def eval_impl(self, episode, task_description) -> bool:
        task_exec_trace = load_agent_exec_trace_by_episode(self.agent_name, episode)
        if len(task_exec_trace) == 1:
            screenshot, vh, action = task_exec_trace[0]
            # query whether a task is completed using a single UI representation
            return self.query_llm_task_completion(task_description, vh, action)

        for i in range(len(task_exec_trace) - 2):
            cur_screenshot, cur_vh, cur_action = task_exec_trace[i]
            next_screenshot, next_vh, _ = task_exec_trace[i + 1]
            single_step_completion = self.query_llm_single_step_completion(
                task_description, cur_vh, cur_action, next_vh
            )
            if not single_step_completion:
                return False
        # check whether the last UI representation can indicate task completion
        last_screenshot, last_vh, last_action = task_exec_trace[-1]
        return self.query_llm_task_completion(task_description, last_vh, last_action)

    def construct_system_prompt_for_LLM(self, episode) -> str:
        task_description = self.query_task_decsription_by_episode(episode)

    def construct_system_prompt_for_multimodal_LLM(self, episode) -> str:
        pass

    def query_llm_task_completion(self, task_description, vh, action) -> bool:
        import random

        return random.choice([True, False])

    def query_llm_single_step_completion(
        self, task_description, cur_vh, cur_action, next_vh
    ) -> bool:
        import random

        return random.choice([True, False])


if __name__ == "__main__":
    e = LLMEvaluator(agent_name=Agents.APPAGENT)
    e.run_evaluation()
    e.report_stats()
