from lxml import etree
import xml.etree.ElementTree as ET
import json
from check_install import check_install, check_uninstall

import os
import logging
import re
from sentence_similarity import check_sentence_similarity



def _get_bounds_and_text(checkpoint_json_fp,node_id):
    """
    function: 根据node_id, 获取bounds和text
    """
    node_id = int(node_id)
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    bounds= str(checkpoint_json_data[node_id]['bounds'])

    text = str(checkpoint_json_data[node_id]['text'])
    content_desc = str(checkpoint_json_data[node_id]['content-desc'])
    if text == "":
        text = content_desc

    return bounds, text


def _parse_bounds(bounds):
    """
    input: str([12,14][1080,2274])
    output: list of int [12,14,1080,2274]
    """
    # 首先去除字符串两端的方括号
    bounds = bounds[1:-1]
    
    # 然后以 '][' 分割字符串，得到中间的数字部分
    numbers_str = bounds.split('][')
    
    # 分割每一部分的数字，并将结果扁平化成一个列表
    result = []
    for num_pair in numbers_str:
        nums = num_pair.split(',')
        result.extend([int(num) for num in nums])
    
    return result


def _expand_bounds(bounds,expand_ratio=10):
    """
    input: list of int [x1,y1,x2,y2]
    output: list of int [x1,y1,x2,y2]
    function: expand bounds by expand_ratio
    """
    x1 = bounds[0]
    y1 = bounds[1]
    x2 = bounds[2]
    y2 = bounds[3]
    bound_height = max(y2-y1,y1-y2)
    bound_width = max(x2-x1,x1-x2)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    x1 = max(center_x - bound_width/2 * expand_ratio,0)
    y1 = max(center_y - bound_height/2 * expand_ratio,0)
    x2 = min(center_x + bound_width/2 * expand_ratio,1080)
    y2 = min(center_y + bound_height/2 * expand_ratio,2400)
    # print(f"expand_bound: {str([x1,y1,x2,y2])}")
    return [x1,y1,x2,y2]


def _is_in_bounds(captured_bounds, checkpoint_bounds,expand_ratio=10):
    """
    function: check if captured_bounds is in expand checkpoint_bounds
    input: str([12,14][1080,2274]), str([12,14][1080,2274])
    output: bool
    """

    if captured_bounds == "" or captured_bounds == None or captured_bounds == 'None':
        return False 
    captured_bounds = _parse_bounds(captured_bounds)
    checkpoint_bounds = _parse_bounds(checkpoint_bounds)
    expand_bound = _expand_bounds(checkpoint_bounds,expand_ratio)

    logging.info(f"textbox search expand_bound: {str(expand_bound)}")

    if captured_bounds[0] >= expand_bound[0] and captured_bounds[1] >= expand_bound[1] and captured_bounds[2] <= expand_bound[2] and captured_bounds[3] <= expand_bound[3]:
        return True
    else:
        return False


def _find_EditText_and_TextView(xml_fp, bounds, allowed_resource_id):
    """
    function : find all EditText class in xml
    input: xml file path, checkpoint bounds example str([0,0][1080,2274])
    output: list of EditText class text 
    """
    # android.widget.EditText
    parser = etree.XMLParser(recover=True,encoding='utf-8')  # 使用宽容的解析器
    tree = etree.parse(xml_fp, parser)  # 解析 XML
    root = tree.getroot()

    logging.info(f"resource_id: {str(allowed_resource_id)} ")


    result_resource_id = []
    result_expand_bound = []

    def traverse_resource_id(node):
        if len(node) == 0:
            # print(node.get('resource-id',None))
            if node.get('resource-id',None) in allowed_resource_id:
                bounds_temp = node.get('bounds',None)
                if _is_in_bounds(bounds_temp, bounds):
                    text_temp = node.get('text',None)
                    if not text_temp:
                        text_temp = node.get('content-desc',None)
                    result_resource_id.append(text_temp)
        else:
            for child in node:
                traverse_resource_id(child)

    def traverse_expand(node):
        if len(node) == 0:
            if node.get('class') == 'android.widget.EditText' or node.get('class') == 'android.widget.TextView':
                bounds_temp = node.get('bounds',None)
                if _is_in_bounds(bounds_temp, bounds):
                    text_temp = node.get('text',None)
                    if not text_temp:
                        text_temp = node.get('content-desc',None)
                    result_expand_bound.append(text_temp)
        else:
            for child in node:
                traverse_expand(child)
    
    traverse_resource_id(root)

    if len(result_resource_id) == 0:
        logging.info(f"not find EditText by resource_id{str(allowed_resource_id)}")
        traverse_expand(root)
        return result_expand_bound  
    else:
        logging.info(f"find EditText by resource_id{str(allowed_resource_id)}")
        return result_resource_id


