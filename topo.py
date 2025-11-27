from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class CustomTopology(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Add switches
        s1 = self.addSwitch('s1')

        # Add links with bandwidth and delay
        self.addLink(h1, s1, cls=TCLink, bw=10, delay='10ms')
        self.addLink(h2, s1, cls=TCLink, bw=10, delay='10ms')

def run_custom_topology():
    topo = CustomTopology()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Dump information about the nodes
    dumpNodeConnections(net.hosts)

    # Start the Mininet CLI
    net.interact()

    # Clean up after exiting the CLI
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_custom_topology()

