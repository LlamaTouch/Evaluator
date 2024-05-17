import json
import re
from typing import Dict, List, Optional

from lxml import etree
from PIL import Image
import imagehash

from ..common.action_type import ActionType
from ..task_trace import EssentialStateKeyword, UIState


def _get_image_patch(image: Image, bounds: List[int]) -> Image:
    left, top, right, bottom = bounds
    return image.crop((left, top, right, bottom))

# def check_img_match(gr_ui_state: UIState, exec_ui_state: UIState, image_similarity_bound: Optional[int] = 1) -> bool:
#     match_node_ids: List[str] = gr_ui_state.essential_state[
#         EssentialStateKeyword.EXACT
#     ]
    
#     for node_id in match_node_ids:
#         node_id = int(node_id)

#         gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path

#         gr_screen_width, gr_screen_height = 0,0
#         exec_screen_width, exec_screen_height = 0,0
#         with Image.open(gr_ui_state.screenshot_path) as img:
#             gr_screen_width, gr_screen_height = img.size
#         with Image.open(exec_ui_state.screenshot_path) as img:
#             exec_screen_width, exec_screen_height = img.size
            
#         annotated_ui_repr: Dict = json.load(
#             open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
#         )[node_id]
#         gr_bounds = annotated_ui_repr["bounds"]
#         assert gr_bounds is not None

#         gr_l, gr_t, gr_r, gr_b =  map(int, re.findall(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", gr_bounds)[0])
#         exec_l, exec_t, exec_r, exec_b =  gr_l * exec_screen_width / gr_screen_width, gr_t * exec_screen_height / gr_screen_height,\
#               gr_r * exec_screen_width / gr_screen_width, gr_b * exec_screen_height / gr_screen_height
        
#         annotate_image_patch: Image = _get_image_patch(Image.open(gr_ui_state.screenshot_path), [gr_l, gr_t, gr_r, gr_b])
#         exec_image_patch: Image = _get_image_patch(Image.open(exec_ui_state.screenshot_path), [exec_l, exec_t, exec_r, exec_b])   

#         gr_hash = imagehash.average_hash(annotate_image_patch)
#         exec_hash = imagehash.average_hash(exec_image_patch)

#         if gr_hash - exec_hash > image_similarity_bound:
#             print(
#                 f"[image] match fail: hamming distance: {gr_hash-exec_hash}, '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}'"
#             )
#             return False
    
#     print(f"[image] match success: hamming distance: {gr_hash-exec_hash}, '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}'")
#     return True

def _check_img_exact_match(
    annotated_ui_node: Dict, gr_screenshot_path: str, exec_screenshot_path: str,
    image_similarity_bound: Optional[int] = 1
)->bool:
    """
    Compare whether the image patch of the annotated UI component matches 
    the corresponding image patch in the execution trace.

    Args:
        annotated_ui_node: annotated essential state that represents a UI node
        gr_screenshot_path: screenshot path of the annotated UI 
        exec_screenshot_path: screenshot path of the execution UI
        image_similarity_bound: threshold to determine whether the image patches are similar
    
    Return:
        boolean value indicating whether the image patch of the annotated UI component 
        and the execution UI component matches
    """
    gr_bounds = annotated_ui_node["bounds"]
    assert gr_bounds is not None

    gr_screen_width, gr_screen_height = 0,0
    exec_screen_width, exec_screen_height = 0,0
    with Image.open(gr_screenshot_path) as img:
        gr_screen_width, gr_screen_height = img.size
    with Image.open(exec_screenshot_path) as img:
        exec_screen_width, exec_screen_height = img.size

    gr_l, gr_t, gr_r, gr_b =  map(int, re.findall(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", gr_bounds)[0])
    exec_l, exec_t, exec_r, exec_b =  gr_l * exec_screen_width / gr_screen_width, gr_t * exec_screen_height / gr_screen_height,\
            gr_r * exec_screen_width / gr_screen_width, gr_b * exec_screen_height / gr_screen_height
    
    annotate_image_patch: Image = _get_image_patch(Image.open(gr_screenshot_path), [gr_l, gr_t, gr_r, gr_b])
    exec_image_patch: Image = _get_image_patch(Image.open(exec_screenshot_path), [exec_l, exec_t, exec_r, exec_b])   

    gr_hash = imagehash.average_hash(annotate_image_patch)
    exec_hash = imagehash.average_hash(exec_image_patch)

    if gr_hash - exec_hash > image_similarity_bound:
        print(
            f"[image] match fail: hamming distance: {gr_hash-exec_hash}, '{gr_screenshot_path}' with '{exec_screenshot_path}'"
        )
        return False
    
    print(f"[image] match success: hamming distance: {gr_hash-exec_hash}, '{gr_screenshot_path}' with '{exec_screenshot_path}'")
    return True


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
        EssentialStateKeyword.EXACT
    ]

    parser = etree.XMLParser(recover=True, encoding="utf-8")
    exec_ui_tree = etree.parse(exec_ui_state.vh_path, parser)

    for node_id in match_node_ids:
        node_id = int(node_id)
        gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path
        annotated_ui_repr: Dict = json.load(
            open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
        )[node_id]

        if annotated_ui_repr.get("text",None) == None and \
            annotated_ui_repr.get("content-desc",None) == None:
             if not _check_img_exact_match(annotated_ui_repr,gr_ui_state.screenshot_path,\
                                           exec_ui_state.screenshot_path):
                 return False
        
        else:
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
    """
    based on the clicked item xpath in gr_ui_state.essential_state, find 
    the corresponding node in the exec_ui_state and check if the click point in the node.
    """

    if exec_ui_state.action.action_type != ActionType.DUAL_POINT:
        return False

    if exec_ui_state.action.touch_point_yx != exec_ui_state.action.lift_point_yx:
        return False

    gr_clicked_item_xpath = str(gr_ui_state.essential_state[EssentialStateKeyword.CLICK][0])
    
    parser = etree.XMLParser(recover=True, encoding="utf-8")
    exec_ui_tree = etree.parse(exec_ui_state.vh_path, parser)

    found_nodes = exec_ui_tree.xpath(gr_clicked_item_xpath)
    if len(found_nodes) == 0:
        raise AssertionError("No corresponding nodes found in the execution UI state.")

    bounds = found_nodes[0].get("bounds")
    if not bounds:
        raise AssertionError("No bounds found for the corresponding node.")
    left, top, right, bottom = map(int, re.findall(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)[0])
    
    screen_width, screen_height = 0,0
    with Image.open(exec_ui_state.screenshot_path) as img:
        screen_width, screen_height = img.size

    # screen_width, screen_height = Image.open(exec_ui_state.screenshot_path).size
    y = exec_ui_state.action.touch_point_yx[0] * screen_height
    x = exec_ui_state.action.touch_point_yx[1] * screen_width

    if left <= x <= right and top <= y <= bottom:
        print(f"[click] match success: click action:{x,y}, '{gr_ui_state.vh_path}' with '{exec_ui_state.vh_path}'")
        return True
    else:
        print(f"[click] match failed: click action:{x,y}, '{gr_ui_state.vh_path}' with '{exec_ui_state.vh_path}'")  
        return False
