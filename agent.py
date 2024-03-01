import os
from abc import ABC, abstractmethod

import pandas as pd

from task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace, load_testbed_trace_by_path


class MobileAgent(ABC):
    def __init__(self) -> None:
        self.agent = None

    @abstractmethod
    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        pass


class AppAgent(MobileAgent):

    APPAGENT_CATEGORY_TO_TRACE_FOLDER_NAME = {
        TaskCategory.GENERAL: "tasks-240214-1-general",
        TaskCategory.GOOGLEAPPS: "tasks-240216-1-googleapp",
        TaskCategory.INSTALL: "tasks-240215-2-install",
        TaskCategory.WEBSHOPPING: "tasks-240215-1-webshopping",
        TaskCategory.GENERATED: None,
    }

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.APPAGENT
        self.epi_to_trace_path = {}
        self.agent_exec_trace_path = "/data/wangshihe/AgentTestbed/AppAgent"

    def proc_all_exec_trace(self):
        base_folder = self.agent_exec_trace_path
        for k, v in AppAgent.APPAGENT_CATEGORY_TO_TRACE_FOLDER_NAME.items():
            if v is None:
                continue
            summary_csv = os.path.join(base_folder, v, "appagent_trace.csv")
            data = pd.read_csv(summary_csv)
            for _, row in data.iterrows():
                folder_name = row["trace_folder_path"].split("/")[-1]
                epi = str(row["episode_id"])
                self.epi_to_trace_path[epi] = os.path.join(
                    base_folder, v, folder_name, epi, "captured_data"
                )

    def load_exec_trace_by_episode(self, episode) -> TaskTrace:
        if not self.epi_to_trace_path:
            self.proc_all_exec_trace()
            print(f"Reading {len(self.epi_to_trace_path)} episodes in total")
        epi_trace_path = self.epi_to_trace_path[episode]
        return load_testbed_trace_by_path(epi_trace_path)


class AutoUI(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTOUI
        self.epi_to_trace_path = None
        self.agent_exec_trace_path = (
            "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result"
        )

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        category = DatasetHelper().get_category_by_episode(episode)
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category, episode, "captured_data"
        )
        return load_testbed_trace_by_path(epi_trace_path)
