import networkx as nx
import matplotlib.pyplot as plt
import json
import math
import sys

def main():
    print('start graphmaker');

    currencygraph = graphmaker('pairlist.json');

    print('end graphmaker');
    print('start check arbitrage');
    findArbitrage(currencygraph);
    print('end check arbitrage');


#---------------------------------------------------------------#
#function to create graph out of exhangerates O(n^2)
#---------------------------------------------------------------#
def graphmaker(currencypairdata):

    G = nx.DiGraph();

    with open(currencypairdata) as file:
        data = json.load(file);
        
        for ticker in data: #O(n) create nodes to graph
            
            if (ticker[1] == 'BTC'): #Tickers like BTC could be removed, API provides rates for Gold,Palladium,BTC, etc.
                continue;

            G.add_node(ticker[1]);

        for ticker in data: #O(n^2) Go through nodes, create edges going out of node to other nodes. Since currency graph should be an complete graph -> O(n^2)
            
            basecurrency = ticker[1]; #ticker[1] is edge startpoint, ticker[2] is list of edge endpoints.

            for conversioncurrency in ticker[2]: #O(n)

                if(conversioncurrency == 'BTC' 
                or conversioncurrency == basecurrency 
                or ticker[2][conversioncurrency] == 0):
                    continue;
                
                conversionrate = ticker[2][conversioncurrency]; #Value of rate from startpoint to endpoint, USD --0,82-> EUR

                G.add_edge(basecurrency,conversioncurrency,weight=conversionrate) #Adds an edge between two points
                
    return G;        

#---------------------------------------------------------------#
#findArbitrage goes through each node, and checks possible arbitrage routes

#---------------------------------------------------------------#         
def findArbitrage(graph):
    #DFS algorithm
    #clf gnf clf 1.0229
    transactionfee = 0.95; #change transactionfee here. Each currency conversion has same fee
    
    arbitragelist = [];

    for n in graph.nodes: #find arbitrage for each ticker/node in graph
        print('checking: '+str(n));

        for a in graph.nodes: #resets nodes in graph before finding arbitrageroute
            graph.nodes[a]['color'] = "white";
            graph.nodes[a]['distance'] = -1;
            graph.nodes[a]['hasEdge'] = False;

        for neighbor in graph.in_edges(n): #used to check, if edge between starting node and a random node in graph exists O(n) (if graph is incomplete)
            graph.nodes[neighbor[0]]['hasEdge'] = True;

        nodelist = [];
        distance = 1; #starting distance
         
        graph.nodes[n]['color'] = "black";
        findPath(graph,n,n,n,distance,transactionfee,nodelist,arbitragelist,0);

        graph.nodes[n]['color'] = "white";

    if (len(arbitragelist) == 0):
        print('no opportunities');
    else:
        for arbitrages in arbitragelist:
            print(arbitrages);

#---------------------------------------------------------------#
#function to
#---------------------------------------------------------------#     
def findPath(graph,startnode,node,previous, distance, transactionfee,nodelist,arbitragelist, dept):
    
    if (dept > 5):
        return nodelist;

    helplist = nodelist[:];
    helplist.append(node);
    
    if (node != startnode):
        graph.nodes[node]['color'] = "gray";
        
        if (graph.nodes[node]['hasEdge']):
            arbitragedistance = distance*graph[node][startnode]['weight']*transactionfee;
            
            if (graph.nodes[node]['distance'] < arbitragedistance):
                graph.nodes[node]['distance'] = arbitragedistance;
            
            if (graph.nodes[previous]['distance'] > arbitragedistance):
                return;
                
            if (arbitragedistance > 1):
                arbitragepath = helplist[:];
                arbitragepath.append(startnode);
                arbitragepath.append(arbitragedistance);
                arbitragelist.append(arbitragepath);

            else:
                graph.nodes[node]['color'] = "white";
                return nodelist;
        else:
            graph.nodes[node]['color'] = "white";
            return nodelist;
    
    for nextnode in graph.neighbors(node):
        color = graph.nodes[nextnode]['color'];
       
        if (color == "gray" or
        nextnode == startnode):
            continue; 

        else:
            newdistance = distance*graph[node][nextnode]['weight']*transactionfee;
            findPath(graph,startnode,nextnode,node,newdistance,transactionfee,helplist,arbitragelist, dept+1);

    graph.nodes[node]['color'] = "white";
            
    return nodelist;


def tickersFromFile():
    tickerlist = [];

    with open('currencylist.json') as file:
        data = json.load(file);
        
        for ticker in data['symbols']:
            tickerlist.append(ticker);
            
    return tickerlist;

main();

