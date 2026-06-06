import simpy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Channels ----------
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

# ---------- TDMA Acoustic Channel ----------
class TDMAChannel:
    def __init__(self, env, frame_duration=10.0, slot_count=10, high_slots=2):
        self.env = env
        self.frame_duration = frame_duration
        self.slot_count = slot_count
        self.high_slots = high_slots
        self.low_slots = slot_count - high_slots
        self.queue = []  # (priority, timestamp, node, critical)

    def request_slot(self, priority, timestamp, node, critical=False):
        self.queue.append((priority, timestamp, node, critical))
        yield self.env.timeout(0)

    def transmit_frame(self):
        while True:
            yield self.env.timeout(self.frame_duration)

            # Separate HIGH and LOW packets
            high_packets = [p for p in self.queue if p[0]=='HIGH'][:self.high_slots]
            low_packets = [p for p in self.queue if p[0]=='LOW'][:self.low_slots]

            # Transmit HIGH packets first
            for p in high_packets:
                priority, ts, node, critical = p
                latency = self.env.now - ts
                node.log_packet(priority, ts, latency, critical)
                self.queue.remove(p)

            # Transmit LOW packets
            for p in low_packets:
                priority, ts, node, critical = p
                latency = self.env.now - ts
                node.log_packet(priority, ts, latency, critical)
                self.queue.remove(p)

# ---------- Node ----------
class Node:
    def __init__(self, env, node_id, tdma, optical, t_agg=10.0):
        self.env = env
        self.node_id = node_id
        self.tdma = tdma
        self.optical = optical
        self.t_agg = t_agg
        self.agg_buffer = []
        self.packet_log = []

        env.process(self.generate_low_packets())
        env.process(self.periodic_aggregator())
        env.process(self.generate_high_packets())

    def log_packet(self, priority, send_time, latency, critical=False):
        self.packet_log.append({
            'node': self.node_id,
            'priority': priority,
            'critical': critical,
            'send_time': send_time,
            'recv_time': send_time + latency,
            'latency': latency
        })

    # LOW packets: aggregated
    def generate_low_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(1/1.0))
            self.agg_buffer.append({'ts': self.env.now, 'critical': False})

    def periodic_aggregator(self):
        while True:
            yield self.env.timeout(self.t_agg)
            if self.agg_buffer:
                ts = self.agg_buffer[0]['ts']
                self.agg_buffer = []
                self.env.process(self.tdma.request_slot('LOW', ts, self, critical=False))

    # HIGH packets: mark critical randomly
    def generate_high_packets(self):
        while True:
            yield self.env.timeout(random.expovariate(0.05))
            is_critical = random.random() < 0.4  # 40% chance
            ts = self.env.now
            if is_critical:
                # Critical → use optical immediately
                self.env.process(self.optical.transmit(self.env, f"CRITICAL_HIGH_NODE{self.node_id}"))
                latency = self.env.now - ts + self.optical.delay
                self.log_packet('HIGH', ts, latency, critical=True)
            else:
                # Non-critical → send via TDMA
                self.env.process(self.tdma.request_slot('HIGH', ts, self, critical=False))

# ---------- Simulation ----------
def run_tdma_critical_sim(num_nodes=5, sim_time=120, t_agg=15.0):
    env = simpy.Environment()
    optical = OpticalChannel()
    tdma = TDMAChannel(env)
    nodes = [Node(env, i, tdma, optical, t_agg) for i in range(num_nodes)]
    env.process(tdma.transmit_frame())
    env.run(until=sim_time)

    # Collect all logs
    log = []
    for n in nodes:
        log.extend(n.packet_log)
    return log

# ---------- Post-processing ----------
def analyze_and_plot(log, filename_prefix="results/hybrid_tdma_critical"):
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
    plt.title("Latency CDF (TDMA + Critical Packets)")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{filename_prefix}_latency_cdf.png")
    plt.show()

if __name__=="__main__":
    log = run_tdma_critical_sim(sim_time=120, t_agg=15.0)
    analyze_and_plot(log)
    print("CSV and CDF plot saved in results/")
