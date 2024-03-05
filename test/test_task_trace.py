from ..task_trace import DatasetHelper, TaskCategory


def test():
    # test 1
    DatasetHelper().init_epi_to_category()
    print(DatasetHelper().epi_metadata_dict)
    # test 2
    gt_trace = DatasetHelper().load_groundtruth_trace_by_category(TaskCategory.GENERAL)
    print(gt_trace)
    # test 3
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/1.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/2.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/3.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/4.action")
    # test 4
    DatasetHelper().load_testbed_trace_by_path(
        "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/web_shopping/10016075255396203771/captured_data"
    )

    assert False
