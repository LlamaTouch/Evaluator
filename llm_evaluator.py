from evaluator import BaseEvaluator
import os


class LLMEvaluator(BaseEvaluator):
    def __init__(self, agent_name, agent_exec_trace_folder):
        super().__init__(agent_name, agent_exec_trace_folder)
        self.evaluator_name = "LLMEvaluator"

    def run_evaluation(self):
        return super().run_evaluation()

    def report_stats(self):
        return super().report_stats()

    def gpt_episodes(self):
        episodes = [123, 345, 567]
        return episodes

    def get_episode_folder(self, episode):
        """Get the folder of agent execution trace for one specific episode"""
        category = self.query_category_by_episode(episode)
        if self.agent_name == "AppAgent":
            trace_folder = os.path.join(
                self.agent_exec_trace_folder,
                category,
                episode,
                episode,
                "captured_data",
            )
        elif self.agent_name == "Auto-UI":
            trace_folder = os.path.join(
                self.agent_exec_trace_folder,
                category,
                episode,
                "captured_data",
            )
        else:
            pass

        return trace_folder


if __name__ == "__main__":
    e = LLMEvaluator(
        agent_name="AppAgent",
        agent_exec_trace_folder="/Users/zl/Documents/mobile-agent/testbed/data/agent-traces/AppAgent/",
    )
