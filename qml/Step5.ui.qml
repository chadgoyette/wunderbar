

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import Wunderbar_POC_UI
import App 1.0

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#1c1c1c"

    Button {
        id: button
        x: 517
        width: 154
        height: 70
        text: qsTr("Next")
        background: Rectangle {
            color: "#1003e8" // shaded gray background
            radius: 6
        }
        anchors.verticalCenter: parent.verticalCenter
        font.pointSize: 15
        anchors.verticalCenterOffset: -55
        anchors.horizontalCenterOffset: 231
        checkable: true

        Connections {
            target: button
            onClicked: animation.start()
        }
    }

    Text {
        id: dynamicLabel
        width: 191
        height: 62
        color: "#eaeaea"
        text: qsTr("Tarring Cup...")
        anchors.top: button.bottom
        font.family: Constants.font.family
        anchors.topMargin: -153
        anchors.horizontalCenter: parent.horizontalCenter
        font.pointSize: 22
        font.styleName: "Bold"

        SequentialAnimation {
            id: animation

            ColorAnimation {
                id: colorAnimation1
                target: rectangle
                property: "color"
                to: "#2294c6"
                from: Constants.backgroundColor
            }

            ColorAnimation {
                id: colorAnimation2
                target: rectangle
                property: "color"
                to: Constants.backgroundColor
                from: "#2294c6"
            }
        }
    }

    Rectangle {
        id: rectangle1
        height: 243
        color: "#1c1c1c"
        radius: 10
        border.color: "#eaeaea"
        border.width: 3
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 328
        anchors.rightMargin: 353
        anchors.bottomMargin: 102

        Rectangle {
            id: dynamicFill
            x: 0
            y: 182
            width: 119
            height: 0
            color: "#b00404"
            radius: 10
        }
    }

    Label {
        id: label
        y: 18
        width: 121
        height: 31
        text: qsTr("Add Flavor")
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenter: parent.horizontalCenter
        font.weight: Font.Bold
        font.pointSize: 22
    }
    states: [
        State {
            name: "clicked"
            when: button.checked

            PropertyChanges {
                target: dynamicLabel
                text: qsTr("Button Checked")
            }
        }
    ]
}
