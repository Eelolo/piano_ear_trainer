"""Данные о нотах и октавах фортепиано."""

from dataclasses import dataclass
from enum import Enum


class NoteName(Enum):
    """Названия нот."""

    C = "До"
    C_SHARP = "До#"
    D = "Ре"
    D_SHARP = "Ре#"
    E = "Ми"
    F = "Фа"
    F_SHARP = "Фа#"
    G = "Соль"
    G_SHARP = "Соль#"
    A = "Ля"
    A_SHARP = "Ля#"
    B = "Си"


class Octave(Enum):
    """Октавы фортепиано с русскими названиями."""

    SUBCONTRA = ("субконтроктава", 0)  # A0-B0
    CONTRA = ("контроктава", 1)  # C1-B1
    GREAT = ("большая октава", 2)  # C2-B2
    SMALL = ("малая октава", 3)  # C3-B3
    FIRST = ("1-я октава", 4)  # C4-B4
    SECOND = ("2-я октава", 5)  # C5-B5
    THIRD = ("3-я октава", 6)  # C6-B6
    FOURTH = ("4-я октава", 7)  # C7-B7
    FIFTH = ("5-я октава", 8)  # C8

    def __init__(self, russian_name: str, number: int) -> None:
        self.russian_name = russian_name
        self.number = number


@dataclass(frozen=True)
class Note:
    """Нота фортепиано."""

    midi_number: int  # MIDI номер (21-108 для 88 клавиш)
    name: NoteName  # Название ноты
    octave: Octave  # Октава
    frequency: float  # Частота в Гц
    is_black_key: bool  # Чёрная клавиша?

    @property
    def full_name(self) -> str:
        """Полное название ноты на русском."""
        return f"{self.name.value} {self.octave.russian_name}"

    @property
    def short_name(self) -> str:
        """Короткое название (например: C4, A#3)."""
        note_names = {
            NoteName.C: "C",
            NoteName.C_SHARP: "C#",
            NoteName.D: "D",
            NoteName.D_SHARP: "D#",
            NoteName.E: "E",
            NoteName.F: "F",
            NoteName.F_SHARP: "F#",
            NoteName.G: "G",
            NoteName.G_SHARP: "G#",
            NoteName.A: "A",
            NoteName.A_SHARP: "A#",
            NoteName.B: "B",
        }
        return f"{note_names[self.name]}{self.octave.number}"

    @property
    def sample_filename(self) -> str:
        """Имя файла семпла."""
        return f"{self.short_name}.wav"


def _calculate_frequency(midi_number: int) -> float:
    """Рассчитать частоту ноты по MIDI номеру (A4 = 440 Гц)."""
    return 440.0 * (2 ** ((midi_number - 69) / 12))


def _get_octave_for_midi(midi_number: int) -> Octave:
    """Определить октаву по MIDI номеру."""
    # MIDI 21 = A0, MIDI 24 = C1, и т.д.
    if midi_number < 24:  # A0, A#0, B0
        return Octave.SUBCONTRA
    octave_num = (midi_number - 12) // 12
    octave_map = {
        1: Octave.CONTRA,
        2: Octave.GREAT,
        3: Octave.SMALL,
        4: Octave.FIRST,
        5: Octave.SECOND,
        6: Octave.THIRD,
        7: Octave.FOURTH,
        8: Octave.FIFTH,
    }
    return octave_map.get(octave_num, Octave.FIFTH)


def _get_note_name_for_midi(midi_number: int) -> NoteName:
    """Определить название ноты по MIDI номеру."""
    note_in_octave = midi_number % 12
    note_map = {
        0: NoteName.C,
        1: NoteName.C_SHARP,
        2: NoteName.D,
        3: NoteName.D_SHARP,
        4: NoteName.E,
        5: NoteName.F,
        6: NoteName.F_SHARP,
        7: NoteName.G,
        8: NoteName.G_SHARP,
        9: NoteName.A,
        10: NoteName.A_SHARP,
        11: NoteName.B,
    }
    return note_map[note_in_octave]


def _is_black_key(midi_number: int) -> bool:
    """Проверить, является ли клавиша чёрной."""
    note_in_octave = midi_number % 12
    black_keys = {1, 3, 6, 8, 10}  # C#, D#, F#, G#, A#
    return note_in_octave in black_keys


def generate_all_notes() -> list[Note]:
    """Сгенерировать все 88 нот фортепиано (A0 до C8)."""
    notes = []
    # Фортепиано: MIDI 21 (A0) до MIDI 108 (C8)
    for midi in range(21, 109):
        note = Note(
            midi_number=midi,
            name=_get_note_name_for_midi(midi),
            octave=_get_octave_for_midi(midi),
            frequency=_calculate_frequency(midi),
            is_black_key=_is_black_key(midi),
        )
        notes.append(note)
    return notes


# Все 88 нот фортепиано
PIANO_NOTES: list[Note] = generate_all_notes()

# Словарь для быстрого доступа по MIDI номеру
NOTES_BY_MIDI: dict[int, Note] = {note.midi_number: note for note in PIANO_NOTES}

# Словарь для быстрого доступа по короткому имени (C4, A#3, и т.д.)
NOTES_BY_NAME: dict[str, Note] = {note.short_name: note for note in PIANO_NOTES}
