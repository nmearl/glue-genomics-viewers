import pandas as pd
import numpy as np
from glue.core import Data, DataCollection
from glue.app.qt.application import GlueApplication
from glue_genomics_viewers.heatmap.data_viewer import HeatmapViewer
from glue.viewers.table.qt import TableViewer
from heatmap.heatmap_coords import HeatmapCoords


def df_to_data(obj,label=None):
    result = Data(label=label)
    for c in obj.columns:
        result.add_component(obj[c], str(c))
    return result

        
if __name__ == "__main__":
#from glue import qglue

    df_counts = pd.read_csv('three_bears_liver_rnaseq_matrix_counts.txt', sep='\t')
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
             
    print(d1.coords)
    
    df_metadata = pd.read_csv('three_bears_liver_rnaseq_matrix_metadata.txt', sep='\t')#.set_index(metadata_index)
    df_metadata.columns = df_metadata.columns.str.lower()  # For consistency
    
    df_metadata['orsam_id'] = [int(x[5:]) for x in df_metadata['barcode']]
    
    d2 = df_to_data(df_metadata,label='rnaseq_metadata')
    
    dc = DataCollection([d1, d2])
    ga = GlueApplication(dc)
    
    dc[0].join_on_key(dc[1],'exp_ids','orsam_id')
    #qglue(gene_exp=counts_data)
    
    scatter = ga.new_data_viewer(HeatmapViewer)
    scatter.add_data(d1)
    
    metadata = ga.new_data_viewer(TableViewer)
    metadata.add_data(d2)
    
    # show the GUI
    ga.start()
