# coding=utf-8
# Copyright 2023 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for visualizing AndroidInTheWild data."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches

from ..common import action_type
from ..task_trace import EssentialStateKeyword

_NUM_EXS_PER_ROW = 5
_ACTION_COLOR = "blue"


def is_tap_action(normalized_start_yx, normalized_end_yx):
    distance = np.linalg.norm(
        np.array(normalized_start_yx) - np.array(normalized_end_yx)
    )
    return distance <= 0.04


def _get_annotation_positions(example, image_height, image_width):
    """Processes the annotation positions into distinct bounding boxes.

    Args:
      example: The example to grab annotation positions for.
      image_height: The height of the screenshot.
      image_width: The width of the screenshot.

    Returns:
      A matrix of annotation positions with dimensions (# of annotations, 4),
        where each annotation bounding box takes the form (y, x, h, w).
    """
    flattened_positions = np.array(
        example.features.feature["image/ui_annotations_positions"].float_list.value
    )

    # Raw annotations are normalized so we multiply by the image's height and
    # width to properly plot them.
    positions = np.reshape(flattened_positions, (-1, 4)) * [
        image_height,
        image_width,
        image_height,
        image_width,
    ]
    return positions.astype(int)


def _add_text(text, screen_width, screen_height, ax):
    """Plots text on the given matplotlib axis."""
    t = ax.text(
        0.5 * screen_width,
        0.95 * screen_height,
        text,
        color="white",
        size=20,
        horizontalalignment="center",
        verticalalignment="center",
    )
    t.set_bbox(dict(facecolor=_ACTION_COLOR, alpha=0.9))


def _add_ess_text(text_list, screen_width, screen_height, ax):
    t = ax.text(
        0.5 * screen_width,
        0.05 * screen_height,
        "\n".join(text_list),
        color="black",
        size=20,
        horizontalalignment="center",
        verticalalignment="center",
        weight="bold",
    )
    t.set_bbox(dict(facecolor="yellow", alpha=0.4))


def _plot_dual_point(
    touch_x,
    touch_y,
    lift_x,
    lift_y,
    screen_height,
    screen_width,
    ax,
):
    """Plots a dual point action on the given matplotlib axis."""
    if not is_tap_action(np.array([touch_y, touch_x]), np.array([lift_y, lift_x])):
        ax.arrow(
            touch_x * screen_width,
            touch_y * screen_height,
            lift_x * screen_width - touch_x * screen_width,
            lift_y * screen_height - touch_y * screen_height,
            head_length=25,
            head_width=25,
            color=_ACTION_COLOR,
        )

    ax.scatter(
        touch_x * screen_width,
        touch_y * screen_height,
        s=550,
        linewidths=5,
        color=_ACTION_COLOR,
        marker="+",
    )
    return ax


def _plot_action(
    ex_action_type,
    screen_height,
    screen_width,
    touch_x,
    touch_y,
    lift_x,
    lift_y,
    action_text,
    ax,
):
    """Plots the example's action on the given matplotlib axis."""
    if ex_action_type == action_type.ActionType.DUAL_POINT:
        return _plot_dual_point(
            touch_x, touch_y, lift_x, lift_y, screen_height, screen_width, ax
        )
    elif ex_action_type in (
        action_type.ActionType.PRESS_BACK,
        action_type.ActionType.PRESS_HOME,
        action_type.ActionType.PRESS_ENTER,
    ):
        text = action_type.ActionType(ex_action_type).name
        _add_text(text, screen_width, screen_height, ax)
    elif ex_action_type == action_type.ActionType.TYPE:
        text = f'Input text "{action_text}"'
        _add_text(text, screen_width, screen_height, ax)
    elif ex_action_type == action_type.ActionType.STATUS_TASK_COMPLETE:
        text = "Set episode status as COMPLETE"
        _add_text(text, screen_width, screen_height, ax)
    elif ex_action_type == action_type.ActionType.STATUS_TASK_IMPOSSIBLE:
        text = "Set episode status as IMPOSSIBLE"
        _add_text(text, screen_width, screen_height, ax)
    else:
        print("Action type not supported")


