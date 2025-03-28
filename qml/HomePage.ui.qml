/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
//mport Wunderbar_POC_UI
import App 1.0

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#1c1c1c"


    Button {
        id: startBtn
        width: 117
        height: 162
        text: qsTr("Start")
        background: Rectangle {
            color: "#0a9721"
            // shaded gray background
            radius: 6
        }
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 0
        anchors.horizontalCenterOffset: 262
        checkable: true
        anchors.horizontalCenter: parent.horizontalCenter
        enabled: flavorCombo.currentIndex >= 0 && AppState.selectedSize
.length > 0
        onClicked: {
            console.log("Start clicked")
            AppStackView.push("Step1.ui.qml")  // ✅ Use the global stack reference
        }
    }
   

    Text {
        id: label
        width: 361
        height: 67
        color: "#eaeaea"
        text: qsTr("Choose the Flavor and Size")
        anchors.top: startBtn.bottom
        font.family: Constants.font.family
        anchors.topMargin: -108
        font.pointSize: 20
        font.styleName: "Bold"
        anchors.horizontalCenterOffset: -45
        anchors.horizontalCenter: parent.horizontalCenter

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

    Button {
        id: smallBtn
        x: 354
        y: 61
        width: 118
        height: 75
        text: qsTr("Small")
        checkable: true
        onClicked: {
            if (AppState) {
                AppState.selectedSize = "Small"
            } else {
                console.error("AppState is null!")
            }
        }
        background: Rectangle {
            color: AppState && AppState.selectedSize === "Small" ? "#2294c6" : "#1003e8"
            radius: 6
        }
    }

    Button {
        id: mediumBtn
        x: 478
        y: 61
        width: 118
        height: 75
        text: qsTr("Medium")
        checkable: true
        onClicked: {
            if (AppState) {
                AppState.selectedSize = "Medium"
            } else {
                console.error("AppState is null!")
            }
        }
        background: Rectangle {
            color: AppState && AppState.selectedSize === "Medium" ? "#2294c6" : "#1003e8"
            radius: 6
        }
    }

    Button {
        id: largeBtn
        x: 602
        y: 61
        width: 118
        height: 75
        text: qsTr("Large")
        checkable: true
        onClicked: {
            if (AppState) {
                AppState.selectedSize = "Large"
            } else {
                console.error("AppState is null!")
            }
        }
        background: Rectangle {
            color: AppState && AppState.selectedSize === "Large" ? "#2294c6" : "#1003e8"
            radius: 6
        }
    }


    ComboBox {
        id: flavorCombo
        width: 287
        height: 75
        model: FlavorModel
        textRole: "display"

        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }

        contentItem: Text {
            text: flavorCombo.currentText
            color: "white"
            font.pointSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            elide: Text.ElideRight
            anchors.fill: parent
            padding: 10
        }

        onCurrentIndexChanged: {
            AppState.selectedFlavor = flavorCombo.currentText
            console.log("Selected flavor from combo:", AppState.selectedFlavor)
        }

        Component.onCompleted: {
            // Force first item to be selected if none yet
            if (currentIndex < 0 && count > 0) {
                currentIndex = 0
            }
            AppState.selectedFlavor = currentText
            console.log("Auto-selected flavor:", AppState.selectedFlavor)
        }
    }

    Text {
    x: 50
    y: 150
    color: "white"
    text: "Flavor: " + flavorCombo.currentText + ", Size: " + AppState.selectedSize

    }

    Button {
        id: exitBtn
        x: 603
        y: 411
        width: 118
        height: 32
        text: qsTr("Exit")
        background: Rectangle {
            color: "#a90404" // shaded gray background
            radius: 6
        }
        onClicked: Qt.quit()
    }

    Button {
        id: settingBtn
        x: 44
        y: 411
        width: 84
        height: 32
        text: qsTr("Settings")
        background: Rectangle {
            color: "#1003e8" // shaded gray background
            radius: 6
        }
        onClicked: {
            AppStackView.push("Settings.ui.qml")
        }
    }
    states: [
        State {
            name: "clicked"
            when: startBtn.checked

            PropertyChanges {
                target: label
                text: qsTr("Button Checked")
            }
        }
    ]
}
