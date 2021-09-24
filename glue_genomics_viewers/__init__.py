"""
This should really by in the heatmap module
"""

def setup():
    from .heatmap.data_viewer import HeatmapViewer  # noqa
    from .heatmap.cluster_tool import ClusterTool # noqa
    #from .heatmap.heatmap_coords import HeatmapCoords #noqa
    #from .genome_track_yo.qt import GenomeTrackViewer
    from glue.config import qt_client
    qt_client.add(HeatmapViewer)
    #qt_client.add(GenomeTrackViewer)