def plot_example(
    example,
    example_index: int,
    show_essential_staets=False,
    show_annotations=False,
    show_action=False,
    ax=None,
):
    """Plots a visualization of the given example.

    Args:
      example: The example that we want to plot the screenshot for.
      show_annotations: Whether or not to plot the annotations over the
        screenshot.
      show_action: Whether or not to plot the action for the given example.
      ax: A matplotlib axis. If provided, the plotter will plot on this axis, else
        it will create a new one.

    Returns:
      The matplotlib axis that the example was plotted on.
    """
    image_height = example["image_height"]
    image_width = example["image_width"]
    image_channels = example["image_channels"]
    image = example["image"]

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(image)
    ax.set_xticks([])
    ax.set_yticks([])

    # add example_index at the top left corner with white background and black text
    ax.text(
        0.02,
        0.98,
        f"{example_index}",
        color="white",
        size=20,
        weight="bold",
        horizontalalignment="left",
        verticalalignment="top",
        transform=ax.transAxes,
        bbox=dict(facecolor=_ACTION_COLOR, alpha=0.9),
    )

    assert ax is not None

    if show_annotations:
        raise NotImplementedError("show_annotations is not implemented yet.")
        positions = _get_annotation_positions(example, image_height, image_width)
        for y, x, h, w in positions:
            rect = patches.Rectangle(
                (x, y), w, h, linewidth=1, edgecolor="r", facecolor="none"
            )
            ax.add_patch(rect)

    # if the action on the current screen is None, skip
    if show_action and example["result_action"][0]:
        touch_y, touch_x = example["result_touch_yx"]
        lift_y, lift_x = example["result_lift_yx"]
        ex_action_type = example["result_action"][0]
        type_text = example["result_action"][1]
        _plot_action(
            ex_action_type,
            image_height,
            image_width,
            touch_x,
            touch_y,
            lift_x,
            lift_y,
            type_text,
            ax,
        )
    assert ax is not None

    if show_essential_staets and example["essential_states"]:
        ess = example["essential_states"]
        ess_all_texts = []
        if EssentialStateKeyword.FUZZY_MATCH in ess:
            for bbox_id in ess[EssentialStateKeyword.FUZZY_MATCH]:
                bbox_id = int(bbox_id)

                if bbox_id == -2:
                    continue
                if bbox_id == -1:
                    ess_all_texts.append(f"FUZZY: {bbox_id}")
                    _plot_bbox_with_id(0, 0, image_width, image_height, bbox_id, ax)
                else:
                    left, top, right, bottom = example[
                        "ui_state"
                    ].get_bbox_bounds_by_keyword_id(bbox_id)
                    _plot_bbox_with_id(left, top, right, bottom, bbox_id, ax)
                    ess_all_texts.append(f"FUZZY: {bbox_id}")

        keys = [
            EssentialStateKeyword.TYPE,
        ]
        for k in keys:
            if not k in ess:
                continue
            ess_all_texts.append(f"{k.value.upper()}: {ess[k][0]}")

        keys = [
            EssentialStateKeyword.TEXTBOX,
            EssentialStateKeyword.CLICK,
        ]
        for k in keys:
            if not k in ess:
                continue
            for bbox_id in ess[k]:
                bbox_id = int(bbox_id)
                left, top, right, bottom = example[
                    "ui_state"
                ].get_bbox_bounds_by_keyword_id(bbox_id)
                _plot_bbox_with_id(left, top, right, bottom, bbox_id, ax)
                ess_all_texts.append(f"{k.value}: {bbox_id}")

        keys = [
            EssentialStateKeyword.ACTIVITY,
            EssentialStateKeyword.CHECK_INSTALL,
            EssentialStateKeyword.CHECK_UNINSTALL,
        ]
        for k in keys:
            if not k in ess:
                continue
            ess_all_texts.append(f"{k.value.upper()}")

        _add_ess_text(ess_all_texts, image_width, image_height, ax)

    return ax


def _plot_bbox_with_id(left, top, right, bottom, bbox_id, ax):
    linewidth = 3 if bbox_id != -1 else 6

    rect = patches.Rectangle(
        (left, top),
        right - left,
        bottom - top,
        linewidth=linewidth,
        edgecolor="r",
        facecolor="none",
    )
    ax.add_patch(rect)

    if bbox_id != -1:
        offset = 10
        ax.text(
            left + offset,
            top + offset,
            str(bbox_id),
            fontsize=25,
            ha="right",
            va="bottom",
            color="r",
            weight="bold",
        )
    return ax


def plot_episode(
    episode,
    output_file=None,
    show_essential_states=True,
    show_annotations=False,
    show_actions=False,
):
    """Plots a visualization of the given episode.

    Args:
      episode: A list of tf.train.Examples representing the episode that should be
        visualized.
      show_annotations: Whether to plot annotations for each episode step.
      show_actions: Whether to plot the actions for each episode step.
    """
    ep_len = len(episode)
    n_cols = min(ep_len, _NUM_EXS_PER_ROW)
    n_rows = 1 + (ep_len - 1) // n_cols
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(30, n_rows * 10))
    axs = axs.flatten()
    goal = ""
    i = 0
    for i, ex in enumerate(episode):
        goal = ex["goal"]
        plot_example(
            ex,
            i,
            show_essential_staets=show_essential_states,
            show_annotations=show_annotations,
            show_action=show_actions,
            ax=axs[i],
        )

    for j in range(i + 1, len(axs)):
        ax = axs[j]
        ax.remove()

    fig.suptitle(
        f"{episode[0]['category']} {episode[0]['episode_id'][:6]}: {goal}",
        size=38,
        y=1.0,
        weight="bold",
    )
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, pad_inches=0, bbox_inches="tight")

    plt.close()
