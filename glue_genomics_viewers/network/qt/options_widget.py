import os

from echo.qt import autoconnect_callbacks_to_qt, connect_checkable_button
from glue.utils.qt import load_ui
from qtpy.QtWidgets import QCheckBox, QVBoxLayout, QWidget


class NetworkViewerStateWidget(QWidget):

    def __init__(self, viewer_state=None, session=None):
        super().__init__()

        self.ui = load_ui('viewer_state.ui', self,
                          directory=os.path.dirname(__file__))

        self.viewer_state = viewer_state
        self._connections = autoconnect_callbacks_to_qt(self.viewer_state, self.ui)
