
from copy import deepcopy
from typing import Dict, List, Tuple
from models.goals import GoalStatement, Group, GroupType, Tag
from services.group_utils import binary, ordered_ranked

class GoalValuation:
    
    def __init__(self, tags: List[Tag], groups: List[Group]):
        self.tags_dict = { t.name: t for t in tags }
        tag_groups = self.group_tags(tags)
        self.tag_score_fn = self.tag_scoring_functions(tag_groups, groups)
        # todo move to config
        self.group_absolute_rankings = {
            "health": 2,
            "goals": 7,
            "hostility": 1,
            "food": 3,
            "shelter": 4,
            "defence": 5,
            "tools": 8,
            "activity": 11,
            "inventory": 6,
            "tasks": 10,
            "money": 9
        }
        
    # select highest score goals
    # returns intersection of selected goal and tags (success != active, failure == active)
    def select(self, goals: List[GoalStatement], active_tags: List[Tag], goal_count: int = 1):
        scores = self.score_goals(goals, active_tags)
        if not scores:
            raise Exception("No goals to select from")
        scores = scores[0: goal_count]
        focus_tags = []
        goals: List[GoalStatement] = []
        
        tag_dict = { a.name: a for a in active_tags }
        goal_scores = {}
        for fscore, sscore, goal in scores:
            goals.append(goal)
            for tag in goal.success:
                if tag not in tag_dict:
                    focus_tags.append(self.tags_dict.get(tag))
            for tag in goal.failure:
                if tag in tag_dict:
                    focus_tags.append(self.tags_dict.get(tag))
            goal_scores[goal.name] = { 'failure': fscore, 'success': sscore }
        
        return goals, focus_tags
    
    def score_goals(self, goals: List[GoalStatement], active_tags: List[Tag]) -> List[Tuple[float, float, GoalStatement]]:
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
        
        # if failure score is high - select those first goals
        # otherwise select high success goals 
        return list(map(lambda x: (x[0], x[1], x[-1]), sorted(chosen_goals, key=lambda x: (x[0], x[1]))))

    # if success and active, skip
    # if success and not active, score
    # if failure and active, score
    def filter_tags(self, goal, active_tags, needs_multiplier_dict):
        success_tags = []
        success_score = 0
        tag_dict = { at.name:at for at in active_tags }
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
        for failure in goal.failure:
            tag = tag_dict.get(failure.tag)
            if not tag:
                continue
            score = self.score(tag, needs_multiplier_dict)
            if score > 0:
                failure_tags.append(failure)
                failure_score += score
        
        return failure_tags, failure_score, success_tags, success_score
    
    def calculate_needs_multiplier(self, active_tags: List[Tag]):        
        # group is the denominator, lowest group is the numerator
        lowest_score = min([self.group_absolute_rankings.get(a.group) for a in active_tags])
        print([self.group_absolute_rankings.get(a.group) for a in active_tags])
        return { g: lowest_score/self.group_absolute_rankings[g]  for g in self.group_absolute_rankings }
    
    # todo use Tag type in calculation
    def score(self, tag: Tag, need_multiplier_dict: Dict[str, any]):
        score = self.tag_score_fn.get(tag.group)(self.groups_lookup[tag.group], tag)
        return float(score) * need_multiplier_dict[tag.group]

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
        self.groups_lookup = {}
        for n, tg in tags.items():
            group = group_dict.get(tg[0].group)
            if group.type == GroupType.ORDERED_RANKED:
                # value should be the order
                tg = sorted(tg, key=lambda x: x.value)
                self.groups_lookup[tg[0].group] = tg   
                thunks[tg[0].group] = lambda tg, ct: ordered_ranked(tg, ct)
            elif group.type == GroupType.BINARY:
                # binary types should have starting values, if not active it's the opposite of that value
                # like a toggle
                self.groups_lookup[tg[0].group] = tg
                thunks[tg[0].group] = lambda tg, ct: binary(tg, ct)
            elif group.type == GroupType.CUSTOM_FUNCTION:
                print("Not implemented")
            
        return thunks
            
        

