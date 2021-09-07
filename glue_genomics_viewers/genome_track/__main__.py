from glue.core import DataCollection
from glue.app.qt import GlueApplication
from ..data import BedgraphData, BedPeData

def demo():


    from .qt import setup

    setup()

    bedgraph = '/Volumes/GoogleDrive/My Drive/JAX-Test-Data/minji/MCF10A_CTCF_ChIA-PET_Rep1_coverage_ENCFF614DRY.chr3.bedgraph'
    bedpe = '/Volumes/GoogleDrive/My Drive/JAX-Test-Data/minji/MCF10A_CTCF_ChIA-PET_Rep1_loops_ENCFF310MTX.chr3.bedpe'

    dc = DataCollection([
        BedgraphData(bedgraph),
        BedPeData(bedpe),
    ])
    ga = GlueApplication(dc)
    ga.start()


if __name__ == "__main__":
    demo()