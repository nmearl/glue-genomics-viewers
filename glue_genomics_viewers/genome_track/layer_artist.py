from glue.viewers.matplotlib.layer_artist import MatplotlibLayerArtist
from glue.utils import defer_draw
from matplotlib.text import Text


from .state import GenomeTrackLayerState


class GenomeTrackLayerArtist(MatplotlibLayerArtist):
    _layer_state_cls = GenomeTrackLayerState

    def __init__(self, axes, viewer_state, layer_state=None, layer=None):

        super().__init__(axes, viewer_state, layer_state=layer_state, layer=layer)

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._handle_state_change)
        self.state.add_global_callback(self._handle_state_change)

    def _handle_state_change(self, force=False, **kwargs):
        if (
            self._viewer_state.chr is None or
            self._viewer_state.start is None or
            self._viewer_state.end is None or
            self.state.layer is None
        ):
            return

        changed = set() if force else self.pop_changed_properties()

        if force or any(prop in changed for prop in ('chr', 'start', 'end')):
            self._update_plot_data(reset=force)

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder', 'visible')):
            self._update_visual_attributes()

    def _update_plot_data(self, force=False):
        # Prepare new data

        self._update_artists()
        self._update_visual_attributes()
        pass

    @defer_draw
    def _update_artists(self):

        msg = "%s %s %s %s" % (self._viewer_state.chr, self._viewer_state.start, self._viewer_state.end, self.state.layer)
        if not self.mpl_artists:
            artist = Text(0.5, 0.5, msg)
            self.mpl_artists.append(artist)
            self.axes.add_artist(artist)
        else:
            self.mpl_artists[-1].set_text(msg)

        self.redraw()

    @defer_draw
    def _update_visual_attributes(self):

        if not self.enabled:
            return

        for mpl_artist in self.mpl_artists:
            mpl_artist.set_visible(self.state.visible)
            mpl_artist.set_zorder(self.state.zorder)

        self.redraw()

    @defer_draw
    def update(self):
        self.state.reset_cache()
        self._update_plot_data(force=True)
        self.redraw()
