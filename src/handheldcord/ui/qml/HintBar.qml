import QtQuick
import QtQuick.Window

// Click-through bar at the top of the screen showing what each button does right now.
Window {
    id: win
    objectName: "hintBar"

    visible: hc.hintsVisible
    color: "#1b1f24"
    width: Math.min(hintRow.implicitWidth + 32, Screen.width - 24)
    height: 42
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + 10

    Row {
        id: hintRow
        anchors.centerIn: parent
        spacing: 16
        // Shrink instead of clipping on narrow (high-DPI) screens.
        scale: Math.min(1, (win.width - 24) / Math.max(1, implicitWidth))

        Repeater {
            model: hc.hints

            delegate: Row {
                id: hint
                property var entry: modelData
                spacing: 6

                Repeater {
                    model: hint.entry.buttons

                    delegate: Row {
                        spacing: 3

                        Text {
                            visible: index > 0
                            anchors.verticalCenter: parent.verticalCenter
                            text: hint.entry.joiner
                            color: "#8b949e"
                            font.pixelSize: 13
                        }
                        ButtonGlyph {
                            name: modelData
                        }
                    }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: hint.entry.label
                    color: "#e6edf3"
                    font.pixelSize: 15
                }
            }
        }
    }
}
