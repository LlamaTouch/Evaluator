import json
import os
from typing import Dict, List

from lxml import etree

from ..task_trace import EssentialStateKeyword, UIState
from ..utils.autodroid_vh2html import simplify_views
from .sentence_similarity import check_sentence_similarity


def compare_entire_ui_vh(gr_ui_state: UIState, exec_ui_state: UIState) -> bool:
    gr_vh_json_path = gr_ui_state.vh_json_path
    exec_vh_json_path = exec_ui_state.vh_json_path
    gr_views: str = simplify_views(json.load(open(gr_vh_json_path)))
    # WARNING: AgentEnv for AppAgent can't get VH
    if not os.path.exists(exec_vh_json_path):
        return True
    exec_views: str = simplify_views(json.load(open(exec_vh_json_path)))

    similarity, similar = check_sentence_similarity(
        gr_views, exec_views, threshold=0.85
    )
    if similar:
        print(
            f"[screen fuzzy match] success: '{gr_ui_state.screenshot_path}' with '{exec_ui_state.screenshot_path}', similarity: {similarity}"
        )

    return similar


def check_fuzzy_match(
    gr_ui_state: UIState,
    exec_ui_state: UIState,
    screen_level_fuzzy_match: bool = True,
    textbox_fuzzy_match: bool = True,
) -> bool:
    fuzzy_match_node_ids: List[str] = gr_ui_state.essential_state[
        EssentialStateKeyword.FUZZY
    ]

    for node_id in fuzzy_match_node_ids:
        """
        TODO: can this be optimized?
        All check_install & check_uninstall keywords are with fuzzy<-2>

        Example:
        check_install<Booking.com>|fuzzy<-2>
        check_uninstall<Microsoft Excel>|fuzzy<-2>

        fuzzy<-1> indicates comparing the entire UI representation

        fuzzy<x (x>=0)> indicates comparing only the node with id=x
        """
        node_id = int(node_id)

        if node_id == -2:
            continue

        # node_id = -1 indicates that the entire UI is to be compared
        if node_id == -1:
            if not screen_level_fuzzy_match or compare_entire_ui_vh(
                gr_ui_state, exec_ui_state
            ):
                # this node has matched, go to the next node
                continue
            else:
                return False

        # if node_id != -1 and shouldn't textbox_fuzzy_match, skip this node
        if not textbox_fuzzy_match:
            continue

        """
        # file content of *gr_vh_simp_ui_json_path*
        [
            {
                "id": 0,
                "class": "android.widget.TextView",
                "text": "hotels in tokyo",
                "resource-id": "com.google.android.googlequicksearchbox:id/googleapp_srp_search_box_text",
                "content-desc": "",
                "bounds": "[189,266][890,323]"
            },
            {
                "id": 1,
                "class": "android.view.View",
                "text": "Filters and Topics",
                "resource-id": "",
                "content-desc": "",
                "bounds": "[0,380][5,388]"
            },
            ...
        ]

        # *annotated_ui_repr*
        {
            "id": 0,
            "class": "android.widget.TextView",
            "text": "hotels in tokyo",
            "resource-id": "com.google.android.googlequicksearchbox:id/googleapp_srp_search_box_text",
            "content-desc": "",
            "bounds": "[189,266][890,323]"
        }
        """
        gr_vh_simp_ui_json_path = gr_ui_state.vh_simp_ui_json_path
        annotated_ui_repr: Dict = json.load(
            open(gr_vh_simp_ui_json_path, "r", encoding="utf-8")
        )[node_id]
        target_text = annotated_ui_repr["text"]
        target_class = annotated_ui_repr["class"]
        target_resource_id = annotated_ui_repr["resource-id"]
        # assert target_text != ""
        # assert target_class != ""
        # assert target_resource_id != ""

        """
        find whether there is an XML item in exec_ui_state that matches the 
        1. target_text, 2. target_class, 3. target_resource_id
        """
        parser = etree.XMLParser(recover=True, encoding="utf-8")

        exec_vh_path = exec_ui_state.vh_path
        exec_ui_tree = etree.parse(exec_vh_path, parser)

        node_text_matched = False
        for node in exec_ui_tree.getroot().iter():
            node_text = node.get("text", "")
            node_class = node.get("class", "'")
            node_resource_id = node.get("resource-id", "")
            # TODO: check if node_text and target_text are semantically similar
            if node_text == target_text:
                # finish this iteration: there is one node identical to the target node
                node_text_matched = True
                break

        # if this annotated node has been matched, go to the next node
        # else this UIState in the exec trace doesnot match the ground-truth UIState
        if node_text_matched:
            continue
        else:
            return False

    # if all nodes have been matched, return True
    return True