def _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp):
    """
    function: check if the textbox exactly match
    """
    node_id = int(node_id)

    bounds, text = _get_bounds_and_text(checkpoint_json_fp, node_id)
    resource_id, _ = _get_resource_id_and_bounds(checkpoint_json_fp, node_id)
    allowed_resource_id = {resource_id,"XSqSsc"}
    
    # 遍历captured_xml_fp 找到所有符合条件的节点
    result = _find_EditText_and_TextView(captured_xml_fp, bounds,allowed_resource_id)
    
    logging.info(f"Total EditText number:{len(result)}")
    # 对比
    for edittext in result:
        similarity, status = check_sentence_similarity(text, edittext, threshold=0.8)
        if status:
            logging.info(f"text exactly match successfully: checkpoint text:{text} == captured text:{edittext} similarity:{similarity}")
            return True, edittext
        else:
            logging.info(f"text exactly match failed: checkpoint text:{text} != captured text:{edittext} similarity:{similarity}")
            continue
    
    return False, ""


def _get_click_point(captured_action_fp):
    """
    function: get the click point from captured action file
    """
    with open(captured_action_fp) as f:
        action_str = f.read()
    # action_str:CLICK|[0.5 0.2403125]|NULL|1440|3200
    width = int(action_str.split('|')[3])
    height = int(action_str.split('|')[4])
    xy_str = action_str.split('|')[1]
    if "  " in xy_str:
        xy_str = xy_str.replace("  "," ")
    click_y = eval(xy_str.split(' ')[0].split('[')[1])
    click_x = eval(xy_str.split(' ')[1].split(']')[0])
    click_x = int(click_x * width)
    click_y = int(click_y * height)
    return click_x, click_y

def _is_click(captured_action_fp):
    """
    function: check if the action is click
    """
    with open(captured_action_fp) as f:
        action_str = f.read()
    action = str(action_str.split('|')[0])
    if action.lower() == "click":
        return True
    else:
        return False
    
def _get_bound(checkpoint_json_fp,node_id):
    """
    function: 根据node_id, 获取bounds
    """
    node_id = int(node_id)
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    bounds= str(checkpoint_json_data[node_id]['bounds'])
    # bounds = "[0,0][1080,1920]"
    x1 = int(bounds.split('[')[1].split(',')[0])
    y1 = int(bounds.split('[')[1].split(',')[1].split(']')[0])
    x2 = int(bounds.split('[')[2].split(',')[0])
    y2 = int(bounds.split('[')[2].split(',')[1].split(']')[0])
    return x1, y1, x2, y2
    
