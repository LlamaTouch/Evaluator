import os
from abc import ABC, abstractmethod
import pickle
from typing import List, Dict

import pandas as pd

from task_trace import (
    Agent,
    DatasetHelper,
    TaskCategory,
    TaskTrace,
    load_testbed_trace_by_path,
)


class MobileAgent(ABC):
    def __init__(self) -> None:
        self.agent = None

    @abstractmethod
    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        pass


class AppAgent(MobileAgent):

    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.APPAGENT
        self.epi_to_exec_trace_path = {}

    def proc_all_exec_trace(self):
        """exec trace on testbed"""
        base_folder = "/data/wangshihe/AgentTestbed/AppAgent"
        appagent_category_to_trace_folder_name = {
            TaskCategory.GENERAL: "tasks-240214-1-general",
            TaskCategory.GOOGLEAPPS: "tasks-240216-1-googleapp",
            TaskCategory.INSTALL: "tasks-240215-2-install",
            TaskCategory.WEBSHOPPING: "tasks-240215-1-webshopping",
            TaskCategory.GENERATED: None,
        }
        for k, v in appagent_category_to_trace_folder_name.items():
            if v is None:
                continue
            summary_csv = os.path.join(base_folder, v, "appagent_trace.csv")
            data = pd.read_csv(summary_csv)
            for _, row in data.iterrows():
                folder_name = row["trace_folder_path"].split("/")[-1]
                epi = str(row["episode_id"])
                self.epi_to_exec_trace_path[epi] = os.path.join(
                    base_folder, v, folder_name, epi, "captured_data"
                )

    def load_predicted_action_by_episode(self, episode: str) -> List[Dict]:
        """Predicted actions on dataset.
        If there is no corresponding action file, return an empty list"""
        base_folder = "/data/wangshihe/AgentTestbed/AppAgent-AITW"
        appagent_category_to_trace_folder_name = {
            TaskCategory.GENERAL: "tasks-240215-1-general",
            TaskCategory.GOOGLEAPPS: "tasks-240216-1-googleapp",
            TaskCategory.INSTALL: "tasks-240215-3-install",
            TaskCategory.WEBSHOPPING: "tasks-240215-2-webshopping",
            TaskCategory.GENERATED: None,
        }
        # build the map between episode and path
        epi_to_trace_path = {}
        for _, v in appagent_category_to_trace_folder_name.items():
            if v is None:
                continue
            for trace_folder in os.listdir(os.path.join(base_folder, v)):
                episode_anno_file = os.path.join(
                    base_folder, v, trace_folder, "episode_anno.obj"
                )
                if not os.path.exists(episode_anno_file):
                    continue
                with open(episode_anno_file, "rb") as f:
                    epi = pickle.load(f)
                episode = epi[0]["episode_id"]
                epi_to_trace_path[episode] = os.path.join(base_folder, v, trace_folder)

        trace_path = epi_to_trace_path[episode]
        predicted_action_file = os.path.join(trace_path, "appagent_action.obj")
        if not os.path.exists(predicted_action_file):
            return []
        with open(os.path.join(trace_path, "appagent_action.obj"), "rb") as f:
            actions = pickle.load(f)
        return actions

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        if not self.epi_to_trace_path:
            self.proc_all_exec_trace()
            print(f"Reading {len(self.epi_to_trace_path)} episodes in total")
        epi_trace_path = self.epi_to_exec_trace_path[episode]
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


if __name__ == "__main__":
    aa = AppAgent()
    print(aa.load_predicted_action_by_episode("339077771907758195"))
