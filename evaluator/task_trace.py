import ast
import logging
import os
import re
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Union

import pandas as pd

from .common.action_type import Action, ActionType


class Agent(Enum):
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


"""
GROUNDTRUTH_DATASET_PATH: this is what we replayed and recorded.
TESTBED_GROUNDTRUTH_DATASET_PATH: Based on GROUNDTRUTH_DATASET_PATH, we manually annotated 
crucial states that will be used in the MATestbed evaluator.
"""
# GROUNDTRUTH_DATASET_PATH = "/data/yyh/mobile/capture/AITW_decode"
GROUNDTRUTH_DATASET_PATH = os.getenv(
    "GROUNDTRUTH_DATASET_PATH", "/data/jxq/mobile-agent/aitw_replay_data"
)

ACTION_SPACE = {
    "Home键": ActionType.PRESS_HOME,
    "Back键": ActionType.PRESS_BACK,
    "点击事件": ActionType.DUAL_POINT,
    "滑动事件": ActionType.DUAL_POINT,
    "键盘输入": ActionType.TYPE,
}


class UIState(NamedTuple):
    """
    - screenshot_path: string
    - vh_path: string
    - action: Action
    """

    screenshot_path: str
    vh_path: str
    action: Action


TaskTrace = List[UIState]


def get_all_screenshot_paths(task_trace: TaskTrace) -> List[str]:
    return [ui_state.screenshot_path for ui_state in task_trace]


def get_all_vh_paths(task_trace: TaskTrace) -> List[str]:
    return [ui_state.vh_path for ui_state in task_trace]


def get_all_actions(task_trace: TaskTrace) -> List[Action]:
    return [ui_state.action for ui_state in task_trace]


