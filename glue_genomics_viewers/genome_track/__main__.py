from glue.core import DataCollection, Data
from glue.app.qt import GlueApplication
from ..data import BedgraphData, BedPeData
import pandas as pd
def demo():


    from .qt import setup

    setup()

    bedgraph = '/Volumes/GoogleDrive/My Drive/JAX-Test-Data/minji/MCF10A_CTCF_ChIA-PET_Rep1_coverage_ENCFF614DRY.chr3.bedgraph'
    bedpe = '/Volumes/GoogleDrive/My Drive/JAX-Test-Data/minji/MCF10A_CTCF_ChIA-PET_Rep1_loops_ENCFF310MTX.chr3.bedpe'
    #bedgraph = '/Users/jfoster/Desktop/sep17-demo-data/mm10_coverage_M.bedgraph'
    tadfile = '/Users/jfoster/Desktop/JAX/Test Data/atac_rna/Gaulton_TAD.mm10Lifted.bed'
    tad_data = pd.read_csv(tadfile,names=['chr','start','end','num','name'],sep='\t')
    #yo = BedgraphData(bedgraph)
    #yo.engine.index()
    dc = DataCollection([
        BedgraphData(bedgraph),
        BedPeData(bedpe),
    ])
    dc['mm10_TAD'] = tad_data
    ga = GlueApplication(dc)
    ga.start()


if __name__ == "__main__":
    demo()