import QtQuick
import QtQuick.Window

// Short click-through notification, e.g. "Mute toggled".
Window {
    id: win
    objectName: "toast"

    visible: false
    color: "#1b1f24"
    width: Math.min(label.implicitWidth + 48, Screen.width - 24)
    height: 50
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + 62

    Text {
        id: label
        anchors.centerIn: parent
        text: hc.toastText
        color: "#ffffff"
        font.pixelSize: 18
    }

    Timer {
        id: hideTimer
        interval: 1800
        onTriggered: win.visible = false
    }

    Connections {
        target: hc

        function onToastChanged() {
            win.visible = true
            hideTimer.restart()
        }
    }
}
