
from typing import List

from models.goals import GoalFailure, GoalStatement, GoalSuccess, Group, GroupType, Tag, TagType
from services.goal_valuation import GoalValuation


class TestGoals:
    def __init__(self):
        self.goals: List[GoalStatement] = [
            GoalStatement(name="health", type=TagType.SURVIVAL, success=[GoalSuccess(tag="high_health")], failure=[GoalFailure(tag="no_health")]),
            GoalStatement(name="handle_hords", type=TagType.THREAT, success=[GoalSuccess(tag="zombie_far")], failure=[GoalFailure(tag="zombie_close")]),
            GoalStatement(name="eat_cake", type=TagType.GOAL, success=[GoalSuccess(tag="eat_cake")], failure=[])
        ]
        
        self.tags = [
            Tag(name="high_health", type=TagType.SURVIVAL, value=0, group="health"),
            Tag(name="no_health", type=TagType.SURVIVAL, value=1, group="health"),
            Tag(name="zombie_close", type=TagType.THREAT, value=1, group="hostility"),
            Tag(name="zombie_far", type=TagType.THREAT, value=1, group="hostility"),
            Tag(name="eat_cake", type=TagType.GOAL, value=1, group="goals")
        ]
        
        self.groups: List[Group] = [
            Group(name="health", type=GroupType.ORDERED_RANKED),
            Group(name="hostility", type=GroupType.BINARY),
            Group(name="goals", type=GroupType.BINARY)
        ]
        
        self.valuation = GoalValuation(self.tags, self.groups)
        
def test_scoring_will_fight_zombies():
    test_object = TestGoals()
    tag_dict = { t.name:t for t in test_object.tags }
    active_tags = [tag_dict.get("high_health"), tag_dict.get("zombie_close")]
    scores = test_object.valuation.score_goals(test_object.goals, active_tags)
    for fail_score, success_score, goals in scores:
        assert fail_score == 1.0
        assert success_score == 0.0
        assert goals == test_object.goals[1]
        
def test_scoring_will_focus_on_hords_low_health():
    test_object = TestGoals()
    tag_dict = { t.name:t for t in test_object.tags }
    active_tags = [tag_dict.get("no_health"), tag_dict.get("zombie_close")]
    scores = test_object.valuation.score_goals(test_object.goals, active_tags)
    for fail_score, success_score, goals in scores:
        assert fail_score == 1.0
        assert success_score == 0.0
        assert goals == test_object.goals[1]
        
def test_scoring_will_focus_on_cake():
    test_object = TestGoals()
    tag_dict = { t.name:t for t in test_object.tags }
    active_tags = [tag_dict.get("high_health"), tag_dict.get("zombie_far")]
    scores = test_object.valuation.score_goals(test_object.goals, active_tags)
    for fail_score, success_score, goals in scores:
        assert fail_score == 0.0
        assert success_score > 0
        assert goals == test_object.goals[2]
    