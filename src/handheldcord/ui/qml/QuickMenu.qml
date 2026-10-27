import QtQuick
import QtQuick.Window

// Quick menu: quick replies, favorites, voice and app actions.
Window {
    id: win
    objectName: "menu"

    readonly property var m: hc.menu
    readonly property var items: hc.menuItems
    readonly property int rowHeight: 48
    readonly property int headerHeight: 30
    readonly property int headerCount: items.filter(item => item.header !== "").length

    visible: m.visible === true
    color: "#1b1f24"
    width: Math.min(560, Screen.width - 32)
    height: Math.min(title.height + 44 + items.length * rowHeight + headerCount * headerHeight, Screen.height - 64)
    x: Screen.virtualX + (Screen.width - width) / 2
    y: Screen.virtualY + (Screen.height - height) / 2

    Text {
        id: title
        x: 24
        y: 18
        text: win.m.title || ""
        color: "#ffffff"
        font.pixelSize: 22
        font.bold: true
    }

    ListView {
        id: list
        x: 16
        y: title.y + title.height + 10
        width: win.width - 32
        height: win.height - y - 12
        clip: true
        model: win.items
        currentIndex: win.m.index !== undefined ? win.m.index : -1
        onCurrentIndexChanged: if (currentIndex >= 0) positionViewAtIndex(currentIndex, ListView.Contain)

        delegate: Column {
            width: list.width

            Text {
                visible: modelData.header !== ""
                height: win.headerHeight
                verticalAlignment: Text.AlignBottom
                leftPadding: 12
                bottomPadding: 4
                text: modelData.header
                color: "#8b949e"
                font.pixelSize: 13
                font.capitalization: Font.AllUppercase
            }

            Rectangle {
                width: parent.width
                height: win.rowHeight
                radius: 8
                color: index === list.currentIndex ? "#14b8a6" : "transparent"

                Text {
                    x: 14
                    width: parent.width - 28
                    anchors.verticalCenter: parent.verticalCenter
                    text: modelData.label
                    elide: Text.ElideRight
                    color: "#ffffff"
                    font.pixelSize: 18
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: hc.menuTap(index)
                }
            }
        }
    }
}
