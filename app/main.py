import sys
from datetime import datetime

from PySide6.QtCore import Qt
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
)


class SmartQueueAnnouncer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_queue = ""
        self.last_called_queue = ""
        self.history = []

        self.normal_size = (500, 700)
        self.compact_size = (450, 620)

        self.setWindowTitle("Smart Queue Announcer")
        self.setMinimumSize(430, 600)
        self.resize(*self.normal_size)

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

        status = QLabel("● READY")
        status.setObjectName("status")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(status)

        main_layout.addLayout(header)

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

        main_layout.addWidget(self.tabs)

        # Footer
        footer = QHBoxLayout()

        voice_status = QLabel(
            "● Voice: Lessac High"
        )
        voice_status.setObjectName("footer")

        offline_status = QLabel(
            "Offline"
        )
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
        layout.setSpacing(8)

        # Current queue
        current_title = QLabel("CURRENT QUEUE")
        current_title.setObjectName("section_title")

        layout.addWidget(current_title)

        self.queue_display = QLabel("—")
        self.queue_display.setObjectName("queue_display")
        self.queue_display.setAlignment(Qt.AlignCenter)
        self.queue_display.setMinimumHeight(72)

        layout.addWidget(self.queue_display)

        # Announcement preview
        self.preview = QLabel(
            "Please enter a queue number."
        )

        self.preview.setObjectName("preview")
        self.preview.setWordWrap(True)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(42)

        layout.addWidget(self.preview)

        # =====================================================
        # KEYPAD
        # =====================================================

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

            # Large touch target
            button.setMinimumHeight(42)

            button.clicked.connect(
                lambda checked=False, value=key:
                self.add_character(value)
            )

            keypad.addWidget(
                button,
                row,
                column
            )

        layout.addLayout(keypad)

        # =====================================================
        # CALL BUTTON
        # =====================================================

        call_button = QPushButton(
            "🔊  CALL QUEUE"
        )

        call_button.setObjectName(
            "call_button"
        )

        # Same height as secondary buttons
        call_button.setMinimumHeight(52)

        call_button.clicked.connect(
            self.call_queue
        )

        layout.addWidget(call_button)

        # =====================================================
        # SECONDARY BUTTONS
        # =====================================================

        actions = QHBoxLayout()
        actions.setSpacing(6)

        recall_button = QPushButton(
            "↻  CALL AGAIN"
        )

        recall_button.setObjectName(
            "recall_button"
        )

        # Same height as CALL
        recall_button.setMinimumHeight(52)

        recall_button.clicked.connect(
            self.recall_queue
        )

        clear_button = QPushButton(
            "🗑  CLEAR QUEUE"
        )

        clear_button.setObjectName(
            "clear_button"
        )

        # Same height as CALL
        clear_button.setMinimumHeight(52)

        clear_button.clicked.connect(
            self.clear_queue
        )

        actions.addWidget(
            recall_button
        )

        actions.addWidget(
            clear_button
        )

        layout.addLayout(actions)

        return page

    # =========================================================
    # HISTORY TAB
    # =========================================================

    def create_history_tab(self):

        page = QWidget()

        main_layout = QVBoxLayout(page)

        main_layout.setContentsMargins(
            8,
            10,
            8,
            8
        )

        # Header
        header = QHBoxLayout()

        title = QLabel(
            "LATEST 10 CALLS"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(title)
        header.addStretch()

        clear_history = QPushButton(
            "Clear History"
        )

        clear_history.setMinimumHeight(44)

        clear_history.clicked.connect(
            self.clear_history
        )

        header.addWidget(
            clear_history
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

        self.history_layout.addStretch()

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        self.history_scroll = scroll

        return page

    # =========================================================
    # SETTINGS TAB
    # =========================================================

    def create_settings_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            8,
            10,
            8,
            8
        )

        layout.setSpacing(13)

        # =====================================================
        # VOICE
        # =====================================================

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

        # =====================================================
        # SPEED
        # =====================================================

        speed_label = QLabel(
            "Voice Speed"
        )

        layout.addWidget(
            speed_label
        )

        speed_value = QLabel(
            "Normal"
        )

        speed_value.setObjectName(
            "slider_value"
        )

        speed_row = QHBoxLayout()

        speed_row.addWidget(
            speed_label
        )

        speed_row.addStretch()

        speed_row.addWidget(
            speed_value
        )

        # Replace the previous label position
        layout.takeAt(
            layout.count() - 1
        )

        layout.addLayout(
            speed_row
        )

        speed = QSlider(
            Qt.Horizontal
        )

        speed.setMinimum(
            -50
        )

        speed.setMaximum(
            50
        )

        speed.setValue(
            0
        )

        # Large touch area
        speed.setMinimumHeight(
            42
        )

        speed.valueChanged.connect(
            lambda value:
            speed_value.setText(
                self.speed_text(value)
            )
        )

        layout.addWidget(
            speed
        )

        # =====================================================
        # VOLUME
        # =====================================================

        volume_row = QHBoxLayout()

        volume_label = QLabel(
            "Volume"
        )

        volume_value = QLabel(
            "80%"
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

        volume = QSlider(
            Qt.Horizontal
        )

        volume.setMinimum(
            0
        )

        volume.setMaximum(
            100
        )

        volume.setValue(
            80
        )

        # Large touch area
        volume.setMinimumHeight(
            42
        )

        volume.valueChanged.connect(
            lambda value:
            volume_value.setText(
                f"{value}%"
            )
        )

        layout.addWidget(
            volume
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

        # Voice will be connected later
        layout.addWidget(
            test_voice
        )

        # =====================================================
        # ANNOUNCEMENT
        # =====================================================

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

        # =====================================================
        # DISPLAY
        # =====================================================

        display_title = QLabel(
            "DISPLAY"
        )

        display_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            display_title
        )

        always_top = QCheckBox(
            "Always keep window on top"
        )

        always_top.setChecked(
            True
        )

        always_top.setMinimumHeight(
            44
        )

        always_top.stateChanged.connect(
            self.toggle_always_on_top
        )

        layout.addWidget(
            always_top
        )

        compact = QCheckBox(
            "Compact Mode"
        )

        compact.setChecked(
            False
        )

        compact.setMinimumHeight(
            44
        )

        compact.stateChanged.connect(
            self.toggle_compact_mode
        )

        layout.addWidget(
            compact
        )

        layout.addStretch()

        return page

    # =========================================================
    # ABOUT TAB
    # =========================================================

    def create_about_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

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
    # CALL
    # =========================================================

    def call_queue(self):

        if not self.current_queue:
            return

        self.last_called_queue = (
            self.current_queue
        )

        self.add_history(
            self.current_queue,
            "First Call"
        )

        # Piper voice will be connected later.

    # =========================================================
    # CALL AGAIN
    # =========================================================

    def recall_queue(self):

        if not self.last_called_queue:
            return

        self.add_history(
            self.last_called_queue,
            "Call Again"
        )

        # Piper voice will be connected later.

    # =========================================================
    # HISTORY
    # =========================================================

    def add_history(
        self,
        queue,
        call_type
    ):

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

        # Keep latest 10 only
        self.history = self.history[:10]

        self.update_history_display()

    def update_history_display(
        self
    ):

        # Remove existing widgets
        while self.history_layout.count():

            item = self.history_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        if not self.history:

            empty = QLabel(
                "No calls yet."
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

            # Queue
            queue_label = QLabel(
                queue
            )

            queue_label.setObjectName(
                "history_queue"
            )

            # Details
            details = QLabel(
                f"{time}\n{call_type}"
            )

            details.setObjectName(
                "history_details"
            )

            details.setWordWrap(
                True
            )

            # Recall
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

    def recall_history(
        self,
        queue
    ):

        # Set as last called
        self.last_called_queue = queue

        # Immediately record the recall
        self.add_history(
            queue,
            "Call Again"
        )

        # Piper voice will be connected later.

    def clear_history(self):

        self.history.clear()

        self.update_history_display()

    # =========================================================
    # SETTINGS
    # =========================================================

    def speed_text(
        self,
        value
    ):

        if value < -10:
            return "Slower"

        if value > 10:
            return "Faster"

        return "Normal"

    # =========================================================
    # ALWAYS ON TOP
    # =========================================================

    def toggle_always_on_top(
        self,
        state
    ):

        enabled = (
            state == Qt.Checked
        )

        self.setWindowFlag(
            Qt.WindowStaysOnTopHint,
            enabled
        )

        self.show()

    # =========================================================
    # COMPACT MODE
    # =========================================================

    def toggle_compact_mode(
        self,
        state
    ):

        enabled = (
            state == Qt.Checked
        )

        if enabled:

            self.resize(
                self.compact_size[0],
                self.compact_size[1]
            )

        else:

            self.resize(
                self.normal_size[0],
                self.normal_size[1]
            )

        self.updateGeometry()

    # =========================================================
    # APPLICATION
    # =========================================================


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
   ANNOUNCEMENT PREVIEW
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
   MAIN CALL
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
   SECONDARY BUTTONS
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
   TOUCH CHECKBOXES
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
