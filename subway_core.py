import csv, heapq, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
LINE_COLORS = {'1': '#0052A4', '2': '#00A84D', '3': '#EF7C1C', '4': '#00A5DE'}


def base_name(st):
    """'서울역(1)' -> '서울역'"""
    return re.sub(r'\(.*\)', '', st)


def line_of(st):
    return re.search(r'\((.*)\)', st).group(1)


def load_graph(path=None):
    """subway.csv -> 인접 리스트 그래프 {역: [(이웃, 시간), ...]} (양방향)"""
    path = path or os.path.join(BASE, 'subway.csv')
    graph, edges = {}, []
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            a, b, w = row[0].strip(), row[1].strip(), int(row[2])
            graph.setdefault(a, []).append((b, w))
            graph.setdefault(b, []).append((a, w))
            edges.append((a, b, w))
    return graph, edges


def load_location(path=None):
    """subwayLocation.csv -> {역이름(호선 제외): (위도, 경도)}"""
    path = path or os.path.join(BASE, 'subwayLocation.csv')
    loc = {}
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.reader(f):
            if len(row) >= 3:
                loc.setdefault(row[0].strip(), (float(row[1]), float(row[2])))
    return loc


def dijkstra(graph, start, goal):
    """다익스트라 알고리즘. (총 시간, 경로 리스트) 반환, 경로 없으면 (None, [])"""
    dist = {n: float('inf') for n in graph}
    prev = {}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == goal:
            break
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:          # 더 작은 Cost 발견 -> 업데이트
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dist[goal] == float('inf'):
        return None, []
    path, cur = [goal], goal
    while cur != start:
        cur = prev[cur]
        path.append(cur)
    return dist[goal], path[::-1]


def describe(path):
    """경로를 사람이 읽기 좋은 문장 목록으로 (환승 표시)"""
    out = []
    for i, s in enumerate(path):
        tag = ''
        if i > 0 and base_name(path[i - 1]) == base_name(s):
            tag = '  ← 환승 (%s호선 → %s호선)' % (line_of(path[i - 1]), line_of(s))
        out.append(s + tag)
    return out
