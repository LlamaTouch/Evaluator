import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from evaluator.agent import MobileAgent

from .common.action_type import Action
from .evaluator import BaseEvaluator, FailedReason
from .exactmatch_evaluation.action_matching import check_actions_match
from .task_trace import (TaskTrace, get_all_actions, get_all_screenshot_paths,
                         get_all_vh_paths)
from .utils.vh_simplify import extract_ui_positions_from_vh


class LCSMatchEvaluator(BaseEvaluator):
    """
    Evaluate the task completion by calculating the Longest Common Subsequence
    (LCS) of the ground-truth trace and the task execution trace by testbed.
    """

    def __init__(
        self,
        agent: MobileAgent,
        epi_metadata_path: str,
        gr_dataset_path: str,
        options: Dict = None,
    ) -> None:
        super().__init__(agent, epi_metadata_path, gr_dataset_path, options)
        self.evaluator_name = self.__class__.__name__
        self.logger = logging.getLogger(self.evaluator_name)
        logging.getLogger().setLevel(logging.INFO)

    def eval_impl(
        self, episode, task_description
    ) -> Tuple[bool, Optional[FailedReason]]:
        gr_trace: TaskTrace = self.helper.load_groundtruth_trace_by_episode(episode)
        if not gr_trace:
            return False, FailedReason.GR_TRACE_NOT_FOUND
        try:
            gt_actions, gt_ui_positions = self._get_all_actions_uipositions(gr_trace)
        except:
            print("Failed to extract ui positions")
            return False, FailedReason.UI_POSITIONS_NOT_FOUND

        exec_trace: TaskTrace = self.agent.load_exec_trace_by_episode(episode)
        if not exec_trace:
            return False, FailedReason.EXEC_TRACE_NOT_FOUND
        try:
            exec_actions, exec_ui_positions = self._get_all_actions_uipositions(
                exec_trace
            )
        except:
            print("Failed to extract ui positions")
            return False, FailedReason.UI_POSITIONS_NOT_FOUND

        MAX_STEPS = 30
        f = np.zeros(shape=(MAX_STEPS + 5, MAX_STEPS + 5), dtype=np.int32)
        # i: index of ground truth trace
        for i in range(0, len(gt_actions)):
            # j: index of execution trace
            for j in range(0, len(exec_actions)):
                if j > 0:
                    f[i][j] = max(f[i][j], f[i][j - 1])
                if i > 0:
                    f[i][j] = max(f[i][j], f[i - 1][j])
                if self.check_action_match_like_AITW(
                    gt_actions[i], exec_actions[j], gt_ui_positions[i]
                ):
                    if i > 0 and j > 0:
                        f[i][j] = max(f[i][j], f[i - 1][j - 1] + 1)
                    else:
                        f[i][j] = max(f[i][j], 1)
        self.logger.info(
            f"episode = {episode}, LCS = {f[len(gt_actions) - 1][len(exec_actions) - 1]}"
        )
        return (
            int(f[len(gt_actions) - 1][len(exec_actions) - 1]) == len(gt_actions),
            FailedReason.STEP_CHECK_FAILED,
        )

    def _get_all_actions_uipositions(
        self, trace: TaskTrace
    ) -> Tuple[List[Action], List[np.ndarray[np.ndarray]]]:
        actions = get_all_actions(trace)
        screenshot_paths = get_all_screenshot_paths(trace)
        vh_paths = get_all_vh_paths(trace)
        ui_positions = [
            self.extract_ui_positions_from_vh(screenshot_path, vh_path)
            for screenshot_path, vh_path in zip(screenshot_paths, vh_paths)
        ]
        return actions, ui_positions

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
        # print(f"extracting {len(ui_positions)} UI positions from {vh_path}")
        if len(ui_positions) == 0:
            return np.array([])
        # normalize every single np.ndarray in ui_positions according to w, h
        ui_positions[:, [0, 2]] /= screen_height
        ui_positions[:, [1, 3]] /= screen_width
        return ui_positions
