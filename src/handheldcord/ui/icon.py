"""The app icon, drawn in code so the repository needs no binary assets."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter

ACCENT = "#14b8a6"


def render_icon(size: int = 256) -> QImage:
    """Needs a QGuiApplication, because drawing text needs the font database."""
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(ACCENT))
    margin = size * 0.0625
    radius = size * 0.22
    painter.drawRoundedRect(QRectF(margin, margin, size - 2 * margin, size - 2 * margin), radius, radius)
    font = QFont("Segoe UI")
    font.setPixelSize(int(size * 0.42))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "HC")
    painter.end()
    return image
