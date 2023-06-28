from typing import List
from models.goals import Tag

def ordered_ranked(tags: List[Tag], current_tag: Tag):
    score = 0
    values = []
    for i in tags:            
        values.append(score)
        
        if i == current_tag or score > 0:
            score += 1
        
    return tuple(values), values[tags.index(current_tag)]

def binary(tags: List[Tag], current_tag: Tag):
    opp = lambda x: 1 if x == 0 else 0
    values = [current_tag.value if t == current_tag else opp(t.value) for t in tags]
    return tuple(values), values[tags.index(current_tag)]
