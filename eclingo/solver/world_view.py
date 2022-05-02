from typing import List, NamedTuple

from eclingo.literals import EpistemicLiteral

class WorldView(NamedTuple):
    symbols: List[EpistemicLiteral]
    
    def __str__(self):
        # print("symbols inside world_view---------",self.symbols)
        return ' '.join(map(str, sorted(self.symbols)))
