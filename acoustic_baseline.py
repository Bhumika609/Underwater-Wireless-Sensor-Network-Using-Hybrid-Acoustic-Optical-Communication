import simpy
import random
import csv
from src.node import Node
from src.tdma_scheduler import Relay
import matplotlib.pyplot as plt
import numpy as np

def run_sim(seed=1, sim_time=600.0):
    random.seed(seed)
    env = simpy.Environment()
    log = []
    # create simple topology: 5 nodes around relay
    relay_pos = (0.0, 0.0)
    nodes = []
    for i in range(5):
        angle = 2 * np.pi * i / 5
        r = 200 + i*50
        pos = (r * np.cos(angle), r * np.sin(angle))
        # Node will be created after Relay is created, so use placeholder
        nodes.append(pos)
    # create dummy node objects then set relay
    node_objs = []
    for i,pos in enumerate(nodes):
        node_objs.append(None)
    # create relay
    # we will create node objects now with relay placeholder
    # create Relay with node placeholders (we'll replace with actual nodes after)
    relay = Relay(env, relay_pos, [], log)
    node_objs = [Node(env, i, nodes[i], relay, log) for i in range(len(nodes))]
    # replace relay.nodes
    relay.nodes = node_objs
    # update relay slot_map to use node ids
    relay.slot_map = {}
    for i,node in enumerate(node_objs):
        relay.slot_map[node.id] = i % relay.SLOT_COUNT if hasattr(relay, 'SLOT_COUNT') else i % 10
    # run
    env.run(until=sim_time)
    # write log
    with open('results/log.csv','w',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['pkt_id','node','send_time','recv_time','success','distance','size','priority'])
        writer.writeheader()
        for r in log:
            writer.writerow(r)
    # analyse HIGH packet latencies
    latencies = [r['recv_time'] - r['send_time'] for r in log if r.get('success') and r.get('priority')=='HIGH']
    if latencies:
        latencies = np.array(latencies)
        print("HIGH mean latency:", latencies.mean(), "95th:", np.percentile(latencies,95))
        # plot CDF
        x = np.sort(latencies)
        y = np.arange(1, len(x)+1) / len(x)
        plt.plot(x,y)
        plt.xlabel("One-way latency (s)")
        plt.ylabel("CDF")
        plt.title("HIGH packet latency CDF (acoustic baseline)")
        plt.grid(True)
        plt.savefig('results/high_latency_cdf.png')
    else:
        print("No successful HIGH packets recorded.")

if __name__ == '__main__':
    run_sim()
