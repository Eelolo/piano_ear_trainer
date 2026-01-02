"""Главное окно приложения."""

import contextlib
import json
import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from piano_ear_trainer.audio import AudioPlayer
from piano_ear_trainer.data import PIANO_NOTES, Note
from piano_ear_trainer.ui.piano_keyboard import PianoKeyboard


class MainWindow(QMainWindow):
    """Главное окно тренера музыкального слуха."""

    # Путь к файлу сохранения
    SAVE_FILE = Path.home() / ".piano_ear_trainer_record.json"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Piano Ear Trainer")
        self.setMinimumSize(900, 700)
        self._set_app_icon()

        # Аудио плеер
        self._audio_player = AudioPlayer()
        self._current_note: Note | None = None
        self._answered = False  # Флаг: пользователь уже ответил?

        # Счётчики
        self._correct_count = 0
        self._wrong_count = 0
        self._best_streak = self._load_record()  # Загружаем рекорд из файла
        self._current_streak = 0  # Текущая серия правильных подряд

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Заголовок
        title_label = QLabel("Тренер музыкального слуха")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Стек виджетов для переключения между экранами
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # Экран 1: Стартовый экран
        self.start_screen = self._create_start_screen()
        self.stacked_widget.addWidget(self.start_screen)

        # Экран 2: Экран тренировки
        self.training_screen = self._create_training_screen()
        self.stacked_widget.addWidget(self.training_screen)

        # Экран 3: Справка по октавам
        self.octaves_screen = self._create_octaves_screen()
        self.stacked_widget.addWidget(self.octaves_screen)

        # Для возврата с экрана октав
        self._previous_screen: QWidget | None = None

        # Начинаем со стартового экрана
        self.stacked_widget.setCurrentWidget(self.start_screen)

    def _create_start_screen(self) -> QWidget:
        """Создаёт стартовый экран с кнопкой 'Начать'."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Описание
        description = QLabel(
            "Проверьте свой музыкальный слух!\n\n"
            "Вам будет проигрываться нота, а вы должны\n"
            "угадать её на виртуальной клавиатуре фортепиано."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(14)
        description.setFont(desc_font)
        layout.addWidget(description)

        layout.addSpacing(20)

        # Настройки тренировки
        settings_font = QFont()
        settings_font.setPointSize(12)

        # Заголовок октав
        octaves_label = QLabel("Октавы:")
        octaves_label.setFont(settings_font)
        layout.addWidget(octaves_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        # Два столбика октав
        octaves_columns = QHBoxLayout()
        octaves_columns.setSpacing(30)

        left_column = QVBoxLayout()
        left_column.setSpacing(5)
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_column = QVBoxLayout()
        right_column.setSpacing(5)
        right_column.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.octave_checkboxes: dict[int, QCheckBox] = {}
        octave_names = [
            (0, "Субконтроктава"),
            (1, "Контроктава"),
            (2, "Большая октава"),
            (3, "Малая октава"),
            (4, "1-я октава"),
            (5, "2-я октава"),
            (6, "3-я октава"),
            (7, "4-я октава"),
            (8, "5-я октава"),
        ]

        for i, (octave_num, name) in enumerate(octave_names):
            checkbox = QCheckBox(name)
            checkbox.setFont(settings_font)
            # По умолчанию выбрана только 1-я октава (номер 4)
            checkbox.setChecked(octave_num == 4)
            self.octave_checkboxes[octave_num] = checkbox
            if i < 5:
                left_column.addWidget(checkbox)
            else:
                right_column.addWidget(checkbox)

        octaves_columns.addStretch()
        octaves_columns.addLayout(left_column)
        octaves_columns.addLayout(right_column)
        octaves_columns.addStretch()

        layout.addLayout(octaves_columns)

        layout.addSpacing(15)

        # Чекбокс "Использовать диезы"
        self.use_sharps_checkbox = QCheckBox("Использовать диезы (чёрные клавиши)")
        self.use_sharps_checkbox.setFont(settings_font)
        self.use_sharps_checkbox.setChecked(False)  # По умолчанию выключены
        layout.addWidget(
            self.use_sharps_checkbox, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(20)

        # Кнопки
        button_font = QFont()
        button_font.setPointSize(18)

        # Кнопка "Начать"
        self.start_button = QPushButton("Начать")
        self.start_button.setMinimumSize(200, 60)
        self.start_button.setFont(button_font)
        self.start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        # Кнопка "Октавы"
        self.octaves_button_start = QPushButton("Октавы")
        self.octaves_button_start.setMinimumSize(200, 60)
        self.octaves_button_start.setFont(button_font)
        self.octaves_button_start.clicked.connect(self._on_octaves_clicked)
        layout.addWidget(
            self.octaves_button_start, alignment=Qt.AlignmentFlag.AlignCenter
        )

        return screen

    def _create_training_screen(self) -> QWidget:
        """Создаёт экран тренировки."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(15)

        # Счётчик результатов (над клавиатурой, всегда виден)
        self.score_label = QLabel("")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_font = QFont()
        score_font.setPointSize(14)
        self.score_label.setFont(score_font)
        self.score_label.setMinimumHeight(30)
        layout.addWidget(self.score_label)

        # Клавиатура фортепиано (масштабируется с окном, сохраняя пропорции)
        self.keyboard = PianoKeyboard()
        self.keyboard.note_clicked.connect(self._on_keyboard_note_clicked)
        layout.addWidget(self.keyboard)

        # Область статуса (под клавиатурой): "Правильно!" / "Неправильно!"
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(18)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setMinimumHeight(30)
        layout.addWidget(self.status_label)

        # Область для отображения результата (название ноты)
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_font = QFont()
        result_font.setPointSize(16)
        self.result_label.setFont(result_font)
        self.result_label.setMinimumHeight(50)
        layout.addWidget(self.result_label)

        layout.addStretch()

        # Панель управления
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)

        # Кнопка "Повторить"
        self.repeat_button = QPushButton("Повторить")
        self.repeat_button.setMinimumSize(150, 50)
        controls_font = QFont()
        controls_font.setPointSize(14)
        self.repeat_button.setFont(controls_font)
        self.repeat_button.clicked.connect(self._on_repeat_clicked)
        controls_layout.addWidget(self.repeat_button)

        # Кнопка "Следующая нота"
        self.next_button = QPushButton("Следующая нота")
        self.next_button.setMinimumSize(150, 50)
        self.next_button.setFont(controls_font)
        self.next_button.clicked.connect(self._on_next_clicked)
        self.next_button.setEnabled(False)  # Активируется после ответа
        controls_layout.addWidget(self.next_button)

        # Кнопка "Октавы"
        self.octaves_button_training = QPushButton("Октавы")
        self.octaves_button_training.setMinimumSize(150, 50)
        self.octaves_button_training.setFont(controls_font)
        self.octaves_button_training.clicked.connect(self._on_octaves_clicked)
        controls_layout.addWidget(self.octaves_button_training)

        # Кнопка "Завершить"
        self.stop_button = QPushButton("Завершить")
        self.stop_button.setMinimumSize(150, 50)
        self.stop_button.setFont(controls_font)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        controls_layout.addWidget(self.stop_button)

        layout.addLayout(controls_layout)

        return screen

    def _create_octaves_screen(self) -> QWidget:
        """Создаёт экран со справкой по октавам."""
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Октавы фортепиано")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Клавиатура с подписями октав
        self.octaves_keyboard = PianoKeyboard(show_octave_labels=True)
        layout.addWidget(self.octaves_keyboard)

        # Таблица октав
        octaves_info = """
<table style="font-size: 14px; margin: auto;">
<tr><td style="padding: 8px;"><b>Субконтроктава</b></td><td style="padding: 8px;">A0 – B0</td><td style="padding: 8px; color: #888;">(Ля – Си)</td></tr>
<tr><td style="padding: 8px;"><b>Контроктава</b></td><td style="padding: 8px;">C1 – B1</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>Большая октава</b></td><td style="padding: 8px;">C2 – B2</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>Малая октава</b></td><td style="padding: 8px;">C3 – B3</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>1-я октава</b></td><td style="padding: 8px;">C4 – B4</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>2-я октава</b></td><td style="padding: 8px;">C5 – B5</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>3-я октава</b></td><td style="padding: 8px;">C6 – B6</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>4-я октава</b></td><td style="padding: 8px;">C7 – B7</td><td style="padding: 8px; color: #888;">(До – Си)</td></tr>
<tr><td style="padding: 8px;"><b>5-я октава</b></td><td style="padding: 8px;">C8</td><td style="padding: 8px; color: #888;">(До)</td></tr>
</table>
        """
        info_label = QLabel(octaves_info)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        layout.addStretch()

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад")
        self.back_button.setMinimumSize(150, 50)
        back_font = QFont()
        back_font.setPointSize(14)
        self.back_button.setFont(back_font)
        self.back_button.clicked.connect(self._on_back_clicked)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return screen

    def _get_filtered_notes(self) -> list[Note]:
        """Возвращает список нот согласно настройкам."""
        use_sharps = self.use_sharps_checkbox.isChecked()
        selected_octaves = {
            num for num, cb in self.octave_checkboxes.items() if cb.isChecked()
        }

        filtered = []
        for note in PIANO_NOTES:
            # Фильтр по диезам
            if not use_sharps and note.is_black_key:
                continue
            # Фильтр по октавам
            if note.octave.number not in selected_octaves:
                continue
            filtered.append(note)

        return filtered

    def _play_new_note(self) -> None:
        """Воспроизводит новую случайную ноту."""
        filtered_notes = self._get_filtered_notes()

        if not filtered_notes:
            self.status_label.setText("Выберите хотя бы одну октаву!")
            self.result_label.setText("")
            return

        note = random.choice(filtered_notes)
        self._audio_player.play_note(note)
        self._current_note = note
        self._answered = False
        self.status_label.setText("")
        self.status_label.setStyleSheet("")
        self.result_label.setText("Выберите ноту на клавиатуре")
        self.result_label.setStyleSheet("color: #888;")
        self.next_button.setEnabled(False)

    def _on_start_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Начать'."""
        # Сброс счётчиков сессии (рекорд сохраняется)
        self._correct_count = 0
        self._wrong_count = 0
        self._current_streak = 0
        self._update_score_label()
        self.stacked_widget.setCurrentWidget(self.training_screen)
        self._play_new_note()

    def _on_repeat_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Повторить'."""
        # Воспроизводим загаданную ноту, а не последнюю нажатую
        if self._current_note is not None:
            self._audio_player.play_note(self._current_note)

    def _on_next_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Следующая нота'."""
        self._play_new_note()

    def _on_stop_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Завершить'."""
        self._audio_player.stop()
        self.stacked_widget.setCurrentWidget(self.start_screen)

    def _on_octaves_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Октавы'."""
        self._previous_screen = self.stacked_widget.currentWidget()
        self.stacked_widget.setCurrentWidget(self.octaves_screen)

    def _on_back_clicked(self) -> None:
        """Обработчик нажатия кнопки 'Назад'."""
        if self._previous_screen is not None:
            self.stacked_widget.setCurrentWidget(self._previous_screen)
        else:
            self.stacked_widget.setCurrentWidget(self.start_screen)

    def _on_keyboard_note_clicked(self, clicked_note: Note) -> None:
        """Обработчик клика по клавише на клавиатуре."""
        # Если уже ответили — свободный режим, просто воспроизводим
        if self._answered:
            self._audio_player.play_note(clicked_note)
            return

        # Нет загаданной ноты — ничего не делаем
        if self._current_note is None:
            return

        # Проверяем ответ
        is_correct = clicked_note.midi_number == self._current_note.midi_number

        # Звук только при правильном ответе
        if is_correct:
            self._audio_player.play_note(clicked_note)
            self._correct_count += 1
            self._current_streak += 1
            if self._current_streak > self._best_streak:
                self._best_streak = self._current_streak
                self._save_record()  # Сохраняем новый рекорд сразу
            self.status_label.setText("Правильно!")
            self.status_label.setStyleSheet("color: #2ecc71;")  # Зелёный
            self.result_label.setText(self._current_note.full_name)
            self.result_label.setStyleSheet("color: #2ecc71;")  # Зелёный
        else:
            # Неправильный ответ — тишина
            self._wrong_count += 1
            self._current_streak = 0
            self.status_label.setText("Неправильно!")
            self.status_label.setStyleSheet("color: #e74c3c;")  # Красный
            self.result_label.setText(
                f"<span style='color: #2ecc71;'>Правильно: {self._current_note.full_name}</span><br>"
                f"<span style='color: #e74c3c;'>Вы выбрали: {clicked_note.full_name}</span>"
            )
            self.result_label.setStyleSheet("")  # Сброс стиля, используем HTML

        self._answered = True
        self._update_score_label()
        # Активируем кнопку "Следующая нота"
        self.next_button.setEnabled(True)

    def _update_score_label(self) -> None:
        """Обновляет отображение счёта (всегда видим)."""
        total = self._correct_count + self._wrong_count
        percent = int(self._correct_count / total * 100) if total > 0 else 0

        self.score_label.setText(
            f"<span style='color: #2ecc71;'>✓ {self._correct_count}</span> | "
            f"<span style='color: #e74c3c;'>✗ {self._wrong_count}</span> | "
            f"{percent}% | "
            f"Серия: {self._current_streak} | "
            f"Рекорд: {self._best_streak}"
        )

    def _load_record(self) -> int:
        """Загружает рекорд из файла."""
        try:
            if self.SAVE_FILE.exists():
                data = json.loads(self.SAVE_FILE.read_text())
                return data.get("best_streak", 0)
        except (json.JSONDecodeError, OSError):
            pass
        return 0

    def _save_record(self) -> None:
        """Сохраняет рекорд в файл."""
        with contextlib.suppress(OSError):
            self.SAVE_FILE.write_text(json.dumps({"best_streak": self._best_streak}))

    def _set_app_icon(self) -> None:
        """Устанавливает иконку приложения."""
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent.parent

        # Пробуем разные форматы иконок
        for ext in ("icns", "ico", "png"):
            icon_path = base_path / "assets" / f"icon.{ext}"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

    def closeEvent(self, event) -> None:
        """Обработчик закрытия окна."""
        self._save_record()
        self._audio_player.cleanup()
        super().closeEvent(event)
