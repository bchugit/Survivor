import pandas as pd
import numpy as np
import networkx as nx
import pickle
import wiki_scrape as ws

# Build pandas df of all centrality scores
# Degree, closeness, betweenness, eigenvector, pagerank


def distance_scores(season, graph):

    # Take largest connected component
    g = graph if nx.is_connected(graph) else max(nx.connected_component_subgraphs(graph), key=len)

    # Ratio of largest connected component subgraph
    conn = len(max(nx.connected_component_subgraphs(g), key=len)) / float(nx.number_of_nodes(graph))
    conn = np.round(conn, 3)

    # Radius, diameter
    rad = nx.radius(g)
    diam = nx.diameter(g)

    # Average eccentricity
    ecc = np.mean(list(nx.eccentricity(g).values()))
    ecc = np.round(ecc, 3)

    # Put it all into a dataframe
    df = pd.DataFrame([[season, conn, rad, diam, ecc]],
                      columns=['season', 'conn', 'rad', 'diam', 'ecc  '])

    return df


def get_distance_scores(season, graph):
    separate_dfs = [distance_scores(k, graph[k]) for k in graph.keys()]
    merged_df = pd.concat(df for df in separate_dfs).set_index('season')
    ordered_df = pd.concat([ws.order_seasons(season), merged_df], axis=1).sort_values('snum')
    return ordered_df


def centrality_scores(vote_matrix, season_graph):
    deg = nx.degree(season_graph)
    deg = {k: round(v, 1) for k, v in dict(deg).items()}

    close = nx.closeness_centrality(season_graph)
    close = {k: round(v, 3) for k, v in dict(close).items()}

    btw = nx.betweenness_centrality(season_graph)
    btw = {k: round(v, 3) for k, v in dict(btw).items()}

    eig = nx.eigenvector_centrality_numpy(season_graph)
    eig = {k: round(v, 3) for k, v in dict(eig).items()}

    page = nx.pagerank(season_graph)
    page = {k: round(v, 3) for k, v in dict(page).items()}

    # Add contestant placement (rank)
    order = list(vote_matrix.index)
    place_num = list(range(len(order)))
    place = {order[i]: i + 1 for i in place_num}

    names = season_graph.nodes()

    # Build a table with centralities
    table = [[name, deg[name], close[name], btw[name], eig[name], page[name], place[name]] for name in names]

    # Convert table to pandas df
    headers = ['name', 'deg', 'close', 'btw', 'eig', 'page', 'place']
    df = pd.DataFrame(table, columns=headers)
    df = df.sort_values(['place'], ascending=True)

    return df


def get_centrality_scores(voteweights, graphs, save_to_disk=False):
    central = {s: centrality_scores(voteweights[s], graphs[s])
               for s in graphs.keys()}
    if save_to_disk:
        pickle.dump(central, open("network.p", "wb"))
    return central
