def setup():
    from .heatmap.data_viewer import HeatmapViewer  # noqa
    from glue.config import qt_client
    qt_client.add(HeatmapViewer)
