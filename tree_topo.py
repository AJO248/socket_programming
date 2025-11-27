#!/usr/bin/env python3
"""
Tree topology for Mininet:
  s1 (root) connected to s2 and s3
  s2 connected to h1,h2
  s3 connected to h3,h4

This script starts Mininet, prints MACs and interfaces, assigns IPs, runs ping tests,
shows ARP tables, and runs an iperf UDP throughput test from h1 to h4.

Usage: sudo python3 tree_topo.py
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import time


def print_macs(net):
    print("\nMAC addresses:")
    for h in net.hosts:
        print(f"  {h.name}: {h.MAC()}")
    for s in net.switches:
        print(f"  {s.name} interfaces:")
        for intf in s.intfList():
            try:
                mac = intf.MAC()
            except Exception:
                mac = 'N/A'
            print(f"    {intf}: {mac}")


def run_tree():
    setLogLevel('info')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)
    # controller: use default controller on localhost:6653 or 6654
    c0 = net.addController('c0')

    # switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    # hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')

    # links: default host links 1Gbps, switch-switch 10Gbps
    net.addLink(s1, s2, bw=10000)
    net.addLink(s1, s3, bw=10000)

    net.addLink(s2, h1, bw=1000)
    net.addLink(s2, h2, bw=1000)
    net.addLink(s3, h3, bw=1000)
    net.addLink(s3, h4, bw=1000)

    net.start()

    print_macs(net)

    # show interfaces on h1 and s1
    print('\nifconfig -a on h1:')
    print(h1.cmd('ifconfig -a'))
    print('\nifconfig -a on s1:')
    print(s1.cmd('ifconfig -a'))

    # assign IPs manually
    ips = ['10.0.0.1/24', '10.0.0.2/24', '10.0.0.3/24', '10.0.0.4/24']
    hosts = [h1, h2, h3, h4]
    for h, ip in zip(hosts, ips):
        print(f"Setting {h.name} -> {ip}")
        h.setIP(ip)

    time.sleep(1)
    # verify IPs
    for h in hosts:
        print(f"\nip addr show on {h.name}:")
        print(h.cmd('ip addr show'))

    # Ping tests
    print('\nPing h1 from h3:')
    print(h3.cmd('ping -c 4 10.0.0.1'))
    print('\nPing h4 from h2:')
    print(h2.cmd('ping -c 4 10.0.0.4'))

    # Show ARP tables on h1 and h3
    print('\nARP table on h1:')
    print(h1.cmd('arp -n'))
    print('\nARP table on h3:')
    print(h3.cmd('arp -n'))

    # UDP throughput using iperf (iperf must be installed)
    print('\nStarting iperf UDP test: h4 as server, h1 as client')
    print('Starting iperf server on h4...')
    h4.cmd('iperf -s -u -p 5001 &')
    time.sleep(1)
    print('Running iperf client on h1...')
    result = h1.cmd('iperf -c 10.0.0.4 -u -b 10M -t 10 -p 5001')
    print('\niperf result:')
    print(result)

    print('\nYou can now interact with the Mininet CLI. Type exit to stop the network.')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    run_tree()
