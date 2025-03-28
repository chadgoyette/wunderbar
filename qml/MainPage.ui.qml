import QtQuick
import QtQuick.Controls
import App 1.0

Item {
    width: 800
    height: 480

    StackView {
        id: stepStack
        objectName: "stepStack"
        anchors.fill: parent
        initialItem: "HomePage.ui.qml"

        Component.onCompleted: {
            AppStackView = stepStack
        }
    }
}
