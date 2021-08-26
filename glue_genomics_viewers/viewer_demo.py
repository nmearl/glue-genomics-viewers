import pandas as pd
import numpy as np
from glue.core import Data, DataCollection
from glue.app.qt.application import GlueApplication
from glue_genomics_viewers.heatmap.data_viewer import HeatmapViewer
from heatmap.heatmap_coords import HeatmapCoords

		
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
	
	d = Data(counts=counts_data, 
			 gene_ids=gene_array, 
			 exp_ids=experiment_array,
			 label='gene_expression',
		 	 coords=HeatmapCoords(n_dim=2, x_axis_ticks=exp_labels, y_axis_ticks=gene_labels, labels=['Experiment ID','Gene ID']))
			 
	print(d.coords)
	dc = DataCollection([d])
	ga = GlueApplication(dc)
	
	#qglue(gene_exp=counts_data)
	
	scatter = ga.new_data_viewer(HeatmapViewer)
	scatter.add_data(d)
	
	# show the GUI
	ga.start()
