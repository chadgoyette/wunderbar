pragma Singleton
import QtQuick 2.15

QtObject {
    // Colors
    readonly property color primaryColor: "#3498db"
    readonly property color dangerColor: "#e74c3c"
    readonly property color backgroundColor: "#202020"
    readonly property color textColor: "white"

    // Fonts
    readonly property QtObject font: QtObject {
    readonly property string family: "Arial"
    }
    
    // Sizes
    readonly property int buttonWidth: 120
    readonly property int buttonHeight: 60
    readonly property int cornerRadius: 8
}
