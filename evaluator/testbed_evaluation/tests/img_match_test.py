import unittest
from evaluator.task_trace import EssentialStateKeyword
from evaluator.testbed_evaluation.exact_match import check_img_match
from unittest.mock import Mock

class TestCheckImgMatch(unittest.TestCase):
    def setUp(self):
        self.image_similarity_bounds = [1,5,10]
        self.test_data = [
            # """small size of EXACT"""
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "image_similarity_bounds": 1,
                "expected": True  
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "image_similarity_bounds": 5,
                "expected": True  
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "image_similarity_bounds": 10,
                "expected": True  
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json', 
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png',
                "image_similarity_bounds": 1,
                "expected": True
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json', 
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png',
                "image_similarity_bounds": 5,
                "expected": True
            },
            {   
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json', 
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/3.png',
                "image_similarity_bounds": 10,
                "expected": True
            },
            {   
                # EXACT don`t match 
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png',
                "image_similarity_bounds": 1,                
                "expected": False
            },
            {   
                # EXACT don`t match 
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png',
                "image_similarity_bounds": 5,                
                "expected": False
            },
            {   
                # EXACT don`t match 
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/2.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["0"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case1/0.png',
                "image_similarity_bounds": 10,                
                "expected": False
            },

            # """middle size of EXACT"""
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "image_similarity_bounds": 1,
                "expected": True
            },
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "image_similarity_bounds": 5,
                "expected": True
            },
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "image_similarity_bounds": 10,
                "expected": True
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png',
                "image_similarity_bounds": 1,
                "expected": False
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png',
                "image_similarity_bounds": 5,
                "expected": True
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["16"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case2/2.png',
                "image_similarity_bounds": 10,
                "expected": True
            },
            # """large size of EXACT"""
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "image_similarity_bounds": 1,
                "expected": True
            },
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "image_similarity_bounds": 5,
                "expected": True
            },
            {
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "image_similarity_bounds": 10,
                "expected": True
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png',
                "image_similarity_bounds": 1,
                "expected": False
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png',
                "image_similarity_bounds": 5,
                "expected": False
            },
            {
                # EXACT don`t match
                "gr_simp_vh_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.json',
                "gr_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/1.png',
                "gr_essential_state": {EssentialStateKeyword.EXACT: ["22"]},
                "exec_image_path": 'evaluator/testbed_evaluation/tests/test_case/img_test_case/case3/2.png',
                "image_similarity_bounds": 10,
                "expected": False
            },
            
        ]

    def test_check_img_match(self):
        for test_case in self.test_data:
                with self.subTest(test_case=test_case):
                    bound = test_case["image_similarity_bounds"]
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