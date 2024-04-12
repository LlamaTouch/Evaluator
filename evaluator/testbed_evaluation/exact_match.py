import json
import re
from typing import Dict, List

from lxml import etree
from PIL import Image

from ..common.action_type import ActionType
from ..task_trace import EssentialStateKeyword, UIState


def check_img_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    pass


def _check_exact_single_node_match(
    annotated_ui_node: Dict, exec_ui_node: etree.ElementTree
) -> bool:
    """Compare whether current UI representation in the execution trace matches
    the annotated UI component.
    The annotated UI component should be matched only when all attributes like
    'text', 'content-desc', 'checked', 'resource-id', etc. are matched.

    Args:
        annotated_ui_node: annotated essential state that represents a UI node
        exec_ui_node: UI hierarchy tree of one screen in the execution trace

    Return:
        boolean value indicating whether there is one node in the current UI
        matches the annotated one
    """
    checked_attrs = [
        "class",
        "text",
        "resource-id",
        "content-desc",
        "enabled",
        "checked",
        "checkable",
        "selected",
        "focused",
        "focusable",
        "clickable",
        "long-clickable",
        "password",
        "scrollable",
    ]

    # for each node, we need to check all attributes listed above
    for node in exec_ui_node.iter():

        # modify this variable to False until current node doesnot match the annotated one
        find_node_match = True
        for attr in checked_attrs:
            assert attr in annotated_ui_node
            node_attr = node.get(attr)
            annotate_ui_node_attr = annotated_ui_node.get(attr)

            if node_attr is None:
                if annotate_ui_node_attr == None or annotate_ui_node_attr in [
                    "",
                    " ",
                    "null",
                ]:
                    continue
                else:
                    find_node_match = False
                    break

            if node_attr == "true":
                node_attr = True
            if node_attr == "false":
                node_attr = False
            if attr == "text" or attr == "content-desc":
                annotate_ui_node_attr = annotate_ui_node_attr.lower()
                node_attr = node_attr.lower()

            if node_attr == annotate_ui_node_attr:
                continue
            else:
                find_node_match = False
                break

        if find_node_match:
            return True
    return False


def check_uicomponent_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    """Exact match on two UI components"""
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

        # if there is one annotated UI component (indicated by node_id) has no
        # matched counterpart, directly return False to indicate
        if not _check_exact_single_node_match(annotated_ui_repr, exec_ui_tree):
            # print(f"[textbox] match failed: '{gr_ui_state.screenshot_path}', essential state: {annotated_ui_repr}")
            return False

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


def check_type_match(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    if exec_ui_state.action.action_type != ActionType.TYPE:
        return False

    if (
        exec_ui_state.action.typed_text
        == gr_ui_state.essential_state[EssentialStateKeyword.TYPE][0]
    ):
        return True
    else:
        return False


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