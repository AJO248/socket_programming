#!/usr/bin/env python3
"""
Linear topology for Mininet with Ryu controller:
  s1 -- s2
  h1 connected to s1
  h2 connected to s2

This script starts Mininet and assumes a Ryu controller running the provided
`ryu_shortest.py` app. It prints interfaces, assigns IPs, runs ping and iperf tests,
and demonstrates link failure.

Usage:
  1) Start Ryu controller: ryu-manager ryu_shortest.py
  2) Run this script with sudo: sudo python3 linear_topo.py
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import time


def run_linear():
    setLogLevel('info')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)
    c0 = net.addController('c0')

    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')

    net.addLink(s1, s2, bw=10000)
    net.addLink(s1, h1, bw=1000)
    net.addLink(s2, h2, bw=1000)

    net.start()

    print('\nInterface details:')
    print(h1.cmd('ifconfig -a'))
    print(s1.cmd('ifconfig -a'))

    # Assign IPs
    h1.setIP('10.0.0.1/24')
    h2.setIP('10.0.0.2/24')
    print('\nAssigned IPs:')
    print(h1.cmd('ip addr show'))
    print(h2.cmd('ip addr show'))

    # Ping
    print('\nPing test h1 -> h2:')
    print(h1.cmd('ping -c 4 10.0.0.2'))

    # TCP throughput test
    print('\nStarting iperf server on h2...')
    h2.cmd('iperf -s -p 5001 &')
    time.sleep(1)
    print('Running iperf TCP from h1 to h2 (10s)...')
    print(h1.cmd('iperf -c 10.0.0.2 -t 10 -p 5001'))

    # Simulate link failure between s1 and s2
    print('\nBringing down link s1-s2 to simulate failure...')
    intf = s1.intf('s1-eth1')
    s1.cmd(f'ifconfig {intf} down')
    time.sleep(1)
    print('Ping after link down (should fail or reroute if controller handles it):')
    print(h1.cmd('ping -c 4 10.0.0.2'))

    print('\nYou can now interact with the CLI. Type exit to stop.')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    run_linear()
