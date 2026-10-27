import QtQuick
import QtQuick.Window

// Setup assistant. Works with the controller and, for once, with touch.
Window {
    id: win
    objectName: "wizard"

    readonly property var w: hc.wizard

    visible: w.visible === true
    color: "#1b1f24"
    width: Math.min(760, Screen.width - 48)
    height: Math.min(content.implicitHeight + 56, Screen.height - 48)
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + (Screen.height - height) / 2

    Column {
        id: content
        x: 28
        y: 28
        width: win.width - 56
        spacing: 16

        Text {
            text: (win.w.step + 1) + " / " + win.w.total
            color: "#768390"
            font.pixelSize: 14
        }

        Text {
            width: parent.width
            text: win.w.title || ""
            wrapMode: Text.WordWrap
            color: "#ffffff"
            font.pixelSize: 26
            font.bold: true
        }

        Text {
            width: parent.width
            text: win.w.body || ""
            wrapMode: Text.WordWrap
            lineHeight: 1.25
            color: "#cdd5df"
            font.pixelSize: 18
        }

        Flow {
            width: parent.width
            spacing: 12

            Repeater {
                model: win.w.buttons || []

                delegate: Rectangle {
                    width: buttonRow.implicitWidth + 28
                    height: 46
                    radius: 10
                    color: modelData.id === "primary" ? "#14b8a6" : "#2a3038"

                    Row {
                        id: buttonRow
                        anchors.centerIn: parent
                        spacing: 8

                        ButtonGlyph {
                            anchors.verticalCenter: parent.verticalCenter
                            name: modelData.glyph
                        }
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.label
                            color: "#ffffff"
                            font.pixelSize: 17
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: hc.wizardButton(modelData.id)
                    }
                }
            }
        }
    }
}
