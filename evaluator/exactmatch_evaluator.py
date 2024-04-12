import logging
from collections import defaultdict
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image

from evaluator.agent import MobileAgent

from .evaluator import BaseEvaluator, FailedReason
from .exactmatch_evaluation.action_matching import check_actions_match
from .task_trace import get_all_actions, get_all_screenshot_paths, get_all_vh_paths
from .utils.vh_simplify import extract_ui_positions_from_vh


class ExactMatchEvaluator(BaseEvaluator):
    def __del__(self):
        for epi, n in self.epi_to_num_correct_action.items():
            print(f"{epi} has {n} correct actions")

    def __init__(self, agent: MobileAgent, options: Dict = None) -> None:
        super().__init__(agent, options)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)
        self.epi_to_num_correct_action = defaultdict(int)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        """Exact match evaluation using self-defined trace"""
        gr_trace = self.helper.load_groundtruth_trace_by_episode(episode)
        if not gr_trace:
            return False, FailedReason.GR_TRACE_NOT_FOUND
        screenshot_paths = get_all_screenshot_paths(gr_trace)
        vh_paths = get_all_vh_paths(gr_trace)
        gr_actions = get_all_actions(gr_trace)
        agent_predicted_actions = self.agent.load_predicted_action_by_episode(episode)
        if not agent_predicted_actions:
            return False, FailedReason.EXEC_TRACE_NOT_FOUND

        # print("=======", len(gr_actions), len(agent_predicted_actions))
        # print(gr_actions[-1])
        # print(agent_predicted_actions[-1])

        for i, gr_action in enumerate(gr_actions):
            if i >= len(agent_predicted_actions):
                return False, FailedReason.STEP_CHECK_FAILED.value + f" on step {i}"
            real_action = agent_predicted_actions[i]
            try:
                ui_positions = self.extract_ui_positions_from_vh(
                    screenshot_paths[i], vh_paths[i]
                )
            except:
                print(f"failed to extract ui positions from file: {vh_paths[i]}")
                return False, FailedReason.UI_POSITIONS_NOT_FOUND
            if len(ui_positions) == 0:
                return False, FailedReason.UI_POSITIONS_NOT_FOUND

            if not self.check_action_match_like_AITW(
                gr_action, real_action, ui_positions
            ):
                return False, FailedReason.STEP_CHECK_FAILED.value + f" on step {i}"
            else:
                self.epi_to_num_correct_action[episode] += 1
                print(f"step{i} passed")
        return True, None

    def check_action_match_like_AITW(
        self, gr_action, exec_action, ui_positions
    ) -> bool:
        try:
            check_match = check_actions_match(
                gr_action.touch_point_yx,
                gr_action.lift_point_yx,
                gr_action.action_type,
                exec_action.touch_point_yx,
                exec_action.lift_point_yx,
                exec_action.action_type,
                ui_positions,
            )
        except Exception as e:
            check_match = False
        return check_match

    def extract_ui_positions_from_vh(
        self, screenshot_path: str, vh_path: str
    ) -> np.ndarray[np.ndarray]:
        """Extract UI positions used for evaluation from view hierarchy

        Args:
            screenshot_path: path to the screenshot; used to get (width, height)
            vh_path: path to the view hierarchy file

        Return:
            normalized_ui_positions: [
                [y, x, height, width],
                [y, x, height, width],
                [y, x, height, width],
                ...
            ]
        """
        screen_width, screen_height = Image.open(screenshot_path).size
        ui_positions = extract_ui_positions_from_vh(vh_path).astype(float)
        print(f"extracting {len(ui_positions)} UI positions from {vh_path}")
        if len(ui_positions) == 0:
            return np.array([])
        # normalize every single np.ndarray in ui_positions according to w, h
        ui_positions[:, [0, 2]] /= screen_height
        ui_positions[:, [1, 3]] /= screen_width
        return ui_positions
