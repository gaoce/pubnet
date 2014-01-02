import networkx as nx


G = nx.read_gpickle('./related.gpickle')
degDict = {}
for node in G.nodes():
    degDict.setdefault(node,G.degree(node))

sorted_degDict = sorted(degDict.keys(),key=degDict.get, reverse=True)

print(sorted_degDict[:10])
