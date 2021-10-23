from glue.core.subset_group import GroupedSubset
import matplotlib.pyplot as plt
import numpy as np
from glue.viewers.common.qt.data_viewer import DataViewer
from glue.viewers.common.qt.toolbar import BasicToolbar
from glue.core.subset import roi_to_subset_state, ElementSubsetState

from .layer_artist import NetworkLayerArtist
from .qt import NetworkLayerStateWidget, NetworkViewerStateWidget
from .state import NetworkViewerState

__all__ = ['NetworkDataViewer']


class NetworkDataViewer(DataViewer):

    LABEL = 'Network viewer'
    _state_cls = NetworkViewerState
    _data_artist_cls = NetworkLayerArtist
    _subset_artist_cls = NetworkLayerArtist
    _options_cls = NetworkViewerStateWidget
    _layer_style_widget_cls = NetworkLayerStateWidget
    _toolbar_cls = BasicToolbar
    tools = ['mpl:home', 'mpl:pan', 'mpl:zoom', 'select:circle', 
             'select:polygon', 'select:rectangle']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure that a new figure object is created upon data viewer creation
        _, self.axes = plt.subplots()
        self.setCentralWidget(self.axes.figure.canvas)

    @property
    def central_widget(self):
        return self.axes.figure

    def apply_roi(self, roi):
        layer = self.selected_layer

        if isinstance(layer.state.layer, GroupedSubset):
            return

        positions = np.array(list(layer._viewer_state.node_positions.values()))
        names = np.array(list(layer._viewer_state.node_positions.keys()))
        mask = roi.contains(positions[:, 0], positions[:, 1])

        if names[mask].size == 0:
            return

        true_mask = np.isin(layer.state.layer['peak'], names[mask])
        subset_state = ElementSubsetState(true_mask, layer.state.layer)
        self.apply_subset_state(subset_state)

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self.axes, self.state, layer=layer, layer_state=layer_state)

