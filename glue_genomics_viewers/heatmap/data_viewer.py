#This would ideally be in qt subfolder, but I cannot get that to work with 
#setup.cfg properly (seems to double-import qt)

from glue.viewers.matplotlib.qt.data_viewer import MatplotlibDataViewer
from glue.viewers.scatter.qt.layer_style_editor import ScatterLayerStyleEditor
from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.viewers.image.qt.layer_style_editor import ImageLayerStyleEditor
from glue.viewers.image.qt.layer_style_editor_subset import ImageLayerSubsetStyleEditor
from glue.viewers.image.layer_artist import ImageLayerArtist, ImageSubsetLayerArtist
from glue.viewers.image.qt.options_widget import ImageOptionsWidget
from glue.viewers.image.qt.mouse_mode import RoiClickAndDragMode
from glue.viewers.image.state import ImageViewerState
from glue.utils import defer_draw, decorate_all_methods

# Import the mouse mode to make sure it gets registered
#from .qt.contrast_mouse_mode import ContrastBiasMode  # noqa
#from .qt.pixel_selection_mode import PixelSelectionTool  # noqa

from .viewer import MatplotlibImageMixin

__all__ = ['ImageHeatmapViewer']


@decorate_all_methods(defer_draw)
class HeatmapViewer(MatplotlibImageMixin, MatplotlibDataViewer):

    LABEL = 'Heatmap'
    _default_mouse_mode_cls = RoiClickAndDragMode
    _layer_style_widget_cls = {ImageLayerArtist: ImageLayerStyleEditor,
                               ImageSubsetLayerArtist: ImageLayerSubsetStyleEditor,
                               ScatterLayerArtist: ScatterLayerStyleEditor}
    _state_cls = ImageViewerState
    _options_cls = ImageOptionsWidget

    allow_duplicate_data = True

    # NOTE: _data_artist_cls and _subset_artist_cls are not defined - instead
    #       we override get_data_layer_artist and get_subset_layer_artist for
    #       more advanced logic.

    tools = ['select:rectangle', 'select:xrange',
             'select:yrange', 'image:point_selection', 'image:contrast_bias']

    def __init__(self, session, parent=None, state=None):
        MatplotlibDataViewer.__init__(self, session, wcs=True, parent=parent, state=state)
        MatplotlibImageMixin.setup_callbacks(self)

    def closeEvent(self, *args):
        super(HeatmapViewer, self).closeEvent(*args)
        if self.axes._composite_image is not None:
            self.axes._composite_image.remove()
            self.axes._composite_image = None
