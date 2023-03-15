import simpy
import random
import math

def calculate_distance(position_a, position_b):
    return math.sqrt((position_a[0] - position_b[0])**2 + (position_a[1] - position_b[1])**2)

def path_loss(distance):
    frequency = 5.0  # GHz
    c = 3.0e8  # speed of light in m/s
    wavelength = c / (frequency * 1.0e9)
    tx_power = 20  # dBm
    rx_power = tx_power - 20 * math.log10(4 * math.pi * distance / wavelength)
    return rx_power

def shadowing(sigma):
    return random.gauss(0, sigma)

class Station:
    def __init__(self, env, ap, position):
        self.env = env
        self.ap = ap
        self.position = position
        self.backoff = 0

    def start_transmission(self, packet_size):
        distance = calculate_distance(self.position, self.ap.position)
        power = path_loss(distance) + shadowing(4)
        self.backoff = random.randint(0, 63)
        print ("Backoff and power and distance",self.backoff,power,distance)
        yield self.env.timeout(self.backoff * 9e-6)
        if power > -80:  # threshold for successful transmission
            self.ap.request_transmission(self, packet_size)

class AccessPoint:
    def __init__(self, env, position, data_rate=100):
        self.env = env
        self.data_rate = data_rate
        self.busy = False
        self.station_queue = []
        self.transmission_time = 0
        self.position = position

    def transmit(self, station, packet_size):
        self.busy = True
        self.transmission_time = packet_size / self.data_rate
        yield self.env.timeout(self.transmission_time)
        self.busy = False
        self.transmission_time = 0
        if len(self.station_queue) > 0:
            next_station = self.station_queue.pop(0)
            self.env.process(self.transmit(next_station[0], next_station[1]))

    def request_transmission(self, station, packet_size):
        if self.busy:
            self.station_queue.append((station, packet_size))
        else:
            self.env.process(self.transmit(station, packet_size))

def packet_generator(env, ap, num_stations, mean_packet_size=1000, packet_interval=0.1, x_range=(0, 100), y_range=(0, 100)):
    for i in range(num_stations):
        x = random.uniform(*x_range)
        y = random.uniform(*y_range)
        station = Station(env, ap, (x, y))
        env.process(station.start_transmission(random.expovariate(1 / mean_packet_size)))
        yield env.timeout(packet_interval)
      
"""This function now takes in additional arguments num_stations, x_range, and y_range, which specify the number of STAs to generate and the range of x and y coordinates for their positions. Inside the loop, we generate a random position for each STA using the random.uniform function, and then create a Station instance with that position. Finally, we start a transmission for the station with a random packet size using the start_transmission method, and wait for the next packet interval using yield env.timeout(packet_interval)."""

def simulation(num_stations, sim_time):
    env = simpy.Environment()
    ap = AccessPoint(env, (50, 50))
    env.process(packet_generator(env, ap, num_stations))
    env.run(until=sim_time)

if __name__ == '__main__':
    num_stations = 10
    sim_time = 10
    simulation(num_stations, sim_time)
