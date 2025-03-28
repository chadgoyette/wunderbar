// File: qml/MainApp.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 480

    Loader {
        anchors.fill: parent
        source: "MainPage.ui.qml"
        //source: "MainUI.qml"
    }
}
