import simpy
import random
import numpy as np

# ---------- Channel Models ----------
class AcousticChannel:
    def __init__(self, delay=0.3, range=2000):
        self.delay = delay
        self.range = range  # meters

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

class OpticalChannel:
    def __init__(self, delay=0.05, range=200):
        self.delay = delay
        self.range = range  # meters

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

# ---------- Node Model ----------
class Node:
    def __init__(self, env, node_id, hybrid_manager):
        self.env = env
        self.node_id = node_id
        self.hybrid_manager = hybrid_manager
        self.sent_packets = 0
        self.received_packets = 0
        self.latencies = []

    def generate_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(1/1.0))  # mean 1 sec interval
            priority = random.choice(["HIGH", "LOW"])
            timestamp = self.env.now
            self.env.process(self.hybrid_manager.send_packet(self, priority, timestamp))

# ---------- Hybrid Communication Manager ----------
class HybridManager:
    def __init__(self, env):
        self.env = env
        self.acoustic = AcousticChannel()
        self.optical = OpticalChannel()
        self.latency_data = {"HIGH": [], "LOW": []}

    def send_packet(self, node, priority, timestamp):
        # choose channel
        if priority == "HIGH":
            channel = self.optical
        else:
            channel = self.acoustic

        yield self.env.process(channel.transmit(self.env, f"{priority}_PACKET"))
        latency = self.env.now - timestamp
        self.latency_data[priority].append(latency)

# ---------- Simulation Setup ----------
def run_hybrid_simulation(num_nodes=5, sim_time=30):
    env = simpy.Environment()
    hybrid_manager = HybridManager(env)
    nodes = [Node(env, i, hybrid_manager) for i in range(num_nodes)]

    for n in nodes:
        env.process(n.generate_packets())

    env.run(until=sim_time)

    # Calculate statistics
    results = {}
    for ptype in ["HIGH", "LOW"]:
        data = hybrid_manager.latency_data[ptype]
        if len(data) > 0:
            results[ptype] = {
                "mean": np.mean(data),
                "95th": np.percentile(data, 95),
                "count": len(data)
            }
    return results

if __name__ == "__main__":
    results = run_hybrid_simulation()
    for ptype, stats in results.items():
        print(f"{ptype} mean latency: {stats['mean']:.3f}s | 95th: {stats['95th']:.3f}s | count: {stats['count']}")
