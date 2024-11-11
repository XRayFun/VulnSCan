from typing import List, Any, Set
from _log import logger


_module_name = "utils.cleaner"


@logger(_module_name)
def get_filtered_list(inp:List[Any]|Set[Any], lowercase=False) -> List[Any]:
    cleared_set = set(filter(None, inp))
    if lowercase:
        return list({item.lower() if isinstance(item, str) else item for item in cleared_set})
    return list(cleared_set)


@logger(_module_name)
def get_filtered_str(inp:str, spaces=True, breaks=True) -> str:
    out = inp
    if spaces:
        out.replace(" ", "")
    if breaks:
        out.replace("\r", "").replace("\n", "")
    return out
