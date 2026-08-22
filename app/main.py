import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class SmartQueueAnnouncer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_queue = ""
        self.last_called_queue = ""
        self.history = []

        self.setWindowTitle("Smart Queue Announcer")
        self.setMinimumSize(430, 620)
        self.resize(500, 700)

        self.build_interface()

    # =========================================================
    # MAIN INTERFACE
    # =========================================================

    def build_interface(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        title = QLabel("🔊  Smart Queue Announcer")
        title.setObjectName("app_title")

        header.addWidget(title)
        header.addStretch()

        status = QLabel("● READY")
        status.setObjectName("status")

        header.addWidget(status)

        main_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()

        self.tabs.addTab(self.create_announcer_tab(), "🔊 Announcer")
        self.tabs.addTab(self.create_history_tab(), "◷ History")
        self.tabs.addTab(self.create_settings_tab(), "⚙ Settings")
        self.tabs.addTab(self.create_about_tab(), "ⓘ About")

        main_layout.addWidget(self.tabs)

        # Footer
        footer = QHBoxLayout()

        voice_status = QLabel("● Voice: Lessac High")
        voice_status.setObjectName("footer")

        offline_status = QLabel("Offline")
        offline_status.setObjectName("offline")

        footer.addWidget(voice_status)
        footer.addStretch()
        footer.addWidget(offline_status)

        main_layout.addLayout(footer)

    # =========================================================
    # ANNOUNCER TAB
    # =========================================================

    def create_announcer_tab(self):

        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(9)

        # Current queue
        current_title = QLabel("CURRENT QUEUE")
        current_title.setObjectName("section_title")

        layout.addWidget(current_title)

        self.queue_display = QLabel("—")
        self.queue_display.setObjectName("queue_display")
        self.queue_display.setAlignment(Qt.AlignCenter)
        self.queue_display.setMinimumHeight(75)

        layout.addWidget(self.queue_display)

        # Announcement preview
        self.preview = QLabel(
            "Please enter a queue number."
        )
        self.preview.setObjectName("preview")
        self.preview.setWordWrap(True)

        layout.addWidget(self.preview)

        # Keypad
        keypad = QGridLayout()
        keypad.setSpacing(5)

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

            button = QPushButton(key)
            button.setObjectName("key_button")
            button.setMinimumHeight(38)

            button.clicked.connect(
                lambda checked=False, value=key:
                self.add_character(value)
            )

            keypad.addWidget(button, row, column)

        layout.addLayout(keypad)

        # Main CALL button
        call_button = QPushButton("🔊  CALL QUEUE")
        call_button.setObjectName("call_button")
        call_button.setMinimumHeight(52)

        call_button.clicked.connect(self.call_queue)

        layout.addWidget(call_button)

        # Secondary buttons
        actions = QHBoxLayout()
        actions.setSpacing(6)

        recall_button = QPushButton("↻  CALL AGAIN")
        recall_button.setObjectName("recall_button")
        recall_button.clicked.connect(self.recall_queue)

        clear_button = QPushButton("🗑  CLEAR QUEUE")
        clear_button.setObjectName("clear_button")
        clear_button.clicked.connect(self.clear_queue)

        actions.addWidget(recall_button)
        actions.addWidget(clear_button)

        layout.addLayout(actions)

        return page

    # =========================================================
    # HISTORY TAB
    # =========================================================

    def create_history_tab(self):

        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(8, 10, 8, 8)

        title_row = QHBoxLayout()

        title = QLabel("CALL HISTORY")
        title.setObjectName("section_title")

        title_row.addWidget(title)
        title_row.addStretch()

        clear_history = QPushButton("Clear History")
        clear_history.clicked.connect(self.clear_history)

        title_row.addWidget(clear_history)

        layout.addLayout(title_row)

        self.history_display = QLabel("No calls yet.")
        self.history_display.setObjectName("history")
        self.history_display.setAlignment(Qt.AlignTop)

        layout.addWidget(self.history_display)

        layout.addStretch()

        return page

    # =========================================================
    # SETTINGS TAB
    # =========================================================

    def create_settings_tab(self):

        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(15)

        # Voice
        voice_title = QLabel("VOICE SETTINGS")
        voice_title.setObjectName("section_title")

        layout.addWidget(voice_title)

        voice = QComboBox()
        voice.addItem("Lessac High (en_US)")
        voice.addItem("Other local voices — coming soon")

        layout.addWidget(voice)

        # Speed
        speed_label = QLabel("Voice Speed")
        layout.addWidget(speed_label)

        speed = QSlider(Qt.Horizontal)
        speed.setMinimum(-50)
        speed.setMaximum(50)
        speed.setValue(0)

        layout.addWidget(speed)

        # Volume
        volume_label = QLabel("Volume")
        layout.addWidget(volume_label)

        volume = QSlider(Qt.Horizontal)
        volume.setMinimum(0)
        volume.setMaximum(100)
        volume.setValue(80)

        layout.addWidget(volume)

        # Test voice
        test_voice = QPushButton("▶  Test Voice")
        test_voice.setObjectName("secondary_button")

        layout.addWidget(test_voice)

        # Announcement
        announcement_title = QLabel("ANNOUNCEMENT")
        announcement_title.setObjectName("section_title")

        layout.addWidget(announcement_title)

        announcement = QLabel(
            "{queue}, please pick up your order."
        )
        announcement.setObjectName("announcement_box")
        announcement.setWordWrap(True)

        layout.addWidget(announcement)

        # Display settings
        display_title = QLabel("DISPLAY")
        display_title.setObjectName("section_title")

        layout.addWidget(display_title)

        always_top = QCheckBox("Always keep window on top")
        always_top.setChecked(True)
        always_top.stateChanged.connect(self.toggle_always_on_top)

        layout.addWidget(always_top)

        compact = QCheckBox("Compact Mode")
        compact.setChecked(False)
        compact.stateChanged.connect(self.toggle_compact_mode)

        layout.addWidget(compact)

        layout.addStretch()

        return page

    # =========================================================
    # ABOUT TAB
    # =========================================================

    def create_about_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("🔊")
        icon.setObjectName("about_icon")
        icon.setAlignment(Qt.AlignCenter)

        title = QLabel("Smart Queue Announcer")
        title.setObjectName("about_title")
        title.setAlignment(Qt.AlignCenter)

        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)

        description = QLabel(
            "A simple Windows queue announcement system\n"
            "using a local natural voice engine."
        )

        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(description)

        return page

    # =========================================================
    # QUEUE FUNCTIONS
    # =========================================================

    def add_character(self, character):

        self.current_queue += character

        self.queue_display.setText(
            self.current_queue
        )

        self.update_preview()

    def clear_queue(self):

        self.current_queue = ""

        self.queue_display.setText("—")

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
    # CALL FUNCTIONS
    # =========================================================

    def call_queue(self):

        if not self.current_queue:
            return

        self.last_called_queue = self.current_queue

        self.add_history(
            self.current_queue,
            "First Call"
        )

        # Voice will be added in the next stage.

    def recall_queue(self):

        if not self.last_called_queue:
            return

        self.add_history(
            self.last_called_queue,
            "Call Again"
        )

        # Voice will be added in the next stage.

    # =========================================================
    # HISTORY
    # =========================================================

    def add_history(self, queue, call_type):

        timestamp = datetime.now().strftime(
            "%I:%M:%S %p"
        )

        self.history.insert(
            0,
            (queue, timestamp, call_type)
        )

        self.update_history_display()

    def update_history_display(self):

        if not self.history:

            self.history_display.setText(
                "No calls yet."
            )

            return

        lines = []

        for queue, time, call_type in self.history[:30]:

            lines.append(
                f"{queue}    {time}    {call_type}"
            )

        self.history_display.setText(
            "\n\n".join(lines)
        )

    def clear_history(self):

        self.history.clear()

        self.update_history_display()

    # =========================================================
    # DISPLAY SETTINGS
    # =========================================================

    def toggle_always_on_top(self, state):

        enabled = state == Qt.Checked

        self.setWindowFlag(
            Qt.WindowStaysOnTopHint,
            enabled
        )

        self.show()

    def toggle_compact_mode(self, state):

        enabled = state == Qt.Checked

        if enabled:

            self.resize(430, 620)

        else:

            self.resize(500, 700)


