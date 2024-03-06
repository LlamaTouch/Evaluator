
from comparison_algorithm import comparison_algorithm
import time
import logging
import os
import pandas as pd

dir_map = dict()


part = ""
classes = "web_shopping"
# classes = "general"
# classes = "install"
# classes = "googleapps"

agent = "auto-ui"
COSSINE_BOUND = 0.7
# agent = "appagent"
log_dir_path = f"/data/jxq/mobile-agent/comparison_algorithm/log/{agent}/{classes}"

dir_map["web_shopping"] = f"/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/{classes}/"
dir_map["general"] = f"/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/{classes}/"
dir_map["install"] = f"/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/{classes}/"
dir_map["googleapps"] = f"/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/google_apps/"

# 获取当前时间
current_time = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(f'{log_dir_path}/COSSINE_BOUND_{COSSINE_BOUND}_comparison_algorithm_{formatted_time}.log', 'w'),
                            logging.StreamHandler()])

instruction_fp = f"/data/jxq/mobile-agent/comparison_algorithm/tasks/{classes}/all_instruction{part}.csv"
# instruction_fp = "/data/jxq/all_instruction_appagent-2.csv"
top_checkpoint_dir = f"/data/jxq/mobile-agent/aitw_replay_data/{classes}/"
top_capture_dir = dir_map[classes]



checkpoint_dir_ls = []
captured_dir_ls = []

instruction_data = pd.read_csv(instruction_fp)
total_instruction_num = len(instruction_data)
testbed_judge_success_state = []
output_data = pd.DataFrame(columns=["episode_id", "instruction", "success_flag"])

for index, row in instruction_data.iterrows():
    trace_temp = row["trace_folder_path"].split("/")[-1]
    checkpoint_dir_ls.append(os.path.join(top_checkpoint_dir, trace_temp))
    captured_dir_ls.append(os.path.join(top_capture_dir, str(row["episode_id"])))
    
    # for i in range(len(captured_epsoide_dir)):
    #     if str(row["episode_id"]) in captured_epsoide_dir[i]:
    #         captured_dir_ls.append(captured_epsoide_dir[i])
    #         break



for i, row in instruction_data.iterrows():
    checkpoint_dir = checkpoint_dir_ls[i]
    captured_dir = captured_dir_ls[i]

    logging.info(f"task {i}:{instruction_data.iloc[i]['instruction']}")
    logging.info(f"checkpoint_dir: {checkpoint_dir}")
    logging.info(f"captured_dir: {captured_dir}")

    if comparison_algorithm(checkpoint_dir, captured_dir, COSSINE_BOUND):
        logging.info(f"comparison_algorithm successfully: {checkpoint_dir} and {captured_dir}")
        testbed_judge_success_state.append(True)
    else:
        logging.info(f"comparison_algorithm failed: {checkpoint_dir} and {captured_dir}")
        testbed_judge_success_state.append(False)

for index, row in instruction_data.iterrows():
    output_data.loc[index] = [str(row["episode_id"]), row["instruction"], testbed_judge_success_state[index]]

output_data.to_csv(f"/data/jxq/mobile-agent/comparison_algorithm/output_data/{classes}/{agent}/{formatted_time}_{part}_COSSINE_BOUND_{COSSINE_BOUND}.csv", index=False)
logging.info(f"success_num: {testbed_judge_success_state.count(True)}")
logging.info(f"total_instruction_num: {total_instruction_num}")
logging.info(f"testbed judge success_rate: {testbed_judge_success_state.count(True)/total_instruction_num}")


# testbed_judge_success_state = pd.read_csv("/data/jxq/mobile-agent/comparison_algorithm/output_data/{classes}/appagent/2024-01-31 20:24:31.csv")
# testbed_judge_success_state = list(testbed_judge_success_state["success_flag"])
# human_judegement = pd.read_csv("/data/jxq/mobile-agent/comparison_algorithm/output_data/{classes}/appagent-task-human.csv")
# human_judegement_state = list(human_judegement["success_flag"])

# testbed_accuracy_state = [ts == hs for ts, hs in zip(testbed_judge_success_state,human_judegement_state)]
# logging.info(f"testbed_accuracy: {testbed_accuracy_state.count(True)/len(testbed_accuracy_state)}")

# testbed_tp = []
# testbed_fp = []
# testbed_tn = []
# testbed_fn = []

# for ts, hs in zip(testbed_judge_success_state,human_judegement_state):
#     if ts == True and hs == True:
#         testbed_tp.append(True)
#         testbed_fp.append(False)
#         testbed_fn.append(False)
#         testbed_tn.append(False)
#     elif ts == True and hs == False:
#         testbed_tp.append(False)
#         testbed_fp.append(True)
#         testbed_fn.append(False)
#         testbed_tn.append(False)
#     elif ts == False and hs == True:
#         testbed_tp.append(False)
#         testbed_fp.append(False)
#         testbed_fn.append(True)
#         testbed_tn.append(False)
#     elif ts == False and hs == False:
#         testbed_tp.append(False)
#         testbed_fp.append(False)
#         testbed_fn.append(False)
#         testbed_tn.append(True)

# logging.info(f"testbed true positive number: {testbed_tp.count(True)}")
# logging.info(f"testbed false positive numnber: {testbed_fp.count(True)}")
# logging.info(f"testbed false negative number: {testbed_fn.count(True)}")
# logging.info(f"testbed true negative number: {testbed_tn.count(True)}")



    
    





