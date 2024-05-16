import unittest
from evaluator.task_trace import EssentialStateKeyword
from evaluator.testbed_evaluation.exact_match import check_img_match
from unittest.mock import Mock

class TestCheckImgMatch(unittest.TestCase):
    def setUp(self):
        self.image_similarity_bounds = [1,5,10]
        self.test_data = [
            # """small size of image"""
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "expected": True  
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json', 
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png',
                "expected": True
            },
            {   
                # image don`t match 
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png',
                "expected": False
            },
            # """middle size of image"""
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "expected": True
            },
            {
                # image don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png',
                "expected": False
            },
            # """large size of image"""
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "expected": True
            },
            {
                # image don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.IMAGE: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png',
                "expected": False
            },
            
        ]

    def test_check_img_match(self):
        for test_case in self.test_data:
            for bound in self.image_similarity_bounds:
                with self.subTest(test_case=test_case, bound=bound):
                    gr_ui_state = Mock()
                    gr_ui_state.vh_simp_ui_json_path = test_case["gr_simp_vh_path"]
                    gr_ui_state.screenshot_path = test_case["gr_image_path"]
                    gr_ui_state.essential_state = test_case["gr_essential_state"]
                    exec_ui_state = Mock()
                    exec_ui_state.screenshot_path = test_case["exec_image_path"]
                    result = check_img_match(gr_ui_state, exec_ui_state, bound)
                    print(f"Testing with bound {bound} and paths {test_case['gr_image_path']} vs {test_case['exec_image_path']}, Result: {result}")
                    self.assertEqual(result, test_case["expected"])

if __name__ == '__main__':
    unittest.main()