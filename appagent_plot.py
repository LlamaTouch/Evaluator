import copy
import os

import numpy as np
from PIL import Image
from tqdm import tqdm

from config import CONFIG
from evaluator.task_trace import DatasetHelper, TaskTrace
from evaluator.utils.visualization import plot_episode

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH, CONFIG.GR_DATASET_PATH)


def plot_by_folder(folder_path: str):
    path_list = [
        item
        for item in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, item))
    ]
    epi_id = path_list[0]
    task_description = helper.get_task_description_by_episode(epi_id)
    cat = helper.get_category_by_episode(epi_id).value

    load_path = os.path.join(folder_path, str(epi_id), "captured_data")
    trace = helper.load_testbed_trace_by_path(load_path)

    output_file = os.path.join(folder_path, "agg_plot.pdf")
    plot_single_trace(
        epi=epi_id,
        category=cat,
        task_description=task_description,
        task_trace=trace,
        output_file=output_file,
    )


def plot_single_trace(
    epi: str,
    category: str,
    task_description: str,
    task_trace: TaskTrace,
    output_file: str,
):

    ui_infos_for_plot = []
    step_id = 0
    for ui_state in task_trace:
        current_ui_state = {
            "image": None,
            "episode_id": None,
            "category": None,
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
            "ui_state": None,
            "essential_states": None,
        }
        img = Image.open(ui_state.screenshot_path).convert("RGB")
        img_arr = np.array(img)
        current_ui_state["image_height"] = img.height
        current_ui_state["image_width"] = img.width
        current_ui_state["category"] = category
        current_ui_state["image"] = img_arr
        current_ui_state["episode_id"] = epi
        current_ui_state["step_id"] = step_id
        step_id += 1
        current_ui_state["goal"] = task_description
        # when taking testbed trace as the input, the action on the last screen
        # could be None
        if ui_state.action:
            current_ui_state["result_action"][0] = ui_state.action.action_type
            current_ui_state["result_action"][1] = ui_state.action.typed_text
            current_ui_state["result_touch_yx"] = ui_state.action.touch_point_yx
            current_ui_state["result_lift_yx"] = ui_state.action.lift_point_yx

        if ui_state.state_type == "groundtruth":
            ess = ui_state.essential_state
            current_ui_state["essential_states"] = ess
            # passing the whole ui_state for a quick implementation
            current_ui_state["ui_state"] = ui_state

        ui_infos_for_plot.append(copy.deepcopy(current_ui_state))
    plot_episode(
        ui_infos_for_plot,
        show_essential_states=False,
        show_annotations=False,
        show_actions=True,
        output_file=output_file,
    )


if __name__ == "__main__":
    path = ""
    path_list = os.listdir(path)
    path_list = [
        item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))
    ]
    path_list.sort()
    for idx, folder in enumerate(tqdm(path_list)):
        try:
            plot_by_folder(os.path.join(path, folder))
        except Exception as e:
            print(f"error: {e}")
