from scapy.all import *
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd


def save_pcap(dir, filename):
    df = read_pcap(dir, filename)
    save_dataframe_h5(df, dir, filename)


def save_dataframe_h5(df, dir, filename):
    key = filename.split('-')[0]
    df.to_hdf(dir + filename + '.h5', key=key)


def read_pcap(dir, filename):
    timeS = time.clock()
    count = 0
    label = filename.split('-')[0]
    print("Read PCAP, label is %s" % label)
    data = rdpcap(dir + filename + '.pcap')
    totalPackets = len(data)
    percentage = int(totalPackets / 100)
    # Workaround/speedup for pandas append to dataframe
    frametimes =[]
    dsts = []
    srcs = []
    protocols = []
    dports = []
    sports = []
    payloads = []
    labels = []

    print("Total packages: %d" % totalPackets)
    timeR = time.clock()
    timeRead = timeR-timeS
    print("Time to read PCAP: "+ str(timeRead))
    sessions = data.sessions()
    for id, session in sessions.items():
        for packet in session:
            if IP in packet and (UDP in packet or TCP in packet):
                ip_layer = packet[IP]
                frametimes.append(packet.time)
                dsts.append(ip_layer.dst)
                srcs.append(ip_layer.src)
                transport_layer = ip_layer.payload
                protocols.append(transport_layer.name)
                dports.append(transport_layer.dport)
                sports.append(transport_layer.sport)
                # hex() converts a bytestring to a string with 2 hex digits for each byte:
                # https://docs.python.org/3/library/stdtypes.html#bytes.hex
                payloads.append(transport_layer.payload.original.hex())
                labels.append(label)
                if(count%(percentage*5) == 0):
                    print(str(count/percentage) + '%')
                count += 1
    timeT = time.clock()
    print("Time spend: %ds" % (timeT-timeR))
    d = {'time': frametimes,
         'ip.dst': dsts,
         'ip.src': srcs,
         'protocol': protocols,
         'port.dst': dports,
         'port.src': sports,
         'payload': payloads,
         'label': labels}
    df = pd.DataFrame(data=d)
    timeE = time.clock()
    totalTime = timeE - timeS
    print("Time to convert PCAP to dataframe: " + str(totalTime))
    return df


def load_h5(filename, key=''):
    timeS = time.clock()
    df = pd.read_hdf(filename, key=key)
    timeE = time.clock()
    loadTime = timeE-timeS
    print("Time to load " + filename + ": " + str(loadTime))
    return df

def plotHex(hexvalues, filename):
    '''
        Plot an example as an image
    '''
    size = 39
    canvas = np.zeros((size,size))
    padding = (size*size)-len(hexvalues)
    #odd = if padding % 2 == 0 false  else true
    odd = False
    if padding %2 == 0:
        odd = False
    else:
        odd = True
    padding = int(np.floor(padding/2))
    hexvalues = np.pad(hexvalues,padding,'constant')
    print(hexvalues)
    if odd:
        hexvalues = np.append(hexvalues,[0])
    canvas = np.reshape(np.array(hexvalues),(size,size))
    plt.figure(figsize=(4, 4))
    plt.axis('off')
    plt.imshow(canvas, cmap='gray')
    plt.title(filename)
    plt.show()


def pad_elements_with_zero(payloads):
    # Assume max payload to be 1460 bytes but as each byte is now 2 hex digits we take double length
    max_payload_len = 1460*2
    # Pad with '0'
    payloads = [s.ljust(max_payload_len, '0') for s in payloads]
    return payloads


def hash_elements(payloads):
    return payloads
