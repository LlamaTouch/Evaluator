import os
from enum import Enum
from typing import Any, Dict, List, Tuple


class Agents(Enum):
    APPAGENT = "AppAgent"
    AUTOUI = "Auto-UI"
    AUTODROID = "AutoDroid"
    COGAGENT = "CogAgent"


class TaskCategory(Enum):
    GENERAL = "general"
    GOOGLEAPPS = "googleapps"
    INSTALL = "install"
    WEBSHOPPING = "webshopping"
    GENERATED = "generated"


GROUNDTRUTH_DATASET_PATH = "/data/xxx"

AGENT_EXEC_TRACE_FOLDER = {
    Agents.APPAGENT: "data/agent_exec_trace/AppAgent",
    Agents.AUTOUI: "...",
    Agents.AUTODROID: "...",
    Agents.COGAGENT: "...",
}


def load_groundtruth_trace_by_episode(episode) -> List[Tuple[Any, str, Dict]]:
    """
    *TODO*
    Return: [[screenshot1, XML1, action1], [screenshot2, XML2, action2], ...]
    """
    category = DatasetHelper().get_category_by_episode(episode)
    groundtruth_trace_folder = os.path.join(
        GROUNDTRUTH_DATASET_PATH, category, episode, "captured_data"
    )
    return load_trace(groundtruth_trace_folder)


def get_agent_exec_trace_folder(agent_name, episode) -> str:
    """Get the folder of agent execution trace for one specific episode"""
    category = DatasetHelper().get_category_by_episode(episode)
    if agent_name == Agents.APPAGENT:
        trace_folder = os.path.join(
            AGENT_EXEC_TRACE_FOLDER[Agents.APPAGENT],
            category,
            episode,
            episode,
            "captured_data",
        )
    elif agent_name == Agents.AUTOUI:
        trace_folder = os.path.join(
            AGENT_EXEC_TRACE_FOLDER[Agents.AUTOUI],
            category,
            episode,
            "captured_data",
        )
    else:
        pass
    return trace_folder


def load_agent_exec_trace_by_episode(
    agent_name: Agents, episode: str
) -> List[Tuple[Any, str, Dict]]:
    agent_exec_trace_folder = get_agent_exec_trace_folder(agent_name, episode)
    return load_trace(agent_exec_trace_folder)


def load_groundtruth_trace_by_episode(episode) -> List[Tuple[Any, str, Dict]]:
    category = DatasetHelper().get_category_by_episode(episode)
    groundtruth_trace_folder = os.path.join(
        GROUNDTRUTH_DATASET_PATH, category, episode, "captured_data"
    )
    return load_trace(groundtruth_trace_folder)


def load_trace(trace_folder) -> List[Tuple[Any, str, Dict]]:
    """
    TODO
    Return: [[screenshot1, XML1, action1], [screenshot2, XML2, action2], ...]
    """
    return [(None, None, None), (None, None, None)]


class DatasetHelper:
    """A singleton class to help load task metadata from the dataset."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatasetHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        # load task metadata
        self.epi_to_category_file = "data/epi_to_category.csv"
        assert os.path.exists(
            self.epi_to_category_file
        ), f"The file {self.epi_to_category_file} does not exist"
        self.epi_metadata_dict = {}
        self.init_epi_to_category()

    def init_epi_to_category(self):
        """
        Load episode metadata from the file {self.epi_to_category_file}
        Format: {
            "episode": {
                "category": xx,
                "task_description": xx,
            },
            ...
        }
        """
        with open(self.epi_to_category_file, "r") as f:
            next(f)  # f is an iterable file object; skip the header
            for line in f:
                epi, category, task_description = line.strip().split(",", maxsplit=2)
                self.epi_metadata_dict[epi] = {
                    "category": category,
                    "task_description": task_description,
                }

    def get_all_episodes(self) -> List[str]:
        return self.epi_metadata_dict.keys()

    def get_task_decsription_by_episode(self, episode) -> str:
        return self.epi_metadata_dict[episode]["task_description"]

    def get_category_by_episode(self, episode) -> TaskCategory:
        return self.epi_metadata_dict[episode]["category"]
