import json
import copy
from rdflib import Graph, plugin
from rdflib.serializer import Serializer


class Util():
    nquards = []
    objs = {}

    def __init__(self):
        self.nquards = []
        self.objs = {}

    # convert class to nquard
    # data format:
    # [
    #     {
    #         'data':{},
    #         'subject':'',
    #         'label':'',
    #         'isBlankNode':""
    #     }
    # ]
    @staticmethod
    def objects2Nquard(data):
        del Util.nquards[:]
        Util.objs.clear()
        if isinstance(data, list) == False:
            return 'Input should be a valid JSON array.'
        if Util.validataParams(data) == False:
            return 'Input should be a valid JSON array.'
        # nquards = []
        for e in data:
            jsonData = e['data']
            Util.getNquards(jsonData, e['subject'], e['label'], e['isBlankNode'])
        return Util.nquards

    # validate input params
    @staticmethod
    def validataParams(data):
        for e in data:
            if len(e) != 4:
                return False
            for v in e:
                if v not in ['data', 'subject', 'label', 'isBlankNode']:
                    return False
        return True
        # pass

    # get nquard
    @staticmethod
    def getNquards(jsonData, subject, label, isBlankNode):
        Util.objs = copy.deepcopy(jsonData)
        Util.convertNquards(jsonData, subject, label, isBlankNode)
        # self.convertNquards(self.objs, subject, label, isBlankNode)
        return Util.nquards

    @staticmethod
    def getNquard(subject, predicat, object, label, isBlankNode):
        if not isinstance(subject, str):
            subject = subject.encode('utf-8')
        if not isinstance(predicat, str):
            predicat = predicat.encode('utf-8')
        if not isinstance(object, str):
            object = object.encode('utf-8')
        if label is not None:
            if not isinstance(label, str):
                label = label.encode('utf-8')
        if isBlankNode is not None:
            if not isinstance(isBlankNode, str):
                isBlankNode = isBlankNode.encode('utf-8')

        nquard = {
            'subject': "\"" + subject + "\"",
            'predicate': "\"" + predicat + "\"",
            'object': "\"" + object + "\""
        }
        if isBlankNode is not None:
            nquard['subject'] = "\"" + isBlankNode + "\""
        if label is not None:
            nquard['label'] = "\"" + label + "\""
        return nquard

    @staticmethod
    def convertNquards(jsonData, subject, label, isBlankNode):
        for key in jsonData:
            predicate = ('<' + key + '>').replace('<<', '<').replace('>>', '>')
            if isinstance(jsonData[key], dict):
                obj = None
                if isBlankNode is None:
                    obj = '_:BN@' + subject + '.' + predicate
                else:
                    obj = isBlankNode + '.' + predicate
                Util.nquards.append(Util.getNquard(subject, predicate, obj, label, isBlankNode))
                if len(jsonData[key]) > 1:
                    result = jsonData[key]
                    Util.objs.clear()
                    isBlankNode = obj
                    for e in result:
                        if not isinstance(result[e], dict):
                            predicate = ('<' + e + '>').replace('<<', '<').replace('>>', '>')
                            Util.nquards.append(Util.getNquard(subject, predicate, result[e], label, isBlankNode))
                        else:
                            Util.objs[e] = result[e]
                    Util.convertNquards(copy.deepcopy(Util.objs), subject, label, isBlankNode)
                else:
                    Util.convertNquards(jsonData[key], subject, label, isBlankNode)
            else:
                Util.nquards.append(Util.getNquard(subject, predicate, jsonData[key], label, isBlankNode))

    @staticmethod
    def convert_nquard_to_jsonld(data):
        g = Graph().parse(data=data, format='n3')
        print(g.serialize(format='json-ld', indent=4))
