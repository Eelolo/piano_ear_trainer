"""Виджет виртуальной клавиатуры фортепиано."""

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPalette, QPen
from PySide6.QtWidgets import QWidget

from piano_ear_trainer.data import PIANO_NOTES, Note


class PianoKeyboard(QWidget):
    """Виджет клавиатуры фортепиано с 88 клавишами."""

    # Сигнал при нажатии клавиши
    note_clicked = Signal(Note)

    # Соотношения размеров клавиш
    WHITE_KEY_RATIO = 6.0  # Соотношение высота/ширина белой клавиши
    BLACK_KEY_WIDTH_RATIO = 0.6  # Ширина чёрной относительно белой
    BLACK_KEY_HEIGHT_RATIO = 0.65  # Высота чёрной относительно белой
    LABEL_HEIGHT = 70  # Высота области для подписей октав

    # Цвета
    WHITE_KEY_COLOR = QColor(255, 255, 255)
    WHITE_KEY_HOVER = QColor(230, 230, 230)
    BLACK_KEY_COLOR = QColor(30, 30, 30)
    BLACK_KEY_HOVER = QColor(60, 60, 60)
    BORDER_COLOR = QColor(100, 100, 100)
    LABEL_COLOR = QColor(80, 80, 80)

    # Названия октав и их начальные MIDI-номера
    OCTAVE_LABELS = [
        (24, "Контр-\nоктава"),  # C1
        (36, "Большая\nоктава"),  # C2
        (48, "Малая\nоктава"),  # C3
        (60, "1-я\nоктава"),  # C4
        (72, "2-я\nоктава"),  # C5
        (84, "3-я\nоктава"),  # C6
        (96, "4-я\nоктава"),  # C7
        (108, "5-я\nоктава"),  # C8
    ]

    def __init__(
        self, parent: QWidget | None = None, show_octave_labels: bool = False
    ) -> None:
        super().__init__(parent)

        self._notes = PIANO_NOTES
        self._hovered_note: Note | None = None
        self._key_rects: dict[int, QRect] = {}  # MIDI -> QRect
        self._white_key_count = sum(1 for n in self._notes if not n.is_black_key)
        self._show_octave_labels = show_octave_labels

        # Для глиссандо (проведение с зажатой кнопкой)
        self._is_dragging = False
        self._last_dragged_note: Note | None = None

        # Включаем отслеживание мыши для hover эффекта
        self.setMouseTracking(True)

        # Политика размеров - расширяемся по горизонтали, фиксированы по вертикали
        from PySide6.QtWidgets import QSizePolicy

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Минимальная ширина
        self.setMinimumWidth(400)

    def _calculate_layout(self) -> None:
        """Вычисляет расположение клавиш на основе текущего размера виджета."""
        self._key_rects.clear()

        # Вычисляем размеры клавиш на основе ширины, сохраняя пропорции
        width = self.width()

        white_key_width = width / self._white_key_count
        white_key_height = white_key_width * self.WHITE_KEY_RATIO  # Сохраняем пропорцию
        black_key_width = int(white_key_width * self.BLACK_KEY_WIDTH_RATIO)
        black_key_height = int(white_key_height * self.BLACK_KEY_HEIGHT_RATIO)

        # Расставляем белые клавиши
        white_x = 0
        for note in self._notes:
            if not note.is_black_key:
                rect = QRect(
                    int(white_x), 0, int(white_key_width), int(white_key_height)
                )
                self._key_rects[note.midi_number] = rect
                white_x += white_key_width

        # Чёрные клавиши (поверх белых)
        white_x = 0
        for i, note in enumerate(self._notes):
            if not note.is_black_key:
                if i + 1 < len(self._notes) and self._notes[i + 1].is_black_key:
                    black_note = self._notes[i + 1]
                    black_x = int(white_x + white_key_width - black_key_width / 2)
                    rect = QRect(black_x, 0, black_key_width, black_key_height)
                    self._key_rects[black_note.midi_number] = rect
                white_x += white_key_width

    def resizeEvent(self, event) -> None:
        """Пересчитываем layout при изменении размера."""
        # Вычисляем правильную высоту на основе ширины
        white_key_width = self.width() / self._white_key_count
        keys_height = int(white_key_width * self.WHITE_KEY_RATIO)

        # Добавляем место для подписей если нужно
        target_height = keys_height
        if self._show_octave_labels:
            target_height += self.LABEL_HEIGHT

        # Устанавливаем фиксированную высоту для сохранения пропорций
        if self.height() != target_height:
            self.setFixedHeight(target_height)

        self._calculate_layout()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        """Отрисовка клавиатуры."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Сначала рисуем белые клавиши
        for note in self._notes:
            if not note.is_black_key:
                self._draw_key(painter, note)

        # Потом чёрные клавиши (поверх)
        for note in self._notes:
            if note.is_black_key:
                self._draw_key(painter, note)

        # Рисуем подписи октав если включено
        if self._show_octave_labels:
            self._draw_octave_labels(painter)

    def _draw_octave_labels(self, painter: QPainter) -> None:
        """Рисует подписи октав под клавиатурой."""
        white_key_width = self.width() / self._white_key_count
        keys_height = int(white_key_width * self.WHITE_KEY_RATIO)

        # Настройка шрифта — крупный и жирный
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        # Используем системный цвет текста (адаптируется к теме ОС)
        text_color = self.palette().color(QPalette.ColorRole.WindowText)
        painter.setPen(QPen(text_color))

        for i, (midi_number, label) in enumerate(self.OCTAVE_LABELS):
            # Находим позицию клавиши
            rect = self._key_rects.get(midi_number)
            if rect is None:
                continue

            # Рисуем маркер (линию от клавиши к подписи)
            marker_x = rect.x() + rect.width() // 2
            painter.drawLine(marker_x, keys_height, marker_x, keys_height + 8)

            # Определяем выравнивание и позицию в зависимости от положения
            if i == 0:  # Первая (субконтроктава) - выравнивание влево
                text_rect = QRect(
                    0,
                    keys_height + 12,
                    rect.x() + rect.width() + 40,
                    self.LABEL_HEIGHT - 12,
                )
                alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            elif i == len(self.OCTAVE_LABELS) - 1:  # Последняя (5-я) - вправо
                text_x = rect.x() - 80
                text_width = self.width() - text_x - 2  # 2px отступ от края
                text_rect = QRect(
                    text_x, keys_height + 12, text_width, self.LABEL_HEIGHT - 12
                )
                alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
            else:  # Остальные - по центру
                text_rect = QRect(
                    rect.x() - 30,
                    keys_height + 12,
                    rect.width() + 60,
                    self.LABEL_HEIGHT - 12,
                )
                alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop

            painter.drawText(text_rect, alignment, label)

    def _draw_key(self, painter: QPainter, note: Note) -> None:
        """Рисует одну клавишу."""
        rect = self._key_rects.get(note.midi_number)
        if rect is None:
            return

        is_hovered = self._hovered_note == note

        if note.is_black_key:
            color = self.BLACK_KEY_HOVER if is_hovered else self.BLACK_KEY_COLOR
        else:
            color = self.WHITE_KEY_HOVER if is_hovered else self.WHITE_KEY_COLOR

        painter.setPen(QPen(self.BORDER_COLOR, 1))
        painter.setBrush(QBrush(color))
        painter.drawRect(rect)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Обработка движения мыши (hover эффект и глиссандо)."""
        note = self._get_note_at_pos(event.position().toPoint())

        # Hover эффект
        if note != self._hovered_note:
            self._hovered_note = note
            self.update()

        # Глиссандо: при зажатой кнопке воспроизводим новые ноты
        if self._is_dragging and note is not None and note != self._last_dragged_note:
            self._last_dragged_note = note
            self.note_clicked.emit(note)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Обработка клика мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            note = self._get_note_at_pos(event.position().toPoint())
            if note is not None:
                self._last_dragged_note = note
                self.note_clicked.emit(note)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Обработка отпускания кнопки мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._last_dragged_note = None

    def leaveEvent(self, event) -> None:
        """Мышь покинула виджет."""
        self._hovered_note = None
        self._is_dragging = False
        self._last_dragged_note = None
        self.update()

    def _get_note_at_pos(self, pos) -> Note | None:
        """Находит ноту по позиции клика."""
        # Сначала проверяем чёрные клавиши (они сверху)
        for note in self._notes:
            if note.is_black_key:
                rect = self._key_rects.get(note.midi_number)
                if rect and rect.contains(pos):
                    return note

        # Затем белые
        for note in self._notes:
            if not note.is_black_key:
                rect = self._key_rects.get(note.midi_number)
                if rect and rect.contains(pos):
                    return note

        return None

    def sizeHint(self):
        """Рекомендуемый размер виджета."""
        from PySide6.QtCore import QSize

        return QSize(800, 150)
