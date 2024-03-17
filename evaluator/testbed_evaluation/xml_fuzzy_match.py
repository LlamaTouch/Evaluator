import json
import logging
import os

from lxml import etree

from .get_essential_states import EssentialState
from .sentence_similarity import check_sentence_similarity
from .xml_exactly_match import _is_in_bounds


def get_bounds(checkpoint_xml_path: str, node_id: int):
    """
    function: 根据node_id, 获取bounds str "[x1,y1][x2,y2]"
    """
    dir_path = "/".join(checkpoint_xml_path.split("/")[:-1])
    checkpoint_json_path = os.path.join(
        dir_path, checkpoint_xml_path.split("/")[-1].split(".")[0] + ".json"
    )
    with open(checkpoint_json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    if node_id != -1:
        bounds = json_data[node_id]["bounds"]
        # bounds = _parse_bounds(bounds)
    else:
        bounds = "[-1,-1][-1,-1]"
    return bounds


def simplify_xml(xml_path, bounds):
    """
    function: 根据bounds范围来 simplify xml ,只保留bounds范围内的node
    input: xml_path, bounds(str)
    output: simplified xml str
    """
    parser = etree.XMLParser(recover=True, encoding="utf-8")  # 使用宽容的解析器
    tree = etree.parse(xml_path, parser)  # 解析 XML
    root = tree.getroot()

    result_str = ""
    for node in root.iter():

        attributes = [
            f"class: {node.get('class', '')}",
            f"text: {node.get('text', '')}",
            f"resource-id: {node.get('resource-id', '')}",
            f"content-desc: {node.get('content-desc', '')}",
            f"bounds: {node.get('bounds', '')}",
        ]
        label = f"{node.tag} {' '.join(attributes)}"

        if "[-1,-1][-1,-1]" == bounds:
            result_str += label
            # result_str += etree.tostring(node, encoding='utf-8').decode('utf-8')
        else:
            if _is_in_bounds(node.get("bounds", ""), bounds, 10):
                result_str += label

    return result_str


def get_xml_fuzzy_match(
    fuzzy_essential_state: EssentialState, exec_vh_path: str, cosine_bound=0.7
) -> bool:
    """
    Args:
        - fuzzy_essential_state: an EssentialState object that should be fuzzily matched
        - captured_xml_path: path of the XML file in agent execution trace
        - cosine_bound: the threshold of cosine similarity
    """
    if fuzzy_essential_state.node_id == -2:
        logging.info(f"check_install dont need fuzzy match")
        return True

    bounds = get_bounds(
        fuzzy_essential_state.ui_state.vh_path, fuzzy_essential_state.node_id
    )
    # bounds = "[-1,-1][-1,-1]"
    simp_tree1 = simplify_xml(fuzzy_essential_state.ui_state.vh_path, bounds)
    # print(f"simp_tree1{simp_tree1}")
    # print("----------")
    simp_tree2 = simplify_xml(exec_vh_path, bounds)
    # print(f"simp_tree2{simp_tree2}")

    # logging.info(f"xml similarity COSINE_BOUND: {COSINE_BOUND}")
    # cosine_similarity only

    cosine_similarity, status = check_sentence_similarity(
        simp_tree1, simp_tree2, threshold=cosine_bound
    )
    # print(f"similarity: {similarity}")
    logging.info(
        f"fuzzy match: {fuzzy_essential_state.ui_state.vh_path} vs {exec_vh_path}: cosine_similarity: {cosine_similarity}"
    )

    return status
