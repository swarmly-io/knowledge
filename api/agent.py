from typing import List
from api.models import AgentDto
from domain_models.decisions.goals import TagDto, GoalStatement
from services.agent import Agent

from minecraft_graph.feasibility import NodeFeasibility
from domain_models.decisions.links import TagLink
from domain_models.minecraft.state import AgentMCState

class AgentService:
    def __init__(self):
        self.goals: List[GoalStatement] = []
        self.agent: Agent = None

    def create_agent(self, agent: AgentDto):
        self.agent = Agent(
            agent.name,
            agent.goals,
            agent.actions,
            agent.tag_list,
            agent.groups)

    def add_tag_links(self, links: List[str]):
        self.agent.add_tag_links(links)

    def set_composer(self, composer):
        self.composer = composer

    def set_mc_state(self, state: AgentMCState):
        self.agent.state.mcState = state

    def add_active_tags(self, tags: List[str]) -> List[TagDto]:
        tag_dict = {t.name: t for t in self.agent.all_tags}
        
        def update_tags_by_group(new_tags):
            active_tags = self.agent.state.tags
            existing_groups = {tag.group: tag for tag in active_tags}
                        
            for tag in new_tags:
                if tag.group in existing_groups:
                    active_tags.remove(existing_groups[tag.group])
                
                active_tags.append(tag)
            
            return active_tags
        
        new_tags = [tag_dict.get(t) for t in tags if tag_dict.get(t)]
        self.agent.state.tags = update_tags_by_group(new_tags)
        rankings = self.agent.goal_valuation.group_absolute_rankings
        tags_resp = [TagDto(**t.dict(), group_rank=rankings.get(t.group))
                     for t in self.agent.state.tags]
        return tags_resp

    def get_agent_service(self):
        return self

    def add_goals(self, goals: List[GoalStatement]):
        self.goals = self.goals + goals