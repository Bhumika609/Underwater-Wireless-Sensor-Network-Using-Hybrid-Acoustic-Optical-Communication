import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Channel Models ----------
class AcousticChannel:
    def __init__(self, delay=0.3):
        self.delay = delay

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

class OpticalChannel:
    def __init__(self, delay=0.05):
        self.delay = delay

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

# ---------- Node Model ----------
class Node:
    def __init__(self, env, node_id, hybrid_manager, t_agg=10.0):
        self.env = env
        self.node_id = node_id
        self.hybrid_manager = hybrid_manager
        self.t_agg = t_agg
        self.agg_buffer = []
        env.process(self.generate_low_packets())
        env.process(self.periodic_aggregator())
        env.process(self.generate_high_packets())

    # LOW packets — periodic aggregation
    def generate_low_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(1/1.0))
            self.agg_buffer.append({'priority':'LOW', 'ts': self.env.now})

    def periodic_aggregator(self):
        while True:
            yield self.env.timeout(self.t_agg)
            if self.agg_buffer:
                # Aggregate all buffered LOW packets into one
                packet = {'priority':'LOW', 'ts': self.agg_buffer[0]['ts'], 'size': len(self.agg_buffer)}
                self.agg_buffer = []
                yield self.env.process(self.hybrid_manager.send_packet(self, packet['priority'], packet['ts']))

    # HIGH packets — immediate send
    def generate_high_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(0.05))  # less frequent HIGH events
            yield self.env.process(self.hybrid_manager.send_packet(self, 'HIGH', self.env.now))

# ---------- Hybrid Manager ----------
class HybridManager:
    def __init__(self, env):
        self.env = env
        self.acoustic = AcousticChannel()
        self.optical = OpticalChannel()
        self.log = []

    def send_packet(self, node, priority, timestamp):
        channel = self.optical if priority=='HIGH' else self.acoustic
        yield self.env.process(channel.transmit(self.env, f"{priority}_PACKET"))
        latency = self.env.now - timestamp
        self.log.append({
            'node': node.node_id,
            'priority': priority,
            'send_time': timestamp,
            'recv_time': self.env.now,
            'latency': latency
        })

# ---------- Simulation ----------
def run_sim(num_nodes=5, sim_time=60, t_agg=10.0):
    env = simpy.Environment()
    manager = HybridManager(env)
    nodes = [Node(env, i, manager, t_agg) for i in range(num_nodes)]
    env.run(until=sim_time)
    return manager.log

# ---------- Post-processing ----------
def analyze_and_plot(log, filename_prefix="results/hybrid_agg"):
    df = pd.DataFrame(log)
    df.to_csv(f"{filename_prefix}_log.csv", index=False)
    plt.figure()
    for priority in ['HIGH','LOW']:
        data = df[df.priority==priority]['latency']
        if len(data) > 0:
            x = np.sort(data)
            y = np.arange(1,len(x)+1)/len(x)
            plt.plot(x, y, label=priority)
    plt.xlabel("Latency (s)")
    plt.ylabel("CDF")
    plt.title("Latency CDF (Hybrid with Aggregation)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{filename_prefix}_latency_cdf.png")
    plt.show()

if __name__=="__main__":
    log = run_sim(sim_time=120, t_agg=15.0)
    analyze_and_plot(log)
    print("CSV and CDF plot saved in results/")
