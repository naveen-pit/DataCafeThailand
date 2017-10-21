import networkx as nx
import json
import pylab as plt
def load_json(path):
    json_file = open(path)
    json_string = json_file.read()
    return json.loads(json_string)
def show_degree_distribution(g):
    degree_sequence_tuple=sorted(nx.degree(g),key=lambda x:x[1],reverse=True) # degree sequence
    degree_sequence = [t[1] for t in degree_sequence_tuple]
    in_hist=[]
    #print "Degree sequence", degree_sequence

if __name__=="__main__":
    data = load_json('./view/data1weak.json')
    nodes = data['nodes']
    edges = data['links']
    g= nx.Graph()
    for node in nodes:
        g.add_node(node['id'])
    for edge in edges:
        g.add_edge(edge['source'],edge['target'],weight=[edge['value']])
    #print(g.in_degree())
    betweenness = nx.betweenness_centrality(g)
    closeness = nx.closeness_centrality(g)
    eigenvector = nx.eigenvector_centrality(g)
    print(betweenness)