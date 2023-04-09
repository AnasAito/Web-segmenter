from pyvis.network import Network
import requests
import pprint
from bs4 import BeautifulSoup
from collections import Counter
import hashlib
import networkx as nx
from collections import defaultdict
from bs4 import BeautifulSoup as soup
import itertools as it
import time
import re


def visualize_graph(graph, graph_name=None, root_node=None):
    if root_node is None:
        _graph = graph
    else:
        ego_graph_nodes = [root_node] + list(nx.descendants(graph, root_node))
        _graph = graph.subgraph(ego_graph_nodes)

    net = Network(notebook=True, directed=True)
    for node in _graph.nodes:
        # print(node)
        # label = graph.nodes[node]['payload'].get('text')
        # href = graph.nodes[node]['payload'].get('href')
        try:
            label = _graph.nodes[node]['payload'].get('text')
        except:
            # print(node)
            label = ''
        try:
            href = _graph.nodes[node]['payload'].get('href')
        except:
            href = ''
        group = _graph.nodes[node]['link_meta'] is not None
        group = '#B185A7' if group else '#A6FFA1'
        if root_node is not None and node == root_node:
            group = 'red'
        net.add_node(node, label=f"{label}_{href}", color=group)

    for edge in _graph.edges:
        _edge = {'src': edge[0], 'tgt': edge[1]}
        try:
            net.add_edge(_edge['src'], _edge['tgt'])
        except:
            pass
    net.show_buttons(filter_=['physics'])
    net.show(f'nx_{graph_name}.html')


def encode_element(e_str: str):
    return hashlib.sha1(e_str.encode()) .hexdigest()


def format_text(text):
    text = text.replace('\n', ' ').strip()
    return ' '.join(re.split("\s+", text, flags=re.UNICODE)).strip()


def get_payload(node):
    if isinstance(node, str):
        return {'href': None,
                'text': format_text(node)}
    # only non wrapping links
    if node.name == 'a' and len(node.contents) > 1:
        return {'href': node.get('href', None),
                'text': ''}
    return {'href': node.get('href', None),
            'text': format_text(node.text)}


def str_to_bs4(x):
    html_soup = BeautifulSoup(x, 'html.parser')
    html_tag = html_soup.find('p')
    return html_tag


def normalize_element(element):
    element_name = element.name
    # only free text elements are accepted
    is_valid = True
    if element_name is None:
        if element.text == element and element.text.strip() != '':
            is_valid = True
            return {
                'is_valid': is_valid,
                'element': element.text,
                'formated': True
            }
        is_valid = False
    # scripts,img,ipframe,noscript,svg are not valid
    if element_name in ['script', 'img', 'noscript', 'svg', 'input', 'style', 'form', 'kin-address-form', 'figcaption', 'picture']:
        is_valid = False
    return {
        'is_valid': is_valid,
        'element': element,
        'formated': False
    }


def has_payload(i):
    # print(i,isinstance(i, str))
    if isinstance(i, str):
        return True
    if i.name == 'a':
        return True
    if len(i.contents) == 1 and i.content == i.text and i.text.strip() != '':
        return True
    return False


def _traverse_html(_soup, _graph: nx.Graph, _counter, global_counter, _parent=None) -> None:
    # print('parent',_parent ,_soup.contents )
    for element in _soup.contents:
        element_norm = normalize_element(element)
        #  print(element_norm)
        if element_norm['is_valid']:
            element_content = element_norm['element']
            #  print(element_content, type(element_content))
            #  infer_payload = None
            try:
                element_name = element_content.name
                element_class = element_content.get('class')
            except:
                element_name = 'p'
                element_class = None
                # infer_payload = {'href':None,
                #                   'text':element_content}
            _name_count = _counter.get(element_name)
            _element_name = f"{element_name}_{_name_count}_{element_class}"
            node_id = encode_element(element_name)
            node_id = _element_name

            try:
                if _parent is not None:
                    #  print('node_id', node_id)
                    payload = get_payload(element_content) if has_payload(
                        element_content) else None
                    # print('payload',payload)
                    _graph.add_nodes_from([(node_id, {"element_type": element_name,
                                                      "name_count": _name_count,
                                                      "item_index": global_counter,
                                                      "class": '_'.join(element_class if element_class is not None else []),
                                                      "payload": payload})])
                    global_counter += 1
                    _graph.add_edge(_parent, node_id)

                _counter[element_name] += 1
                _traverse_html(element_content, _graph,
                               _counter, global_counter, node_id)
            except AttributeError:
                pass


