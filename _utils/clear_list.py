from typing import List, Any, Set


def get_filtered_list(inp:List[Any]|Set[Any], lowercase=False) -> List[Any]:
    cleared_set = set(filter(None, inp))
    if lowercase:
        return list({item.lower() if isinstance(item, str) else item for item in cleared_set})
    return list(cleared_set)
