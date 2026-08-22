import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class QueueAnnouncer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_number = ""
        self.history = []

        self.setWindowTitle("Smart Queue Announcer")
        self.setMinimumSize(1100, 700)

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # ─────────────────────────────────────────
        # HEADER
        # ─────────────────────────────────────────

        header = QHBoxLayout()

        title = QLabel("QUEUE ANNOUNCER")
        title.setObjectName("title")

        subtitle = QLabel("Smart Queue Management")
        subtitle.setObjectName("subtitle")

        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        main_layout.addLayout(header)

        # ─────────────────────────────────────────
        # MAIN CONTENT
        # ─────────────────────────────────────────

        content = QHBoxLayout()
        content.setSpacing(20)

        # LEFT PANEL
        left_panel = QFrame()
        left_panel.setObjectName("card")

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)

        current_label = QLabel("CURRENT QUEUE")
        current_label.setObjectName("section_title")

        self.queue_display = QLabel("—")
        self.queue_display.setObjectName("queue_display")
        self.queue_display.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(current_label)
        left_layout.addWidget(self.queue_display)

        # Counter selector
        counter_label = QLabel("COUNTER / WINDOW")
        counter_label.setObjectName("small_label")

        self.counter = QComboBox()
        self.counter.addItems([
            "Counter 1",
            "Counter 2",
            "Counter 3",
            "Counter 4",
            "Counter 5",
        ])

        left_layout.addWidget(counter_label)
        left_layout.addWidget(self.counter)

        # CALL button
        call_button = QPushButton("CALL QUEUE")
        call_button.setObjectName("call_button")
        call_button.setMinimumHeight(60)
        call_button.clicked.connect(self.call_queue)

        # RECALL button
        recall_button = QPushButton("↻  CALL AGAIN")
        recall_button.setObjectName("secondary_button")
        recall_button.setMinimumHeight(50)
        recall_button.clicked.connect(self.recall_queue)

        left_layout.addWidget(call_button)
        left_layout.addWidget(recall_button)

        content.addWidget(left_panel, 1)

        # RIGHT PANEL
        right_panel = QFrame()
        right_panel.setObjectName("card")

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(25, 25, 25, 25)

        history_title = QLabel("CALL HISTORY")
        history_title.setObjectName("section_title")

        right_layout.addWidget(history_title)

        self.history_label = QLabel("No calls yet")
        self.history_label.setObjectName("history")

        self.history_label.setAlignment(
            Qt.AlignTop | Qt.AlignLeft
        )

        right_layout.addWidget(self.history_label)
        right_layout.addStretch()

        content.addWidget(right_panel, 1)

        main_layout.addLayout(content)

        # ─────────────────────────────────────────
        # NUMBER PAD
        # ─────────────────────────────────────────

        keypad_card = QFrame()
        keypad_card.setObjectName("card")

        keypad_layout = QVBoxLayout(keypad_card)
        keypad_layout.setContentsMargins(25, 20, 25, 20)

        keypad_title = QLabel("QUEUE NUMBER")
        keypad_title.setObjectName("section_title")

        keypad_layout.addWidget(keypad_title)

        keypad = QGridLayout()
        keypad.setSpacing(8)

        buttons = [
            ("1", 0, 0),
            ("2", 0, 1),
            ("3", 0, 2),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),
            ("A", 3, 0),
            ("0", 3, 1),
            ("⌫", 3, 2),
        ]

        for text, row, column in buttons:
            button = QPushButton(text)
            button.setObjectName("key_button")
            button.setMinimumHeight(50)

            if text == "⌫":
                button.clicked.connect(self.backspace)
            else:
                button.clicked.connect(
                    lambda checked=False, value=text:
                    self.add_number(value)
                )

            keypad.addWidget(button, row, column)

        keypad_layout.addLayout(keypad)

        main_layout.addWidget(keypad_card)

        # ─────────────────────────────────────────
        # FOOTER
        # ─────────────────────────────────────────

        footer = QLabel("Ready")
        footer.setObjectName("footer")

        footer.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(footer)

    # ─────────────────────────────────────────────
    # QUEUE FUNCTIONS
    # ─────────────────────────────────────────────

    def add_number(self, value):
        self.current_number += value
        self.queue_display.setText(self.current_number)

    def backspace(self):
        self.current_number = self.current_number[:-1]

        if self.current_number:
            self.queue_display.setText(self.current_number)
        else:
            self.queue_display.setText("—")

    def call_queue(self):
        if not self.current_number:
            return

        counter = self.counter.currentText()
        time = datetime.now().strftime("%H:%M:%S")

        entry = f"{self.current_number}  →  {counter}  •  {time}"

        self.history.insert(0, entry)

        self.update_history()

    def recall_queue(self):
        if not self.current_number:
            return

        counter = self.counter.currentText()
        time = datetime.now().strftime("%H:%M:%S")

        entry = f"{self.current_number}  →  {counter}  •  {time}  (RECALL)"

        self.history.insert(0, entry)

        self.update_history()

    def update_history(self):
        if not self.history:
            self.history_label.setText("No calls yet")
            return

        text = "\n\n".join(self.history[:8])
        self.history_label.setText(text)


# ─────────────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────────────

app = QApplication(sys.argv)

app.setStyleSheet("""
    QMainWindow {
        background-color: #0f1115;
    }

    QWidget {
        color: #f4f5f7;
        font-family: "Segoe UI";
    }

    #title {
        font-size: 28px;
        font-weight: 700;
    }

    #subtitle {
        color: #8d94a1;
        font-size: 13px;
    }

    #card {
        background-color: #181b21;
        border: 1px solid #292e37;
        border-radius: 16px;
    }

    #section_title {
        color: #ffffff;
        font-size: 15px;
        font-weight: 700;
    }

    #small_label {
        color: #8d94a1;
        font-size: 11px;
        font-weight: 600;
    }

    #queue_display {
        background-color: #101318;
        border: 1px solid #303641;
        border-radius: 12px;
        color: #4da3ff;
        font-size: 58px;
        font-weight: 700;
        min-height: 130px;
    }

    QComboBox {
        background-color: #101318;
        border: 1px solid #303641;
        border-radius: 8px;
        padding: 12px;
        color: white;
        font-size: 14px;
    }

    #call_button {
        background-color: #2878d4;
        border: none;
        border-radius: 10px;
        color: white;
        font-size: 16px;
        font-weight: 700;
    }

    #call_button:hover {
        background-color: #3689e5;
    }

    #secondary_button {
        background-color: #252a33;
        border: 1px solid #343b46;
        border-radius: 10px;
        color: white;
        font-size: 14px;
        font-weight: 600;
    }

    #secondary_button:hover {
        background-color: #303743;
    }

    #key_button {
        background-color: #222730;
        border: 1px solid #343b46;
        border-radius: 8px;
        color: white;
        font-size: 18px;
        font-weight: 600;
    }

    #key_button:hover {
        background-color: #303743;
    }

    #history {
        color: #c8cdd5;
        font-size: 14px;
    }

    #footer {
        color: #707784;
        font-size: 12px;
    }
""")


window = QueueAnnouncer()
window.show()

sys.exit(app.exec())
