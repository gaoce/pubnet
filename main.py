#! /usr/bin/env python3
import requests as rq
import xml.etree.ElementTree as et
import time
import networkx as nx
import matplotlib.pyplot as plt


base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
para = {
        'email' :   'gaoce@coe.neu.edu',
        'tool'  :   'biopython',
        'retmax':   10000,
        'db'    :   'pubmed',
        }
delay = 0.35


def searchArticles(kwrds):
    '''
    search pubmed against the list of keywords in kwrds
    input:
        kwrds: keyword list, list of strings. eg, ['science[journal]','cancer']
    output:
        pmid_list: a list of PMID

    '''
    
    # make get request
    para['term'] = '+AND+'.join(kwrds)
    r = rq.get(base_url + 'esearch.fcgi?', params=para)
    
    # parse returned XML
    root = et.fromstring(r.content)
    pmid_nodes = root.findall('.//IdList/Id')
    pmid_list = [pmid.text for pmid in pmid_nodes]
    return(pmid_list)


def getLinks(pmid_in, linktype):
    '''
    query related/cited article for each pmid_in
    Input:
        pmid_in: pmid input, a string, eg, '24374157'
        linktype: 'related' or 'citation'
    output:
        pmid_list: a list of returned pmid
        
    '''
    
    # construct parameters and make the get request
    
    if linktype == 'related':
        para['linkname'] = 'pubmed_pubmed'
    elif linktype == 'citation':
        para['linkname'] = 'pubmed_pubmed_citedin'
    else:
        raise ValueError('linktype must be either "related" or "citation"' + \
                         ' instead of "' + str(linktype) + '"')
    para['id'] = str(pmid_in)
    r = rq.get(base_url + 'elink.fcgi?', params=para)
    
    # parse the returned xml
    root = et.fromstring(r.content)
    pmid_nodes = root.findall('.//LinkSetDb//Id')
    pmid_list = [pmid.text for pmid in pmid_nodes if pmid.text != pmid_in]

    return(pmid_list)


def createGraph(pmids, linktype='related'):
    '''
    search related article against each pmid and return a graph with each edge
    representing relation (related or citation)
    input:
        pmids: a list of pmids
        linktype: 'related' or 'citation'
    output:
        G: a graph
    '''
    
    if linktype == 'related':
        graph_fun = nx.Graph  # undirected graph
    elif linktype == 'citation':
        graph_fun = nx.DiGraph  # directed graph
    else:
        raise ValueError('linktype must be either "related" or "citation"' + \
                         ' instead of "' + str(linktype) + '"') 
    
    G = graph_fun()
    G.add_nodes_from(pmids)
    
    n_pmids = len(pmids)
    i = 1
    for pmid_from in pmids:
        # display progress
        print('\r{:.2f}%'.format(i / n_pmids * 100), end='')
        i += 1
        
        time.sleep(delay)
        pmid_list = getLinks(pmid_from, linktype)
        for pmid_to in pmid_list:
            if pmid_to not in G: break
            G.add_edge(pmid_from, pmid_to)
    print()
    return(G)


def main():
    pmidList = searchArticles(['"time series"', '"gene expression"']);
    G = createGraph(pmidList, linktype='related')
    nx.write_gpickle(G, "related.gpickle")


if __name__ == '__main__':
    main()


'''
cited
http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?db=pubmed&linkname=pubmed_pubmed_citedin&id=20708821
http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?db=pubmed&linkname=pubmed_pubmed&id=20708821

'''
