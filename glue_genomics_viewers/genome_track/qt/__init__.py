from .data_viewer import GenomeTrackViewer  # noqa


def setup():
    from glue.config import qt_client
    qt_client.add(GenomeTrackViewer)
