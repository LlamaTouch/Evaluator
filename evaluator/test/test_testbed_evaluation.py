from ..task_trace import DatasetHelper
from ..testbed_evaluation.get_crucial_states import CrucialStates


def test_crucial_state_initialization():
    epis = DatasetHelper().get_all_episodes()

    no_cs_cnt = 0
    cs_empty_list = []
    for epi in epis:
        gt_trace_path = DatasetHelper().load_testbed_goundtruth_trace_path_by_episode(
            epi
        )

        cs = CrucialStates(episode=epi, checkpoint_dir=gt_trace_path)
        if len(cs.get_crucial_states()) == 0:
            no_cs_cnt += 1
            cs_empty_list.append(cs.checkpoint_dir)
        else:
            cs.print_crucial_states()

    print(f"{no_cs_cnt} episodes has no crucial states")
    print("\n".join(cs_empty_list))

    assert False
