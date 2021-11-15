from platform import node
from glue.viewers.common.layer_artist import LayerArtist

import numpy as np
from .state import NetworkLayerState
import networkx as nx
import mplcursors as mplc

RENDER_LAYOUTS = {
    'spring': lambda x: nx.spring_layout(x, iterations=20),
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

        self._viewer_state.add_callback('layout', self._on_layout_changed)

    def path_artist(self, layer):
        return self._collection_handler[layer]['path']

    def line_artist(self, layer):
        return self._collection_handler[layer]['line']

    def _make_graph(self, reset=False):
        G = nx.Graph()
        render_layout = RENDER_LAYOUTS[self._selected_layout]

        layer = self.state.layer

        index = layer["index"]
        chrm = layer["chrm"]
        peak = layer["peak"]
        corr = layer["corr"]

        for i in range(len(self.state.layer['chrm'])):
            G.add_edge(f"{chrm[i]} {index[i]}", peak[i], strength=corr[i])
            G.nodes[f"{chrm[i]} {index[i]}"]
        
        d = dict(nx.degree(G))

        weights = np.array(list(nx.get_edge_attributes(G, 'strength').values())) * 5

        node_positions = render_layout(G)
        # self._viewer_state.node_positions = render_layout(G)

        if self._viewer_state.node_positions is None or reset:
            self._viewer_state.node_positions = node_positions
        else:
            node_positions = {k: self._viewer_state.node_positions[k] 
                              for k in node_positions}
            self._viewer_state.node_positions = node_positions

        nx.draw(G, pos=self._viewer_state.node_positions, ax=self.axes,
                with_labels=False, width=weights, 
                node_size=[v * 20 + 20 for v in d.values()], 
                node_color=layer.style.color,
                edgecolors=layer.style.color, 
                linewidths=layer.style.linewidth, 
                alpha=layer.style.alpha)

        self._collection_handler[layer] = {
            'path' : self.axes.collections[-2],
            'line': self.axes.collections[-1]}

        crs = mplc.cursor(self.path_artist(layer), hover=2)

        @crs.connect("add")
        def _node_labels(sel):
            if sel.index < len(G.nodes):
                label = list(G.nodes)[sel.index]
                sel.annotation.set_text(label)

    def _on_visual_change(self, value=None):
        if len(self.axes.collections) == 0 or len(self._collection_handler) == 0:
            return

        layer = self.state.layer

        self.path_artist(layer).set_visible(self.state.visible)
        self.line_artist(layer).set_visible(self.state.visible)

        for artist in [self.path_artist(layer), self.line_artist(layer)]:
            artist.set_visible(self.state.visible)
            artist.set_zorder(self.state.zorder)

            artist.set_edgecolor(layer.style.color)
            artist.set_facecolor(layer.style.color)
            artist.set_alpha(layer.style.alpha)

        self.redraw()

    def _on_attribute_change(self, value=None):
        layer = self.state.layer
        self._remove_layer(layer)

        self._make_graph()
        self.redraw()

    def _on_layout_changed(self, layout):
        self._selected_layout = layout.lower()
        self.remove()
        self._make_graph(reset=True)
        self.redraw()

    def clear(self):
        if len(self.axes.collections) == 0:
            return

        layer = self.state.layer

        self.path_artist(layer).set_visible(False)
        self.line_artist(layer).set_visible(False)

    def _remove_layer(self, layer):
        if layer not in self._collection_handler:
            return

        self._collection_handler[layer]['path'].remove()
        self._collection_handler[layer]['line'].remove()

        del self._collection_handler[layer]

    def remove(self):
        for coll in [x for x in self.axes.collections]:
            coll.remove()

        for txt in [x for x in self.axes.texts]:
            txt.remove()

        self._collection_handler = {}

    def redraw(self):
        self.axes.figure.canvas.draw_idle()

    def update(self):
        self._on_attribute_change()
        self._on_visual_change()
