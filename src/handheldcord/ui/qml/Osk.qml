import QtQuick
import QtQuick.Window

// On-screen keyboard. It never takes the focus, so the committed text lands in Discord.
Window {
    id: win
    objectName: "osk"

    readonly property var kb: hc.osk
    readonly property int gap: 6
    // The widest row is 11.5 key units with 11 gaps.
    readonly property real unit: (width - 32 - 11 * gap) / 11.5

    visible: kb.visible === true
    color: "#14171b"
    width: Math.min(Screen.width - 32, 1100)
    height: column.implicitHeight + 32
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + Screen.height - height - 24

    Column {
        id: column
        x: 16
        y: 16
        width: win.width - 32
        spacing: win.gap + 2

        Rectangle {
            id: preview
            width: parent.width
            height: 56
            radius: 10
            color: "#232830"
            clip: true

            Row {
                x: 16
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    id: before
                    width: Math.min(implicitWidth, preview.width - 40 - after.width)
                    text: win.kb.before || ""
                    elide: Text.ElideLeft
                    color: "#ffffff"
                    font.pixelSize: 24
                }
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: 2
                    height: 30
                    color: "#2dd4bf"
                }
                Text {
                    id: after
                    width: Math.min(implicitWidth, (preview.width - 40) / 3)
                    text: win.kb.after || ""
                    elide: Text.ElideRight
                    color: "#ffffff"
                    font.pixelSize: 24
                }
            }

            Text {
                visible: !win.kb.before && !win.kb.after
                x: 24
                anchors.verticalCenter: parent.verticalCenter
                text: win.kb.placeholder || ""
                color: "#768390"
                font.pixelSize: 22
            }
        }

        Repeater {
            model: hc.oskRows

            delegate: Row {
                id: keyRow
                property int rowIndex: index
                property var keys: modelData
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: win.gap

                Repeater {
                    model: keyRow.keys

                    delegate: Rectangle {
                        readonly property bool selected: keyRow.rowIndex === win.kb.row && index === win.kb.col

                        width: win.unit * modelData.width + win.gap * (modelData.width - 1)
                        height: 52
                        radius: 8
                        z: selected ? 1 : 0
                        scale: selected ? 1.06 : 1.0
                        color: selected ? "#14b8a6"
                             : modelData.active ? "#0f766e"
                             : modelData.kind === "char" ? "#2a3038" : "#363d47"
                        border.width: selected ? 2 : 0
                        border.color: "#99f6e4"

                        Text {
                            anchors.centerIn: parent
                            text: modelData.label
                            color: "#ffffff"
                            font.pixelSize: modelData.kind === "char" ? 22 : 16
                            font.bold: modelData.kind !== "char"
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: hc.oskTap(keyRow.rowIndex, index)
                        }
                    }
                }
            }
        }
    }
}
