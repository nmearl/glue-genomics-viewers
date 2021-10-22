import pandas as pd
import numpy as np

from glue.core import Data
from glue.viewers.matplotlib.layer_artist import MatplotlibLayerArtist
from glue.utils import defer_draw
from matplotlib.patches import Arc

from .state import GenomeTrackLayerState
from .utils import PanTrackerMixin, GenomeTrackFormatter


class GenomeTrackLayerArtist(MatplotlibLayerArtist, PanTrackerMixin):
    _layer_state_cls = GenomeTrackLayerState

    def __init__(self, axes, viewer_state, layer_state=None, layer=None):

        x_min, x_max = viewer_state.x_min, viewer_state.x_max
        self.track_key = id(layer.data)
        self.track_axes = self._setup_track_axes(axes, self.track_key, viewer_state)
        super().__init__(axes, viewer_state, layer_state=layer_state, layer=layer)
        self.init_pan_tracking(axes)

        # View limits get reset to (0, 1) during setup somewhere, restore.
        viewer_state.x_min = x_min
        viewer_state.x_max = x_max

        # Watch for changes in the viewer state which would require the
        # layers to be redrawn
        self._viewer_state.add_global_callback(self._handle_state_change)
        self.state.add_global_callback(self._handle_state_change)

    def on_pan_end(self):
        self._handle_state_change(force=True)

    @staticmethod
    def _setup_track_axes(axes, key, viewer_state):
        """Configure a child Axes representing `layer` as a single track."""
        if key in viewer_state.tracks:
            return viewer_state.tracks[key]

        axes.get_yaxis().set_visible(False)
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.spines['left'].set_visible(False)

        xlim = axes.get_xlim()
        result = axes.inset_axes([0, .1 * len(viewer_state.tracks) + .3, 1, .1])
        axes.get_shared_x_axes().join(result, axes)
        axes.set_xlim(*xlim)

        result.get_xaxis().set_visible(False)
        result.get_shared_x_axes().join(axes, result)
        result.spines['right'].set_visible(False)
        result.spines['top'].set_visible(False)
        viewer_state.tracks[key] = result

        fmt = GenomeTrackFormatter()
        fmt.set_powerlimits((-3, 3))
        axes.xaxis.set_major_formatter(fmt)
        return result

    def _handle_state_change(self, force=False, **kwargs):
        if (
            self.panning or
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
        self.axes.xaxis.get_major_formatter().chrom = f'chr{self._viewer_state.chr}'
        self._update_artists()
        self._update_visual_attributes()

    @defer_draw
    def update(self):
        self.state.reset_cache()
        self._update_plot_data(force=True)
        self.redraw()

    def _update_visual_attributes(self):
        if not self.enabled:
            return

        if isinstance(self.layer, Data):
            self.track_axes.set_visible(self.state.visible)


class GenomeProfileLayerArtist(GenomeTrackLayerArtist):

    @defer_draw
    def _update_artists(self):
        df: pd.DataFrame = self.state.viz_data
        if df.empty:
            x = np.array([])
            y = np.array([])
        else:
            x = np.vstack([df.start, df.start, df.stop, df.stop]).T.ravel()
            y = np.vstack([df.value * 0, df.value, df.value, df.value * 0]).T.ravel()

        if not self.mpl_artists:
            artist = self.track_axes.fill_between(x, y)
            self.mpl_artists.append(artist)
        else:
            self.mpl_artists[-1].set_verts([np.column_stack([x, y])])

        if isinstance(self.layer, Data) and x.size > 0:
            self.track_axes.set_ylim(y.min(), y.max())

        self.redraw()

    @defer_draw
    def _update_visual_attributes(self):
        super()._update_visual_attributes()

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
        for artist in self.mpl_artists:
            artist.remove()
        self.mpl_artists = []

        df: pd.DataFrame = self.state.viz_data
        if df.empty:
            return

        df['diameter'] = (df.start2 + df.end2) / 2. - (df.start1 + df.end1) / 2.

        for _, rec in df.iterrows():
            center = (rec.start1 + rec.end1 + rec.start2 + rec.end2) / 4.
            height = rec.diameter
            width = np.sqrt(min(rec.value, 10)) / 2.
            arc = Arc(
                (center, 0), rec.diameter,
                height, 0, 0, 180, lw=width, alpha=0.3
            )

            self.track_axes.add_patch(arc)
            self.mpl_artists.append(arc)

        if isinstance(self.layer, Data):
            self.track_axes.autoscale(axis='y', enable=True)
            rng = df.diameter.max() / 2
            domain = self.track_axes.get_xlim()
            domain = (domain[1] - domain[0]) / 2
            self.track_axes.set_ylim(0, min(domain, rng))

        self.redraw()

    @defer_draw
    def _update_visual_attributes(self):
        super()._update_visual_attributes()

        if not self.enabled:
            return

        for mpl_artist in self.mpl_artists:
            mpl_artist.set_visible(self.state.visible)
            mpl_artist.set_zorder(self.state.zorder)
            mpl_artist.set_alpha(self.state.alpha)
            mpl_artist.set_facecolor(self.state.color)
            mpl_artist.set_edgecolor(self.state.color)

        self.redraw()
