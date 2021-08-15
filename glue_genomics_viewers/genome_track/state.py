import numpy as np

from glue.core import BaseData, Subset

from echo import delay_callback
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)
from glue.core.state_objects import (StateAttributeLimitsHelper,
                                     StateAttributeHistogramHelper)
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.utils import defer_draw, datetime64_to_mpl
from glue.utils.decorators import avoid_circular

__all__ = ['GenomeTrackState']

class GenomeTrackState(MatplotlibDataViewerState):
    """
    Encapsulates all state for a Genome Track Viewer
    """
    chr = DDCProperty(docstring='The Chromosome to view')
    start = DDCProperty(docstring="Left edge of the window")
    end = DDCProperty(docstring="Right edge of the window")

    # TODO: Include a configurable list of tracks. For now hardcode


class GenomeTrackLayerState(MatplotlibLayerState):

    _cache = None

    def reset_cache(self, *args):
        self._cache = None

    @property
    def viewer_state(self):
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state):
        self._viewer_state = viewer_state

    def recalculate_plot_data(self):

        if isinstance(self.layer, Subset):
            data = self.layer.data
            subset_state = self.layer.subset_state
        else:
            data = self.layer
            subset_state = None