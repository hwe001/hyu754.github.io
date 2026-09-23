import sys, collections
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
graph = root.find('graph')

node_ids = set()
for node in graph.findall('node'):
    node_ids.add(int(node.get('id')[1:]))

edges = []
for edge in graph.findall('edge'):
    to_id = int(edge.get('to')[1:])
    from_id = int(edge.get('from')[1:])
    edges.append((from_id, to_id))

print(f"{path}: {len(node_ids)} nodes, {len(edges)} edges")

adj = collections.defaultdict(list)
for f, t in edges:
    adj[f].append(t)
    adj[t].append(f)

visited = {0}
q = collections.deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in visited:
            visited.add(v)
            q.append(v)

print(f"BFS from node 0 reached {len(visited)}/{len(node_ids)}")
unreached = node_ids - visited
print(f"unreached: {len(unreached)}")
if unreached:
    sample = sorted(unreached)[:10]
    print("sample unreached ids:", sample)
    for uid in sample[:3]:
        incoming = [e for e in edges if e[1] == uid]
        outgoing = [e for e in edges if e[0] == uid]
        print(f"  node {uid}: incoming_edges={incoming} outgoing_edges={outgoing}")
