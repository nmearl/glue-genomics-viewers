import matplotlib.pyplot as plt
from glue.config import qt_client
from glue.viewers.common.qt.data_viewer import DataViewer

from .layer_artist import NetworkLayerArtist
from .qt import NetworkLayerStateWidget, NetworkViewerStateWidget
from .state import NetworkViewerState
from glue.viewers.common.qt.toolbar import BasicToolbar


class NetworkDataViewer(DataViewer):

    LABEL = 'Network viewer'
    _state_cls = NetworkViewerState
    _data_artist_cls = NetworkLayerArtist
    _subset_artist_cls = NetworkLayerArtist
    _options_cls = NetworkViewerStateWidget
    _layer_style_widget_cls = NetworkLayerStateWidget
    _toolbar_cls = BasicToolbar
    tools = ['select:circle', 'select:polygon', 'select:rectangle', 'mpl:home',
             'mpl:pan', 'mpl:zoom']

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


qt_client.add(NetworkDataViewer)
