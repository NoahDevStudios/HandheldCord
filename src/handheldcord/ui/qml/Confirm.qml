import QtQuick
import QtQuick.Window

// Yes/no question, e.g. before leaving a call. Ⓐ = yes, Ⓑ = no.
Window {
    id: win
    objectName: "confirm"

    readonly property var c: hc.confirm

    visible: c.visible === true
    color: "#1b1f24"
    width: Math.min(440, Screen.width - 32)
    height: column.implicitHeight + 44
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + (Screen.height - height) / 2

    Column {
        id: column
        x: 24
        y: 22
        width: win.width - 48
        spacing: 14

        Text {
            width: parent.width
            text: win.c.title || ""
            wrapMode: Text.WordWrap
            color: "#ffffff"
            font.pixelSize: 22
            font.bold: true
        }

        Text {
            width: parent.width
            text: win.c.body || ""
            wrapMode: Text.WordWrap
            color: "#cdd5df"
            font.pixelSize: 16
        }

        Row {
            spacing: 12

            GlyphButton {
                glyph: "A"
                label: win.c.yes || ""
                primary: true
                onTapped: hc.confirmAnswer(true)
            }
            GlyphButton {
                glyph: "B"
                label: win.c.no || ""
                onTapped: hc.confirmAnswer(false)
            }
        }
    }
}