def populate_empty_meta(graph):
    for node in graph.nodes:
        try:
            _ = graph.nodes[node]['payload']
        except:
            attrs = {node: {"element_type": node.split('_')[0],
                            "class": node.split('_')[2],
                            "payload": None}}
            nx.set_node_attributes(graph, attrs)
    return graph


def get_neighbors(graph, node):
    return [{'id': n, 'meta': graph.nodes[n]} for n in graph.neighbors(node)]


def get_predecessors(graph, node):
    return [{'id': n, 'meta': graph.nodes[n]} for n in graph.predecessors(node)]


def clean_graph(graph):
    def is_empty_leaf(node): return graph.nodes[node]['payload'] is None and len(
        get_neighbors(graph, node)) == 0

    def is_bridge_node(node): return graph.nodes[node]['payload'] is None and len(
        get_predecessors(graph, node)) == len(get_neighbors(graph, node))

    nodes_to_delete = [node for node in graph.nodes if is_empty_leaf(
        node) or is_bridge_node(node)]

    for node in nodes_to_delete:
        try:
            graph.add_edges_from(
                it.product(
                    graph.predecessors(node),
                    graph.successors(node)
                )
            )
            graph.remove_node(node)
        except:
            pass
    return graph


def url_to_graph(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser').body
    _full_graph = nx.DiGraph()
    _global_counter = 0
    _traverse_html(soup, _full_graph, defaultdict(int), _global_counter)
    graph = populate_empty_meta(_full_graph)
    graph = clean_graph(graph)
    mapping = {node: encode_element(node) for node in graph.nodes}
    graph = nx.relabel_nodes(graph, mapping)
    return graph


def simplify_link_nodes(graph):

    attrs = {node: {"link_meta": None} for node in graph.nodes}
    nx.set_node_attributes(graph, attrs)
    # get links
    link_nodes = [
        node for node in graph.nodes if graph.nodes[node]['element_type'] == 'a']

    def summarize_link(graph, link):
        descendants_nodes = nx.descendants(graph, link)
        text_payload = [graph.nodes[link]['payload'].get('text')]
        for node in descendants_nodes:
            try:
                text = graph.nodes[node]['payload'].get('text')
                text_payload.append(text)
            except:
                pass
        text_payload = list(set(text_payload))
        atom_meta = {
            'href':  graph.nodes[link]['payload'].get('href'),
            'text_payload': text_payload
        }
        nodes_to_delete = descendants_nodes
        node_to_update = link
        return node_to_update, atom_meta, nodes_to_delete

    for node in link_nodes:
        try:
            node_to_update, atom_meta, nodes_to_delete = summarize_link(
                graph, node)

            # update link node
            attrs = {node_to_update: {"link_meta": atom_meta}}
            nx.set_node_attributes(graph, attrs)
            # delete detail nodes
            nodes_to_delete = nodes_to_delete
            for node in nodes_to_delete:
                graph.add_edges_from(
                    it.product(
                        graph.predecessors(node),
                        graph.successors(node)
                    )
                )
                graph.remove_node(node)
        except:
            pass
    graph = clean_graph(graph)
    return graph


def score_tag(tag):
    if 'h' in tag:
        return 0
    if 'p' == tag:
        return 1
    return 2


def process_container(graph, container_id):

    all_childs = [(n, 1)for n in list(
        nx.descendants_at_distance(graph, container_id, 1))]
    all_childs += [(n, 2)
                   for n in list(nx.descendants_at_distance(graph, container_id, 2))]

    all_childs_contentfull = [
        (node, level) for node, level in all_childs if graph.nodes[node]['payload'] is not None]
    all_childs_contentfull = [{'id': node,
                               'text': graph.nodes[node]['payload']['text'],
                               'element_type_score':score_tag(graph.nodes[node]['element_type']),
                               "name_count":graph.nodes[node]['name_count'] if graph.nodes[node]['name_count'] is not None else -1,
                               "level": level,
                               "item_index": graph.nodes[node]['item_index'],
                               }
                              for node, level in all_childs_contentfull]

    all_childs_contentfull = sorted(
        all_childs_contentfull, key=lambda x: x['item_index'])

    text_neighbors = [node['text']
                      for node in all_childs_contentfull if node['text'] != '']

    # flag lists
    neighbors = [n['id'] for n in get_neighbors(graph, container_id)]
    neighbors_weight = [len(list(nx.descendants(graph, node)))
                        for node in neighbors]

    label = text_neighbors[0] if len(text_neighbors) > 0 else None
    to_filter = False
    if label is not None:
        label = label.strip().replace('\n', '').replace('\t', '')
        to_filter = len(label.split(' ')) > 10
    # flag script coontainers
    if label is not None:
        label = label if '%' not in label else None

    is_valid_container = (len(set(neighbors_weight)) !=
                          1) or (sum(neighbors_weight) == 0)

    if label is None:
        is_valid_container = False

    return {
        'id': container_id,
        'is_valid_container': is_valid_container,
        'label': label,
        'score': len(nx.descendants(graph, container_id)),
        'to_filter': to_filter
    }


def get_central_nodes(graph):
    central_nodes_candidates = [
        node for node in graph.nodes if graph.nodes[node]['payload'] is None]
    central_nodes = {}
    for n in central_nodes_candidates:
        n_processed = process_container(graph, n)
        if n_processed['is_valid_container']:
            central_nodes[n_processed['id']] = {'label': n_processed['label'],
                                                'score': n_processed['score'],
                                                'to_filter': n_processed['to_filter']}

    # print(len(central_nodes))
    ranked_nodes = {k: v for k, v in sorted(
        central_nodes.items(), key=lambda item: item[1]['score'], reverse=True)}
    # ranked_nodes_filtred = {k: v for k,v in ranked_nodes.items() if not v['to_filter']}
    return ranked_nodes


def is_grid(graph, node_id):
    # flag lists
    neighbors = [n['id'] for n in get_neighbors(graph, node_id)]
    neighbors_weight = [len(list(nx.descendants(graph, node)))
                        for node in neighbors]

    is_grid_element = (len(set(neighbors_weight)) ==
                       1) and (sum(neighbors_weight) != 0)
    return is_grid_element


def is_leaf(graph, node_id):
    # flag lists
    neighbors = [n['id'] for n in get_neighbors(graph, node_id)]
    neighbors_weight = [len(list(nx.descendants(graph, node)))
                        for node in neighbors]

    is_leaf_elemnt = sum(neighbors_weight) == 0
    return is_leaf_elemnt


def get_unique_links(links):
    unique_links = {}
    for link in links:
        if link['href'] in unique_links:
            unique_links[link['href']] = unique_links[link['href']
                                                      ] + link['text_payload']
        else:
            unique_links[link['href']] = link['text_payload']
    return [{'href': k, 'text_payload': list(set(v))}for k, v in unique_links.items()]


def get_summary(graph, node_id):
    summary = {
        'id': node_id,
        'content': [],
        'links': []
    }
    # get links
    all_childs = list(nx.descendants(graph, node_id))
    links = [n for n in all_childs if graph.nodes[n]['link_meta'] is not None]
    links = [graph.nodes[link]['link_meta'] for link in links]
    # clean links
    links = [{'href': link['href'], 'text_payload': [text for text in link['text_payload'] if text != '']}
             for link in links if link]
    # unique links

    summary['links'] = get_unique_links(links)

    # get neighbors
    node_neis = get_neighbors(graph, node_id)

    node_neis = [node['id'] for node in node_neis]
    # print(node_id, node_neis)
    # print([graph.nodes[n]['item_index'] for n in node_neis])
    for node in node_neis:
        if is_grid(graph, node):
            # print('is grid', node)

            grid_items = get_neighbors(graph, node)
            grid_items = [_node['id'] for _node in grid_items]
            grid_items_content = []
            for item in grid_items:
                _item_summary = {
                    'type': 'grid_item',
                    'payload': [],
                    'index': graph.nodes[item]['item_index']
                }
                # get all sub childs
                all_childs = list(nx.descendants(graph, item))
                all_childs_contentfull = [
                    _node for _node in all_childs if graph.nodes[_node]['payload'] is not None]
                text_content = []
                for atom in all_childs_contentfull:

                    if graph.nodes[atom]['payload']['text'] != '' and graph.nodes[atom]['link_meta'] is None:
                        text_content.append({
                            'type': 'atom',
                            'payload': graph.nodes[atom]['payload']['text']
                        })

                _item_summary['payload'] += text_content
                if _item_summary['payload'] != []:
                    grid_items_content.append(
                        _item_summary
                    )
            if grid_items_content != []:
                summary['content'].append({
                    'type': 'grid',
                    'payload': sorted(grid_items_content, key=lambda x: x['index']),
                    'index': graph.nodes[node]['item_index']
                })

        elif is_leaf(graph, node):
            # print('has_leaf', node)
            if graph.nodes[node]['payload'] is not None:
                summary['content'] += [
                    {
                        'type': 'atom',
                        'payload': graph.nodes[node]['payload']['text'],
                        'index': graph.nodes[node]['item_index']
                    }
                ]
            for n in graph.neighbors(node):

                if graph.nodes[n]['payload']['text'] != '' and graph.nodes[n]['link_meta'] is None:
                    summary['content'] += [
                        {
                            'type': 'atom',
                            'payload': graph.nodes[n]['payload']['text'],
                            'index': graph.nodes[n]['item_index']
                        }
                    ]

        else:
            print('not leaf or grid', node)
            # get all sub childs
            all_childs = list(nx.descendants(graph, node))
            all_childs_contentfull = [
                _node for _node in all_childs if graph.nodes[_node]['payload'] is not None]
            for atom in all_childs_contentfull:

                if graph.nodes[atom]['payload']['text'] != '' and graph.nodes[atom]['link_meta'] is None:
                    summary['content'].append(
                        {
                            'type': 'atom',
                            'payload': graph.nodes[atom]['payload']['text'],
                            'index': graph.nodes[atom]['item_index']
                        }
                    )

    # sort
    summary['content'] = sorted(summary['content'], key=lambda x: x['index']),
    return summary


# # test
# url = 'https://www.microsoft.com/en-us/ai'
# graph = url_to_graph(url)
# print(len(graph.nodes))
# graph = simplify_link_nodes(graph)
# print(len(graph.nodes))
# ranked_nodes = get_central_nodes(graph)
# print(len(ranked_nodes))
# pprint.pprint(ranked_nodes)

class WebSegmenter:
    def __init__(self, url: str):
        self.url = url
        self.graph = None
        self.ranked_nodes = None

    def run(self):
        graph = url_to_graph(self.url)
        graph = simplify_link_nodes(graph)
        self.graph = clean_graph(graph)
        self.ranked_nodes = get_central_nodes(self.graph)

    def search(self, keyword):
        keyword = keyword.lower()
        return [(node_id, meta) for node_id, meta in self.ranked_nodes.items() if keyword in meta['label'].lower()]

    def summarize(self, node_id):
        return get_summary(self.graph, node_id)