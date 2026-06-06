# 🌊 Hybrid Acoustic-Optical Communication for Underwater Wireless Sensor Networks

## Overview

Underwater Wireless Sensor Networks (UWSNs) are widely used in:

- Ocean monitoring
- Environmental sensing
- Military surveillance
- Underwater exploration
- Disaster detection
- Offshore infrastructure monitoring

Traditional underwater communication systems mainly rely on acoustic communication, which suffers from:

- High propagation delay
- Limited bandwidth
- High energy consumption
- Packet collisions

This project introduces a Hybrid Acoustic-Optical Communication Framework that combines acoustic and optical channels with intelligent scheduling and packet management techniques.

---

## Objectives

- Reduce communication latency.
- Improve packet delivery efficiency.
- Prioritize critical underwater events.
- Reduce energy consumption.
- Compare multiple communication strategies.
- Visualize underwater communication behavior.

---

## Key Features

### Acoustic Communication Baseline

Implements traditional underwater acoustic communication for performance comparison.

### Hybrid Acoustic-Optical Communication

Uses:

- Optical Channel → High Priority Packets
- Acoustic Channel → Low Priority Packets

to improve response time.

### TDMA Scheduling

Implements Time Division Multiple Access (TDMA) to:

- Eliminate collisions
- Improve channel utilization
- Ensure fair transmission opportunities

### Packet Aggregation

Combines multiple low-priority packets into larger packets to reduce overhead and save energy.

### Critical Packet Prioritization

Emergency and critical packets bypass normal scheduling and use optical communication immediately.

### Real-Time Visualization

GUI displays:

- Underwater nodes
- Packet transmission animation
- Active TDMA slots
- Buffer status
- Communication links

### Performance Analytics

Measures:

- Latency
- Throughput
- Packet Delivery Ratio (PDR)
- Energy Consumption
- Channel Utilization

---

## System Architecture

Sensor Nodes
      |
      V
Packet Generation
      |
      +---- HIGH Priority Data
      |           |
      |           V
      |     Optical Channel
      |
      +---- LOW Priority Data
                  |
                  V
           Acoustic Channel
                  |
                  V
           TDMA Scheduler
                  |
                  V
          Packet Aggregator
                  |
                  V
             Relay Node
                  |
                  V
             Sink Node

---

## Technologies Used

### Programming Language

- Python

### Simulation Framework

- SimPy

### Visualization

- Matplotlib

### GUI

- Tkinter

### Numerical Analysis

- NumPy

### Data Processing

- Pandas

---

## Communication Models

### Acoustic Channel

Characteristics:

- Long communication range
- Higher latency
- Greater energy consumption

### Optical Channel

Characteristics:

- Low latency
- High bandwidth
- Short communication range

### Hybrid Communication

Combines the strengths of both communication methods.

---

## Scheduling Mechanisms

### TDMA Scheduling

Time slots are allocated to sensor nodes to avoid packet collisions.

Benefits:

- Predictable communication
- Reduced retransmissions
- Better reliability

### Packet Aggregation

Multiple low-priority packets are grouped into a single transmission.

Benefits:

- Lower overhead
- Reduced energy consumption
- Better bandwidth utilization

---

## Performance Metrics

### Latency

Measures end-to-end transmission delay.

### Throughput

Measures successful packet transmission rate.

### Packet Delivery Ratio (PDR)

PDR = Successfully Delivered Packets / Total Packets Sent

### Energy Consumption

Tracks communication energy requirements across different protocols.

---

## Project Structure

```text
├── acoustic_baseline.py
├── channel.py
├── hybrid_network.py
├── hybrid_network_plot.py
├── hybrid_network_aggregation.py
├── hybrid_network_tdma.py
├── hybrid_network_tdma_critical.py
├── node.py
├── tdma_scheduler.py
├── underwater_gui.py
├── results/
└── README.md
```

---

## Running the Project

### Install Dependencies

```bash
pip install simpy numpy pandas matplotlib
```

### Run Acoustic Baseline

```bash
python acoustic_baseline.py
```

### Run Hybrid Network

```bash
python hybrid_network.py
```

### Run TDMA Version

```bash
python hybrid_network_tdma.py
```

### Run Aggregation Version

```bash
python hybrid_network_aggregation.py
```

### Run Critical Packet Version

```bash
python hybrid_network_tdma_critical.py
```

### Launch GUI

```bash
python underwater_gui.py
```

---

## GUI Features

### Network Visualization

- Underwater nodes
- Sink node
- Packet movement

### Live Statistics

- Packet count
- Average latency
- Energy consumption
- PDR
- Throughput

### Performance Graphs

- Latency Comparison
- Energy Consumption
- Throughput Analysis
- Packet Delivery Ratio

### Burst Monitoring

Displays packet aggregation bursts and transmission statistics.

---

## Applications

### Ocean Monitoring

Environmental data collection from underwater sensors.

### Military Surveillance

Secure underwater communication systems.

### Offshore Oil and Gas

Pipeline and infrastructure monitoring.

### Marine Research

Real-time underwater data acquisition.

### Disaster Warning Systems

Tsunami and earthquake monitoring.

### Underwater IoT

Smart underwater sensing and communication.

---

## Results

The proposed hybrid framework demonstrates:

✔ Lower latency for critical packets

✔ Better throughput compared to acoustic-only systems

✔ Improved energy efficiency

✔ Reduced packet collisions

✔ Enhanced reliability using TDMA scheduling

✔ Better bandwidth utilization through packet aggregation

---

## Future Enhancements

- AI-Based Routing
- Reinforcement Learning Scheduling
- Underwater Drone Communication
- Real-Time Hardware Integration
- 3D Underwater Mobility Models
- Multi-Hop Routing Protocols

---

## Authors

Developed as an Underwater Wireless Sensor Network (UWSN) research project focusing on hybrid communication, scheduling, and performance optimization.

---

## License

MIT License
