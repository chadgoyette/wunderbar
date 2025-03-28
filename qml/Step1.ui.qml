/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
//import Wunderbar_POC_UI
import App 1.0

Rectangle {
    id: rectangle
    anchors.fill: parent  // Ensure no conflicting anchors
    color: "#1c1c1c"

    property bool tareComplete: false

    Connections {
        target: LoadCellReader
        function onTareCompleted() {  // Fix syntax error here
            console.log("✅ Backend tare confirmed")
            rectangle.tareComplete = true
            label.text = "Tare complete"
            nextBtn.visible = true
        }
    }

    Button {
        id: backBtn
        text: qsTr("Back")
        width: 154
        height: 70
        font.pointSize: 15
        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20

        onClicked: {
            if (AppStackView.depth > 1)
                AppStackView.pop()
        }
    }

    Text {
        id: label
        text: qsTr("Place Cup on Scale")
        anchors.centerIn: parent
        font.family: Constants.font.family
        font.pointSize: 26
        color: "#eaeaea"
        font.styleName: "Bold"
    }

    Button {
        id: okBtn
        text: qsTr("OK")
        width: 154
        height: 70
        font.pointSize: 15
        anchors.verticalCenter: label.verticalCenter
        anchors.left: label.right
        anchors.leftMargin: 20

        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }

        onClicked: {
            console.log("OK clicked — starting tare")
            label.text = "Taring..."
            rectangle.tareComplete = false
            okBtn.visible = false
            LoadCellReader.initialize_sensor()  // Explicitly initialize the load cell
            LoadCellReader.tare()  // Trigger taring here
        }
    }

    Button {
        id: nextBtn
        text: qsTr("Next")
        width: 154
        height: 70
        font.pointSize: 15
        visible: false
        anchors.bottom: backBtn.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 20

        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }

        onClicked: {
            console.log("Next clicked — proceeding to Step2")
            AppStackView.push("Step2.ui.qml")
        }
    }

    Component.onCompleted: {
        console.log("✅ Step1 loaded")
    }
}
