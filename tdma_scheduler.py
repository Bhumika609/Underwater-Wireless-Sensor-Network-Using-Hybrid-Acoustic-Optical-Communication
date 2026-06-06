import simpy
from src.channel import propagation_delay, transmit_success, C_SOUND
ACOUSTIC_RATE = 20000.0
FRAME_DURATION = 10.0
SLOT_COUNT = 10

class Relay:
    def __init__(self, env, pos, nodes, log):
        self.env = env
        self.pos = pos
        self.nodes = nodes  # list of Node objects
        self.log = log
        # simple fixed assignment: each node gets one slot per frame in round-robin
        self.slot_map = {}
        for i, node in enumerate(nodes):
            self.slot_map[node.id] = i % SLOT_COUNT
        env.process(self.beacon_frames())

    def beacon_frames(self):
        while True:
            # emit beacon (we don't model transmission time of beacon in detail)
            # in a real sim you'd notify nodes; here nodes call request_transmit and we schedule.
            yield self.env.timeout(FRAME_DURATION)

    def request_transmit(self, node, pkt):
        # schedule the transmission at the node's next assigned slot
        slot_index = self.slot_map[node.id]
        # compute start_time of next frame's slot
        # figure current frame start
        now = self.env.now
        frame_no = int(now // FRAME_DURATION)
        frame_start = frame_no * FRAME_DURATION
        slot_duration = FRAME_DURATION / SLOT_COUNT
        slot_start = frame_start + slot_index * slot_duration
        if slot_start <= now:
            # schedule in next frame
            slot_start += FRAME_DURATION
        # wait until slot_start
        yield self.env.timeout(slot_start - now)
        # perform transmit
        prop_delay, dist = propagation_delay(node.pos, self.pos)
        tx_time = (pkt['size'] * 8) / ACOUSTIC_RATE
        # log send time
        self.log.append({'pkt_id': pkt['id'], 'node': node.id, 'send_time': self.env.now, 'size': pkt['size'], 'priority': pkt['priority']})
        # simulate transmission and propagation
        yield self.env.timeout(tx_time + prop_delay)
        success = transmit_success(dist)
        recv_time = self.env.now
        self.log[-1].update({'recv_time': recv_time if success else None, 'success': success, 'distance': dist})
        return success
