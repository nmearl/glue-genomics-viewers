#This would ideally be in qt subfolder, but I cannot get that to work with 
#setup.cfg properly (seems to double-import qt)

from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer
from glue.viewers.scatter.qt.layer_style_editor import ScatterLayerStyleEditor
from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.utils import defer_draw, decorate_all_methods


from .qt.layer_style_editor import HeatmapLayerStyleEditor
from .qt.layer_style_editor_subset import HeatmapLayerSubsetStyleEditor
from .layer_artist import HeatmapLayerArtist, HeatampSubsetLayerArtist
from .qt.options_widget import HeatmapOptionsWidget
from .qt.mouse_mode import RoiClickAndDragMode

# Import the mouse mode to make sure it gets registered
#from .qt.contrast_mouse_mode import ContrastBiasMode  # noqa
#from .qt.pixel_selection_mode import PixelSelectionTool  # noqa

from .viewer import MatplotlibHeatmapMixin
from .state import HeatmapViewerState

__all__ = ['HeatmapViewer']

@decorate_all_methods(defer_draw)
class HeatmapViewer(MatplotlibHeatmapMixin, MatplotlibDataViewer):

    LABEL = 'Heatmap'
    _default_mouse_mode_cls = RoiClickAndDragMode
    _layer_style_widget_cls = {HeatmapLayerArtist: HeatmapLayerStyleEditor,
                               HeatampSubsetLayerArtist: HeatmapLayerSubsetStyleEditor,
                               ScatterLayerArtist: ScatterLayerStyleEditor}
    _state_cls = HeatmapViewerState
    _options_cls = HeatmapOptionsWidget

    allow_duplicate_data = True

    # NOTE: _data_artist_cls and _subset_artist_cls are not defined - instead
    #       we override get_data_layer_artist and get_subset_layer_artist for
    #       more advanced logic.

    tools = ['select:xrange', 'select:yrange', 'image:contrast_bias', 'heatmap:cluster']

    def __init__(self, session, parent=None, state=None):
        MatplotlibDataViewer.__init__(self, session, wcs=False, parent=parent, state=state)
        MatplotlibHeatmapMixin.setup_callbacks(self)

    def closeEvent(self, *args):
        super(HeatmapViewer, self).closeEvent(*args)
        if self.axes._composite_image is not None:
            self.axes._composite_image.remove()
            self.axes._composite_image = None
