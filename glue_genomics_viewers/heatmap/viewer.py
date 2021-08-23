import os

from glue.core.subset import roi_to_subset_state
from glue.core.coordinates import Coordinates, LegacyCoordinates
from glue.core.coordinate_helpers import dependent_axes

from glue.viewers.scatter.layer_artist import ScatterLayerArtist
from glue.viewers.image.layer_artist import ImageLayerArtist, ImageSubsetLayerArtist
from glue.viewers.image.compat import update_image_viewer_state

from glue.viewers.image.frb_artist import imshow
from glue.viewers.image.composite_array import CompositeArray

__all__ = ['MatplotlibHeatmapMixin']


EXTRA_FOOTER = """
# Set tick label size - for now tick_params (called lower down) doesn't work
# properly, but these lines won't be needed in future.
ax.coords[{x_att_axis}].set_ticklabel(size={x_ticklabel_size})
ax.coords[{y_att_axis}].set_ticklabel(size={y_ticklabel_size})
""".strip()


class MatplotlibHeatmapMixin(object):

    def setup_callbacks(self):
        self._wcs_set = False
        self._changing_slice_requires_wcs_update = None
        self.axes.set_adjustable('datalim')
        #self.state.add_callback('x_att') #We do need these callbacks... see ._on_attribute_change() here http://docs.glueviz.org/en/stable/customizing_guide/matplotlib_qt_viewer.html Used to be _set_wcs
        #self.state.add_callback('y_att')
        #self.state.add_callback('slices') #probably we don't need this
        #self.state.add_callback('reference_data') # probably we don't need this
        self.axes._composite = CompositeArray()
        self.axes._composite_image = imshow(self.axes, self.axes._composite, aspect='auto',
                                            origin='lower', interpolation='nearest')
    def bad_update_x_ticklabel(self, *event):
        # We need to overload this here for WCSAxes
        if hasattr(self, '_wcs_set') and self._wcs_set and self.state.x_att is not None:
            axis = self.state.reference_data.ndim - self.state.x_att.axis - 1
        else:
            axis = 0
        #self.axes.coords[axis].set_ticklabel(size=self.state.x_ticklabel_size) #self.axes is an astropy thing. Setting WCS=False gets here, which crashes
        self.redraw()

    def bad_update_y_ticklabel(self, *event):
        # We need to overload this here for WCSAxes
        if hasattr(self, '_wcs_set') and self._wcs_set and self.state.y_att is not None:
            axis = self.state.reference_data.ndim - self.state.y_att.axis - 1
        else:
            axis = 1
        #self.axes.coords[axis].set_ticklabel(size=self.state.y_ticklabel_size)
        self.redraw()

    def _update_axes(self, *args):

        if self.state.x_att_world is not None:
            self.state.x_axislabel = self.state.x_att_world.label

        if self.state.y_att_world is not None:
            self.state.y_axislabel = self.state.y_att_world.label

        self.axes.figure.canvas.draw_idle()

    def add_data(self, data):
        result = super(MatplotlibHeatmapMixin, self).add_data(data)
        return result


    def apply_roi(self, roi, override_mode=None):

        # Force redraw to get rid of ROI. We do this because applying the
        # subset state below might end up not having an effect on the viewer,
        # for example there may not be any layers, or the active subset may not
        # be one of the layers. So we just explicitly redraw here to make sure
        # a redraw will happen after this method is called.
        self.redraw()

        if len(self.layers) == 0:
            return

        if self.state.x_att is None or self.state.y_att is None or self.state.reference_data is None:
            return

        subset_state = roi_to_subset_state(roi,
                                           x_att=self.state.x_att,
                                           y_att=self.state.y_att)

        self.apply_subset_state(subset_state, override_mode=override_mode)

    def _scatter_artist(self, axes, state, layer=None, layer_state=None):
        if len(self._layer_artist_container) == 0:
            raise Exception("Can only add a scatter plot overlay once an image is present")
        return ScatterLayerArtist(axes, state, layer=layer, layer_state=None)

    def get_data_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = self._scatter_artist
        else:
            cls = ImageLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    def get_subset_layer_artist(self, layer=None, layer_state=None):
        if layer.ndim == 1:
            cls = self._scatter_artist
        else:
            cls = ImageSubsetLayerArtist
        return self.get_layer_artist(cls, layer=layer, layer_state=layer_state)

    @staticmethod
    def update_viewer_state(rec, context):
        return update_image_viewer_state(rec, context)

    def show_crosshairs(self, x, y):

        if getattr(self, '_crosshairs', None) is not None:
            self._crosshairs.remove()

        self._crosshairs, = self.axes.plot([x], [y], '+', ms=12,
                                           mfc='none', mec='#d32d26',
                                           mew=1, zorder=100)

        self.axes.figure.canvas.draw_idle()

    def hide_crosshairs(self):
        if getattr(self, '_crosshairs', None) is not None:
            self._crosshairs.remove()
            self._crosshairs = None
            self.axes.figure.canvas.draw_idle()

    def _script_header(self):

        imports = []
        imports.append('import matplotlib.pyplot as plt')
        imports.append('from glue.viewers.matplotlib.mpl_axes import init_mpl')
        imports.append('from glue.viewers.image.composite_array import CompositeArray')
        imports.append('from glue.viewers.image.frb_artist import imshow')

        script = ""
        script += "fig, ax = init_mpl(wcs=True)\n"
        script += "ax.set_aspect('{0}')\n".format(self.state.aspect)

        script += '\ncomposite = CompositeArray()\n'
        script += "image = imshow(ax, composite, origin='lower', interpolation='nearest', aspect='{0}')\n\n".format(self.state.aspect)

        dindex = self.session.data_collection.index(self.state.reference_data)

        script += "ref_data = data_collection[{0}]\n".format(dindex)

        ref_coords = self.state.reference_data.coords

        if hasattr(ref_coords, 'wcs'):
            script += "ax.reset_wcs(slices={0}, wcs=ref_data.coords.wcs)\n".format(self.state.wcsaxes_slice)
        elif hasattr(ref_coords, 'wcsaxes_dict'):
            raise NotImplementedError()
        else:
            imports.append('from glue.viewers.image.viewer import get_identity_wcs')
            script += "ax.reset_wcs(slices={0}, wcs=get_identity_wcs(ref_data.ndim))\n".format(self.state.wcsaxes_slice)

        script += "# for the legend\n"
        script += "legend_handles = []\n"
        script += "legend_labels = []\n"
        script += "legend_handler_dict = dict()\n\n"

        return imports, script

    def _script_footer(self):
        imports, script = super(MatplotlibImageMixin, self)._script_footer()
        options = dict(x_att_axis=0 if self.state.x_att is None else self.state.reference_data.ndim - self.state.x_att.axis - 1,
                       y_att_axis=1 if self.state.y_att is None else self.state.reference_data.ndim - self.state.y_att.axis - 1,
                       x_ticklabel_size=self.state.x_ticklabel_size,
                       y_ticklabel_size=self.state.y_ticklabel_size)
        return [], EXTRA_FOOTER.format(**options) + os.linesep * 2 + script