def _click_exact_match(checkpoint_json_fp, node_id, captured_action_fp):
    """
    function: check if the click exactly match
    """
    node_id = int(node_id)
    # 防止最后一个界面fuzzy match成功，但是没有action文件
    if not os.path.exists(captured_action_fp):
        return False

    if not _is_click(captured_action_fp):
        return False
    
    x1, y1, x2, y2 = _get_bound(checkpoint_json_fp,node_id)
    click_x, click_y = _get_click_point(captured_action_fp)

    expand_bound = _expand_bounds([x1,y1,x2,y2],expand_ratio=2)
    logging.info(f"click search expand_bound: {str(expand_bound)}")

    # if click_x >= x1 and click_x <= x2 and click_y >= y1 and click_y <= y2:
    if click_x >= expand_bound[0] and click_x <= expand_bound[2] and click_y >= expand_bound[1] and click_y <= expand_bound[3]:
        logging.info(f"click exactly match successfully: ({click_x}, {click_y}) in [{expand_bound[0]}, {expand_bound[1]}][{expand_bound[2]}, {expand_bound[3]}]")
        return True
    else:
        logging.info(f"click exactly match failed: ({click_x}, {click_y}) in [{expand_bound[0]}, {expand_bound[1]}][{expand_bound[2]}, {expand_bound[3]}]")
        return False

# activity
def _parse_checkpoint_activity(checkpoint_activity_fp):
    """
    function: parse the activity from checkpoint activity file
    """
    with open(checkpoint_activity_fp) as f:
        checkpoint_activity_str = f.read()
    if "mObscuringWindow=null" in checkpoint_activity_str:
        return None
    # 使用正则表达式来匹配大括号内的内容
    pattern = r"mObscuringWindow=Window{(.+?)}"
    match = re.search(pattern, checkpoint_activity_str)
    # 如果匹配成功
    if match:
        content_inside_braces = match.group(1)
        checkpoint_activity = content_inside_braces.split()[-1]
    else:
        checkpoint_activity = None
    return checkpoint_activity


def _activity_exact_match(checkpoint_activity_fp, captured_activity_fp):
    """
    function: check if the activity exactly match
    """
    BOUND = 0.95
    checkpoint_activity = _parse_checkpoint_activity(checkpoint_activity_fp)
    if checkpoint_activity is None:
        logging.info(f"activity exactly match successfully: mObscuringWindow=null")
        return True
    with open(captured_activity_fp) as f:
        captured_activity = f.read()
    similarity, status = check_sentence_similarity(str(checkpoint_activity).lower(), str(captured_activity).lower(), threshold=BOUND)
    # if str(checkpoint_activity).lower() == str(captured_activity).lower():
    if status:
        logging.info(f"activity similarity: {similarity}/{BOUND}")
        logging.info(f"activity exactly match successfully: {checkpoint_activity} ==  {captured_activity}")
        return True
    else:
        logging.info(f"activity similarity: {similarity}/{BOUND}")
        logging.info(f"activity exactly match failed: {checkpoint_activity} != {captured_activity}")
        return False

# 
def _get_resource_id_and_bounds(checkpoint_json_fp,node_id):
    """
    function: 根据node_id, 获取resource-id和bounds
    """
    node_id = int(node_id)
    checkpoint_json_data = json.load(open(checkpoint_json_fp))
    resource_id = str(checkpoint_json_data[node_id]['resource-id'])
    bounds= str(checkpoint_json_data[node_id]['bounds'])
    return resource_id, bounds

def check_button_state(pic_id, checkpoint_dir,checkpoint,captured_dir,index):
    """
    function: check if the button state: on or off
    input: index: the index number of file in captured_dir to make sure the captured file
    output: if the button state match
    """
    button_map ={
        "on":True,
        "off":False
    }
    checkpoint_node_id,button_state = str(checkpoint.node_id).split(":")
    checkpoint_node_id = int(checkpoint_node_id)
    checkpoint_json_fp = os.path.join(checkpoint_dir, f"{pic_id}.json")
    checkpoint_resource_id, checkpoint_bounds = _get_resource_id_and_bounds(checkpoint_json_fp,checkpoint_node_id)
    captured_vh_fp = os.path.join(captured_dir, "captured_data","view_hierarchy", f"{index}.json")
    flag = False
    with open(captured_vh_fp, "r") as f:
        data = json.load(f)
    for item in data:
        temp = str(item.get("bounds"))
        temp = temp.replace("], [", "][")[1:-1]
        temp = temp.replace(", ", ",")
        captured_bounds = temp
        if _is_in_bounds(captured_bounds, checkpoint_bounds,expand_ratio=5) and \
            item.get("resource-id") == checkpoint_resource_id:
            flag = True
            if item.get("checked") == button_map[button_state]:
                logging.info(f"button state exactly match successfully: {checkpoint_json_fp}-{checkpoint_node_id}-{button_state} is checked")
                return True
    if not flag:
        logging.info(f"no resource-id matched{checkpoint_json_fp}-{checkpoint_node_id}")
        return True
    
    return False
            




