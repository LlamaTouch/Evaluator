import unittest
from unittest.mock import Mock
from evaluator.testbed_evaluation.exact_match import check_click_match
from evaluator.task_trace import EssentialStateKeyword, ActionType


class TestCheckClickMatch(unittest.TestCase):
    def setUp(self):
        self.test_cases = [
            {
                "gr_essential_state": {
                    EssentialStateKeyword.CLICK: ['//*[@text="Done"]']
                },
                "gr_vh_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.xml",
                "exec_action": Mock(
                    action_type=ActionType.DUAL_POINT,
                    touch_point_yx=(0.55, 0.5),
                    lift_point_yx=(0.55, 0.5),
                ),
                "exec_vh_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.xml",
                "exec_screenshot_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.png",
                "expected_result": True,
            },
            {
                # click on the wrong place
                "gr_essential_state": {
                    EssentialStateKeyword.CLICK: ['//*[@text="Done"]']
                },
                "gr_vh_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.xml",
                "exec_action": Mock(
                    action_type=ActionType.DUAL_POINT,
                    touch_point_yx=(0.5, 0.5),
                    lift_point_yx=(0.5, 0.5),
                ),
                "exec_vh_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.xml",
                "exec_screenshot_path": "evaluator/testbed_evaluation/tests/test_case/click_test_case/case1/10.png",
                "expected_result": False,
            },
        ]

    def test_click_match(self):
        for case in self.test_cases:
            with self.subTest(case=case):
                gr_ui_state = Mock()
                gr_ui_state.essential_state = case["gr_essential_state"]
                gr_ui_state.vh_path = case["gr_vh_path"]
                exec_ui_state = Mock()
                exec_ui_state.action = case["exec_action"]
                exec_ui_state.vh_path = case["exec_vh_path"]
                exec_ui_state.screenshot_path = case["exec_screenshot_path"]
                result = check_click_match(gr_ui_state, exec_ui_state)
                self.assertEqual(result, case["expected_result"])


if __name__ == "__main__":
    unittest.main()
