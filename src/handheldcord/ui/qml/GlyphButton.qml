import QtQuick

// Touchable button showing a controller glyph and an optional label.
Rectangle {
    id: button

    property string glyph: "A"
    property string label: ""
    property bool primary: false
    signal tapped()

    implicitWidth: row.implicitWidth + 24
    implicitHeight: 40
    radius: 9
    color: primary ? "#14b8a6" : "#2a3038"

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 8

        ButtonGlyph {
            anchors.verticalCenter: parent.verticalCenter
            name: button.glyph
        }
        Text {
            visible: button.label !== ""
            anchors.verticalCenter: parent.verticalCenter
            text: button.label
            color: "#ffffff"
            font.pixelSize: 15
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: button.tapped()
    }
}
