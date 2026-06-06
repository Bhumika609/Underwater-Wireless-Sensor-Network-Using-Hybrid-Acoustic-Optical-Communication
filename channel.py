import math
import random

C_SOUND = 1500.0
MAX_RANGE = 2000.0

def propagation_delay(p1, p2):
    dx = p1[0] - p2[0]; dy = p1[1] - p2[1]
    d = math.hypot(dx, dy)
    return d / C_SOUND, d

def packet_error_rate(distance):
    # simple quadratic PER model; tune as needed
    per = (distance / MAX_RANGE) ** 2
    if per > 0.5:
        per = 0.5
    return per

def transmit_success(distance):
    per = packet_error_rate(distance)
    return random.random() > per
