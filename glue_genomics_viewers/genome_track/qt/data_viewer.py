from glue.utils import defer_draw, decorate_all_methods
from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer
from .layer_style_editor import GenomeTrackLayerStyleEditor
from .options_widget import GenomeTrackOptionsWidget
from ..layer_artist import GenomeTrackLayerArtist
from ..state import GenomeTrackState


__all__ = ['GenomeTrackViewer']


@decorate_all_methods(defer_draw)
class GenomeTrackViewer(MatplotlibDataViewer):

    LABEL = 'Genome Track Viewer'

    _layer_style_widget_cls = GenomeTrackLayerStyleEditor
    _options_cls = GenomeTrackOptionsWidget

    _state_cls = GenomeTrackState
    _data_artist_cls = GenomeTrackLayerArtist
    _subset_artist_cls = GenomeTrackLayerArtist

    large_data_size = 2e7

    tools = ['select:xrange']

    def __init__(self, session, parent=None, state=None):
        super().__init__(session, parent=parent, state=state)
