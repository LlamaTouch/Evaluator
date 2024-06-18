# Evaluate Collected Traces

This document provides an example of how to run the LlamaTouch Evaluator using collected traces from [AgentEnv](https://github.com/LlamaTouch/AgentEnv).
Typically, users need to run their own agents on top of AgentEnv and collect their own traces.

We use the agent, AutoUI, as an example and provides the traces during its execution on AgentEnv.

## Requirements

Before you begin, ensure you have the following files:

1. The ground-truth dataset: [download guide](https://github.com/LlamaTouch/LlamaTouch/tree/main/dataset)
2. Agent execution traces: download AutoUI's execution traces along with human validation results through this [OneDrive link](https://bupteducn-my.sharepoint.com/:u:/g/personal/li_zhang_bupt_edu_cn/EXA_L4k2ztlInCUeGD75ZqABRg-pI1iym5m5QJT9phh5Og?e=6Zp2uk)
3. Install the LlamaTouch Evaluator: [installation guide](../README.md#installation)

## Configuration

To run LlamaTouch Evaluator, you need to configure the following paths in [config.py](../config.py)

- `EPI_METADATA_PATH`: task metadata path; [link](https://github.com/LlamaTouch/LlamaTouch/blob/main/dataset/llamatouch_task_metadata.tsv)

- `GR_DATASET_PATH`: the ground-truth dataset path

- `AUTOUI_EXEC_TRACE_PATH`: path of AutoUI execution traces

- `AUTOUI_HUMANEVAL_PATH` (optional): path of the CSV file containing human validation results

## Run evaluators

In the root folder of this project, run the following commands to execute (1) the exact action method, (2) the LCS-based exact action match method, and (3) the LlamaTouch evaluation method:

```bash
# exact action match
python3 autoui.py --eval e

# lcs-based exact action match 
python3 autoui.py --eval lcse

# LlamaTouch evaluator
python3 autoui.py --eval t
```