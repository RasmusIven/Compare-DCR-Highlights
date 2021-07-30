class Elem:
    def __init__(self, type, ID):
        self.type: str  = type
        self.id: str = ID
        self.highlights: list = []

    def set_H(self, H):
        self.highlights.append(H)
        
    def get_H(self) -> list:
        return self.highlights
    
    def get_spans(self) -> list:
        ranges = []
        for H in self.highlights:
            ranges.append(H.span())
        return ranges

    
class H:
    def __init__(self, start, end):
        self.start: int = start
        self.end: int = end
    
    def span(self) -> list:
        return [self.start, self.end]

 