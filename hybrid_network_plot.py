import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Channel Models ----------
class AcousticChannel:
    def __init__(self, delay=0.3):
        self.delay = delay  # seconds

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

class OpticalChannel:
    def __init__(self, delay=0.05):
        self.delay = delay

    def transmit(self, env, packet):
        yield env.timeout(self.delay)

# ---------- Node Model ----------
class Node:
    def __init__(self, env, node_id, hybrid_manager):
        self.env = env
        self.node_id = node_id
        self.hybrid_manager = hybrid_manager

    def generate_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(1/1.0))  # mean 1s
            priority = random.choice(["HIGH", "LOW"])
            timestamp = self.env.now
            self.env.process(self.hybrid_manager.send_packet(self, priority, timestamp))

# ---------- Hybrid Manager ----------
class HybridManager:
    def __init__(self, env):
        self.env = env
        self.acoustic = AcousticChannel()
        self.optical = OpticalChannel()
        self.log = []  # store all packets

    def send_packet(self, node, priority, timestamp):
        channel = self.optical if priority=="HIGH" else self.acoustic
        yield self.env.process(channel.transmit(self.env, f"{priority}_PACKET"))
        latency = self.env.now - timestamp
        self.log.append({
            "node": node.node_id,
            "priority": priority,
            "send_time": timestamp,
            "recv_time": self.env.now,
            "latency": latency
        })

# ---------- Simulation ----------
def run_sim(num_nodes=5, sim_time=30):
    env = simpy.Environment()
    hybrid_manager = HybridManager(env)
    nodes = [Node(env, i, hybrid_manager) for i in range(num_nodes)]
    for n in nodes:
        env.process(n.generate_packets())
    env.run(until=sim_time)
    return hybrid_manager.log

# ---------- Post-processing ----------
def analyze_and_plot(log, filename_prefix="results/hybrid"):
    df = pd.DataFrame(log)
    # Save CSV
    df.to_csv(f"{filename_prefix}_log.csv", index=False)
    # CDF plot
    plt.figure()
    for priority in ["HIGH", "LOW"]:
        data = df[df.priority==priority]["latency"]
        if len(data) > 0:
            x = np.sort(data)
            y = np.arange(1, len(x)+1)/len(x)
            plt.plot(x, y, label=f"{priority}")
    plt.xlabel("Latency (s)")
    plt.ylabel("CDF")
    plt.title("Latency CDF (Hybrid Network)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{filename_prefix}_latency_cdf.png")
    plt.show()

if __name__ == "__main__":
    log = run_sim(sim_time=60)
    analyze_and_plot(log)
    print("CSV and CDF plot saved in results/")
