/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import App 1.0

Rectangle {
    id: rectangle
    anchors.fill: parent  // Ensure no conflicting anchors
    color: "#1c1c1c"

    property bool motorRunning: false
    property bool motorDone: false
    property real targetWeight: {
        const flavor = AppState.selectedFlavor
        const size = AppState.selectedSize
        const sizes = AppSettings.sizes

        console.log("DEBUG Step2 - Flavor:", flavor)
        console.log("DEBUG Step2 - Size:", size)

        if (sizes && sizes[flavor] && sizes[flavor][size]) {
            const ice = sizes[flavor][size]["Ice"]
            console.log("DEBUG Step2 - Target ICE weight =", ice)
            return ice
        }

        console.log("DEBUG Step2 - Missing data. Fallback to 1.")
        return 1.0
    }

    Timer {
        id: motorStartDelay
        interval: 3000
        running: false  // Start manually on Component.onCompleted
        repeat: false
        onTriggered: {
            console.log("⏳ Motor delay done — attempting to start motor")
            MotorController.start_motor()
            console.log("✅ Motor start command issued.")
            motorRunning = true
            statusLabel.text = "Shaving Ice..."
            stabilizationDelay.start()  // Start stabilization delay
        }
    }

    Timer {
        id: stabilizationDelay
        interval: 2000  // 2-second delay for load cell stabilization
        running: false
        repeat: false
        onTriggered: {
            console.log("✅ Stabilization complete — starting weight polling")
            weightPoller.start()
        }
    }

    Timer {
        id: weightPoller
        interval: 100  // Reduced interval for better responsiveness
        repeat: true
        running: false
        onTriggered: {
            const g = LoadCellReader.weight || 0
            const oz = Math.max(g * 0.035274, 0);  // Ensure no negative weights
            console.log("DEBUG: Current weight:", oz.toFixed(2), "oz")
            weightLabel.text = oz.toFixed(2) + " oz / " + targetWeight.toFixed(1) + " oz"
            if (motorRunning && !motorDone && oz >= targetWeight) {
                console.log("✅ Target reached – stopping motor")
                MotorController.stop_motor()
                motorRunning = false
                motorDone = true
                statusLabel.text = "Shaving Complete!"
                weightPoller.stop()
            } else if (!motorRunning) {
                console.log("⚠️ Motor is not running but weightPoller is active.")
            }
        }
    }

    Text {
        id: statusLabel
        text: "Motor Starting!!!"
        font.pixelSize: 24
        color: "yellow"
        anchors.top: weightLabel.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 10
    }

    Text {
        id: weightLabel
        text: "0.00 oz"
        font.pixelSize: 28
        color: "white"
        z: 10
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        anchors.top: parent.top
        anchors.topMargin: 20
    }

    Button {
        id: abortButton
        text: "Abort"
        width: 120
        height: 50
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.bottomMargin: 20
        anchors.rightMargin: 20
        background: Rectangle {
            color: "#b00404"
            radius: 6
        }
        onClicked: {
            MotorController.stop_motor()
            motorRunning = false
            weightPoller.stop()
            AppStackView.pop()
        }
    }

    Rectangle {
        id: progressBar
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
        //height: 243
        Rectangle {
            id: dynamicFill
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: {
                const g = LoadCellReader.weight || 0
                const oz = g * 0.035274
                return Math.min(oz / targetWeight, 1.0) * parent.height
            }
            color: {
                const g = LoadCellReader.weight || 0
                const oz = g * 0.035274
                const percent = Math.min(oz / targetWeight, 1.0)
                return Qt.rgba(1 - percent, percent, 0, 1)
            }
        }
    }

    Label {
        id: label
        text: qsTr("Ice Shaving")
        font.weight: Font.Bold
        font.pointSize: 22
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10
    }

    Component.onCompleted: {
        console.log("📦 Step2 loaded — initializing load cell and starting motor delay timer")
        LoadCellReader.tare()  // Tare the load cell before starting the motor
        motorStartDelay.start()  // Start motor delay directly
    }
}