"""On-screen keyboard model: layouts, highlight navigation and the text buffer."""
from __future__ import annotations

from dataclasses import dataclass

LETTER_ROWS = {
    "de": ("1234567890ß", "qwertzuiopü", "asdfghjklöä", "yxcvbnm,.-"),
    "en": ("1234567890-", "qwertyuiop", "asdfghjkl'", "zxcvbnm,.?"),
}
SYMBOL_ROWS = ("!?@#&%+=*/", "()\"':;_-<>", "$€§~^|\\[]{}")
EMOJI_ROW = ("👍", "😂", "❤️", "🔥", "😅", "🎮", "👋", "🙏", "😭", "💀")
VARIATION_SELECTOR = "️"


@dataclass(frozen=True)
class Key:
    kind: str  # char, shift, symbols, space, backspace, insert, send
    value: str = ""
    width: float = 1.0


class OskModel:
    def __init__(self, layout: str = "en", labels: dict[str, str] | None = None) -> None:
        self.layout = layout if layout in LETTER_ROWS else "en"
        self.labels = labels or {}
        self.text = ""
        self.cursor = 0
        self.shift = False
        self.symbols = False
        self.rows = self._build()
        self.row, self.col = 1, 0

    def clear(self) -> None:
        self.text = ""
        self.cursor = 0
        self.shift = False

    @property
    def current(self) -> Key:
        return self.rows[self.row][self.col]

    def move(self, d_row: int, d_col: int) -> None:
        if d_col:
            self.col = (self.col + d_col) % len(self.rows[self.row])
        if d_row:
            # Rows have different lengths: keep the horizontal position, not the index.
            x = self._center(self.row, self.col)
            self.row = (self.row + d_row) % len(self.rows)
            self.col = self._key_at(self.row, x)

    def select(self, row: int, col: int) -> bool:
        if 0 <= row < len(self.rows) and 0 <= col < len(self.rows[row]):
            self.row, self.col = row, col
            return True
        return False

    def press(self) -> str | None:
        """Activate the highlighted key; returns "insert" or "send" to commit the text."""
        key = self.current
        if key.kind == "char":
            self.insert(key.value)
        elif key.kind == "shift":
            self.toggle_shift()
        elif key.kind == "symbols":
            self.toggle_symbols()
        elif key.kind == "space":
            self.insert(" ")
        elif key.kind == "backspace":
            self.backspace()
        elif key.kind in ("insert", "send"):
            return key.kind
        return None

    def insert(self, value: str) -> None:
        if self.shift and value.isalpha():
            value = _shifted(value)
            self.shift = False
        self.text = self.text[:self.cursor] + value + self.text[self.cursor:]
        self.cursor += len(value)

    def backspace(self) -> None:
        if not self.cursor:
            return
        start = self.cursor - 1
        if self.text[start] == VARIATION_SELECTOR and start > 0:
            start -= 1  # "❤️" is two code points
        self.text = self.text[:start] + self.text[self.cursor:]
        self.cursor = start

    def cursor_left(self) -> None:
        self.cursor = max(0, self.cursor - 1)

    def cursor_right(self) -> None:
        self.cursor = min(len(self.text), self.cursor + 1)

    def toggle_shift(self) -> None:
        self.shift = not self.shift

    def toggle_symbols(self) -> None:
        x = self._center(self.row, self.col)
        self.symbols = not self.symbols
        self.rows = self._build()
        self.row = min(self.row, len(self.rows) - 1)
        self.col = self._key_at(self.row, x)

    def snapshot(self) -> dict:
        return {
            "rows": [
                [{"label": self._label(k), "kind": k.kind, "width": k.width, "active": self._active(k)} for k in row]
                for row in self.rows
            ],
            "row": self.row,
            "col": self.col,
            "before": self.text[:self.cursor],
            "after": self.text[self.cursor:],
            "placeholder": self.labels.get("placeholder", ""),
        }

    def _build(self) -> list[list[Key]]:
        if self.symbols:
            rows = [[Key("char", c) for c in chars] for chars in SYMBOL_ROWS]
            rows.append([Key("char", e) for e in EMOJI_ROW])
        else:
            letters = LETTER_ROWS[self.layout]
            rows = [[Key("char", c) for c in chars] for chars in letters[:3]]
            rows.append([Key("shift", width=1.5)] + [Key("char", c) for c in letters[3]])
        rows.append([
            Key("symbols", width=1.5),
            Key("space", width=4),
            Key("backspace", width=1.5),
            Key("insert", width=2),
            Key("send", width=2.5),
        ])
        return rows

    def _label(self, key: Key) -> str:
        if key.kind == "char":
            if self.shift and not self.symbols and key.value.isalpha():
                return _shifted(key.value)
            return key.value
        if key.kind == "shift":
            return "⇧"
        if key.kind == "symbols":
            return "ABC" if self.symbols else "?123"
        if key.kind == "backspace":
            return "⌫"
        return self.labels.get(key.kind, key.kind)

    def _active(self, key: Key) -> bool:
        return (key.kind == "shift" and self.shift) or (key.kind == "symbols" and self.symbols)

    def _center(self, row: int, col: int) -> float:
        keys = self.rows[row]
        total = sum(k.width for k in keys)
        left = sum(k.width for k in keys[:col])
        return (left + keys[col].width / 2) / total

    def _key_at(self, row: int, x: float) -> int:
        keys = self.rows[row]
        total = sum(k.width for k in keys)
        edge = 0.0
        for index, key in enumerate(keys):
            edge += key.width
            if x <= edge / total:
                return index
        return len(keys) - 1


def _shifted(char: str) -> str:
    upper = char.upper()
    return upper if len(upper) == len(char) else char  # "ß".upper() would be "SS"
