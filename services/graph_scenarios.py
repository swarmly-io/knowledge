
from copy import deepcopy
from typing import Dict, List
from models.goals import GoalStatement, Tag
from services.graph_composer import GraphComposer
from services.models import TagLink
from utils import flatten


class GraphScenarios:
    def __init__(self, composer: GraphComposer, tag_dict: Dict[str, Tag]):
        self.composer = deepcopy(composer)
        self.tag_dict = tag_dict

    def get_graph(self, goals: List[GoalStatement], tag_links: List[TagLink], lenses=[]):
        def tag(x): return [self.tag_dict.get(g.tag) for g in x]
        all_tags = flatten([tag(g.success) + tag(g.failure) for g in goals])
        _ = self.composer.link_goals_and_get_targets(goals, all_tags, tag_links)

        if not lenses:
            return self.composer.get_composed_graph()
        else:
            return self.composer.apply_lenses(lenses, flag_infeasible=True)
