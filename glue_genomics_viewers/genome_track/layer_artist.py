import pandas as pd
import numpy as np
from glue.viewers.matplotlib.layer_artist import MatplotlibLayerArtist
from glue.utils import defer_draw
from matplotlib.patches import Arc

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
        if force or any(prop in changed for prop in ('chr', 'start', 'end', 'loop_count')):
            self._update_plot_data(force=force)

        if force or any(prop in changed for prop in ('alpha', 'color', 'zorder', 'visible')):
            self._update_visual_attributes()

    def _update_plot_data(self, force=False):
        # Prepare new data
        self._update_artists()
        self._update_visual_attributes()

    @defer_draw
    def update(self):
        self.state.reset_cache()
        self._update_plot_data(force=True)
        self.redraw()


class GenomeProfileLayerArtist(GenomeTrackLayerArtist):

    @defer_draw
    def _update_artists(self):
        df: pd.DataFrame = self.state.viz_data
        if df.empty:
            return

        x = np.vstack([df.start, df.start, df.stop, df.stop]).T.ravel()
        y = np.vstack([df.value * 0, df.value, df.value, df.value * 0]).T.ravel()

        if not self.mpl_artists:
            artist = self.axes.fill_between(x, y)
            self.mpl_artists.append(artist)
        else:
            self.mpl_artists[-1].set_verts([np.column_stack([x, y])])

        self.redraw()

    @defer_draw
    def _update_visual_attributes(self):

        if not self.enabled:
            return

        for mpl_artist in self.mpl_artists:
            mpl_artist.set_visible(self.state.visible)
            mpl_artist.set_zorder(self.state.zorder)
            mpl_artist.set_alpha(self.state.alpha)
            mpl_artist.set_facecolors(self.state.color)

        self.redraw()

class GenomeLoopLayerArtist(GenomeTrackLayerArtist):

    @defer_draw
    def _update_artists(self):
        df: pd.DataFrame = self.state.viz_data
        if df.empty:
            return

        for artist in self.mpl_artists:
            artist.remove()

        self.mpl_artists = []
        df['diameter'] = (df.start2 + df.end2) / 2. - (df.start1 + df.end1) / 2.

        for _, rec in df.iterrows():
            center = (rec.start1 + rec.end1 + rec.start2 + rec.end2) / 4.
            height = rec.diameter
            width = np.sqrt(min(rec.value, 10)) / 2.
            arc = Arc(
                (center, 0), rec.diameter,
                height, 0, 0, 180, lw=width, alpha=0.3
            )

            self.axes.add_patch(arc)
            self.mpl_artists.append(arc)

        self.redraw()

    @defer_draw
    def _update_visual_attributes(self):

        if not self.enabled:
            return

        for mpl_artist in self.mpl_artists:
            mpl_artist.set_visible(self.state.visible)
            mpl_artist.set_zorder(self.state.zorder)
            mpl_artist.set_alpha(self.state.alpha)
            mpl_artist.set_facecolor(self.state.color)
            mpl_artist.set_edgecolor(self.state.color)

        self.redraw()
