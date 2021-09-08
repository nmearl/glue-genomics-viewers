from glue.core.state import SubsetState


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

    # Todo: attempt to define to_mask and/or to_index_list? These can be expensive...