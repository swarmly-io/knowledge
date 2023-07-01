
from typing import Dict, List
from models.goals import GoalStatement, Group, GroupType, Tag
from services.group_utils import binary, ordered_ranked

class GoalScoring:
    
    def __init__(self, tags: List[Tag], groups: List[Group]):
        self.tags_dict = { t.name: t for t in tags }
        tag_groups = self.group_tags(tags)
        self.tag_score_fn = self.tag_scoring_functions(tag_groups, groups)
        # todo move to config
        self.group_absolute_rankings = {
            "health": 1,
            "goals": 6,
            "hostility": 0,
            "food": 2,
            "shelter": 3,
            "defence": 4,
            "tools": 7,
            "activity": 10,
            "inventory": 5,
            "tasks": 9,
            "money": 8
        }
        
    def select(goals: List[GoalStatement], active_tags: List[Tag]):
        return
    
    def score_goals(self, goals: List[GoalStatement], active_tags: List[Tag]):
        needs_multiplier_dict = self.calculate_needs_multiplier(active_tags)
        chosen_goals = []
        for goal in goals:
            failure_tags, failure_score, success_tags, success_score = self.filter_tags(goal, active_tags, needs_multiplier_dict)
        
            if failure_score > 0:
                chosen_goals.append((failure_score, 0, failure_tags, [], goal))
            elif success_score > 0:
                chosen_goals.append((0, success_score, [], success_tags, goal))
            else:
                print("Skipped ", goal.name)
        
        # todo if failure score is high - select those first goals
        # otherwise select high success goals 
        return list(map(lambda x: (x[0], x[1], x[-1]), sorted(chosen_goals, key=lambda x: (x[0], x[1]))))

    # if success and active, skip
    # if success and not active, score
    # if failure and active, score
    def filter_tags(self, goal, active_tags, needs_multiplier_dict):
        success_tags = []
        success_score = 0
        tag_dict = { at:at for at in active_tags }
        for success in goal.success:
            tag = tag_dict.get(success.tag)
            if tag:
               score = 0
            else:
                tag = self.tags_dict.get(success.tag)
                score = self.score(tag, needs_multiplier_dict)
            if score > 0:
                success_tags.append(success)
                success_score += score
        failure_tags = []
        failure_score = 0
        for failure in goal.success:
            tag = tag_dict.get(failure.tag)
            score = self.score(tag, needs_multiplier_dict)
            if score > 0:
                failure_tags.append(failure)
                failure_score += score
        
        return failure_tags, failure_score, success_tags, success_score
    
    def calculate_needs_multiplier(self, active_tags: List[Tag]):        
        # group is the denominator, lowest group is the numerator
        lowest_score = min([self.group_absolute_rankings.get(a.group) for a in active_tags])
        return { g: lowest_score/self.group_absolute_rankings[g]  for g in self.group_absolute_rankings }
    
    def score(self, tag: Tag, need_multiplier_dict: Dict[str, any]):
        return self.tag_score_fn.get(tag.name)(tag) * need_multiplier_dict[tag.name]

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
            
        

