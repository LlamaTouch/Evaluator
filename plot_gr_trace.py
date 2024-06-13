import copy
import os

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from config import CONFIG
from evaluator.task_trace import DatasetHelper, TaskTrace
from evaluator.utils.visualization import plot_episode

helper = DatasetHelper(CONFIG.EPI_METADATA_PATH, CONFIG.GR_DATASET_PATH)


def plot_single_trace(episode: str, output_file: str):
    task_description: str = helper.get_task_description_by_episode(episode)
    trace: TaskTrace = helper.load_groundtruth_trace_by_episode(episode)
    ui_infos_for_plot = []
    step_id = 0
    for ui_state in trace:
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
        current_ui_state["category"] = helper.get_category_by_episode(
            episode
        ).value.upper()
        current_ui_state["image"] = img_arr
        current_ui_state["episode_id"] = episode
        current_ui_state["step_id"] = step_id
        step_id += 1
        current_ui_state["goal"] = task_description
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
        show_essential_states=True,
        show_annotations=False,
        show_actions=True,
    )
    plt.savefig(output_file, pad_inches=0, bbox_inches="tight")


def plot_all():
    output_path = "gr_trace_plots/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    from concurrent.futures import ProcessPoolExecutor

    with ProcessPoolExecutor(max_workers=60) as e:
        for epi in helper.get_all_episodes():
            category = helper.get_category_by_episode(epi).value
            e.submit(
                plot_single_trace,
                episode=epi,
                output_file=os.path.join(output_path, f"{category}_{epi}.png"),
            )


if __name__ == "__main__":
    plot_all()
