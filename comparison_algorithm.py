
from get_checkpoint_list import Checkpoints
from xml_fuzzy_match import get_xml_fuzzy_match
from xml_exactly_match import exactly_match
from check_install import check_install
import os
import logging
import time

def _get_xml_path_list(xml_dir):
    """
    function: 根据xml_dir, 返回排序好的xml path list
    input: xml_dir: xml文件夹
    output: xml_path_list: xml path list
    """
    xml_list = [f for f in os.listdir(xml_dir) if f.split(".")[-1] == "xml"]
    xml_list.sort(key=lambda x: int(x.split(".")[0]))
    xml_path_list = [os.path.join(xml_dir, xml) for xml in xml_list]
    return xml_path_list

# assistant env
def comparison_algorithm(checkpoint_dir, captured_dir,COSSINE_BOUND=0.75):
    """
    function: 根据checkpoint_dir和captured_dir, 返回是否匹配成功
    input: checkpoint_dir: 标注完之后的文件夹
           captured_dir: captured文件夹
    output: True or False
    """
    checkpoints = Checkpoints(checkpoint_dir)
    checkpoint_fuzzy_match_list = checkpoints.get_fuzzy_match_list()

    # if checkpoints.installed_ls:
    #     return check_install(checkpoints.installed_ls, captured_dir)
    
    # else:
    checkpoint_xml_path_list = _get_xml_path_list(checkpoint_dir)
    captured_xml_path_list = _get_xml_path_list(os.path.join(captured_dir, "captured_data","xml"))
    for i in range(len(checkpoint_fuzzy_match_list)):
    # for i in range(len(checkpoints.checkpoint_ls)):
        # pic_id = int(checkpoints.checkpoint_ls[i].pic_id)
        pic_id = int(checkpoint_fuzzy_match_list[i]["pic_id"])
        fuzzy_match_node_id = int(checkpoint_fuzzy_match_list[i]["node_id"])
        checkpoint_xml_path = checkpoint_xml_path_list[pic_id]

        for index in range(len(captured_xml_path_list)):
            captured_xml_path = captured_xml_path_list[index]
            # 根据fuzzy_match_node_id, 来确实fuzzy match时候的范围
            if get_xml_fuzzy_match(checkpoint_xml_path,fuzzy_match_node_id,captured_xml_path,COSSINE_BOUND):
                logging.info(f"fuzzy match successfully: checkpoint {checkpoint_dir}/{pic_id}.xml and captured {captured_xml_path}")

                exactly_checkpoint_list = checkpoints.get_pic_exactly_match_list(pic_id)
                cnt = 0
                for k in range(len(exactly_checkpoint_list)):
                    checkpoint = exactly_checkpoint_list[k]
                    keyword = checkpoint.keyword
                    node_id = checkpoint.node_id
                    if exactly_match(checkpoint, checkpoint_dir, pic_id, keyword, node_id, captured_dir, index):
                        logging.info(f"{keyword} exactly match successfully: checkpoint {k}/{len(exactly_checkpoint_list)} {checkpoint_dir}/{pic_id}-{keyword}-{node_id} and captured {captured_xml_path}")
                        cnt += 1
                        logging.info(f"exactly matched : {cnt}/{len(exactly_checkpoint_list)}")
                if cnt == len(exactly_checkpoint_list):
                    logging.info(f"pic_id: {pic_id} exactly checkpoint total_match!: checkpoint {checkpoint_dir}/{pic_id}.xml and captured {captured_xml_path}")
                    
                    for k in range(len(exactly_checkpoint_list)):
                        checkpoint = exactly_checkpoint_list[k]
                        checkpoint.matched = True
                        checkpoint.capture_id = captured_xml_path_list[index].split("/")[-1].split(".")[0]
            else:
                logging.info(f"fuzzy match failed: checkpoint {checkpoint_dir}/{pic_id}.xml and captured {captured_xml_path}")
                continue
    
    # 判断checkpoints.checkpoint_ls中的matched是不是全是True
    checkpoints_ls = [checkpoint for checkpoint in checkpoints.checkpoint_ls if checkpoint.keyword != "fuzzy_match"] 
    matched_state = [checkpoint.matched for checkpoint in checkpoints_ls]
    
    if False in matched_state:
        logging.info("False in checkpoints, task not completed!")
        return False
    else:
        # 判断capture_id_list是不是升序序列
        # 升序
        capture_id_list = [int(checkpoint.capture_id) for checkpoint in checkpoints_ls]
        if capture_id_list == sorted(capture_id_list):
            logging.info("All True in checkpoints and capture_id_list is sorted, task completed!")
            return True
        else:
            logging.info("All True in checkpoints but capture_id_list is not sorted, task not completed!")
            return False


             
if __name__ == "__main__":

    log_dir_path = "/data/jxq/mobile-agent/comparison_algorithm/log/log"

    # 获取当前时间
    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler(f'{log_dir_path}/comparison_algorithm_{formatted_time}.log', 'w'),
                                logging.StreamHandler()])
    
    checkpoint_dir = "/data/jxq/mobile-agent/aitw_replay_data/googleapps/trace_5"
    captured_dir = "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/google_apps/12328916592710067202"
    comparison_algorithm(checkpoint_dir=checkpoint_dir, captured_dir=captured_dir)


