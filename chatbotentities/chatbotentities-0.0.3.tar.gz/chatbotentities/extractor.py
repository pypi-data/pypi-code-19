from pattern.es import parsetree
from pattern.search import Pattern


class EntityConfig(object):
    def __init__(self, expression, type, config=None, negation=False, taxonomy=None, strict=False, exclude=None):
        self.expression = expression
        self.type = type
        self.taxonomy = taxonomy
        if config is None:
            config = {'value': 1}
        self.config = config
        if negation is None:
            negation = False
        self.negation = negation
        self.pattern = Pattern.fromstring(expression, taxonomy=taxonomy, strict=strict)
        self.strict = strict
        self.exclude = set() if exclude is None else set(exclude)
        
    def allow_word(self, word):
        if self.taxonomy is None:
            return True;
        if set(self.taxonomy.parents(word)).intersection(self.exclude):
            return False
        return True
        
    def __call__(self, sentence):
        match = self.pattern.match(sentence)
        if match is None:
            return None
        result = {}
        for key, index in self.config.items():
            group = match.group(index);
            position = group[0].index
            group = [group.string for group in match.group(index) if self.allow_word(group.string)]
            if not group:
                return None
            result[key] = ' '.join(group)
            result['position'] = position
        result['negation'] = self.negation
        result['type'] = self.type
        return result
    
    
class EntitiesFirst(object):
    def __init__(self, *configs):
        self.configs = configs
        
    def __call__(self, sentence):
        for config in self.configs:
            entity = config(sentence)
            if not entity:
                continue
            if isinstance(entity, list):
                entity = entity[0]
            return [entity]
        return None


class EntitiesAll(object):
    def __init__(self, *configs):
        self.configs = configs
        
    def __call__(self, sentence):
        result = []
        for config in self.configs:
            entity = config(sentence)
            if not entity:
                continue
            if isinstance(entity, dict):
                entity = [entity]
            result.extend(entity)
        result.sort(key=lambda x: x['position'])
        return result


class EntitiesExtractor(object):
    def __init__(self, config):
        self.config = config
        
    def __call__(self, text):
        result = []
        for sentence in parsetree(text):
            entities = self.config(sentence)
            result.extend(entities)
        return result
