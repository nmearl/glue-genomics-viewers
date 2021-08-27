from glue.core.coordinates import IdentityCoordinates, Coordinates

class HeatmapCoords(IdentityCoordinates):

	def __init__(self, n_dim=2, x_axis_ticks=[], y_axis_ticks=[], labels=[]):
		super().__init__(n_dim=n_dim)
		
		self.x_axis_ticks = x_axis_ticks
		self.y_axis_ticks = y_axis_ticks
		
		self._labels = labels
		
	def get_tick_labels(self, axis_name):
		if (axis_name == 'Pixel Axis 1 [x]') or (axis_name == 'World 1') or (axis_name == 'Experiment Id'):
			return self.x_axis_ticks
		elif (axis_name == 'Pixel Axis 0 [y]') or (axis_name == 'World 0') or (axis_name == 'Gene Id'):
			return self.y_axis_ticks
			
	
	@property
	def world_axis_names(self):
		return self._labels
