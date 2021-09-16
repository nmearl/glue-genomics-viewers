from matplotlib.axes._base import _TransformedBoundsLocator
import numpy as np
from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer

from ...data import BedgraphData
from ...subsets import GenomicRangeSubsetState

from .layer_style_editor import GenomeTrackLayerStyleEditor
from .options_widget import GenomeTrackOptionsWidget
from ..layer_artist import GenomeProfileLayerArtist, GenomeLoopLayerArtist
from ..state import GenomeTrackState

__all__ = ['GenomeTrackViewer']


@decorate_all_methods(defer_draw)
class GenomeTrackViewer(MatplotlibDataViewer):

    LABEL = 'Genome Track Viewer'

    _layer_style_widget_cls = GenomeTrackLayerStyleEditor
    _options_cls = GenomeTrackOptionsWidget
    _state_cls = GenomeTrackState

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super().__init__(session, parent=parent, state=state)
        self._layer_artist_container.on_changed(self.reflow_tracks)

    def get_data_layer_artist(self, layer=None, layer_state=None):
        cls = GenomeProfileLayerArtist if isinstance(layer, BedgraphData) else GenomeLoopLayerArtist
        result = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        result.state.add_callback('zorder', self.reflow_tracks)
        result.state.add_callback('visible', self.reflow_tracks)
        return result

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        data = layer.data if layer else None
        cls = GenomeProfileLayerArtist if isinstance(data, BedgraphData) else GenomeLoopLayerArtist
        result = self.get_layer_artist(cls, layer=layer, layer_state=layer_state)
        result.state.add_callback('zorder', self.reflow_tracks)
        result.state.add_callback('visible', self.reflow_tracks)
        return result

    def apply_roi(self, roi, override_mode=None):

        if len(self.layers) == 0:
            return

        x = roi.to_polygon()[0]
        chr = self.state.chr
        if not chr.startswith('chr'):
            chr = 'chr' + chr
        start, end = min(x), max(x)
        state = GenomicRangeSubsetState(chr, start, end)
        self.apply_subset_state(state, override_mode=override_mode)

    def reflow_tracks(self, *args):
        """
        Reorder each track top->bottom sorted by zorder, removing any gaps of non-visible tracks.
        """
        axes = {}
        for artist in self._layer_artist_container.artists:
            if not artist.state.visible:
                continue
            axes[artist.track_axes] = min(axes.get(artist.track_axes, np.inf), artist.zorder)

        track_cnt = len(axes)
        height = 0.9 / track_cnt
        for i, ax in enumerate(sorted(axes, key=axes.get)):
            bounds = _TransformedBoundsLocator([0, i / track_cnt, 1, height], ax.axes.transAxes)
            ax.set_axes_locator(bounds)