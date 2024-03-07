from zss import simple_distance
import xml.etree.ElementTree as ET
from lxml import etree
import lxml
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io
import logging
import os
import json
from xml_exactly_match import _parse_bounds, _is_in_bounds, _expand_bounds
from sentence_similarity import check_sentence_similarity


def get_bounds(checkpoint_xml_path, node_id):
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
    checkpoint_xml_path, node_id, captured_xml_path, COSSINE_BOUND=0.65
):
    """ "
    根据cossine similarity和tree edit distance match xml
    input xml path
    return true or false
    """
    if node_id == -2:
        logging.info(f"check_install dont need fuzzy match")
        return True

    bounds = get_bounds(checkpoint_xml_path, node_id)
    # bounds = "[-1,-1][-1,-1]"
    simp_tree1 = simplify_xml(checkpoint_xml_path, bounds)
    # print(f"simp_tree1{simp_tree1}")
    # print("----------")
    simp_tree2 = simplify_xml(captured_xml_path, bounds)
    # print(f"simp_tree2{simp_tree2}")

    logging.info(f"xml similarity COSSINE_BOUND: {COSSINE_BOUND}")
    # cosine_similarity only

    cosine_similarity, status = check_sentence_similarity(
        simp_tree1, simp_tree2, threshold=COSSINE_BOUND
    )
    # print(f"similarity: {similarity}")
    logging.info(
        f"fuzzy match: {checkpoint_xml_path} vs {captured_xml_path}: cosine_similarity: {cosine_similarity}"
    )

    return status


if __name__ == "__main__":

    # xml1 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/10.xml')
    # xml2 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/0.xml')
    # xml2 = xml_to_string('/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_2/7.xml')
    xml1 = "/data/jxq/mobile-agent/aitw_replay_data/general/trace_53/5.xml"
    xml2 = "/data/wangshihe/AgentTestbed/AppAgent/tasks-240214-1-general/task_Chrome_2024-02-13_16-24-21/13075604686848738248/captured_data/xml/0.xml"

    similarity = get_xml_fuzzy_match(xml1, 3, xml2)
    print(similarity)

    # distance = tree_edit_distance(xml1, xml2)

    # similarity = cosine_distance(xml1, xml2)
    # print("Cosine Similarity:", similarity)

    # simp_tree1 = get_simplfied_tree(xml1)
    # simp_tree2 = get_simplfied_tree(xml2)

    # tree_to_file(simp_tree1, './tree1.txt')
    # tree_to_file(simp_tree2, './tree2.txt')
    # similarity2 = cosine_distance(tree_to_string(simp_tree1), tree_to_string(simp_tree2))
    # print("Cosine Similarity2:", similarity2)
