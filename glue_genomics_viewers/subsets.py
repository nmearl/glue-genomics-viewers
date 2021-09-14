from glue.core.state import SubsetState
from glue.core.contracts import contract

import numpy as np

class GenomicMulitRangeSubsetState(SubsetState):
    """A subset state which is multiple GenomicRangeSubsetStates
    
    Currently this assumes that we define multiple GenomeRangeSubsetStates
    only as OR states from the Table Viewer; we should make this more
    general. 
    
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
        print(f'Making a subset from {subsets}')
        print(f'self.chroms = {self.chroms}')
        print(f'self.starts = {self.starts}')

            
    def copy(self):
        return GenomicMulitRangeSubsetState(self._subsets)
            
    #@contract(data='isinstance(Data)', view='array_view')
    #def to_mask(self, data, view=None):
    #    """
    #    This is specific to tabular data, and we should make it more general
    #    """
    #    x = data
    #    chrom_code = np.where(x['chr'].categories ==self.chrom)[0][0]
    #    result = (x['chr'].codes == chrom_code) & (x['start'] >= self.start) & (x['start'] <= self.end)
    #    if view is not None:
    #        result = result[view]
    #    return result



class GenomicRangeSubsetState(SubsetState):
    """A subset state defined by a (chrom, start, end) triple.

    The subset is inclusive of the endpoints.
    """
    def __init__(self, chrom, start, end):
        self.chrom = chrom
        self.start = start
        self.end = end

    def copy(self):
        return GenomicRangeSubsetState(self.chrom, self.start, self.end)

    
    @contract(data='isinstance(Data)', view='array_view')
    def to_mask(self, data, view=None):
        """
        This is specific to tabular data, and we should make it more general
        """
        #print(view)
        x = data#[view]
        #print("Inside my custom to_mask method...")
        #print(x)
        #print(self.chrom)
        #print(self.start)
        #print(self.end)
        chrom_code = np.where(x['chr'].categories ==self.chrom)[0][0]
        result = (x['chr'].codes == chrom_code) & (x['start'] >= self.start) & (x['start'] <= self.end)
        if view is not None:
            result = result[view]
        #print(result)
        return result


    def to_index_list(self, data):
        """
        This is specific to tabular data, and we should make it more general.
        """
        #print("Inside my custom to_index_list method...")
        result = (data['chr'] == self.chrom) & (data['start'] >= self.start) & (data['start'] <= self.start)
        #print(result)
        return result
        #chr_code = np.where(data['chr'].categories ==self.chrom)[0][0]
        
        #x = data[data['chr']==self.chrom] #Ignore view for now...
                 
        #In theory this should require that 


    # Todo: attempt to define to_mask and/or to_index_list? These can be expensive...