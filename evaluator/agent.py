import os
import pickle
from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd

from .common.action_type import Action, ActionType
from .task_trace import Agent, DatasetHelper, TaskCategory, TaskTrace


class MobileAgent(ABC):
    def __init__(self) -> None:
        self._agent: Agent = None
        self.agent_name: str = None

    @property
    def agent(self) -> Agent:
        return self._agent

    @agent.setter
    def agent(self, agent: Agent) -> None:
        self._agent = agent
        self.agent_name = self._agent.value

    @abstractmethod
    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        pass

    @abstractmethod
    def load_predicted_action_by_episode(self, episode: str) -> List[Dict]:
        pass

    @abstractmethod
    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        pass




class AutoUI(MobileAgent):
    def __init__(self) -> None:
        super().__init__()
        self.agent = Agent.AUTOUI
        self.agent_exec_trace_path = (
            "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result"
        )

    def load_exec_trace_by_episode(self, episode: str) -> TaskTrace:
        category = DatasetHelper().get_category_by_episode(episode)
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category, episode, "captured_data"
        )
        return DatasetHelper().load_testbed_trace_by_path(epi_trace_path)

    def load_exec_trace_path_by_episode(self, episode: str) -> str:
        category = DatasetHelper().get_category_by_episode(episode)
        epi_trace_path = os.path.join(
            self.agent_exec_trace_path, category, episode, "captured_data"
        )
        return epi_trace_path
