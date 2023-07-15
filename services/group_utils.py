from typing import List
from models.goals import Tag

def ordered_ranked(tags: List[Tag], current_tag):
    values = []
    
    tags = sorted(tags, key=lambda x: x.value)
    for tag in tags:
        if tag.value >= current_tag.value:
            values.append(int(tag.value))
        else:
            values.append(0)
    
    max_value = max(values)

    return values[tags.index(current_tag)]/max_value

def binary(tags: List[Tag], current_tag: Tag):
    opp = lambda x: 1 if int(x) == 0 else 0
    values = [opp(t.value) for t in tags]
    return values[tags.index(current_tag)]