# =============================================================
# APPLICATION
# =============================================================

app = QApplication(sys.argv)

app.setStyleSheet("""

QMainWindow {
    background-color: #07111f;
}

QWidget {
    color: #f5f7fa;
    font-family: "Segoe UI";
    font-size: 12px;
}

QTabWidget::pane {
    border: 1px solid #1d3b5c;
    border-radius: 12px;
    background-color: #0b1828;
}

QTabBar::tab {
    background-color: #0d1c2d;
    color: #8ea4bb;
    padding: 9px 10px;
    margin-right: 3px;
    border-radius: 7px;
}

QTabBar::tab:selected {
    background-color: #086fe8;
    color: white;
}

#app_title {
    font-size: 18px;
    font-weight: 700;
}

#status {
    color: #35d06f;
    font-size: 11px;
    font-weight: 700;
}

#section_title {
    color: #42a5ff;
    font-size: 12px;
    font-weight: 700;
}

#queue_display {
    background-color: #081522;
    border: 1px solid #1e5d91;
    border-radius: 10px;
    color: #3c9bff;
    font-size: 42px;
    font-weight: 700;
}

#preview {
    background-color: #0e2237;
    border: 1px solid #193d5c;
    border-radius: 8px;
    color: #c8d8e8;
    padding: 8px;
    font-size: 12px;
}

#key_button {
    background-color: #0d1d2d;
    border: 1px solid #24435f;
    border-radius: 6px;
    color: #eaf4ff;
    font-size: 15px;
    font-weight: 600;
}

#key_button:hover {
    background-color: #12406c;
    border: 1px solid #2f9cff;
}

#call_button {
    background-color: #0878ed;
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 15px;
    font-weight: 700;
}

#call_button:hover {
    background-color: #1989ff;
}

#recall_button {
    background-color: #11733b;
    border: none;
    border-radius: 7px;
    color: white;
    font-weight: 600;
}

#clear_button {
    background-color: #a92323;
    border: none;
    border-radius: 7px;
    color: white;
    font-weight: 600;
}

#secondary_button {
    background-color: #12314d;
    border: 1px solid #275477;
    border-radius: 7px;
    padding: 8px;
    color: white;
}

#history {
    background-color: #091724;
    border: 1px solid #1b3852;
    border-radius: 8px;
    padding: 12px;
    color: #d6e3ef;
    font-size: 12px;
}

#announcement_box {
    background-color: #0e2237;
    border: 1px solid #234764;
    border-radius: 8px;
    padding: 12px;
    color: #bcd0e4;
}

#footer {
    color: #8ba1b6;
    font-size: 10px;
}

#offline {
    color: #35d06f;
    font-size: 10px;
}

#about_icon {
    font-size: 55px;
}

#about_title {
    font-size: 22px;
    font-weight: 700;
    color: #3c9bff;
}

QComboBox {
    background-color: #0d1d2d;
    border: 1px solid #28465f;
    border-radius: 6px;
    padding: 8px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #29445d;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #1685f5;
    border-radius: 7px;
}

QCheckBox {
    spacing: 8px;
}

""")

window = SmartQueueAnnouncer()
window.show()

sys.exit(app.exec())
