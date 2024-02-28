from evaluator import BaseEvaluator
import os


class LLMEvaluator(BaseEvaluator):
    """
    LLMEvaluator implements the evaluation process in paper:
        - AXNav: Replaying Accessibility Tests from Natural Language (https://arxiv.org/pdf/2310.02424v2.pdf)

    Inputs of the LLM-powered evaluation process:
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

    def query_screen_resolution(self):
        """TODO"""
        pass

    def construct_system_prompt_for_LLM(self, episode):
        task_description = self.query_task_decsription_by_episode(episode)
        system_prompt = """\
You are an expert and knowledgable in smartphone operations, especially familiar with frequently-used smartphone applications such as Maps, Music Player, and Emails.
Your task is to determine whether the user properly and correctly execute a given task instruction on a smartphone.
You will be given the following info for the determination.
(1) A task instruction to describe what the task is to be done.
(2) A smartphone screen representation in HTML format 

For a given task instructio
Assume you can operate my mobile phone directly. \
My ultimate goal is to efficiently execute instructions on my mobile phone.

Firstly, You need to decide which specific app is used to complete complex task, such as "Weather", "Chrome" browser, etc. \
Then you need to acquire tutorial yourself about the required app. \
You should not follow the tutorial to complete the task. You should complete the task by yourself.

Secondly, you must follow the following criteria:
1) You should act as a mentor and guide me break down complex task into single-step instructions.
2) Each single-step instruction should contain if and only if one action.
3) Please be very specific about which action I should perform but do not output which page I should arrive at.
4) Each instruction should follow a concise format, such as "Open [name] app", "Find [item] iron", "Tap [item] iron", "Input [words]" etc. \
You can add a prefix, such as "In the [item] screen", "In the [item] bar", "In the [item] window", etc. But note, the prefix is not neccessary. \
It should be a single phrase. Do not propose multiple tasks at the same time.
5) Please use ['1)', '2)', '3)', etc.] to separate each instruction directly.
6) Do not describe the position of the button, such as "the button in the upper right corner", "the button in the lower left corner", etc.
7) If you can, describe the certain name of the app, such as "in the 'weather' app", "in the 'calendar' app", etc.
8) Minimize third person pronouns or words that indicate referring meanings such as "it", "they", "them", "desired", "wanted", etc.

These are some examples. You only need to refer to this format to answer. It does not need to be consistent with the content in the examples.

Example 1:
'''
Task:
What's the weather like in Moscow?

Answer single-step instructions:
1) Open the "Weather" app.
2) Input "Moscow" in the search bar.
3) Tap "Moscow" in the search results.
'''

Example 2:
'''
Task:
Tell me what happened yesterday?

Answer single-step instructions:
1) Open the "Google Chrome" app.
2) Tap on the search bar.
3) Input "news from yesterday".
4) Tap the "Search" button.
'''
"""

    def construct_system_prompt_for_multimodal_LLM(self, episode):
        pass


if __name__ == "__main__":
    e = LLMEvaluator(
        agent_name="AppAgent",
        agent_exec_trace_folder="/Users/zl/Documents/mobile-agent/testbed/data/agent-traces/AppAgent/",
    )
