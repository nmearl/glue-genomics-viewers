from glue.core.coordinates import IdentityCoordinates, Coordinates
import numpy as np

class HeatmapCoords(IdentityCoordinates):

	def __init__(self, n_dim=2, x_axis_ticks=[], y_axis_ticks=[], labels=[]):
		super().__init__(n_dim=n_dim)
		
		self.x_axis_ticks = x_axis_ticks
		self.y_axis_ticks = y_axis_ticks
		
		#self.np_x_axis_ticks = np.array(x_axis_ticks) #Can we just use this?
		#self.np_y_axis_ticks = np.array(y_axis_ticks)

		self._labels = labels
		
	def get_tick_labels(self, axis_name):
		if (axis_name == 'Pixel Axis 1 [x]') or (axis_name == 'World 1') or (axis_name == 'Experiment Id'):
			return self.x_axis_ticks
		elif (axis_name == 'Pixel Axis 0 [y]') or (axis_name == 'World 0') or (axis_name == 'Gene Id'):
			return self.y_axis_ticks
			
	#def pixel_to_world_values(self, *args):
	#	# This should take N arguments (where N is the number of dimensions
	#	# in your dataset) and assume these are 0-based pixel coordinates,
	#	# then return N world coordinates with the same shape as the input.
	#	# We would need to be able to interpolate to treat these are real WCS coords...
	#	#print(args)
	#	#print(self.x_axis_ticks)
	#	print("Inside pixel to world values")
	#	assert len(args) == 2
	#	y_out = [self.y_axis_ticks[y] for y in args[1]] #y might be backwards?
	#	#print(y_out)
	#	x_out = [self.x_axis_ticks[x] for x in args[0]]
	#	#print(x_out)
	#	return tuple([x_out,y_out])
		
	#def world_to_pixel_values(self, *args):
	#	# This should take N arguments (where N is the number of dimensions
	#	# in your dataset) and assume these are 0-based pixel coordinates,
	#	# then return N world coordinates with the same shape as the input.
	#	
	#	y_pix = np.where(self.np_y_axis_ticks==args[0])[0] #just get first match #Need to iterate through args[0] as above...
	#	x_pix = np.where(self.np_x_axis_ticks==args[1])[0] 
	#	return tuple(y_pix, x_pix)
	
	@property
	def world_axis_names(self):
		return self._labels
