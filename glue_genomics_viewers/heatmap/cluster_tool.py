from glue.config import viewer_tool
from glue.viewers.common.tool import Tool
import seaborn as sns
import pandas as pd
from glue.core.component_id import ComponentID, PixelComponentID
from glue.core import Data
from .heatmap_coords import HeatmapCoords
import numpy as np

@viewer_tool
class ClusterTool(Tool):

	icon = 'glue_tree'
	tool_id = 'heatmap:cluster'
	action_text = 'Apply hierarchical clustering to matrix'
	tool_tip = 'Apply hierarchical clustering to matrix'
	shortcut = 'Ctrl+K'

	def __init__(self, viewer):
		super(ClusterTool, self).__init__(viewer)

	def activate(self):
		"""
		We use seaborn.clustermap to cluster the data and then
		use the indices returned from this method to update the data components and
		update the Coords for the data object
		
		TODO: could/should also spawn a dendrogram showing connectedness
		"""
		data = self.viewer.state.reference_data	
		
		g = sns.clustermap(data['counts']) #This should not be hard coded... I guess it should come from state
		new_row_ind = g.dendrogram_row.reordered_ind
		new_col_ind = g.dendrogram_col.reordered_ind
		
		orig_xticks = data.coords.x_axis_ticks
		orig_yticks = data.coords.y_axis_ticks
		orig_labels = data.coords._labels

		new_xticks = np.array(orig_xticks[np.array(new_col_ind).argsort()])
		new_yticks = np.array(orig_yticks[np.array(new_row_ind).argsort()])

		self.viewer.state.reference_data.coords = HeatmapCoords(n_dim=2, x_axis_ticks=new_xticks, y_axis_ticks= new_yticks,labels=orig_labels)
		
		for component in data.components:
			if not isinstance(component, PixelComponentID):  # Ignore pixel components
				data.update_components({component:pd.DataFrame(data.get_data(component)).iloc[new_row_ind,new_col_ind]})
		self.viewer._update_axes()

	def close(self):
		"""
		If we wanted to make clustering not permanently change the dataset we could
		cache the original data and then restore it on close.
		"""
		pass
