import pandas as pd

from glue.core import Subset

from echo import delay_callback
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty)
from glue.utils.decorators import avoid_circular
from glue.utils import defer_draw, decorate_all_methods

from ..data import BedPeData
from ..subsets import GenomicRangeSubsetState

__all__ = ['GenomeTrackState']


@decorate_all_methods(defer_draw)
class GenomeTrackState(MatplotlibDataViewerState):
    """
    Encapsulates all state for a Genome Track Viewer
    """
    chr = DDCProperty(docstring='The Chromosome to view')
    start = DDCProperty(docstring="Left edge of the window")
    end = DDCProperty(docstring="Right edge of the window")
    loop_count = DDCProperty(docstring="Number of loops to display")
    show_annotations = DDCProperty(default=True, docstring="Show Annotations?")

    def __init__(self, **kwargs):
        super().__init__()

        self.add_callback('start', self.update_view_to_range)
        self.add_callback('end', self.update_view_to_range)

        self.add_callback('x_min', self.update_range_to_view)
        self.add_callback('x_max', self.update_range_to_view)

        self.chr = '3'
        self.start = 100_000 #3_000_000 
        self.end = 500_000 # 27_000_000#
        self.loop_count = 100

        self.tracks = {}

    @avoid_circular
    def update_view_to_range(self, *args):
        with delay_callback(self, 'x_min', 'x_max'):
            self.x_min = self.start
            self.x_max = self.end

    @avoid_circular
    def update_range_to_view(self, *args):
        with delay_callback(self, 'start', 'end'):
            self.start = self.x_min
            self.end = self.x_max


class GenomeTrackLayerState(MatplotlibLayerState):

    _cache = None, None

    def reset_cache(self, *args):
        self._cache = None, None

    @property
    def viewer_state(self) -> GenomeTrackState:
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state: GenomeTrackState):
        self._viewer_state = viewer_state

    @property
    def viz_data(self) -> pd.DataFrame:
        key = self.viewer_state.chr, int(max(self.viewer_state.start, 0)), int(max(self.viewer_state.end, 0)), self.viewer_state.loop_count
        if key == self._cache[0]:
            return self._cache[1]
        chr, start, end, loop_count = key

        
        if isinstance(self.layer, Subset):
            data = self.layer.data
            subset_state = self.layer.subset_state
            if not isinstance(subset_state, GenomicRangeSubsetState):
                try:
                    subset_state = self.layer.subset_state.to_genome_range()
                except AttributeError:
                    pass
            #else:
                
        else:
            data = self.layer
            subset_state = None
        if isinstance(data, BedPeData):
            df = data.profile(chr, start, end, target=loop_count, required_endpoints='both', subset_state=subset_state)
        else:
            df = data.profile(chr, start, end, subset_state=subset_state)

        self._cache = key, df
        return df
