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
#findArbitrage goes through each node, and checks possible arbitrage routes. O(n)*O(n^5) = O(n^6) worst case, practically less
#---------------------------------------------------------------#         
def findArbitrage(graph):
    #DFS algorithm
    transactionfee = 0.95; #change transactionfee here. Each currency conversion has same fee
    
    arbitragelist = [];

    for startnode in graph.nodes: #find arbitrage for each ticker/node in graph
        print('checking: '+str(startnode));

        for a in graph.nodes: #resets nodes in graph before finding arbitrageroute
            graph.nodes[a]['color'] = "white"; #Colors are used to keep track of visited nodes, whites are unvisited, grays are visited and black is a starting node
            graph.nodes[a]['distance'] = 0; #first distance set to nodes, can be used to limit detected arbitrages -> 1.001 value only detects cycles above 1.001
            graph.nodes[a]['hasEdge'] = False; 

        for neighbor in graph.in_edges(startnode): #used to check, if edge between starting node and a random node in graph exists O(n) in complete graphs
            graph.nodes[neighbor[0]]['hasEdge'] = True;

        for neighbor in graph.out_edges(startnode):
            graph.nodes[neighbor[1]]['distance'] = graph[startnode][neighbor[1]]['weight'];

        nodelist = []; # keeps track of path to current node
        distance = 1; #starting distance, path from starting currency to itself is set to 1
         
        graph.nodes[startnode]['color'] = "black"; #Colours starting node black
        findPath(graph,startnode,startnode,startnode,distance,transactionfee,nodelist,arbitragelist,0); 

        # We have to check every node in a graph, and from that node check path (almost) to every other node -> O(n^n)
        # In order to go around this time complexity, I assume that because of transaction costs, longer the path is, more costs eat from profits, leaving less practical arbitrage opportunities.
        # Therefore if we limit the debt to maxinum 5 currencies, we can cut complexity to O(n^5) or O(n^d) where d = dept, which is significantly faster. This doesn't allow us to discover paths longer than 5 currencies
        # To make search even faster, we can stop the search if profitability gets worse when dept gets increased. This only allows us to discover best arbitrage routes, but misses alot of opportunities
        # for example if [USD,AMD,CLP,USD] gave 4% profit and later discovered [USD,EUR,CLP,USD] gave 3,9%, it wouldn't get included because weight of more efficient path is saved onto CLP node.
        # If less currencies are included, O(n^5) becomes more reasonable. There is a lot of tradeoff

    if (len(arbitragelist) == 0):
        print('no opportunities');
    else:
        for arbitrages in arbitragelist: #Go through found arbitrage paths
            print(arbitrages);
    
#---------------------------------------------------------------#
#findPath() iterates over nodes, worst case O(n^5)
#---------------------------------------------------------------#     
def findPath(graph,startnode,node,previous, distance, transactionfee,nodelist,arbitragelist,dept):
    
    if (dept > 5): # If dept is larger than 5, returns. This limits time complexity to O(n^5)
        return nodelist;

    helplist = nodelist[:]; #Copies path into current node to editable list, which keeps track of path to next node
    helplist.append(node);
    
    if (node != startnode): #Skips first node
        graph.nodes[node]['color'] = "gray";
        
        if (graph.nodes[node]['hasEdge']): #Checks that node has an edge to 
            arbitragedistance = distance*graph[node][startnode]['weight']*transactionfee; #calculates current arbitrage profitability
            
            if (graph.nodes[node]['distance'] < arbitragedistance): # If provitability is better than previous route to the node, sets new profitability
                graph.nodes[node]['distance'] = arbitragedistance;
            
            if (graph.nodes[previous]['distance'] > graph.nodes[node]['distance']): #returns back to previous node, if profitability got worse
                return;
                  
            if (arbitragedistance > 1): # If pathlenght is over 1, arbitrage is profitable. Adds path to arbitragelist
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
    
    for nextnode in graph.neighbors(node): # Goes through currency rates. In complete graph O(n)
        color = graph.nodes[nextnode]['color'];
       
        if (color == "gray" or
        nextnode == startnode): #If node is already part of path, hops over the node
            continue; 

        else:
            newdistance = distance*graph[node][nextnode]['weight']*transactionfee; #Calculates new distance at next node
            findPath(graph,startnode,nextnode,node,newdistance,transactionfee,helplist,arbitragelist, dept+1); #Increases dept by one and starts over at next node

    graph.nodes[node]['color'] = "white"; #Recolours node to white so it can be used again
            
    return nodelist;


def tickersFromFile():
    tickerlist = [];

    with open('currencylist.json') as file:
        data = json.load(file);
        
        for ticker in data['symbols']:
            tickerlist.append(ticker);
            
    return tickerlist;

main();

