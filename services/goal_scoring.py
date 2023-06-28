
from typing import Dict, List
from models.goals import GoalStatement, Group, GroupType, Tag
from services.group_utils import binary, ordered_ranked

class GoalScoring:
    
    def __init__(self, tags: List[Tag], groups: List[Group]):
        tag_groups = self.group_tags(tags)
        self.tag_score_fn = self.tag_scoring_functions(tag_groups, groups)
    
    def score_goals(self, goals: List[GoalStatement], active_tags: List[Tag]):
        chosen_goals = []
        for goal in goals:
            failure_tags, failure_score, success_tags, success_score = self.filter_tags(goal, active_tags)
        
            if failure_score > 0:
                chosen_goals.append((failure_score, 0, failure_tags, [], goal))
            elif success_score > 0:
                chosen_goals.append((0, success_score, [], success_tags, goal))
            else:
                print("Skipped ", goal.name)
        
        return list(map(lambda x: x[-1], sorted(chosen_goals, key=lambda x: (x[0], x[1]))))

    def filter_tags(self, goal, active_tags):
        success_tags = []
        success_score = 0
        tag_dict = { at:at for at in active_tags }
        for success in goal.success:
            score = self.score(tag_dict.get(success.tag))
            if score > 0:
                success_tags.append(success)
                success_score += score
        failure_tags = []
        failure_score = 0
        for failure in goal.success:
            score = self.score(tag_dict.get(failure.tag))
            if score > 0:
                failure_tags.append(failure)
                failure_score += score
        
        return failure_tags, failure_score, success_tags, success_score
    
    def score(self, tag: Tag):
        return self.tag_score_fn.get(tag.name)(tag)

    def group_tags(self, tags: List[Tag]):
        groups = {}
        for t in tags:
            if not groups.get(t.group):
                groups[t.group] = []
            groups[t.group].append(t)
        return groups

    def tag_scoring_functions(self, tags: Dict[str, List[Tag]], groups: List[Group]):
        group_dict = { g.name: g for g in groups } 
        thunks = { }
        for n, tg in tags.items():
            group = group_dict.get(tg[0].group)
            if group.type == GroupType.ORDERED_RANKED:
                # value should be the order
                tg = sorted(tg, key=lambda x: x.value)
                thunks[tg[0].name] = lambda ct: ordered_ranked(tags, ct)
            elif group.type == GroupType.BINARY:
                # binary types should have starting values, if not active it's the opposite of that value
                # like a toggle
                thunks[tg[0].name] = lambda ct: binary(tags, ct)
            elif group.type == GroupType.CUSTOM_FUNCTION:
                print("Not implemented")
            
        return thunks
            
        

