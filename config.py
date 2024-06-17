class CONFIG:
    # task metadata and the dataset
    # see docs at https://github.com/LlamaTouch/LlamaTouch/tree/main/dataset
    EPI_METADATA_PATH = "/path/to/llamatouch_task_metadata.tsv"
    GR_DATASET_PATH = "/path/to/llamatouch_dataset"

    # agent exec trace path
    AUTOUI_EXEC_TRACE_PATH = "/path/to/trace"
    AUTODROID_EXEC_TRACE_PATH = "/path/to/trace"
    APPAGENT_EXEC_TRACE_PATH = "/path/to/trace"
    COCOAGENT_EXEC_TRACE_PATH = "/path/to/trace"

    # human eval result path
    AUTOUI_HUMANEVAL_PATH = "/path/to/human_eval_result"
    AUTODROID_HUMANEVAL_PATH = "/path/to/human_eval_result"
    APPAGENT_HUMANEVAL_PATH = "/path/to/human_eval_result"
    COCOAGENT_HUMANEVAL_PATH = "/path/to/human_eval_result"
