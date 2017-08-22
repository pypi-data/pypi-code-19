import abc
from pattern.es import parsetree
from pattern.search import Pattern


class AbstractEntity(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __call__(self, sentence, default=None):
        """Si no reconoce ninguna entidad devuelve None. Si reconoce al menos
        una entidad devuelve una lista con las entidades"""
        return None
    
    def __add__(self, other):
        if not isinstance(other, AbstractEntity):
            raise TypeError("Cannot add an entity with a non entity.")
        return EntityAnd(self, other)
    
    def __mul__(self, other):
        if not isinstance(other, AbstractEntity):
            raise TypeError("Cannot mult an entity with a non entity.")
        return EntityOr(self, other)


class EntityPattern(AbstractEntity):
    def __init__(self, entity_type, expression, variables=None, negation=False, taxonomy=None, strict=False, exclude=None):
        self.entity_type = entity_type
        self.expression = expression
        if variables is None:
            variables = {}
        self.variables = variables
        if negation is None:
            negation = False
        self.negation = negation
        self.taxonomy = taxonomy
        self.strict = strict
        self.exclude = set() if exclude is None else set(exclude)
        self.pattern = Pattern.fromstring(expression, taxonomy=taxonomy, strict=strict)

    def allow_word(self, word):
        if self.taxonomy is None:
            return True;
        if set(self.taxonomy.parents(word)).intersection(self.exclude):
            return False
        return True
        
    def __call__(self, sentence, default=None):
        match = self.pattern.match(sentence)
        if match is None:
            return None
        result = {}
        if self.variables:
            for key, index in self.variables.items():
                if isinstance(index, basestring) or index is None:
                    result[key] = index
                    continue
                group = match.group(index);
                position = group[0].index
                group = [group.string for group in match.group(index) if self.allow_word(group.string)]
                if not group:
                    return None
                result[key] = ' '.join(group)
                result['position'] = position
        result['negation'] = self.negation
        result['entity_type'] = self.entity_type if self.entity_type else default
        return [result]


class EntityOr(AbstractEntity):
    def __init__(self, left, right):
        if not isinstance(left, AbstractEntity):
            raise TypeError("The parameter 'left' must inherits from AbstractEntity.")
        if not isinstance(right, AbstractEntity):
            raise TypeError("The parameter 'right' must inherits from AbstractEntity.")
        self.left = left
        self.right = right
        
    def __call__(self, sentence, default=None):
        left_result = self.left(sentence, default)
        if left_result:
            return left_result
        return self.right(sentence, default)


class EntityAnd(AbstractEntity):
    def __init__(self, left, right):
        if not isinstance(left, AbstractEntity):
            raise TypeError("The parameter 'left' must inherits from AbstractEntity.")
        if not isinstance(right, AbstractEntity):
            raise TypeError("The parameter 'right' must inherits from AbstractEntity.")
        self.left = left
        self.right = right
        
    def __call__(self, sentence, default=None):
        result = []
        left_result = self.left(sentence, default)
        if left_result:
            result.extend(left_result)
        right_result = self.right(sentence, default)
        if right_result:
            result.extend(right_result)
        if not result:
            return None
        return result


class EntityFirst(AbstractEntity):
    def __init__(self, *entities):
        if not entities:
            raise TypeError("You must provide at least one entity to EntityFirst.")
        for entity in entities:
            if not isinstance(entity, AbstractEntity):
                raise TypeError("All entities provided to EntityFirst must inherits from AbstractEntity.")
        self.entities = entities

    def __call__(self, sentence, default=None):
        for entity in self.entities:
            entity_result = entity(sentence, default)
            if entity_result:
                return [entity_result[0]]
        return None


class EntityConcat(AbstractEntity):
    def __init__(self, *entities):
        if not entities:
            raise TypeError("You must provide at least one entity to EntityConcat.")
        for entity in entities:
            if not isinstance(entity, AbstractEntity):
                raise TypeError("All entities provided to EntityConcat must inherits from AbstractEntity.")
        self.entities = entities

    def __call__(self, sentence, default=None):
        result = []
        for entity in self.entities:
            entity_result = entity(sentence, default)
            if entity_result:
                result.extend(entity_result)
        if not result:
            return None
        return result



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
        print self.config, self.pattern.string
        if self.config:
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


class EntityNegation(object):
    def __init__(self, expression, type, taxonomy=None):
        self.expression = expression
        self.type = type
        self.taxonomy = taxonomy
        self.pattern = Pattern.fromstring(expression, taxonomy=taxonomy)
        
    def __call__(self, sentence):
        match = self.pattern.match(sentence)
        if match is None:
            return None
        return dict(type=self.type, negation=True)


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
        result.sort(key=lambda x: x['position'] if x and isinstance(x, dict) and 'position' in x else None)
        return result


class EntitiesExtractor(object):
    def __init__(self, entity):
        self.entity = entity
        
    def __call__(self, text, default=None):
        result = []
        for sentence in parsetree(text):
            result.extend(self.entity(sentence))
        result = [item for item in result if item]
        if not result:
            return None
        return result
