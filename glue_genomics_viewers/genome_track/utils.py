import math
from matplotlib.ticker import ScalarFormatter


class PanTrackerMixin:
    """
    Helper class that tracks drag events when using the pan/zoom mode in the matplotlib toolbar.

    The `panning` holds whether the user is currently panning+zooming, and the `on_pan_end` method
    (a no-op that can be overloaded) is called immediately after a pan+zoom ends.

    This can be used to skip expensive operations during pan+zoom, to keep that interaction fluid.
    """
    def init_pan_tracking(self, axes):
        self.panning = False
        self.__axes = axes
        axes.figure.canvas.mpl_connect('button_press_event', self._on_press)
        axes.figure.canvas.mpl_connect('button_release_event', self._on_release)

    def _on_press(self, event=None, force=False):
        try:
            mode = self.__axes.figure.canvas.toolbar.mode
        except AttributeError:  # pragma: nocover
            return
        self.panning = mode == 'pan/zoom'

    def _on_release(self, event=None):
        was_panning = self.panning
        self.panning = False

        if was_panning:
            self.on_pan_end()

    def on_pan_end(self):
        pass


class GenomeTrackFormatter(ScalarFormatter):
    """Format numbers in kdb/Mbp, instead of scientific notation"""
    chrom = ''

    def format_data(self, value):
        e = math.floor(math.log10(abs(value)))
        s = round(value / 10**e, 10)
        exponent = self._format_maybe_minus_and_locale("%d", e)
        if e == 3:
            suffix = ' kbp'
        elif e == 4:
            suffix = ' kbp'
            s *= 10
        elif e == 5:
            suffix = ' kbp'
            s *= 100
        elif e == 6:
            suffix = ' Mbp'
        elif e == 7:
            suffix = ' Mbp'
            s *= 10
        elif e == 8:
            suffix = ' Mbp'
            s *= 100
        else:
            suffix = f'e{exponent}'

        significand = self._format_maybe_minus_and_locale(
            "%d" if s % 1 == 0 else "%1.10f", s)
        if e == 0:
            return significand
        return f"{significand}{suffix}"

    def get_offset(self):
        if len(self.locs) == 0:
            return ''

        s = ''
        if self.orderOfMagnitude or self.offset:
            offsetStr = ''
            sciNotStr = ''
            if self.offset:
                print(self.offset)
                offsetStr = self.format_data(self.offset)
                if self.offset > 0:
                    offsetStr = '+' + offsetStr
            if self.orderOfMagnitude:
                if self.orderOfMagnitude == 3:
                    sciNotStr = ' kbp'
                elif self.orderOfMagnitude == 4:
                    sciNotStr = '10 kbp'
                elif self.orderOfMagnitude == 5:
                    sciNotStr = '100 kbp'
                elif self.orderOfMagnitude == 6:
                    sciNotStr = ' Mbp'
                elif self.orderOfMagnitude == 7:
                    sciNotStr = '10 Mbp'
                elif self.orderOfMagnitude == 8:
                    sciNotStr = '100 Mbp'
                else:
                    sciNotStr = f'1e{self.orderOfMagnitude}'
            s = ''.join((sciNotStr, offsetStr))

        return f'{self.chrom}:{self.fix_minus(s)}'

