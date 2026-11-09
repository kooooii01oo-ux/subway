import pandas as pd
import pydeck as pdk
import streamlit as st
from subway_core import (load_graph, load_location, dijkstra, describe,
                         base_name, line_of, LINE_COLORS)

st.set_page_config(page_title='지하철 최단 경로', layout='wide')
st.title('🚇 지하철 최단 경로 (다익스트라)')


@st.cache_data
def load():
    g, e = load_graph()
    return g, e, load_location()


graph, edges, loc = load()
names = sorted(graph, key=lambda s: (base_name(s), line_of(s)))


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def lonlat(s):
    la, lo = loc[base_name(s)]
    return [lo, la]


c1, c2 = st.columns(2)
start = c1.selectbox('출발역', names, index=names.index('서울역(1)') if '서울역(1)' in names else 0)
end = c2.selectbox('도착역', names, index=len(names) - 1)

cost, path = dijkstra(graph, start, end)
bg = pd.DataFrame([{'path': [lonlat(a), lonlat(b)], 'color': rgb(LINE_COLORS[line_of(a)]) + [90]}
                   for a, b, w in edges if base_name(a) != base_name(b)])
layers = [pdk.Layer('PathLayer', bg, get_path='path', get_color='color', width_min_pixels=2)]

if cost is None:
    st.error('경로가 없습니다.')
else:
    st.success('총 소요시간 %d분 · %d개 역 통과' % (cost, len(path)))
    route = pd.DataFrame([{'path': [lonlat(a), lonlat(b)]} for a, b in zip(path, path[1:])])
    pts = pd.DataFrame([{'name': s, 'pos': lonlat(s)} for s in path])
    layers += [
        pdk.Layer('PathLayer', route, get_path='path', get_color=[229, 35, 27], width_min_pixels=6),
        pdk.Layer('ScatterplotLayer', pts, get_position='pos', get_fill_color=[255, 255, 255],
                  get_line_color=[0, 0, 0], stroked=True, line_width_min_pixels=1, radius_min_pixels=5),
    ]
    st.pydeck_chart(pdk.Deck(layers=layers, tooltip={'text': '{name}'},
                             initial_view_state=pdk.ViewState(latitude=37.55, longitude=126.99, zoom=10.3)))
    st.subheader('경로')
    for line in describe(path):
        st.write(line)
