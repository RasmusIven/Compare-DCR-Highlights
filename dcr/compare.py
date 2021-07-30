def percentage(part, whole):
    if part > 0 and whole > 0:
        return 100 * float(part)/float(whole)
    else:
        return 0

def overlap(start1, end1, start2, end2):
    """
    Check if the ranges overlap.
    """
    return (end1 >= start2) and (end2 >= start1)


class Compare:
    def __init__(self, source: list, target: list, types: list):
        self.source = source
        self.target = target
        self.types = types
        self.results = dict()
    
    def set_result(self, result:list, typ:str):
        self.results[typ] = result
    

class CompareSpans(Compare):
    def give_score(self, aspan, bspan) -> int:
        """
        Given two annotations, checks if they are identical, or otherwise a overlap.
        Returns a score of 0, 0.5 or 1
        """
        score = 0
        if aspan == bspan:
            score = 1
        elif overlap(aspan[0], aspan[1], bspan[1], bspan[1]):
            score = 0.9

        return score

    # given two lists of elements with highlights, find overlaps in highlights.
    def overlaps(self, typ) -> list:
        matches = []
        source = self.source[f'{typ}']
        target = self.target[f'{typ}']
        scores ={}
        scores['points'] = 0
        for a in source:
            match = False
            if a.type == typ:
                for ah in a.highlights:
                    for b in target:
                        if b.type == typ:
                            for bh in b.highlights:
                                if match == False and self.give_score(ah.span(), bh.span() ) > 0:
                                    match = True
                                    score = self.give_score(ah.span(), bh.span())
                                    scores['points'] = scores['points'] + score
                                    matches.append({'score': score, 'matches': [a, b]})
                                    print(vars(a), vars(b))
                                    target.remove(b)
                                    source.remove(a)
                                    break;
            
        scores['amount'] = len(target) + len(source) + len(matches)
        scores['score'] = percentage(scores['points'], scores['amount'])
        return scores

