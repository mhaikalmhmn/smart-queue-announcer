import sys
import subprocess
import ctypes
import json
from ctypes import wintypes
import tempfile
from pathlib import Path
from datetime import datetime, date

from pydub import AudioSegment

from piper import PiperVoice

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QFrame,
)


# =============================================================
# VOICE SETTINGS
# =============================================================

if getattr(sys, "frozen", False):

    BASE_DIR = Path(sys._MEIPASS)

else:

    BASE_DIR = Path(__file__).resolve().parent.parent

SETTINGS_DIR = Path.home() / "AppData" / "Local" / "SmartQueueAnnouncer"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

PIPER_MODEL = BASE_DIR / "piper" / "voices" / "en_US-lessac-high.onnx"

BELL_FILE = BASE_DIR / "sounds" / "bell.wav"
VOICE_CACHE_DIR = BASE_DIR / "voice_cache"

CHARACTER_DELAY = 0.30
BELL_DELAY = 0.50
PHRASE_DELAY = 0.80

FINAL_PHRASE = "Please pick up your order."


# =============================================================
# FINAL PRONUNCIATION MAP
# =============================================================

PRONUNCIATION = {
    "A": "a",
    "B": "bee",
    "C": "sea",
    "D": "dee",
    "E": "ee",
    "F": "F",
    "G": "gee",
    "H": "aitch",
    "I": "eye",
    "J": "jay",
    "K": "kay",
    "L": "el",
    "M": "em",
    "N": "en",
    "O": "oh",
    "P": "pee",
    "Q": "cue",
    "R": "ar",
    "S": "ess",
    "T": "tee",
    "U": "you",
    "V": "vee",
    "W": "double you",
    "X": "ex",
    "Y": "why",
    "Z": "zed",

    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


# =============================================================
# VOICE WORKER
# =============================================================

class VoiceWorker(QThread):

    finished = Signal()
    error = Signal(str)

    def __init__(self, owner, queue, include_bell=True):
        super().__init__()
        self.owner = owner
        self.queue = queue
        self.include_bell = include_bell

    def run(self):
        try:
            self.owner.announce_queue(
                self.queue,
                self.include_bell
            )
        except Exception as error:
            self.error.emit(str(error))
        finally:
            self.finished.emit()


# =============================================================
# MAIN WINDOW
# =============================================================

class SmartQueueAnnouncer(QMainWindow):

    def __init__(self):

        super().__init__()

        self.current_queue = ""
        self.last_called_queue = ""
        self.voice_worker = None
        self.piper_voice = None

        self.settings = self.load_settings()

        # Today's history only
        self.history = []
        self.history_date = date.today()

        self.setWindowTitle(
            "Smart Queue Announcer"
        )

        self.setWindowIcon(
            QIcon(
                str(
                    BASE_DIR / "assets" / "smart_queue_announcer.ico"
                )
            )
        )

        self.setMinimumSize(
            500,
            700
        )

        self.resize(
            500,
            700
        )

        self.build_interface()

    # =========================================================
    # SETTINGS
    # =========================================================

    def load_settings(self):

        if not SETTINGS_FILE.exists():
            return {
                "volume": 80,
                "always_on_top": True
            }

        try:

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return {
                "volume": 80,
                "always_on_top": True
            }    

    def save_settings(self):

        SETTINGS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        settings = {
            "volume": self.volume.value(),
            "always_on_top": self.always_on_top.isChecked()
        }

        try:

            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    settings,
                    file,
                    indent=4
                )

        except Exception as error:

            print(
                "Settings error:",
                error
            )     

    def volume_changed(self, value):

         self.save_settings()                 


    # =========================================================
    # MAIN INTERFACE
    # =========================================================

    def build_interface(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        main_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        title = QLabel(
            "🔊  Smart Queue Announcer"
        )

        title.setObjectName(
            "app_title"
        )

        self.status = QLabel(
            "● READY"
        )

        self.status.setObjectName(
            "status"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        header.addWidget(
            self.status
        )

        main_layout.addLayout(
            header
        )

        # Tabs
        self.tabs = QTabWidget()

        self.tabs.addTab(
            self.create_announcer_tab(),
            "🔊 Announcer"
        )

        self.tabs.addTab(
            self.create_history_tab(),
            "◷ History"
        )

        self.tabs.addTab(
            self.create_settings_tab(),
            "⚙ Settings"
        )

        self.tabs.addTab(
            self.create_about_tab(),
            "ⓘ About"
        )

        main_layout.addWidget(
            self.tabs
        )

        # Footer
        footer = QHBoxLayout()

        voice_status = QLabel(
            "● Voice: Lessac High"
        )

        voice_status.setObjectName(
            "footer"
        )

        offline_status = QLabel(
            "Offline"
        )

        offline_status.setObjectName(
            "offline"
        )

        footer.addWidget(
            voice_status
        )

        footer.addStretch()

        footer.addWidget(
            offline_status
        )

        main_layout.addLayout(
            footer
        )


    # =========================================================
    # ANNOUNCER TAB
    # =========================================================

    def create_announcer_tab(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            8,
            10,
            8,
            8
        )

        layout.setSpacing(8)

        # Current queue
        current_title = QLabel(
            "CURRENT QUEUE"
        )

        current_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            current_title
        )

        self.queue_display = QLabel(
            "—"
        )

        self.queue_display.setObjectName(
            "queue_display"
        )

        self.queue_display.setAlignment(
            Qt.AlignCenter
        )

        self.queue_display.setMinimumHeight(
            72
        )

        layout.addWidget(
            self.queue_display
        )

        # Announcement preview
        self.preview = QLabel(
            "Please enter a queue number."
        )

        self.preview.setObjectName(
            "preview"
        )

        self.preview.setWordWrap(
            True
        )

        self.preview.setAlignment(
            Qt.AlignCenter
        )

        self.preview.setMinimumHeight(
            42
        )

        layout.addWidget(
            self.preview
        )

        # =====================================================
        # KEYPAD
        # =====================================================

        keypad = QGridLayout()

        keypad.setSpacing(
            5
        )

        keys = [
            "A", "B", "C", "D", "E", "F",
            "G", "H", "I", "J", "K", "L",
            "M", "N", "O", "P", "Q", "R",
            "S", "T", "U", "V", "W", "X",
            "Y", "Z", "1", "2", "3", "4",
            "5", "6", "7", "8", "9", "0",
        ]

        for index, key in enumerate(keys):

            row = index // 6
            column = index % 6

            button = QPushButton(
                key
            )

            button.setObjectName(
                "key_button"
            )

            button.setMinimumHeight(
                42
            )

            button.clicked.connect(
                lambda checked=False,
                value=key:
                self.add_character(
                    value
                )
            )

            keypad.addWidget(
                button,
                row,
                column
            )

        layout.addLayout(
            keypad
        )

        # =====================================================
        # CALL QUEUE
        # =====================================================

        call_button = QPushButton(
            "🔊  CALL QUEUE"
        )

        call_button.setObjectName(
            "call_button"
        )

        call_button.setMinimumHeight(
            52
        )

        call_button.clicked.connect(
            self.call_queue
        )

        layout.addWidget(
            call_button
        )

        # =====================================================
        # CALL AGAIN + CLEAR
        # =====================================================

        actions = QHBoxLayout()

        actions.setSpacing(
            6
        )

        recall_button = QPushButton(
            "↻  CALL AGAIN"
        )

        recall_button.setObjectName(
            "recall_button"
        )

        recall_button.setMinimumHeight(
            52
        )

        recall_button.clicked.connect(
            self.recall_queue
        )

        clear_button = QPushButton(
            "🗑  CLEAR QUEUE"
        )

        clear_button.setObjectName(
            "clear_button"
        )

        clear_button.setMinimumHeight(
            52
        )

        clear_button.clicked.connect(
            self.clear_queue
        )

        actions.addWidget(
            recall_button
        )

        actions.addWidget(
            clear_button
        )

        layout.addLayout(
            actions
        )

        return page


    # =========================================================
    # HISTORY TAB
    # =========================================================

    def create_history_tab(self):

        page = QWidget()

        main_layout = QVBoxLayout(
            page
        )

        main_layout.setContentsMargins(
            8,
            10,
            8,
            8
        )

        # History heading
        header = QHBoxLayout()

        self.history_title = QLabel()

        self.history_title.setObjectName(
            "section_title"
        )

        header.addWidget(
            self.history_title
        )

        header.addStretch()

        clear_history_button = QPushButton(
            "Clear History"
        )

        clear_history_button.setMinimumHeight(
            44
        )

        clear_history_button.clicked.connect(
            self.clear_history
        )

        header.addWidget(
            clear_history_button
        )

        main_layout.addLayout(
            header
        )

        # Scroll area
        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        container = QWidget()

        self.history_layout = QVBoxLayout(
            container
        )

        self.history_layout.setContentsMargins(
            4,
            8,
            4,
            8
        )

        self.history_layout.setSpacing(
            6
        )

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        self.history_scroll = scroll

        self.update_history_display()

        return page


    # =========================================================
    # SETTINGS TAB
    # =========================================================

    def create_settings_tab(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            8,
            10,
            8,
            8
        )

        layout.setSpacing(
            13
        )

        # Voice
        voice_title = QLabel(
            "VOICE SETTINGS"
        )

        voice_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            voice_title
        )

        voice = QComboBox()

        voice.addItem(
            "Lessac High (en_US)"
        )

        voice.addItem(
            "Other local voices — coming soon"
        )

        voice.setMinimumHeight(
            46
        )

        layout.addWidget(
            voice
        )

        # Volume
        volume_row = QHBoxLayout()

        volume_label = QLabel(
            "Announcement Volume"
        )

        volume_value = QLabel(
            f"{self.settings.get('volume', 80)}%"
        )

        volume_value.setObjectName(
            "slider_value"
        )

        volume_row.addWidget(
            volume_label
        )

        volume_row.addStretch()

        volume_row.addWidget(
            volume_value
        )

        layout.addLayout(
            volume_row
        )

        self.volume = QSlider(
            Qt.Horizontal
        )

        self.volume.setMinimum(
            0
        )

        self.volume.setMaximum(
            100
        )

        self.volume.setValue(
            self.settings.get(
            "volume",
             80
            )
        )

        self.volume.setMinimumHeight(
            42
        )

        self.volume.valueChanged.connect(
            lambda value: (
                volume_value.setText(
                    f"{value}%"
                ),
            self.volume_changed(value)
            )
        )

        layout.addWidget(
            self.volume
        )

        # Test voice
        test_voice = QPushButton(
            "▶  TEST VOICE"
        )

        test_voice.setObjectName(
            "secondary_button"
        )

        test_voice.setMinimumHeight(
            48
        )

        test_voice.clicked.connect(
            self.test_voice
        )

        layout.addWidget(
            test_voice
        )

        # Announcement
        announcement_title = QLabel(
            "ANNOUNCEMENT"
        )

        announcement_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            announcement_title
        )

        announcement = QLabel(
            "{queue}, please pick up your order."
        )

        announcement.setObjectName(
            "announcement_box"
        )

        announcement.setWordWrap(
            True
        )

        layout.addWidget(
            announcement
        )

        # Display
        display_title = QLabel(
            "DISPLAY"
        )

        display_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            display_title
        )

        self.always_on_top = QCheckBox(
            "Always keep window on top"
        )

        self.always_on_top.setChecked(
            self.settings.get(
                "always_on_top",
                True
            )
        )

        QTimer.singleShot(
            100,
                lambda: self.toggle_always_on_top(
                    self.always_on_top.isChecked()
                )
        )

        self.always_on_top.setMinimumHeight(
            44
        )

        self.always_on_top.stateChanged.connect(
            self.toggle_always_on_top
        )

        self.always_on_top.stateChanged.connect(
            lambda state: self.save_settings()
        )

        layout.addWidget(
            self.always_on_top
        )

        layout.addStretch()

        return page


    # =========================================================
    # ABOUT TAB
    # =========================================================

    def create_about_tab(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setAlignment(
            Qt.AlignCenter
        )

        icon = QLabel(
            "🔊"
        )

        icon.setObjectName(
            "about_icon"
        )

        icon.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            "Smart Queue Announcer"
        )

        title.setObjectName(
            "about_title"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        version = QLabel(
            "Version 1.0.0"
        )

        version.setAlignment(
            Qt.AlignCenter
        )

        description = QLabel(
            "A simple Windows queue announcement system\n"
            "using a local natural voice engine."
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            icon
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            version
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            description
        )

        return page


    # =========================================================
    # QUEUE INPUT
    # =========================================================

    def add_character(
        self,
        character
    ):

        self.current_queue += character

        self.queue_display.setText(
            self.current_queue
        )

        self.update_preview()


    def clear_queue(self):

        self.current_queue = ""

        self.queue_display.setText(
            "—"
        )

        self.preview.setText(
            "Please enter a queue number."
        )


    def update_preview(self):

        if self.current_queue:

            self.preview.setText(
                f"🔊  {self.current_queue}, "
                "please pick up your order."
            )

        else:

            self.preview.setText(
                "Please enter a queue number."
            )


    # =========================================================
    # VOICE ENGINE
    # =========================================================

    def generate_speech(
        self,
        text,
        output_file
    ):

        if self.piper_voice is None:

            self.piper_voice = PiperVoice.load(
                str(PIPER_MODEL)
            )

        with open(
            output_file,
            "wb"
        ) as wav_file:

            self.piper_voice.synthesize_wav(
                text,
                wav_file
            )

        command = [
            str(PIPER_PYTHON),
            "-m",
            "piper",
            "--model",
            str(PIPER_MODEL),
            "--output_file",
            str(output_file),
        ]

        subprocess.run(
            command,
            input=text,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
            if sys.platform == "win32"
            else 0
        )


    def build_queue_audio(
        self,
        queue,
        output_file,
        include_bell=True
    ):

        if not VOICE_CACHE_DIR.exists():
            raise FileNotFoundError(
                f"Voice cache folder not found:\\n"
                f"{VOICE_CACHE_DIR}"
            )

        if include_bell and not BELL_FILE.exists():
            raise FileNotFoundError(
                f"Bell sound not found:\\n"
                f"{BELL_FILE}"
            )

        parts = []

        if include_bell:
            bell = AudioSegment.from_wav(
                BELL_FILE
            )

            parts.append(bell)

            parts.append(
                AudioSegment.silent(
                    duration=int(
                        BELL_DELAY * 1000
                    )
                )
            )

        for index, character in enumerate(queue.upper()):

            character_file = (
                VOICE_CACHE_DIR /
                f"{character}.wav"
            )

            if not character_file.exists():
                raise FileNotFoundError(
                    f"Voice cache file not found:\\n"
                    f"{character_file}"
                )

            character_audio = AudioSegment.from_wav(
                character_file
            )

            parts.append(character_audio)

            if index < len(queue) - 1:
                parts.append(
                    AudioSegment.silent(
                        duration=int(
                            CHARACTER_DELAY * 1000
                        )
                    )
                )

        phrase_file = (
            VOICE_CACHE_DIR /
            "final_phrase.wav"
        )

        if not phrase_file.exists():
            raise FileNotFoundError(
                f"Final phrase cache file not found:\\n"
                f"{phrase_file}"
            )

        parts.append(
            AudioSegment.silent(
                duration=int(
                    PHRASE_DELAY * 1000
                )
            )
        )

        parts.append(
            AudioSegment.from_wav(
                phrase_file
            )
        )

        if not parts:
            return

        announcement = parts[0]

        for part in parts[1:]:
            announcement += part

        announcement.export(
            output_file,
            format="wav"
        )


    def play_audio(
        self,
        audio_file
    ):

        if sys.platform == "win32":

            volume = self.volume.value()

            import winsound

            audio = AudioSegment.from_wav(
                audio_file
            )

            volume_change = (
                20 * __import__("math").log10(
                max(volume, 1) / 100
                )
            )

            audio = audio + volume_change

            audio.export(
                audio_file,
                format="wav"
            )

            winsound.PlaySound(
                str(audio_file),
                winsound.SND_FILENAME
            )

        else:

            subprocess.run(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    str(audio_file)
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )


    def start_voice_worker(
        self,
        queue,
        include_bell=True
    ):

        if self.voice_worker is not None and self.voice_worker.isRunning():
            return

        self.voice_worker = VoiceWorker(
            self,
            queue,
            include_bell
        )

        self.voice_worker.error.connect(
            lambda message: print(
                "Voice error:",
                message
            )
        )

        self.voice_worker.finished.connect(
            self._voice_worker_finished
        )

        self.voice_worker.finished.connect(
            self.voice_worker.deleteLater
        )

        self.status.setText(
           "● CALLING..."
        )

        self.status.setStyleSheet(
             "color: #f5c542;"
        )

        self.voice_worker.start()


    def _voice_worker_finished(self):

        self.status.setText(
            "● READY"
     )

        self.status.setStyleSheet(
            "color: #35d06f;"
    )

        self.voice_worker = None


    def announce_queue(
        self,
        queue,
        include_bell=True
    ):

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:

            output_file = Path(
                temp_file.name
            )

        try:

            self.build_queue_audio(
                queue,
                output_file,
                include_bell
            )

            self.play_audio(
                output_file
            )

        except Exception as error:

            print(
                "Voice error:",
                error
            )

        finally:

            try:
                output_file.unlink(
                    missing_ok=True
                )

            except Exception:
                pass


    # =========================================================
    # CALL QUEUE
    # =========================================================

    def call_queue(self):

        self.check_new_day()

        if not self.current_queue:

            return

        self.last_called_queue = (
            self.current_queue
        )

        self.add_history(
            self.current_queue,
            "First Call"
        )

        self.start_voice_worker(
            self.current_queue,
            include_bell=True
        )


    # =========================================================
    # CALL AGAIN
    # =========================================================

    def recall_queue(self):

        self.check_new_day()

        if not self.last_called_queue:

            return

        self.add_history(
            self.last_called_queue,
            "Call Again"
        )

        self.start_voice_worker(
            self.last_called_queue,
            include_bell=False
        )


    # =========================================================
    # TEST VOICE
    # =========================================================

    def test_voice(self):

        self.start_voice_worker(
            "AMNVZ001",
            include_bell=True
        )


    # =========================================================
    # DAILY HISTORY
    # =========================================================

    def check_new_day(self):

        today = date.today()

        if today != self.history_date:

            self.history.clear()

            self.history_date = today

            self.update_history_display()


    def add_history(
        self,
        queue,
        call_type
    ):

        self.check_new_day()

        timestamp = datetime.now().strftime(
            "%I:%M:%S %p"
        )

        self.history.insert(
            0,
            (
                queue,
                timestamp,
                call_type
            )
        )

        self.history = self.history[:10]

        self.update_history_display()


    def update_history_display(
        self
    ):

        today_text = date.today().strftime(
            "%d %b %Y"
        )

        self.history_title.setText(
            f"TODAY'S CALLS — {today_text}"
        )

        while self.history_layout.count():

            item = (
                self.history_layout.takeAt(0)
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

        if not self.history:

            empty = QLabel(
                "No calls yet today."
            )

            empty.setObjectName(
                "history_empty"
            )

            empty.setAlignment(
                Qt.AlignCenter
            )

            self.history_layout.addWidget(
                empty
            )

            self.history_layout.addStretch()

            return

        for queue, time, call_type in self.history:

            card = QFrame()

            card.setObjectName(
                "history_card"
            )

            card_layout = QHBoxLayout(
                card
            )

            card_layout.setContentsMargins(
                10,
                8,
                8,
                8
            )

            queue_label = QLabel(
                queue
            )

            queue_label.setObjectName(
                "history_queue"
            )

            details = QLabel(
                f"{time}\n{call_type}"
            )

            details.setObjectName(
                "history_details"
            )

            recall_button = QPushButton(
                "↻\nRECALL"
            )

            recall_button.setObjectName(
                "history_recall"
            )

            recall_button.setMinimumSize(
                72,
                54
            )

            recall_button.clicked.connect(
                lambda checked=False,
                q=queue:
                self.recall_history(q)
            )

            card_layout.addWidget(
                queue_label
            )

            card_layout.addWidget(
                details,
                1
            )

            card_layout.addWidget(
                recall_button
            )

            self.history_layout.addWidget(
                card
            )

        self.history_layout.addStretch()


    # =========================================================
    # HISTORY RECALL
    # =========================================================

    def recall_history(
        self,
        queue
    ):

        self.check_new_day()

        self.last_called_queue = queue

        self.add_history(
            queue,
            "Call Again"
        )

        self.start_voice_worker(
            queue,
            include_bell=False
        )


    # =========================================================
    # CLEAR HISTORY
    # =========================================================

    def clear_history(self):

        self.history.clear()

        self.history_date = date.today()

        self.update_history_display()


    # =========================================================
    # SETTINGS
    # =========================================================


    def toggle_always_on_top(
        self,
        state
    ):

        enabled = bool(
        state
        )

        if sys.platform == "win32":

            user32 = ctypes.WinDLL(
                "user32",
                use_last_error=True
            )

            hwnd = int(self.winId())

            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2

            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_SHOWWINDOW = 0x0040

            user32.SetWindowPos.argtypes = [
                wintypes.HWND,
                wintypes.HWND,
                wintypes.INT,
                wintypes.INT,
                wintypes.INT,
                wintypes.INT,
                wintypes.UINT,
            ]

            user32.SetWindowPos.restype = wintypes.BOOL

            result = user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST if enabled else HWND_NOTOPMOST,
                0,
                0,
                0,
                0,
                SWP_NOSIZE
                | SWP_NOMOVE
                | SWP_SHOWWINDOW
            )

        else:

            flags = self.windowFlags()

            if enabled:
                flags |= Qt.WindowStaysOnTopHint
            else:
                flags &= ~Qt.WindowStaysOnTopHint

            self.setWindowFlags(flags)
            self.show()


# =============================================================
# APPLICATION
# =============================================================

app = QApplication(
    sys.argv
)


app.setStyleSheet("""

QMainWindow {
    background-color: #07111f;
}

QWidget {
    color: #f5f7fa;
    font-family: "Segoe UI";
    font-size: 12px;
}

/* =========================================================
   TABS
   ========================================================= */

QTabWidget::pane {
    border: 1px solid #1d3b5c;
    border-radius: 12px;
    background-color: #0b1828;
}

QTabBar::tab {
    background-color: #0d1c2d;
    color: #8ea4bb;
    padding: 11px 10px;
    margin-right: 3px;
    border-radius: 7px;
    min-height: 34px;
}

QTabBar::tab:selected {
    background-color: #086fe8;
    color: white;
}

/* =========================================================
   HEADER
   ========================================================= */

#app_title {
    font-size: 18px;
    font-weight: 700;
}

#status {
    color: #35d06f;
    font-size: 11px;
    font-weight: 700;
}

/* =========================================================
   SECTION TITLES
   ========================================================= */

#section_title {
    color: #42a5ff;
    font-size: 12px;
    font-weight: 700;
}

/* =========================================================
   QUEUE DISPLAY
   ========================================================= */

#queue_display {
    background-color: #081522;
    border: 1px solid #1e5d91;
    border-radius: 10px;
    color: #3c9bff;
    font-size: 42px;
    font-weight: 700;
}

/* =========================================================
   PREVIEW
   ========================================================= */

#preview {
    background-color: #0e2237;
    border: 1px solid #193d5c;
    border-radius: 8px;
    color: #c8d8e8;
    padding: 8px;
    font-size: 12px;
}

/* =========================================================
   KEYPAD
   ========================================================= */

#key_button {
    background-color: #0d1d2d;
    border: 1px solid #24435f;
    border-radius: 7px;
    color: #eaf4ff;
    font-size: 15px;
    font-weight: 600;
    min-height: 42px;
}

#key_button:hover {
    background-color: #12406c;
    border: 1px solid #2f9cff;
}

#key_button:pressed {
    background-color: #086fe8;
}

/* =========================================================
   CALL
   ========================================================= */

#call_button {
    background-color: #0878ed;
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 15px;
    font-weight: 700;
    min-height: 52px;
}

#call_button:hover {
    background-color: #1989ff;
}

#call_button:pressed {
    background-color: #075db7;
}

/* =========================================================
   CALL AGAIN
   ========================================================= */

#recall_button {
    background-color: #11733b;
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    min-height: 52px;
}

#recall_button:hover {
    background-color: #168b48;
}

#recall_button:pressed {
    background-color: #0c5c2f;
}

/* =========================================================
   CLEAR QUEUE
   ========================================================= */

#clear_button {
    background-color: #a92323;
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    min-height: 52px;
}

#clear_button:hover {
    background-color: #c12c2c;
}

#clear_button:pressed {
    background-color: #8d1d1d;
}

/* =========================================================
   HISTORY
   ========================================================= */

#history_card {
    background-color: #0d1d2d;
    border: 1px solid #24435f;
    border-radius: 9px;
}

#history_queue {
    color: #3c9bff;
    font-size: 18px;
    font-weight: 700;
    min-width: 65px;
}

#history_details {
    color: #9db2c7;
    font-size: 11px;
}

#history_recall {
    background-color: #11733b;
    border: none;
    border-radius: 7px;
    color: white;
    font-size: 10px;
    font-weight: 700;
}

#history_recall:hover {
    background-color: #168b48;
}

#history_recall:pressed {
    background-color: #0c5c2f;
}

#history_empty {
    color: #7e94aa;
    padding: 30px;
}

/* =========================================================
   SETTINGS
   ========================================================= */

QComboBox {
    background-color: #0d1d2d;
    border: 1px solid #28465f;
    border-radius: 7px;
    padding: 8px;
    min-height: 28px;
}

#secondary_button {
    background-color: #12314d;
    border: 1px solid #275477;
    border-radius: 8px;
    padding: 8px;
    color: white;
    font-weight: 600;
    min-height: 48px;
}

#secondary_button:hover {
    background-color: #174363;
}

#announcement_box {
    background-color: #0e2237;
    border: 1px solid #234764;
    border-radius: 8px;
    padding: 12px;
    color: #bcd0e4;
    min-height: 35px;
}

#slider_value {
    color: #42a5ff;
    font-weight: 700;
}

/* =========================================================
   TOUCH SLIDERS
   ========================================================= */

QSlider::groove:horizontal {
    height: 10px;
    background: #29445d;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: #1685f5;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    width: 26px;
    height: 26px;
    margin: -8px 0;
    background: #ffffff;
    border: 3px solid #1685f5;
    border-radius: 13px;
}

/* =========================================================
   TOUCH CHECKBOX
   ========================================================= */

QCheckBox {
    spacing: 10px;
    min-height: 44px;
}

/* =========================================================
   FOOTER
   ========================================================= */

#footer {
    color: #8ba1b6;
    font-size: 10px;
}

#offline {
    color: #35d06f;
    font-size: 10px;
}

/* =========================================================
   ABOUT
   ========================================================= */

#about_icon {
    font-size: 55px;
}

#about_title {
    font-size: 22px;
    font-weight: 700;
    color: #3c9bff;
}

""")


window = SmartQueueAnnouncer()

window.show()

sys.exit(
    app.exec()
)
