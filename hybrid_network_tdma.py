import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Acoustic TDMA Channel ----------
class TDMAChannel:
    def __init__(self, env, frame_duration=10.0, slot_count=10, high_slots=2):
        self.env = env
        self.frame_duration = frame_duration
        self.slot_count = slot_count
        self.high_slots = high_slots
        self.low_slots = slot_count - high_slots
        self.frame_start = 0
        self.queue = []  # (priority, timestamp, node)

    def request_slot(self, priority, timestamp, node):
        self.queue.append((priority, timestamp, node))
        yield self.env.timeout(0)  # continue simulation immediately

    def transmit_frame(self):
        while True:
            yield self.env.timeout(self.frame_duration)
            # Get HIGH and LOW packets
            high_packets = [p for p in self.queue if p[0]=='HIGH'][:self.high_slots]
            low_packets = [p for p in self.queue if p[0]=='LOW'][:self.low_slots]

            # Transmit HIGH packets
            for p in high_packets:
                priority, ts, node = p
                latency = self.env.now - ts
                node.log_packet(priority, ts, latency)
                self.queue.remove(p)

            # Transmit LOW packets
            for p in low_packets:
                priority, ts, node = p
                latency = self.env.now - ts
                node.log_packet(priority, ts, latency)
                self.queue.remove(p)

# ---------- Node ----------
class Node:
    def __init__(self, env, node_id, tdma, t_agg=10.0):
        self.env = env
        self.node_id = node_id
        self.tdma = tdma
        self.t_agg = t_agg
        self.agg_buffer = []
        self.packet_log = []
        env.process(self.generate_low_packets())
        env.process(self.periodic_aggregator())
        env.process(self.generate_high_packets())

    def log_packet(self, priority, send_time, latency):
        self.packet_log.append({
            'node': self.node_id,
            'priority': priority,
            'send_time': send_time,
            'recv_time': send_time + latency,
            'latency': latency
        })

    # LOW packets: aggregated
    def generate_low_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(1/1.0))
            self.agg_buffer.append(self.env.now)

    def periodic_aggregator(self):
        while True:
            yield self.env.timeout(self.t_agg)
            if self.agg_buffer:
                ts = self.agg_buffer[0]
                self.agg_buffer = []
                self.env.process(self.tdma.request_slot('LOW', ts, self))

    # HIGH packets: immediate
    def generate_high_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(0.05))
            self.env.process(self.tdma.request_slot('HIGH', self.env.now, self))

# ---------- Simulation ----------
def run_tdma_sim(num_nodes=5, sim_time=60, t_agg=15.0):
    env = simpy.Environment()
    tdma = TDMAChannel(env)
    nodes = [Node(env, i, tdma, t_agg) for i in range(num_nodes)]
    env.process(tdma.transmit_frame())
    env.run(until=sim_time)

    # Collect all logs
    log = []
    for n in nodes:
        log.extend(n.packet_log)
    return log

# ---------- Post-processing ----------
def analyze_and_plot(log, filename_prefix="results/hybrid_tdma"):
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
    plt.title("Latency CDF (TDMA Priority)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{filename_prefix}_latency_cdf.png")
    plt.show()

if __name__=="__main__":
    log = run_tdma_sim(sim_time=120, t_agg=15.0)
    analyze_and_plot(log)
    print("CSV and CDF plot saved in results/")
