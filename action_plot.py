import ast
import copy
import pickle
from typing import List

import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from tqdm import tqdm

from config import CONFIG
from evaluator.common import action_type
from evaluator.task_trace import DatasetHelper, TaskTrace
from evaluator.utils.visualization import plot_episode

"""
actions_list_file_path and save_path are the file paths of actions_list and the path to save the plot images.

The format of actions_list is List[Dict], the keys contains "episode_id", "actions".
    episode_id: str
    actions: List[Dict]
        action_type: str
        touch_point: str
        lift_point: str
        typed_text: str
Examples:
    [{
    "episode_id": "12876601525605324725",
    "actions": [
        {
            "action_type": "DUAL_POINT",
            "touch_point": "[0.2279, 0.1277]",
            "lift_point": "[0.2279, 0.1277]",
            "typed_text": ""
        }
    ]
    }]
"""

if __name__ == "__main__":

    actions_list_file_path = ""
    save_path = ""

    with open(actions_list_file_path, "rb") as rp:
        actions_list = pickle.load(rp)

    current_episode = {
        "image": None,
        "episode_id": None,
        "step_id": None,
        "goal": None,
        "result_action": [None, None],
        "result_touch_yx": None,
        "result_lift_yx": None,
        "image_height": 1140,
        "image_width": 540,
        "image_channels": 3,
        "ui_positions": None,
        "ui_text": None,
        "ui_type": None,
    }

    helper = DatasetHelper(CONFIG.EPI_METADATA_PATH, CONFIG.GR_DATASET_PATH)
    episodes: List[str] = helper.get_all_episodes()
    current_actions = None
    for epi in tqdm(episodes):
        current_episodes = []
        task_description: str = helper.get_task_description_by_episode(epi)
        trace: TaskTrace = helper.load_groundtruth_trace_by_episode(epi)
        screenshot_paths: List[str] = [ui_state[0] for ui_state in trace]
        print(screenshot_paths)
        vhs: List[str] = [ui_state[1] for ui_state in trace]
        step_id = 0
        for actions in actions_list:
            if actions["episode_id"] == epi:
                current_actions = actions
                break
        if current_actions is None:
            print("find episode error:", epi)
            continue
        for screenshot_path in screenshot_paths:
            img = Image.open(screenshot_path)
            img = img.resize((540, 1140))
            img_rgb = img.convert("RGB")
            img_array = np.array(img_rgb)
            # print(img_array.shape)
            current_episode["image"] = img_array
            current_episode["episode_id"] = epi
            current_episode["step_id"] = step_id
            current_episode["goal"] = task_description
            action = current_actions["actions"][step_id]
            current_episode["result_action"][0] = action_type.ActionType[
                action["action_type"]
            ]
            current_episode["result_touch_yx"] = ast.literal_eval(action["touch_point"])
            current_episode["result_lift_yx"] = ast.literal_eval(action["lift_point"])
            current_episode["result_action"][1] = action["typed_text"]
            current_episode_copy = copy.deepcopy(current_episode)
            current_episodes.append(current_episode_copy)
            step_id += 1
        try:
            plot_episode(current_episodes, show_annotations=False, show_actions=True)
            plt.savefig(f"{save_path}/{epi}.pdf")
        except Exception as e:
            print(f"An error occurred: {e}")
