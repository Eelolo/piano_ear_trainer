"""Модуль воспроизведения звука нот."""

import random
import sys
from pathlib import Path

import pygame

from piano_ear_trainer.data import PIANO_NOTES, Note


def _get_base_path() -> Path:
    """Возвращает базовый путь (для PyInstaller и обычного запуска)."""
    if getattr(sys, "frozen", False):
        # Запуск из собранного .exe (PyInstaller)
        return Path(sys._MEIPASS)
    else:
        # Обычный запуск
        return Path(__file__).parent.parent.parent


class AudioPlayer:
    """Плеер для воспроизведения семплов нот."""

    def __init__(self, samples_dir: Path | None = None) -> None:
        """
        Инициализирует аудио плеер.

        Args:
            samples_dir: Путь к папке с семплами. Если None, используется
                        стандартный путь assets/samples/
        """
        # Инициализация pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        # Устанавливаем много каналов для одновременного воспроизведения (глиссандо)
        pygame.mixer.set_num_channels(32)

        # Определяем путь к семплам
        if samples_dir is None:
            # Базовый путь (работает и для .exe, и для обычного запуска)
            base_dir = _get_base_path()
            # Сначала проверяем MP3 (реальные сэмплы пианино)
            mp3_dir = base_dir / "assets" / "samples_mp3"
            wav_dir = base_dir / "assets" / "samples"
            if mp3_dir.exists():
                samples_dir = mp3_dir
                self._format = "mp3"
            else:
                samples_dir = wav_dir
                self._format = "wav"
        else:
            self._format = "wav"

        self.samples_dir = samples_dir
        self._current_note: Note | None = None
        self._sounds_cache: dict[str, pygame.mixer.Sound] = {}

    def _get_sound(self, note: Note) -> pygame.mixer.Sound:
        """Получает звук ноты (с кэшированием)."""
        if note.short_name not in self._sounds_cache:
            # Формируем имя файла с правильным расширением
            filename = f"{note.short_name}.{self._format}"
            sample_path = self.samples_dir / filename
            if not sample_path.exists():
                raise FileNotFoundError(f"Семпл не найден: {sample_path}")
            self._sounds_cache[note.short_name] = pygame.mixer.Sound(str(sample_path))
        return self._sounds_cache[note.short_name]

    def play_note(self, note: Note) -> None:
        """Воспроизводит указанную ноту."""
        sound = self._get_sound(note)
        sound.play()
        self._current_note = note

    def play_random_note(self) -> Note:
        """Выбирает и воспроизводит случайную ноту."""
        note = random.choice(PIANO_NOTES)
        self.play_note(note)
        return note

    def repeat_current_note(self) -> Note | None:
        """Повторяет текущую ноту."""
        if self._current_note is not None:
            self.play_note(self._current_note)
        return self._current_note

    @property
    def current_note(self) -> Note | None:
        """Возвращает текущую ноту."""
        return self._current_note

    def stop(self) -> None:
        """Останавливает воспроизведение."""
        pygame.mixer.stop()

    def cleanup(self) -> None:
        """Освобождает ресурсы."""
        pygame.mixer.quit()
