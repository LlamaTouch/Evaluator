from ..task_trace import DatasetHelper
from ..testbed_evaluation.get_essential_states import EssentialState, EssentialStates
from ..testbed_evaluation.xml_fuzzy_match import get_xml_fuzzy_match


def test_essential_state_initialization():
    epis = DatasetHelper().get_all_episodes()

    no_cs_cnt = 0
    cs_empty_list = []
    for epi in epis:
        gt_trace_path = DatasetHelper().load_testbed_goundtruth_trace_path_by_episode(
            epi
        )

        cs = EssentialStates(episode=epi, checkpoint_dir=gt_trace_path)
        if len(cs.get_essential_states()) == 0:
            no_cs_cnt += 1
            cs_empty_list.append(cs.checkpoint_dir)
        else:
            cs.print_essential_states()

    print(f"{no_cs_cnt} episodes has no essential states")
    print("\n".join(cs_empty_list))

    assert False
