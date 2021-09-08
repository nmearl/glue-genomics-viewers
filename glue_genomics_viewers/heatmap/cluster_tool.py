from glue.config import viewer_tool
from glue.viewers.common.tool import Tool
import seaborn as sns
import pandas as pd
from glue.core.component_id import ComponentID, PixelComponentID
from glue.core import Data
from glue.core.decorators import clear_cache
from glue.core.message import NumericalDataChangedMessage

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

		new_xticks = [orig_xticks[i] for i in new_col_ind]
		new_yticks = [orig_yticks[i] for i in new_row_ind]

		data.coords.x_axis_ticks = np.array(new_xticks)
		data.coords.y_axis_ticks = np.array(new_yticks)
		
		for component in data.components:
			if not isinstance(component, PixelComponentID):  # Ignore pixel components
				data.update_components({component:pd.DataFrame(data.get_data(component)).iloc[new_row_ind,new_col_ind]})
		
		# We might need to update join_on_key mappings after we re-order things
		# for other_dataset, key_join in data._key_joins.items():
		#	print(f'other_dataset = {other_dataset}')
		#	print(f'key_join  = {key_join}')
		#	cid, cid_other = key_join
		#	data.join_on_key(other_dataset, cid, cid_other)
		
		#In theory this is already done in update_components
		#if data.hub is not None:
		#	msg = NumericalDataChangedMessage(data)
		#	data.hub.broadcast(msg)

		#if other_dataset.hub is not None:
		#	msg = NumericalDataChangedMessage(other_dataset)
		#	data.hub.broadcast(msg)

		#In theory this is already done in update_components
		#for subset in data.subsets:
		#	print(subset)
		#	clear_cache(subset.subset_state.to_mask)

		#for subset in other_dataset.subsets:
		#	clear_cache(subset.subset_state.to_mask)

		
		self.viewer._update_axes()

	def close(self):
		"""
		If we wanted to make clustering not permanently change the dataset we could
		cache the original data and then restore it on close.
		"""
		pass
