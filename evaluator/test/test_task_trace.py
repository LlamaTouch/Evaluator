import pytest

from ..task_trace import DatasetHelper, TaskCategory, TaskTrace


def test_general():
    # test 1
    DatasetHelper().init_epi_to_category()
    print(DatasetHelper().epi_metadata_dict)
    # test 2
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/1.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/2.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/3.action")
    DatasetHelper()._proc_testbed_trace_action_file("test_asset/4.action")

    assert False


def test_load_groundtruth_trace_wrong_episode():
    wrong_epi = "100100100100"
    with pytest.raises(KeyError):
        DatasetHelper().load_groundtruth_trace_by_episode(wrong_epi)


def test_load_groundtruth_trace():
    """Test whether all groundtruth traces are loaded in the correct order."""
    gt_trace = DatasetHelper()._load_groundtruth_trace_by_category(TaskCategory.GENERAL)

    for epi in gt_trace.keys():
        # catch exception
        if epi not in DatasetHelper().epi_metadata_dict.keys():
            with pytest.raises(KeyError):
                trace: TaskTrace = DatasetHelper().load_groundtruth_trace_by_episode(
                    epi
                )
            continue

        trace: TaskTrace = DatasetHelper().load_groundtruth_trace_by_episode(epi)

        # assert all items in two lists are identiacl
        screen_paths = [ui_state[0].split("/")[-1] for ui_state in trace]
        sorted_screen_paths = sorted(screen_paths)
        assert screen_paths == sorted_screen_paths

        vh_paths = [ui_state[1].split("/")[-1] for ui_state in trace]
        sorted_vh_paths = sorted(vh_paths)
        assert vh_paths == sorted_vh_paths


def test_load_testbed_trace():
    DatasetHelper().load_testbed_trace_by_path(
        "/data/zzh/mobile-agent/Auto-UI/agentenv/agent_result/web_shopping/10016075255396203771/captured_data"
    )

    assert False