class DatasetHelper:
    """A singleton class to help load task metadata from the our constructed dataset."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatasetHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        # load task metadata
        self.epi_to_category_file = os.path.join(
            GROUNDTRUTH_DATASET_PATH, "epi_metadata.csv"
        )
        assert os.path.exists(
            self.epi_to_category_file
        ), f"The file {self.epi_to_category_file} does not exist"

        self.epi_metadata_dict: Dict[str, Dict[str, Union[TaskCategory, str]]] = {}
        self.init_epi_to_category()

    def init_epi_to_category(self) -> None:
        """Load episode metadata from the file {self.epi_to_category_file}
        Columns: [episode,category,path,description,nsteps]

        Format: {
            "episode": {
                "category": TaskCategory,
                "task_description": str,
            },
            ...
        }
        """
        with open(self.epi_to_category_file, "r") as f:
            next(f)  # f is an iterable file object; skip the header
            for line in f:
                epi, category, path, task_description, _ = line.strip().split(
                    ",", maxsplit=4
                )
                self.epi_metadata_dict[epi] = {
                    # convert string-format category to TaskCategory,
                    # e.g., "general" -> TaskCategory.GENERAL
                    "category": TaskCategory[category.upper()],
                    "task_description": task_description,
                    "path": path,
                }

    def get_all_episodes(self) -> List[str]:
        return [*self.epi_metadata_dict.keys()]

    def get_episodes_by_category(self, episode: Union[TaskCategory, str]) -> List[str]:
        if isinstance(episode, str):
            episode = TaskCategory[episode.upper()]
        return [
            epi
            for epi in self.get_all_episodes()
            if self.get_category_by_episode(epi) == episode
        ]

    def get_task_description_by_episode(self, episode) -> str:
        if episode not in self.epi_metadata_dict:
            raise KeyError(f"episode: {episode} not found in dataset")
        return self.epi_metadata_dict[episode]["task_description"]

    def get_category_by_episode(self, episode) -> TaskCategory:
        if episode not in self.epi_metadata_dict:
            raise KeyError(f"episode: {episode} not found in dataset")
        return self.epi_metadata_dict[episode]["category"]

    # ---------------------------------------------------- #
    # -------- Processing testbed exectuion traces ------- #
    # -------- Used for the testbed evaluator ------------ #
    # -- Methods                                           #
    # ---- load_testbed_trace_by_episode                   #
    # ---- load_testbed_trace_by_path                      #
    # -- Data (always in the captured_data folder)         #
    # ---- xml: [0.xml, 1.xml, ...]                        #
    # ---- activity: [0.activity, 1.activity, ...]         #
    # ---- action: [-1.action, 0.action, 1.action, ...]    #
    # ---- screenshot: [0.png, 1.png, ...]                 #
    # ---------------------------------------------------- #
    def _proc_testbed_trace_action_file(self, action_file):
        """
        action_type: "CLICK", "SWIPE", "TYPE", "PRESS_BACK", "PRESS_HOME",
                    "PRESS_ENTER", "STATUS_TASK_COMPLETE", "STATUS_TASK_IMPOSSIBLE"
        action_param:
            - "CLICK": [x, y]
            - "SWIPE": [st_x, st_y, end_x, end_y]
            - "TEXT": str
            - others: None
        """
        with open(action_file) as f:
            action_repr = f.read()
        action_repr = action_repr.split("|")
        action_type = action_repr[0]
        if action_repr[2] != "NULL":
            # convert [x x] to [x,x]
            # convert [x, x] to [x,x]
            action_repr[1] = action_repr[1].replace(", ", ",").replace(" ", ",")
            action_repr[2] = action_repr[2].replace(", ", ",").replace(" ", ",")
            action_param = ast.literal_eval(action_repr[1]) + ast.literal_eval(
                action_repr[2]
            )
        elif action_repr[1] != "NULL":
            action_repr[1] = action_repr[1].replace(", ", ",").replace(" ", ",")
            action_param = ast.literal_eval(action_repr[1])
        else:
            action_param = None
        screen_width = int(action_repr[-2])
        screen_height = int(action_repr[-1])
        print(action_type, action_param, screen_width, screen_height)
        return action_type, action_param

    def load_testbed_trace_by_path(self, path: str) -> TaskTrace:
        screenshot_folder_path = os.path.join(path, "screenshot")
        num_UIState = len(os.listdir(screenshot_folder_path))
        task_trace: List[UIState] = []
        for i in range(num_UIState):
            screenshot_path = os.path.join(screenshot_folder_path, f"{i}.png")
            xml_path = os.path.join(path, "xml", f"{i}.xml")
            activity_path = os.path.join(path, "activity", f"{i}.activity")
            action_path = os.path.join(path, "action", f"{i}.action")
            action = self._proc_testbed_trace_action_file(action_path)
            ui_state = UIState(
                screenshot_path=screenshot_path, vh_path=xml_path, action=action
            )
            task_trace.append(ui_state)
        return task_trace

    # ---------------------------------------------------- #
    # -- Processing the ground-truth trace we annotated -- #
    # -- Used for the exact evaluator and task execution - #
    # -- Exposed Methods                                   #
    # ---- load_groundtruth_trace_by_episode               #
    # ---------------------------------------------------- #
    def load_groundtruth_trace_by_episode(self, episode: str) -> Optional[TaskTrace]:
        category: TaskCategory = self.get_category_by_episode(episode)
        print(f"episode: {episode}, category: {category}")
        if episode in self._load_groundtruth_trace_by_category(category):
            return self._load_groundtruth_trace_by_category(category)[episode]
        else:
            return None

    def _load_groundtruth_trace_by_category(
        self, category: TaskCategory
    ) -> Dict[str, TaskTrace]:
        """
        Load ground-truth traces in a whole category
        *Note*: There is a potential risk when directly invoking this method, as
        the ground-truth trace dict may contain traces that their episodes are not
        in self.epi_metadata_dict. Always loading ground-truth traces by episode.


        Return: {
            "episode_id_1": [(screenshot_1_1, XML_1_1, action_1_1), (screenshot_1_2, XML_1_2, action_1_2), ...],
            "episode_id_2": [(screenshot_2_1, XML_2_1, action_2_1), (screenshot_2_2, XML_2_2, action_2_2), ...],
            ...
        }
        """
        groundtruth_trace_folder = os.path.join(
            GROUNDTRUTH_DATASET_PATH, category.value
        )
        gt_trace_dict = {}
        dirs = [
            d
            for d in os.listdir(groundtruth_trace_folder)
            if os.path.isdir(os.path.join(groundtruth_trace_folder, d))
        ]
        dirs.sort()
        for dir in dirs:
            path = os.path.join(groundtruth_trace_folder, dir)
            ep_id_path = os.path.join(path, "instruction.txt")
            with open(ep_id_path, "r") as f:
                ep_id = f.readline().strip()

            ep_trace: TaskTrace = self._load_groundtruth_trace_by_path(path)
            gt_trace_dict[ep_id] = ep_trace

        return gt_trace_dict

    def _load_groundtruth_trace_by_path(self, path: str) -> TaskTrace:
        self.logger.debug(f"loading groundtruth trace in path: {path}")
        ep_trace_list: TaskTrace = []
        # the task trace folder may contain png-format images
        # their name could be 0.png, 1.png, and 0_drawed.png, 1_drawed.png
        # 0_drawed.png and 1_drawed.png are used in the annotation process
        # we only want to get 0.png and 1.png
        files = [
            f for f in os.listdir(path) if f.endswith(".png") and "drawed" not in f
        ]
        files.sort()

        action_path = os.path.join(path, "eventStructs.txt")
        action_list = []
        with open(action_path, "r") as f:
            action_texts = f.readlines()

        # this for-range is for processing the action record
        for action_text in action_texts:
            action_type = re.search("【(?P<action_type>.+)】", action_text).groupdict()[
                "action_type"
            ]
            if action_type == "Home键" or action_type == "Back键":
                action_list.append(Action(action_type=ACTION_SPACE[action_type]))
            elif action_type == "点击事件":
                pattern = re.compile(
                    "屏幕大小：（w(?P<screen_width>\d+)，h(?P<screen_height>\d+)），触摸位置：（x(?P<position_1_x>\d+)，y(?P<position_1_y>\d+)）"
                )
                re_dict = re.search(pattern, action_text).groupdict()
                screen_width = int(re_dict["screen_width"])
                screen_height = int(re_dict["screen_height"])
                action_list.append(
                    Action(
                        action_type=ACTION_SPACE[action_type],
                        touch_point_yx=(
                            int(re_dict["position_1_y"]) / screen_height,
                            int(re_dict["position_1_x"]) / screen_width,
                        ),
                        lift_point_yx=(
                            int(re_dict["position_1_y"]) / screen_height,
                            int(re_dict["position_1_x"]) / screen_width,
                        ),
                    )
                )
            elif action_type == "滑动事件":
                pattern = re.compile(
                    "屏幕大小：（w(?P<screen_width>\d+)，h(?P<screen_height>\d+)），起始位置：（x(?P<position_1_x>\d+)，y(?P<position_1_y>\d+)），结束位置：（x(?P<position_2_x>\d+)，y(?P<position_2_y>\d+)）"
                )
                re_dict = re.search(pattern, action_text).groupdict()
                screen_width = int(re_dict["screen_width"])
                screen_height = int(re_dict["screen_height"])
                action_list.append(
                    Action(
                        action_type=ACTION_SPACE[action_type],
                        touch_point_yx=(
                            int(re_dict["position_1_y"]) / screen_height,
                            int(re_dict["position_1_x"]) / screen_width,
                        ),
                        lift_point_yx=(
                            int(re_dict["position_2_y"]) / screen_height,
                            int(re_dict["position_2_x"]) / screen_width,
                        ),
                    )
                )
            elif action_type == "键盘输入":
                pattern = re.compile("【键盘输入】(?P<text>.*)")
                text = re.search(pattern, action_text).groupdict()["text"]
                action_list.append(
                    Action(action_type=ACTION_SPACE[action_type], typed_text=text)
                )
            else:
                raise ValueError(f"Unknown action type: {action_type}")

        self.logger.debug(
            f"{len(action_list)} actions detected, # of screenshots/vhs: {len(files)}"
        )
        for file, action in zip(files, action_list):
            img_path = os.path.join(path, file)
            xml_path = os.path.join(path, file.replace("png_image.png", "png_xml.txt"))
            self.logger.debug(f"processing screenshot file: {img_path}")

            ep_trace_list.append(
                UIState(screenshot_path=img_path, vh_path=xml_path, action=action)
            )

        return ep_trace_list

    def load_testbed_goundtruth_trace_path_by_episode(self, episode: str) -> str:
        category: TaskCategory = self.get_category_by_episode(episode)
        category_path = os.path.join(GROUNDTRUTH_DATASET_PATH, category.value)
        summary_csv = os.path.join(category_path, "all_instruction.csv")
        data = pd.read_csv(summary_csv)
        epi_to_testbed_trace_path = data[data["episode_id"] == int(episode)][
            "trace_folder_path"
        ].iloc[0]
        return os.path.join(category_path, epi_to_testbed_trace_path)
