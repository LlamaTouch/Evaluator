import json
import unittest

from evaluator.task_trace import EssentialStateKeyword
from evaluator.testbed_evaluation.exact_match import _check_img_exact_match


class TestCheckImgMatch(unittest.TestCase):
    def setUp(self):
        self.case_json = [
            "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json",
            "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json",
            "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json",
        ]
        self.test_data = [
            # """small size of EXACT"""
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "image_similarity_bounds": 1,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "image_similarity_bounds": 5,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "image_similarity_bounds": 10,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png",
                "image_similarity_bounds": 1,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png",
                "image_similarity_bounds": 5,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png",
                "image_similarity_bounds": 10,
                "expected": True,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png",
                "image_similarity_bounds": 1,
                "expected": False,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png",
                "image_similarity_bounds": 5,
                "expected": False,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[0], "r", encoding="utf-8")
                )[0],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png",
                "image_similarity_bounds": 10,
                "expected": False,
            },
            # """middle size of EXACT"""
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "image_similarity_bounds": 1,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "image_similarity_bounds": 5,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "image_similarity_bounds": 10,
                "expected": True,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png",
                "image_similarity_bounds": 1,
                "expected": False,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png",
                "image_similarity_bounds": 5,
                "expected": True,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[1], "r", encoding="utf-8")
                )[16],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png",
                "image_similarity_bounds": 10,
                "expected": True,
            },
            # """large size of EXACT"""
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "image_similarity_bounds": 1,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "image_similarity_bounds": 5,
                "expected": True,
            },
            {
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "image_similarity_bounds": 10,
                "expected": True,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png",
                "image_similarity_bounds": 1,
                "expected": False,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png",
                "image_similarity_bounds": 5,
                "expected": False,
            },
            {
                # EXACT don`t match
                "annotated_ui_node": json.load(
                    open(self.case_json[2], "r", encoding="utf-8")
                )[22],
                "gr_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png",
                "exec_image_path": "evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png",
                "image_similarity_bounds": 10,
                "expected": False,
            },
        ]

    def test_check_img_match(self):
        for test_case in self.test_data:
            with self.subTest(test_case=test_case):
                bound = test_case["image_similarity_bounds"]
                annotated_ui_node = test_case["annotated_ui_node"]
                gr_screenshot_path = test_case["gr_image_path"]
                exec_screenshot_path = test_case["exec_image_path"]
                result = _check_img_exact_match(
                    annotated_ui_node, gr_screenshot_path, exec_screenshot_path, bound
                )
                print(
                    f"Testing with bound {bound} and paths {test_case['gr_image_path']} vs {test_case['exec_image_path']}, Result: {result}"
                )
                self.assertEqual(result, test_case["expected"])


if __name__ == "__main__":
    unittest.main()
