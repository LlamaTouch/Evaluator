import logging
from typing import Dict, List, Optional, Tuple

from evaluator.agent import MobileAgent

from .evaluator import BaseEvaluator, FailedReason
from .task_trace import EssentialStateKeyword, TaskTrace, UIState
from .testbed_evaluation.exact_match import (
    check_activity_match,
    check_click_match,
    check_type_match,
    check_uicomponent_match,
)
from .testbed_evaluation.fuzzy_match import check_fuzzy_match
from .testbed_evaluation.system_state_match import (
    check_install_match,
    check_uninstall_match,
)


class TestbedEvaluator(BaseEvaluator):
    def __init__(self, agent: MobileAgent, options: Dict = None) -> None:
        super().__init__(agent, options)
        self.evaluator_name = self.__class__.__name__

        """Ablation Study
        1. fuzzy_match
            - screen_level_fuzzy_match
            - textbox_fuzzy_match
        2. exact_match
            - activity_exact_match
            - action_exact_match
            - UI_component_exact_match
            - system_state_exact_match
        close [fuzzy_match] means close all related to fuzzy match
        close [exact_match] means close all related to exact match
        open [screen_level_fuzzy_match, etc.] means only open itself
        """
        self.fuzzy_match = options.get("fuzzy_match", True) if options else True
        self.exact_match = options.get("exact_match", True) if options else True
        self.screen_level_fuzzy_match = (
            options.get("screen_level_fuzzy_match", False) if options else False
        )
        self.textbox_fuzzy_match = (
            options.get("textbox_fuzzy_match", False) if options else False
        )
        self.activity_exact_match = (
            options.get("activity_exact_match", False) if options else False
        )
        self.action_exact_match = (
            options.get("action_exact_match", False) if options else False
        )
        self.UI_component_exact_match = (
            options.get("UI_component_exact_match", False) if options else False
        )
        self.system_state_exact_match = (
            options.get("system_state_exact_match", False) if options else False
        )

        if (
            self.screen_level_fuzzy_match
            or self.textbox_fuzzy_match
            or self.activity_exact_match
            or self.action_exact_match
            or self.UI_component_exact_match
            or self.system_state_exact_match
        ):
            assert (
                self.screen_level_fuzzy_match
                + self.textbox_fuzzy_match
                + self.activity_exact_match
                + self.action_exact_match
                + self.UI_component_exact_match
                + self.system_state_exact_match
                <= 1
            ), "Only one ablation study can be enabled"
        if self.fuzzy_match:
            self.screen_level_fuzzy_match = True
            self.textbox_fuzzy_match = True
        if self.exact_match:
            self.activity_exact_match = True
            self.action_exact_match = True
            self.UI_component_exact_match = True
            self.system_state_exact_match = True

        self.logger = logging.getLogger(self.evaluator_name)
        logging.getLogger().setLevel(logging.WARNING)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        gr_trace: TaskTrace = self.helper.load_groundtruth_trace_by_episode(episode)
        if not gr_trace:
            return False, FailedReason.GR_TRACE_NOT_FOUND
        exec_trace: TaskTrace = self.agent.load_exec_trace_by_episode(episode)
        if not exec_trace:
            return False, FailedReason.EXEC_TRACE_NOT_FOUND

        # index for iterating exec_trace
        i = 0

        for ui_state in gr_trace:
            # if the current UIState contains no essential state, go to the next
            if ui_state.essential_state is None:
                continue

            # in this case, there is at least on essential state that is not matched
            # but the exec_traec has been iterated to the end of the list,
            # indicating the task is not completed
            if i == len(exec_trace):
                return False, "Remaining essential states are not matched"

            gr_ui_state_matched = False
            # when there is remaining UIState in the ground-truth trace and
            # remaining UIState in the task exec trace, compare and find two
            # matched UIState
            while i < len(exec_trace):
                cur_exec_ui_state: UIState = exec_trace[i]
                i += 1

                if not self.check_essential_state_match(ui_state, cur_exec_ui_state):
                    # current UIState in the exec trace does not match the
                    # essential state, go to the next UIState in the exec trace
                    continue
                else:
                    # current essential state matches UIState in the exec trace,
                    # go to the next essential state in the ground-truth trace
                    # and the next UIState in the exec trace
                    gr_ui_state_matched = True
                    break

            if gr_ui_state_matched:
                continue
            else:
                return False, None

        return True, None

    def check_essential_state_match(
        self, gr_ui_state: UIState, exec_ui_state: UIState
    ) -> bool:
        assert (
            gr_ui_state.essential_state is not None
        ), f"essential state in {gr_ui_state} is None"

        es_dict = gr_ui_state.essential_state

        if True:  # fuzzy_match
            fuzzy_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.FUZZY_MATCH, None
            )
            if fuzzy_match_states and not check_fuzzy_match(
                gr_ui_state,
                exec_ui_state,
                self.screen_level_fuzzy_match,
                self.textbox_fuzzy_match,
            ):
                return False

        if True:  # exact_match:
            uicomponent_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.EXACT, None
            )
            activity_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.ACTIVITY, None
            )
            click_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.CLICK, None
            )
            type_match_states: List[str] = es_dict.get(EssentialStateKeyword.TYPE, None)

            if (
                self.activity_exact_match
                and activity_match_states
                and not check_activity_match(gr_ui_state, exec_ui_state)
            ):
                return False

            if (
                self.UI_component_exact_match
                and uicomponent_match_states
                and not check_uicomponent_match(gr_ui_state, exec_ui_state)
            ):
                return False

            if (
                self.action_exact_match
                and type_match_states
                and not check_type_match(gr_ui_state, exec_ui_state)
            ):
                return False

            if (
                self.action_exact_match
                and click_match_states
                and not check_click_match(gr_ui_state, exec_ui_state)
            ):
                return False

        if self.system_state_exact_match:
            install_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.CHECK_INSTALL, None
            )
            uninstall_match_states: List[str] = es_dict.get(
                EssentialStateKeyword.CHECK_UNINSTALL, None
            )

            if install_match_states and not check_install_match(
                gr_ui_state, exec_ui_state
            ):
                return False

            if uninstall_match_states and not check_uninstall_match(
                gr_ui_state, exec_ui_state
            ):
                return False

        return True
