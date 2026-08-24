# -*- coding: utf-8 -*-
"""
Temperature trend widget.
Rolling 30-minute plot of heater / rectal / skin temperatures
(fed by MSGID 0x25 temperature telemetry frames).
"""

from collections import deque
import time

import numpy as np
import pyqtgraph as pg

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class TempWidget(QWidget):
    """
    Temperature history plot (30-minute rolling window, 0.5Hz frames).
    """

    WINDOW_S = 30 * 60          # rolling window length

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.plot = pg.PlotWidget()
        self.plot.setBackground('#101018')
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.plot.setLabel('left', '温度', units='℃')
        self.plot.setLabel('bottom', '时间', units='s')
        self.plot.addLegend(offset=(10, 5), labelTextSize='8pt')
        self.plot.setTitle('温度监测（板/肛/皮）', color='#e0e0e0', size='10pt')

        from PyQt5.QtGui import QFont
        for axis in ('left', 'bottom'):
            self.plot.getAxis(axis).setTextPen('#b0b0b0')
            self.plot.getAxis(axis).setFont(QFont('Microsoft YaHei UI', 8))

        self.curves = {
            'heater': self.plot.plot(pen=pg.mkPen('#4dd0e1', width=2), name='加热板'),
            'rect':   self.plot.plot(pen=pg.mkPen('#ffb74d', width=2), name='肛温'),
            'skin':   self.plot.plot(pen=pg.mkPen('#81c784', width=2), name='体表'),
        }

        layout.addWidget(self.plot)

        # (t, heater, rect, skin) history
        self.hist = deque(maxlen=1200)   # 0.5Hz x 30min = 900, headroom
        self.t0 = None

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh)
        self.timer.start(1000)

    def add_temp(self, t_heater, t_rect, t_skin):
        now = time.time()
        if self.t0 is None:
            self.t0 = now
        self.hist.append((now - self.t0, t_heater, t_rect, t_skin))

    def _refresh(self):
        if not self.hist:
            return
        cutoff = (self.hist[-1][0]) - self.WINDOW_S
        data = [row for row in self.hist if row[0] >= cutoff]
        arr = np.array(data)
        x = arr[:, 0]
        for i, key in enumerate(('heater', 'rect', 'skin'), start=1):
            # skip unplugged channels (0) so they do not squash the y-axis
            y = arr[:, i]
            mask = y > 0.5
            if mask.any():
                self.curves[key].setData(x[mask], y[mask])
            else:
                self.curves[key].setData([], [])

    def clear(self):
        self.hist.clear()
        self.t0 = None
        for c in self.curves.values():
            c.setData([], [])
