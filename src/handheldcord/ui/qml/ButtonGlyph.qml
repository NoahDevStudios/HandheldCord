import QtQuick

// Xbox-style button glyph: coloured face buttons, labelled pills for everything else.
Rectangle {
    id: glyph

    property string name: "A"
    readonly property var faces: ({ "A": "#3fb950", "B": "#f85149", "X": "#4493f8", "Y": "#d29922" })
    readonly property var symbols: ({
        "DPAD_UP": "↑", "DPAD_DOWN": "↓", "DPAD_LEFT": "←", "DPAD_RIGHT": "→",
        "VIEW": "⧉", "MENU": "☰"
    })
    readonly property bool face: faces[name] !== undefined

    implicitHeight: 24
    implicitWidth: face ? implicitHeight : Math.max(implicitHeight, label.implicitWidth + 12)
    radius: face ? height / 2 : 6
    color: face ? faces[name] : "#373e47"
    border.width: face ? 0 : 1
    border.color: "#545d68"

    Text {
        id: label
        anchors.centerIn: parent
        text: glyph.symbols[glyph.name] || glyph.name
        color: "#ffffff"
        font.pixelSize: glyph.face ? 14 : 12
        font.bold: true
    }
}
