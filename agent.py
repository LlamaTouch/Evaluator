import os
from abc import ABC, abstractmethod

import pandas as pd

from task_trace import Agent, TaskCategory, TaskTrace, get_trace_by_path

AGENT_EXEC_TRACE_PATH = {
    Agent.APPAGENT: "/data/wangshihe/AgentTestbed/AppAgent",
    Agent.AUTOUI: "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result",
    Agent.AUTODROID: None,
    Agent.COGAGENT: None,
}


class MobileAgent(ABC):
    def __init__(self, agent: Agent) -> None:
        self.agent = agent

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
        super().__init__(Agent.APPAGENT)
        self.epi_to_trace_path = None

    def proc_all_exec_trace(self):
        base_folder = AGENT_EXEC_TRACE_PATH[self.agent]
        for k, v in AppAgent.APPAGENT_CATEGORY_TO_TRACE_FOLDER_NAME.items():
            if v is None:
                continue
            summary_csv = os.path.join(base_folder, v, "appagent_trace.csv")
            data = pd.read_csv(summary_csv)
            for _, row in data.iterrows():
                folder_name = row["trace_folder_path"].split("/")[-1]
                epi = row["episode_id"]
                self.epi_to_trace_path[epi] = os.path.join(
                    base_folder, v, folder_name, epi, "captured_data"
                )

    def load_exec_trace_by_episode(self, episode) -> TaskTrace:
        if self.epi_to_trace_path is None:
            self.proc_all_exec_trace()
        epi_trace_path = self.epi_to_trace_path[episode]
        return get_trace_by_path(epi_trace_path)
