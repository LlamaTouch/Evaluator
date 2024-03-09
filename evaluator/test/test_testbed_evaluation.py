from ..task_trace import DatasetHelper
from ..testbed_evaluation.get_crucial_states import CrucialStates


def test_crucial_state_initialization():
    epis = DatasetHelper().get_all_episodes()
    print(len(epis))

    no_cs_cnt = 0
    for epi in DatasetHelper().get_all_episodes():
        gt_trace_path = DatasetHelper().load_testbed_goundtruth_trace_path_by_episode(
            epi
        )

        cs = CrucialStates(episode=epi, checkpoint_dir=gt_trace_path)
        if len(cs.get_crucial_states()) == 0:
            no_cs_cnt += 1
            print(f"{gt_trace_path} has no crucial states annotated")

    print(f"{no_cs_cnt} episodes has no crucial states")

    assert False
