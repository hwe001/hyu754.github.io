import json, subprocess, sys
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, '.')
from write_vol import write_vol, read_vol


def parse_opencco_xml(path):
    """OpenCCO's -e/.txt exporter has a real bug: it looks up each segment's
    parent coordinate by indexing myVectSegments[myVectParent[idx]] as a raw
    array position, which does not reliably track the parent's actual
    identity as the tree grows via bifurcation -- this fragments the
    exported tree into hundreds of disconnected mini-clusters. The -x/.xml
    exporter is architected correctly: every node is referenced by an
    explicit id, and edges carry from/to ids resolved through that id table.
    Parse the XML instead; it round-trips as a single connected tree."""
    root = ET.parse(path).getroot()
    graph = root.find('graph')
    node_pos = {}
    for node in graph.findall('node'):
        nid = int(node.get('id')[1:])
        floats = node.find(".//attr[@name=' position']/tup").findall('float')
        node_pos[nid] = tuple(float(f.text) for f in floats)
    edges = []
    for edge in graph.findall('edge'):
        eid = int(edge.get('id')[1:])
        to_id = int(edge.get('to')[1:])
        from_id = int(edge.get('from')[1:])
        radius = float(edge.find(".//attr[@name=' radius']/float").text)
        edges.append((from_id, to_id, radius))
    return node_pos, edges