def exactly_match(checkpoint,checkpoint_dir, pic_id, keyword, node_id, captured_dir, index):
    """
    input:
    checkpoint_dir: 标注完之后的文件夹
    pic_id: 图片id
    keyword: 标注的关键字
    node_id: 节点id
    captured_dir: 抓取的文件夹
    index: 抓取的图片id
    output: return True or False
    """
    keyword = str(keyword).lower()
    if keyword == "textbox":
        checkpoint_json_fp = os.path.join(checkpoint_dir, f"{pic_id}.json")
        captured_xml_fp = os.path.join(captured_dir, "captured_data","xml", f"{index}.xml")
        state, text = _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp)
        return state

    elif keyword == "click":
        checkpoint_json_fp = os.path.join(checkpoint_dir, f"{pic_id}.json")
        captured_action_fp = os.path.join(captured_dir, "captured_data","action", f"{index}.action")
        state = _click_exact_match(checkpoint_json_fp, node_id, captured_action_fp)
        return state
    
    elif keyword == "fuzzy_match":
        # logging.info("fuzzy have matched successfully")
        return True
    
    elif keyword == "activity":
        checkpoint_activity_fp = os.path.join(checkpoint_dir, f"{pic_id}.activity")
        captured_activity_fp = os.path.join(captured_dir, "captured_data","activity", f"{index}.activity")
        state = _activity_exact_match(checkpoint_activity_fp, captured_activity_fp)
        return state
    elif keyword == "check_install":
        state = check_install([checkpoint],captured_dir)
        return state
    elif keyword == "check_uninstall":
        state = check_uninstall([checkpoint],captured_dir)
        return state
    elif keyword == "button":
        state = check_button_state(pic_id, checkpoint_dir, checkpoint, captured_dir,index)
        return state

    

    
if __name__ == "__main__":
    # checkpoint_json_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.json"
    # node_id = 32
    # captured_xml_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.xml"
    # state, text = _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp)
    # if state:
    #     print(f"match successfully: {text}")
    # else:
    #     print("match failed")
    # x,y = _get_click_point("/data/wangshihe/AgentTestbed/AppAgent/tasks/task_Chrome_2024-01-16_21-40-04/151130279482320639/captured_data/action/0.action")
    # print(f"x: {x}, y: {y}")
    # _get_bound("/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.json", 32)

    # bounds = _parse_bounds("[0,0][1080,1920]")
    # action_str = "CLICK|[0.3337 0.8657]|NULL|1080|2400"
    # xy = action_str.split('|')[1]
    # if " " in xy:
    #     click_x,click_y = xy.s
    # elif "  " in xy:
    #     click_x,click_y = eval(xy)
    # print(xy)
    # click_x,click_y = eval(xy)
    # print(click_x,click_y)

    # a = 'com.android.chrome:id/url_bar' in {'com.android.chrome:id/url_bar', 'XSqSsc'}
    # print(a)
    
    # checkpoint_activity_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.activity"
    # captured_activity_fp = "/data/jxq/mobile-agent/testbed_draw_temp/jxq/trace_3/6.activity"
    
    checkpoint_json_fp = "/data/jxq/mobile-agent/aitw_replay_data/googleapps/trace_17/3.json"
    node_id = 16
    captured_xml_fp = "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/google_apps/2516012004368191039/captured_data/xml/1.xml"
    _textbox_exact_match(checkpoint_json_fp, node_id, captured_xml_fp)









