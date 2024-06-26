from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .task_trace import Agent, TaskTrace


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
    def load_exec_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        pass

    @abstractmethod
    def load_predicted_action_by_episode(self, episode: str) -> Optional[List[Dict]]:
        pass
