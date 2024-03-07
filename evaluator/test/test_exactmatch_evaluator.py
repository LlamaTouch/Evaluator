from ..agent import AppAgent
from ..exactmatch_evaluator import ExactMatchEvaluator


def test_appagent_eval():
    agent = AppAgent()
    e = ExactMatchEvaluator(agent=agent)
    e.run_evaluation()
    e.report_stats()

    assert False
