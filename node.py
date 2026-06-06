import simpy
import random
import time
from src.channel import propagation_delay, transmit_success

ACOUSTIC_RATE = 20000.0  # bps

class Node:
    def __init__(self, env, node_id, pos, relay, log):
        self.env = env
        self.id = node_id
        self.pos = pos
        self.relay = relay
        self.log = log
        self.agg_buffer = []
        self.next_agg_time = 0.0
        # start processes
        env.process(self.generate_high_events())
        env.process(self.periodic_aggregator())

    def generate_high_events(self):
        while True:
            # interarrival exponentially distributed
            ia = random.expovariate(0.01)  # HIGH_EVENT_RATE default
            yield self.env.timeout(ia)
            pkt = {'id': f"H-{self.id}-{self.env.now}", 'size': 64, 'priority': 'HIGH', 'ts': self.env.now}
            # immediate send: schedule for next available slot via relay
            yield self.env.process(self.relay.request_transmit(self, pkt))

    def periodic_aggregator(self):
        while True:
            yield self.env.timeout(30.0)  # T_AGG
            # create aggregated packet
            pkt = {'id': f"L-{self.id}-{self.env.now}", 'size': 1024, 'priority': 'LOW', 'ts': self.env.now}
            yield self.env.process(self.relay.request_transmit(self, pkt))
