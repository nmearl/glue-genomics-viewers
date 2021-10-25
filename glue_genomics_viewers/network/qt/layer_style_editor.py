import os

from echo.qt import autoconnect_callbacks_to_qt, connect_checkable_button
from glue.utils.qt import load_ui
from qtpy.QtWidgets import QCheckBox, QVBoxLayout, QWidget


class NetworkLayerStateWidget(QWidget):

    def __init__(self, layer_artist):
        super().__init__()

        # self.checkbox = QCheckBox('Fill markers')
        # layout = QVBoxLayout()
        # layout.addWidget(self.checkbox)
        # self.setLayout(layout)

        # self.layer_state = layer_artist.state
        # connect_checkable_button(self.layer_state, 'fill', self.checkbox)
