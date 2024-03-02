import os
import re
import ast
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Tuple

from action_type import ActionType, Action


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


GROUNDTRUTH_DATASET_PATH = "/data/yyh/mobile/capture/AITW_decode"


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
    - vh: string; view hierarchy
    - action: Action
    """
    screenshot_path: str
    vh: str
    action: Action


TaskTrace = List[UIState]


# ---------------------------------------------------- #
# -- Processing the ground-truth trace we generated -- #
# -- Methods                                           #
# ---- load_groundtruth_trace_by_episode               #
# ---- load_groundtruth_trace_by_category              #
# ---- load_groundtruth_trace_by_path                  #
# ---------------------------------------------------- #
def load_groundtruth_trace_by_episode(episode: str) -> TaskTrace:
    category: TaskCategory = DatasetHelper().get_category_by_episode(episode)
    print(f"episode: {episode}, category: {category}")
    return load_groundtruth_trace_by_category(category)[episode]


def load_groundtruth_trace_by_category(category: TaskCategory) -> Dict[str, TaskTrace]:
    """
    Load ground-truth traces in a whole category

    Return: {
        "episode_id_1": [(screenshot_1_1, XML_1_1, action_1_1), (screenshot_1_2, XML_1_2, action_1_2), ...],
        "episode_id_2": [(screenshot_2_1, XML_2_1, action_2_1), (screenshot_2_2, XML_2_2, action_2_2), ...],
        ...
    }
    """
    groundtruth_trace_folder = os.path.join(GROUNDTRUTH_DATASET_PATH, category.value)
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

        ep_trace_list = load_groundtruth_trace_by_path(path)
        gt_trace_dict[ep_id] = ep_trace_list

    return gt_trace_dict


def load_groundtruth_trace_by_path(path: str) -> TaskTrace:
    ep_trace_list: TaskTrace = []
    files = [
        f for f in os.listdir(path) if f.endswith(".png") and f.find("png_image") != -1
    ]
    files.sort()

    action_path = os.path.join(path, "eventStructs.txt")
    action_list = []
    with open(action_path, "r") as f:
        action_texts = f.readlines()

    for action_text in action_texts:
        action_type = re.search("【(?P<action_type>.+)】", action_text).groupdict()[
            "action_type"
        ]
        if action_type == "Home键" or action_type == "Back键":
            action_list.append({"action_type": ACTION_SPACE[action_type]})
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
                    begin_x=int(re_dict["position_1_x"]) / screen_width,
                    begin_y=int(re_dict["position_1_y"]) / screen_height,
                    end_x=int(re_dict["position_1_x"]) / screen_width,
                    end_y=int(re_dict["position_1_y"]) / screen_height,
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
                    begin_x=int(re_dict["position_1_x"]) / screen_width,
                    begin_y=int(re_dict["position_1_y"]) / screen_height,
                    end_x=int(re_dict["position_2_x"]) / screen_width,
                    end_y=int(re_dict["position_2_y"]) / screen_height,
                )
            )
        elif action_type == "键盘输入":
            pattern = re.compile("【键盘输入】(?P<text>.+)")
            text = re.search(pattern, action_text).groupdict()["text"]
            action_list.append({"action_type": ACTION_SPACE[action_type], "text": text})
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    for file, action in zip(files, action_list):
        img_path = os.path.join(path, file)
        xml_path = os.path.join(path, file.replace("png_image.png", "png_xml.txt"))
        with open(xml_path, "r") as f:
            xml_text = f.read()
        ep_trace_list.append(
            UIState(screenshot_path=img_path, vh=xml_text, action=action)
        )

    return ep_trace_list


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
                    # convert string-format category to TaskCategory,
                    # e.g., "general" -> TaskCategory.GENERAL
                    "category": TaskCategory[category.upper()],
                    "task_description": task_description,
                }

    def get_all_episodes(self) -> List[str]:
        return self.epi_metadata_dict.keys()

    def get_task_decsription_by_episode(self, episode) -> str:
        return self.epi_metadata_dict[episode]["task_description"]

    def get_category_by_episode(self, episode) -> TaskCategory:
        return self.epi_metadata_dict[episode]["category"]


# ---------------------------------------------------- #
# -------- Processing testbed-generated traces ------- #
# -------- Used for the testbed evaluator ------------ #
# -- Methods                                           #
# ---- load_testbed_trace_by_episode                   #
# ---- load_testbed_trace_by_path                      #
# -- Data (always in the captured_data folder)         #
# ---- xml: [0.xml, 1.xml, ...]
# ---- activity: [0.activity, 1.activity, ...]
# ---- action: [-1.action, 0.action, 1.action, ...]
# ---- screenshot: [0.png, 1.png, ...]
# ---------------------------------------------------- #
def _proc_testbed_trace_action_file(action_file):
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


def load_testbed_trace_by_episode(episode: str) -> TaskTrace:
    pass


def load_testbed_trace_by_path(path: str) -> TaskTrace:
    screenshot_folder_path = os.path.join(path, "screenshot")
    num_UIState = len(os.listdir(screenshot_folder_path))
    task_trace: List[UIState] = []
    for i in range(num_UIState):
        screenshot_path = os.path.join(screenshot_folder_path, f"{i}.png")
        xml_path = os.path.join(path, "xml", f"{i}.xml")
        activity_path = os.path.join(path, "activity", f"{i}.activity")
        action_path = os.path.join(path, "action", f"{i}.action")
        with open(xml_path) as f:
            xml_text = f.read()
        action = _proc_testbed_trace_action_file(action_path)
        ui_state = UIState(screenshot_path=screenshot_path, vh=xml_text, action=action)
        task_trace.append(ui_state)
    print(len(task_trace))
    return task_trace


if __name__ == "__main__":
    # test 1
    DatasetHelper().init_epi_to_category()
    print(DatasetHelper().epi_metadata_dict)
    # test 2
    gt_trace = load_groundtruth_trace_by_category(TaskCategory.GENERAL)
    print(gt_trace)
    # test 3
    _proc_testbed_trace_action_file("test-asset/1.action")
    _proc_testbed_trace_action_file("test-asset/2.action")
    _proc_testbed_trace_action_file("test-asset/3.action")
    _proc_testbed_trace_action_file("test-asset/4.action")
    # test 4
    load_testbed_trace_by_path(
        "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/web_shopping/10016075255396203771/captured_data"
    )
