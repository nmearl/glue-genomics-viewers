import os

from glue.core import DataCollection, Data
from glue.app.qt import GlueApplication
from ..data import BedgraphData, BedPeData
import numpy as np
from glue_genomics_viewers.heatmap.data_viewer import HeatmapViewer
from glue.viewers.table.qt import TableViewer
from glue_genomics_viewers.genome_track.qt import GenomeTrackViewer
from glue_genomics_viewers.heatmap.heatmap_coords import HeatmapCoords

import pandas as pd

def df_to_data(obj,label=None):
    result = Data(label=label)
    for c in obj.columns:
        result.add_component(obj[c], str(c))
    return result

def classify(row):
    if row['state'].startswith('Tss'):
        val = 'Promoter'
    elif row['state'].startswith('Enh'):
        val = 'Enhancer'
    else:
        val = 'Other'
    return val

def demo():


    from .qt import setup

    setup()

    base_dir = os.environ.get('GLUEGENES_DEMO_DIR', '/Users/jfoster/Desktop/JAX/TestData')
    bedgraph = f'{base_dir}/minji/MCF10A_CTCF_ChIA-PET_Rep1_coverage_ENCFF614DRY.chr3.bedgraph'
    bedpe = f'{base_dir}/minji/MCF10A_CTCF_ChIA-PET_Rep1_loops_ENCFF310MTX.chr3.bedpe'
    #bedgraph = '/Users/jfoster/Desktop/sep17-demo-data/mm10_coverage_M.bedgraph'
    tadfile = f'{base_dir}/atac_rna/Test_TAD.mm10Lifted.bed'
    #tad_data = pd.read_csv(tadfile,names=['chr','start','end','num','name'],sep='\t')
    
    enhancer_file = f'{base_dir}/minji_loops/Enhancers_and_Promoters.bed'
    #enhancer_data = pd.read_csv(enhancer_file,names=['chr','start','end','state'],usecols=['chr','start','end','state'],sep='\t')
    #enhancer_data = enhancer_data[enhancer_data['chr']=='chr3']
    #enhancer_data['major_states'] =  enhancer_data.apply(classify,axis=1)
    #yo = BedgraphData(bedgraph)
    #yo.engine.index()
    
    #yo = BedPeData(bedpe)
    #yo.engine.index()

    
    df_counts = pd.read_csv(f'{base_dir}/three_bears/three_bears_liver_rnaseq_matrix_counts.txt', sep='\t')
    counts_data = np.array(df_counts)
    
    gene_numbers = [int(x[7:]) for x in df_counts.index.values]  # Not general
    # Cast as int, not string for performance reasons
    gene_array = np.outer(gene_numbers, np.ones(df_counts.shape[1])).astype('int')
    
    experiment_id = [int(x[5:]) for x in df_counts.columns]
    experiment_array = np.broadcast_to(experiment_id,df_counts.shape).astype('int')
    
    gene_labels = np.array(gene_numbers) #df_counts.index is proper, but these are way too long
    exp_labels = np.array(experiment_id) #df_counts.columns is proper, but a bit too long
    
    d1 = Data(counts=counts_data, 
             gene_ids=gene_array, 
             exp_ids=experiment_array,
             label='gene_expression',
              coords=HeatmapCoords(n_dim=2, x_axis_ticks=exp_labels, y_axis_ticks=gene_labels, labels=['Experiment ID','Gene ID']))
    df_metadata = pd.read_csv(f'{base_dir}/three_bears/three_bears_liver_rnaseq_matrix_metadata.txt', sep='\t')#.set_index(metadata_index)
    df_metadata.columns = df_metadata.columns.str.lower()  # For consistency
    
    df_metadata['orsam_id'] = [int(x[5:]) for x in df_metadata['barcode']]
    
    d2 = df_to_data(df_metadata,label='rnaseq_metadata')

    
    df_gene_table = pd.read_csv(f'{base_dir}/three_bears/three_bears_liver_rnaseq_geneInfo.txt', sep='\t').set_index('gene.id')
    df_gene_table['gene_ids'] = [int(x[7:]) for x in df_gene_table.index.values]
    df_gene_table['chr'] = 'chr'+df_gene_table['chr'].astype(str)
    df_gene_table['start'] = df_gene_table['start']*100_000
    df_gene_table['end'] = df_gene_table['end']*100_000
    df_gene_table['middle'] = df_gene_table['middle']*100_000
    d_gene = df_to_data(df_gene_table,label="gene_metadata")

    dc = DataCollection([
        d1,
        d2,
        #d_gene,
        BedgraphData(bedgraph,label='CTCF_ChIA-PET_coverage'),
        #BedgraphData(bedgraph,label='Moredata'),
        BedPeData(bedpe,label='CTCF_ChIA-PET_loops'),
    ])
    #dc['Chromatin State'] = enhancer_data
    ga = GlueApplication(dc)
    dc[0].join_on_key(dc[1],'exp_ids','orsam_id')
    #dc[0].join_on_key(dc[2],'gene_ids','gene_ids')

    #scatter = ga.new_data_viewer(HeatmapViewer)
    #scatter.add_data(d1)
    
    #metadata = ga.new_data_viewer(TableViewer)
    #metadata.add_data(d2)

    t = ga.new_data_viewer(GenomeTrackViewer)
    t.add_data(dc[2])
    t.state.chr = '3'
    t.state.start = 3828283
    t.state.end = 3831057

    ga.start()

if __name__ == "__main__":
    demo()