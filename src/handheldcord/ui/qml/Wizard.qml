import QtQuick
import QtQuick.Window

// Setup assistant, docked in a corner so Discord stays readable behind it.
// Ⓨ collapses it into a small pill, ⧉ moves it to the next corner, touch can drag it by its header.
Window {
    id: win
    objectName: "wizard"

    readonly property var w: hc.wizard
    readonly property bool collapsed: w.collapsed === true
    readonly property int margin: 16
    property bool dragged: false
    property string lastPosition: ""

    visible: w.visible === true
    color: "#1b1f24"
    width: collapsed ? pill.implicitWidth + 32 : Math.min(500, Screen.width * 0.45)
    height: collapsed ? 48 : Math.min(content.implicitHeight + 36, Screen.height - 2 * margin)

    function place() {
        if (dragged)
            return
        const position = w.position || "bottom-right"
        x = Screen.virtualX + (position.endsWith("left") ? margin : Screen.width - width - margin)
        y = Screen.virtualY + (position.startsWith("top") ? margin : Screen.height - height - margin)
    }

    onWChanged: {
        if ((w.position || "") !== lastPosition) {
            lastPosition = w.position || ""
            dragged = false  // ⧉ docks it again after a manual drag
        }
        place()
    }
    onWidthChanged: place()
    onHeightChanged: place()
    Component.onCompleted: place()

    // Collapsed: a small pill that brings the assistant back.
    Row {
        id: pill
        visible: win.collapsed
        anchors.centerIn: parent
        spacing: 8

        ButtonGlyph {
            anchors.verticalCenter: parent.verticalCenter
            name: "Y"
        }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: win.w.expandLabel || ""
            color: "#ffffff"
            font.pixelSize: 16
        }
    }

    MouseArea {
        visible: win.collapsed
        anchors.fill: parent
        onClicked: hc.wizardButton("collapse")
    }

    Column {
        id: content
        visible: !win.collapsed
        x: 20
        y: 16
        width: win.width - 40
        spacing: 12

        // Header: step counter and collapse button; dragging it moves the window.
        Item {
            width: parent.width
            height: 30

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: (win.w.step + 1) + " / " + win.w.total
                color: "#768390"
                font.pixelSize: 13
            }

            MouseArea {
                property point grab
                anchors.fill: parent
                cursorShape: Qt.SizeAllCursor
                onPressed: mouse => grab = Qt.point(mouse.x, mouse.y)
                onPositionChanged: mouse => {
                    win.dragged = true
                    win.x += mouse.x - grab.x
                    win.y += mouse.y - grab.y
                }
            }

            Rectangle {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                width: 30
                height: 30
                radius: 6
                color: "#2a3038"

                Text {
                    anchors.centerIn: parent
                    text: "–"
                    color: "#ffffff"
                    font.pixelSize: 18
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: hc.wizardButton("collapse")
                }
            }
        }

        Text {
            width: parent.width
            text: win.w.title || ""
            wrapMode: Text.WordWrap
            color: "#ffffff"
            font.pixelSize: 22
            font.bold: true
        }

        Text {
            width: parent.width
            text: win.w.body || ""
            wrapMode: Text.WordWrap
            lineHeight: 1.2
            color: "#cdd5df"
            font.pixelSize: 16
        }

        // Key picker (◀ ▶) on steps that choose a handheld key.
        Row {
            visible: !!win.w.key
            spacing: 10

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: win.w.key ? win.w.key.caption : ""
                color: "#cdd5df"
                font.pixelSize: 16
            }
            GlyphButton {
                glyph: "DPAD_LEFT"
                onTapped: hc.wizardButton("key_prev")
            }
            Rectangle {
                width: keyLabel.implicitWidth + 32
                height: 40
                radius: 9
                color: "#0f766e"

                Text {
                    id: keyLabel
                    anchors.centerIn: parent
                    text: win.w.key ? win.w.key.label : ""
                    color: "#ffffff"
                    font.pixelSize: 20
                    font.bold: true
                }
            }
            GlyphButton {
                glyph: "DPAD_RIGHT"
                onTapped: hc.wizardButton("key_next")
            }
        }

        Flow {
            width: parent.width
            spacing: 10

            Repeater {
                model: win.w.buttons || []

                delegate: GlyphButton {
                    glyph: modelData.glyph
                    label: modelData.label
                    primary: modelData.id === "primary"
                    onTapped: hc.wizardButton(modelData.id)
                }
            }
        }

        Flow {
            width: parent.width
            spacing: 10

            Repeater {
                model: win.w.controls || []

                delegate: GlyphButton {
                    implicitHeight: 32
                    glyph: modelData.glyph
                    label: modelData.label
                    color: "transparent"
                    border.width: 1
                    border.color: "#373e47"
                    onTapped: hc.wizardButton(modelData.id)
                }
            }
        }
    }
}
