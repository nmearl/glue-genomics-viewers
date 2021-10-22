from glue.core.state import SubsetState
from glue.core.contracts import contract
from glue.core.exceptions import IncompatibleAttribute

import numpy as np

class GenomicMulitRangeSubsetState(SubsetState):
    """A subset state which is multiple GenomicRangeSubsetStates
    
    Currently this assumes that we define multiple GenomeRangeSubsetStates
    only as OR states from the Table Viewer; we should make this more
    general and probably this should be built as a bunch of GenomicRangeSubsetStates
    
    """
    def __init__(self, subsets):
        self._subsets = subsets
        self.chroms = []
        self.starts = []
        self.ends = []
        for subset in subsets: #These should only be GenomicRangeSubsetState
            self.chroms.append(subset.chrom)
            self.starts.append(subset.start)
            self.ends.append(subset.end)

    def extent(self):
        return self.chroms[0], min(self.starts), max(self.ends)

    def copy(self):
        return GenomicMulitRangeSubsetState(self._subsets)
            
    @contract(data='isinstance(Data)', view='array_view')
    def to_mask(self, data, view=None):
        """
        This assumes that the data we wish to express
        this subset on has certain components to wit either:
        chr, start, end: generic BED file regions
        chr, genome_position: a 3D GNOME model
        """
        result = np.zeros(data.components[0].shape)
        try:
            for c,s,e in zip(self.chroms, self.starts, self.ends):
                result |= (data['chr'] == c) & (data['start'] >= s) & (data['start'] <= e)
        except:
            try:
                for c,s,e in zip(self.chroms, self.starts, self.ends):
                    result |= (data['chr'] == c) & (data['genome_position'] >= s) & (data['genome_position'] <= e)
            except:
                raise IncompatibleAttribute()            
        if view is not None:
            result = result[view]
        return result



class GenomicRangeSubsetState(SubsetState):
    """A subset state defined by a (chrom, start, end) triple.

    The subset is inclusive of the endpoints.
    """
    def __init__(self, chrom, start, end):
        self.chrom = chrom
        self.start = start
        self.end = end

    def extent(self):
        return self.chrom, self.start, self.end

    def copy(self):
        return GenomicRangeSubsetState(self.chrom, self.start, self.end)

    
    @contract(data='isinstance(Data)', view='array_view')
    def to_mask(self, data, view=None):
        """
        This assumes that the data we wish to express
        this subset on has certain components to wit either:
        chr, start, end: generic BED file regions
        chr, genome_position: a 3D GNOME model
        """
        try:
            result = (data['chr'] == self.chrom) & (data['start'] >= self.start) & (data['start'] <= self.end)
        except:
            try:
                result = (data['chr'] == self.chrom) & (data['genome_position'] >= self.start) & (data['genome_position'] <= self.end)
            except:
                raise IncompatibleAttribute()
        if view is not None:
            result = result[view]
        return result


    def to_index_list(self, data):
        """
        This assumes that the data we wish to express
        this subset on has certain components to wit either:
        chr, start, end: generic BED file regions
        chr, genome_position: a 3D GNOME model
        """
        try:
            result = (data['chr'] == self.chrom) & (data['start'] >= self.start) & (data['start'] <= self.end)
        except:
            try:
                result = (data['chr'] == self.chrom) & (data['genome_position'] >= self.start) & (data['genome_position'] <= self.end)
            except:
                raise IncompatibleAttribute()
        return result

