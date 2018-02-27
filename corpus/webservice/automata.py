#!/usr/bin/env python3

import random
import uuid
import re
import traceback
import json
from pymongo import MongoClient

import transitions
from transitions.extensions import GraphMachine as Machine
from transitions import State

from mongodb_client import Mongo

class Policy(object):
    def __init__(self, config):
        self.id = str(uuid.uuid4())
        self.slots = []
        self.instructions = config['instructions']
        self.false_instructions = config['false_instructions']

        self.current_instruction = None

class StateCard(transitions.State):
    def __init__(self, config):
        name = config['name']
        on_enter = config.get('on_enter')
        on_exit = config.get('on_exit')
        ignore_invalid_triggers = config.get('ignore_invalid_triggers', False)
        interpreters = config.get('interpreters', ['regex'])
        portal_dest = config.get('portal_dest', None)
        super().__init__(name, on_enter, on_exit, ignore_invalid_triggers)
        self.id = str(uuid.uuid4())
        self.max_out_num = 2
        self.interpreters = interpreters
        self.portal_dest = portal_dest
        self._inputs = set()
        self.instruction = config.get('instruction', '@apiapi_call_base')
        self.false_instruction = config.get('instruction', '@apiapi_call_base')
        if config.get("counted", "False") == "True":
            self.counter = 0
        else:
            self.counter = None

    def append_input(self, input_):
        self._inputs.add(input_)

class Automata(Machine):
    def __init__(self, config):
        self.config = config
        self.id = str(uuid.uuid4())
        self.scene_id = config.get('scene_id', 'base')
        self.name = config['name']
        self._load_states(config)
        self.transitions = config['transitions']
        self.policy = Policy(config)
        Machine.__init__(self, model=self.policy, states=self.states,
                         transitions=self.transitions,
                         initial=self.init_state,
                         after_state_change=['instruct'])
        self._load_state_inputs()

    def _load_states(self, config):
        self.states = []
        self.state_mapper = {}
        self.instructions = {}
        self.false_instructions = {}
        for state_json in config['states']:
            state = StateCard(state_json)
            self.states.append(state)
            self.state_mapper[state.name] = state
            self.instructions[state.name] = state.instruction
            self.false_instructions[state.name] = state.false_instruction
        self.init_state = self.state_mapper[config['init_state']]
        config["instructions"] = self.instructions\
            if "instructions" not in config else config["instructions"]
        config["false_instructions"] = self.false_instructions\
            if "false_instructions" not in config else config["false_instructions"]

    def _load_state_inputs(self):
        for transition in self.transitions:
            trigger_input = transition['trigger']
            state = self.state_mapper[transition['source']]
            state.append_input(trigger_input)

    def show_graph(self):
        self.get_graph().draw(self.config['scene_id']+'.png', prog='dot')


class Mongo_automata():
    def __init__(self, ip='127.0.0.1'):
        self.db_name = 'automata'
        self.db = MongoClient(ip, 27017)[self.db_name]
        self.collection = self.db['machines']

    def load_graph_config(self, scene_id):
        try:
            result = self.collection.find_one({'scene_id':scene_id})
            return result
        except:
            traceback.print_exc()
            return None

    def insert_graph_config(self, data):
        try:
            if self.collection.find_one({'scene_id':data['scene_id']}):
                return 0
            self.collection.insert(data)
            return 1
        except:
            traceback.print_exc()
            return 0

    def update_graph_config(self, data):
        try:
            self.collection.update_one({'scene_id':data['scene_id']},
                    {'$set':data})
            return 1
        except:
            traceback.print_exc()
            return 0

    def delete_graph_config(self, scene):
        try:
            self.collection.delete_many({'scene_id':scene})
            return 1
        except:
            traceback.print_exc()
            return 0

def show_graph(scene_id):
    try:
        mongo = Mongo_automata('127.0.0.1')
        config = mongo.load_graph_config(scene_id=scene_id)
        if not config:
            return 0
        machine = Automata(config)
        machine.show_graph()
        return 1
    except:
        traceback.print_exc()
        return -1


if __name__ == '__main__':
    show_graph('bookstore')
