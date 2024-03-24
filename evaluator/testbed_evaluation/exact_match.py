import json
import re
from typing import Dict, List

from lxml import etree
from PIL import Image

from ..common.action_type import ActionType
from ..task_trace import EssentialStateKeyword, UIState


def check_textbox_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    match_node_ids: List[str] = gr_ui_state.essential_state[
        EssentialStateKeyword.TEXTBOX
    ]

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    exec_ui_tree = etree.parse(exec_ui_state.vh_path, parser)

    for node_id in match_node_ids:
        node_id = int(node_id)
        gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path
        annotated_ui_repr: Dict = json.load(
            open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
        )[node_id]
        target_resource_id = annotated_ui_repr["resource-id"]
        target_text = annotated_ui_repr["text"]
        target_content_desc = annotated_ui_repr["content-desc"]
        assert target_text != "" or target_content_desc != ""

        node_with_text = False
        for node in exec_ui_tree.iter():
            if (
                node.get("resource-id") == target_resource_id
                and node.get("text") == target_text
                and node.get("content-desc") == target_content_desc
            ):
                node_with_text = True
                break

        if not node_with_text:
            return False
        else:
            continue

    print(
        f"[textbox] match success: '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}'"
    )
    return True


def check_activity_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    if gr_ui_state.activity == "null":
        return True
        # raise Exception("[activity] match required; but annotated activity is null.")

    match = True if exec_ui_state.activity in gr_ui_state.activity else False
    if match:
        print(
            f"[actvity] match success: '{gr_ui_state.activity}' with '{exec_ui_state.activity}'"
        )
    return match


def check_click_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    """TODO: this implementation can be optimized"""
    if exec_ui_state.action.action_type != ActionType.DUAL_POINT:
        return False

    if exec_ui_state.action.touch_point_yx != exec_ui_state.action.lift_point_yx:
        return False

    # based on exec_ui_state.action.touch_point_yx, find the corresponding node
    # in the XML
    screen_width, screen_height = Image.open(exec_ui_state.screenshot_path).size
    y: float = exec_ui_state.action.touch_point_yx[0] * screen_height
    x: float = exec_ui_state.action.touch_point_yx[1] * screen_width

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    exec_ui_tree = etree.parse(exec_ui_state.vh_path, parser)

    smallest_node = None

    for node in exec_ui_tree.iter():
        bounds = node.get("bounds")
        if bounds is None:
            continue
        left, top, right, bottom = map(
            float, re.findall(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)[0]
        )
        if left <= x <= right and top <= y <= bottom:
            area = (right - left) * (bottom - top)

            if smallest_node is None or area < smallest_area:
                smallest_node = node
                smallest_area = area

    # there will be only one click action on the screen
    gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path
    node_id: int = int(gr_ui_state.essential_state[EssentialStateKeyword.CLICK][0])
    annotated_ui_repr: Dict = json.load(
        open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
    )[node_id]
    target_class = annotated_ui_repr["class"]
    target_text = annotated_ui_repr["text"]
    target_resource_id = annotated_ui_repr["resource-id"]

    if (
        smallest_node.get("class") == target_class
        and smallest_node.get("text") == target_text
        and smallest_node.get("resource-id") == target_resource_id
    ):
        print(
            f"[click] match success: '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}'"
        )
        return True
    else:
        return False


def check_button_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    match_node_ids: List[str] = gr_ui_state.essential_state[
        EssentialStateKeyword.BUTTON
    ]

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    exec_ui_tree = etree.parse(exec_ui_state.vh_path, parser)

    for node_id in match_node_ids:
        id, state = node_id.split(":")
        id = int(id)
        assert state in ["on", "off"], f"annotation for button state error: {node_id}"

        gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path
        annotated_ui_repr: Dict = json.load(
            open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
        )[id]
        # extract whether this button is checked or not
        # annotated_ui_repr["check"] is a boolean variable
        target_button_state = "on" if annotated_ui_repr["checked"] else "off"
        assert state == target_button_state, f"{state=} != {target_button_state=}"
        target_button_class = annotated_ui_repr["class"]
        target_button_resource_id = annotated_ui_repr["resource-id"]

        button_state_matched = False
        for node in exec_ui_tree.iter():
            if (
                node.get("checked") == target_button_state
                and node.get("class") == target_button_class
                and node.get("resource-id") == target_button_resource_id
            ):
                button_state_matched = True
                break

        if button_state_matched:
            continue
        else:
            return False

    print(
        f"[button] match success: '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}'"
    )
    return True
