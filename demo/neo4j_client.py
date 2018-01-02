#!/usr/bin/env python3
import os, sys
from py2neo import Graph, Node, Relationship
from py2neo import order, size, walk
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom

graph = Graph('http://localhost:7474', user='neo4j', password='ecovacs01!')

'''
a = Node('Person', name='A_Jack', age=20)
a.setdefault('location', '北京')
b = Node('Person', name='B_Tom', age=22)
c = Node('Person', name='C_Mary', age=22)
ab = Relationship(a, 'KNOWS', b)
ab['time'] = '2017/12/12'
ac = Relationship(a, 'KNOWS', c)
s = a | b | ab | ac
#print(s)
#print(s.nodes())
#print(s.relationships())
#print(s.keys())
#print(order(s), size(s))
ca = Relationship(c, 'KNOWS', a)
w = ab + Relationship(b, 'LIKES', c) + ca +ac
for x in walk(w):
    pass#print('@@@', x)

graph.create(s)
node = graph.find_one(label='Person', property_key='name', property_value='A_Jack')
print('node', node)
relations = graph.match(start_node=node)
for r in relations:
    print(r)

#graph.delete_all()
'''

class Movie(GraphObject):
    __primarykey__ = 'title'

    title = Property()
    released = Property()
    actors = RelatedFrom('Person', 'ACTED_IN')
    directors = RelatedFrom('Person', 'DIRECTED')
    producers = RelatedFrom('Person', 'PRODUCED')

class Person(GraphObject):
    __primarykey__ = 'name'

    name = Property()
    age = Property()
    location = Property()
    acted_in = RelatedTo('Movie')
    directed = RelatedTo('Movie')
    produced = RelatedTo('Movie')
    likes = RelatedTo('Person')

if __name__ == '__main__':
    print('ok')
    jack = Person().select(graph, 'A_Jack').first()
    print(jack.name, jack.age, jack.location)
