<img width="886" height="723" alt="image" src="https://github.com/user-attachments/assets/c3e68651-f92f-45c5-a3ae-c317380bd437" />

# Piano Ear Trainer

Десктопное приложение для тренировки музыкального слуха.

## Зачем?

Развитие музыкального слуха — важный навык для музыкантов. Приложение помогает научиться определять ноты на слух через практику:

1. Слушаете случайную ноту
2. Пытаетесь угадать её на виртуальной клавиатуре
3. Получаете обратную связь и учитесь на ошибках

## Возможности

- 88 реальных сэмплов фортепиано (полный диапазон A0–C8)
- Виртуальная клавиатура с визуализацией всех клавиш
- Выбор октав для тренировки (от субконтроктавы до 5-й)
- Режим с диезами (чёрные клавиши) или без
- Счётчик правильных/неправильных ответов
- Отслеживание серии и рекорда
- Справочник октав с визуализацией

## Использование

### С Poetry (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/Eelolo/piano_ear_trainer.git
cd piano_ear_trainer

# Установить зависимости
poetry install

# Запустить
poetry run piano-ear-trainer
# или
poetry run python -m piano_ear_trainer
```

### С pip

```bash
# Клонировать репозиторий
git clone https://github.com/Eelolo/piano_ear_trainer.git
cd piano_ear_trainer

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или: .venv\Scripts\activate  # Windows

# Установить зависимости
pip install -e .

# Запустить
python -m piano_ear_trainer
```

### Как тренироваться

1. Выберите октавы для тренировки (по умолчанию — 1-я октава)
2. Включите диезы, если хотите тренировать чёрные клавиши
3. Нажмите **Начать**
4. Слушайте ноту и выбирайте её на клавиатуре
5. Используйте **Повторить** для повторного прослушивания
6. После ответа нажмите **Следующая нота**

## Сборка

### Требования

- Python 3.11+
- PyInstaller

### macOS

```bash
# Установить PyInstaller
pip install pyinstaller

# Собрать
pyinstaller piano_ear_trainer.spec --clean

# Результат
ls dist/PianoEarTrainer
```

### Windows

```cmd
pip install pyinstaller
pyinstaller piano_ear_trainer.spec --clean

Результат
dir dist\PianoEarTrainer.exe
```

## Технологии

- **Python 3.11+**
- **PySide6** — GUI (Qt)
- **pygame** — воспроизведение аудио
- **PyInstaller** — сборка в исполняемый файл

## Лицензия

MIT

Сэмплы фортепиано: FluidR3_GM Soundfont (MIT)
