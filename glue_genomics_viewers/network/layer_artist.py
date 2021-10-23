from glue.viewers.common.layer_artist import LayerArtist

import numpy as np
from .state import NetworkLayerState
import networkx as nx
from astropy.table import Table
from matplotlib.collections import PathCollection, LineCollection
import mplcursors as mplc

RENDER_LAYOUTS = {
    'spring': lambda x: nx.spring_layout(x, iterations=30),
    'circular': nx.circular_layout,
    'kamada kawaii': nx.kamada_kawai_layout,
    'planar': nx.planar_layout,
    'spectral': nx.spectral_layout,
    'shell': nx.shell_layout
}


class NetworkLayerArtist(LayerArtist):

    _layer_state_cls = NetworkLayerState

    def __init__(self, axes, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.axes = axes
        self.figure = self.axes.figure
        self.axes.figure.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self._collection_handler = {}

        self.state.add_callback('visible', self._on_visual_change)
        self.state.add_callback('zorder', self._on_visual_change)

        self.state.layer.style.add_callback('color', self._on_visual_change)
        self.state.layer.style.add_callback('alpha', self._on_visual_change)

        self._selected_layout = 'spring'
        
        nx.Graph(ax=axes)

        self.state.add_callback('fill', self._on_fill_change)
        self.state.add_callback('visible', self._on_visible_change)
        self.state.add_callback('zorder', self._on_zorder_change)

        # self._viewer_state.add_callback('x_att', self._on_attribute_change)
        # self._viewer_state.add_callback('y_att', self._on_attribute_change)
        self._viewer_state.add_callback('layout', self._on_layout_changed)

    @property
    def path_artist(self):
        return self.axes.collections[0]

    @property
    def line_artist(self):
        return self.axes.collections[1]

    def _make_graph(self):
        G = nx.Graph()
        render_layout = RENDER_LAYOUTS[self._selected_layout]

        index = self.state.layer["index"]
        chrm = self.state.layer["chrm"]
        peak = self.state.layer["peak"]
        corr = self.state.layer["corr"]

        for i in range(len(self.state.layer['chrm'])):
            G.add_edge(f"{chrm[i]} {index[i]}", peak[i], strength=corr[i])
        
        d = dict(nx.degree(G))

        weights = np.array(list(nx.get_edge_attributes(G, 'strength').values())) * 5

        nx.draw(G, pos=render_layout(G), ax=self.axes, 
                with_labels=False, width=weights, 
                node_size=[v * 20 + 20 for v in d.values()], 
                node_color=['red' if 'index' in n else 'blue' for n in G],
                edgecolors='black', linewidths=1)

        self.axes.figure.subplots_adjust(bottom=0, top=1, left=0, right=1)

        crs = mplc.cursor(self.path_artist, hover=2)

        @crs.connect("add")
        def _node_labels(sel):
            label = list(G.nodes)[sel.index]
            sel.annotation.set_text(label)

    def _on_fill_change(self, value=None):
        if len(self.axes.collections) == 0:
            return

        if self.state.fill:
            self.path_artist.set_markerfacecolor(self.state.layer.style.color)
        else:
            self.path_artist.set_markerfacecolor('none')
        self.redraw()

    def _on_visible_change(self, value=None):
        if len(self.axes.collections) == 0:
            return

        self.path_artist.set_visible(self.state.visible)
        self.line_artist.set_visible(self.state.visible)
        self.redraw()

    def _on_zorder_change(self, value=None):
        if len(self.axes.collections) == 0:
            return

        self.path_artist.set_zorder(self.state.zorder)
        self.line_artist.set_zorder(self.state.zorder)
        self.redraw()

    def _on_attribute_change(self, value=None):
        self._make_graph()
        self.redraw()

    def _on_layout_changed(self, layout):
        self._selected_layout = layout.lower()
        self.remove()
        self._make_graph()
        self.redraw()

    def clear(self):
        if len(self.axes.collections) == 0:
            return

        self.path_artist.set_visible(False)
        self.line_artist.set_visible(False)

    def remove(self):
        for coll in [x for x in self.axes.collections]:
            coll.remove()

        for txt in [x for x in self.axes.texts]:
            txt.remove()

    def redraw(self):
        self.axes.figure.canvas.draw_idle()

    def update(self):
        self._on_fill_change()
        self._on_attribute_change()
