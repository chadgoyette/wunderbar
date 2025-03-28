import QtQuick
import QtQuick.Controls
import App 1.0

Rectangle {
    id: mainUI
    width: 800
    height: 480
    color: "#1c1c1c"

    property bool motorStopped: false
    property int state: 0

    // Flavor dropdown
    ComboBox {
        id: flavorDropdown
        width: 275
        height: 80
        model: FlavorModel
        textRole: "display"
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: parent.top
        anchors.topMargin: 20
        background: Rectangle {
            color: "#444"
            radius: 6
        }
        contentItem: Text {
            text: flavorDropdown.currentText
            color: "white"
            font.pointSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            elide: Text.ElideRight
            anchors.fill: parent
            padding: 10
        }
        onCurrentIndexChanged: {
            AppState.selectedFlavor = flavorDropdown.currentText
            console.log("Selected flavor:", AppState.selectedFlavor)
        }
    }

    // Size buttons
    Row {
        id: sizeButtons
        spacing: 10
        anchors.left: flavorDropdown.right
        anchors.leftMargin: 20
        anchors.verticalCenter: flavorDropdown.verticalCenter

        Button {
            id: smallBtn
            text: "Small"
            width: 100
            height: 50
            checkable: true
            background: Rectangle {
                color: AppState.selectedSize === "Small" ? "#2294c6" : "#444"
                radius: 6
            }
            onClicked: {
                AppState.selectedSize = "Small"
                console.log("Selected size: Small")
            }
        }

        Button {
            id: mediumBtn
            text: "Medium"
            width: 100
            height: 50
            checkable: true
            background: Rectangle {
                color: AppState.selectedSize === "Medium" ? "#2294c6" : "#444"
                radius: 6
            }
            onClicked: {
                AppState.selectedSize = "Medium"
                console.log("Selected size: Medium")
            }
        }

        Button {
            id: largeBtn
            text: "Large"
            width: 100
            height: 50
            checkable: true
            background: Rectangle {
                color: AppState.selectedSize === "Large" ? "#2294c6" : "#444"
                radius: 6
            }
            onClicked: {
                AppState.selectedSize = "Large"
                console.log("Selected size: Large")
            }
        }
    }

    // Start button
    Button {
        id: startButton
        text: "Start"
        width: 120
        height: 60
        anchors.left: flavorDropdown.left
        anchors.top: flavorDropdown.bottom
        anchors.topMargin: 20
        background: Rectangle {
            color: "green"
            radius: 6
        }
        onClicked: {
            if (!AppState.selectedSize || !AppState.selectedFlavor) {
                instructionLabel.text = "Please select a flavor and size!";
                return;
            }
            console.log("Starting process with flavor:", AppState.selectedFlavor, "and size:", AppState.selectedSize);
            instructionLabel.text = "Process started. Please follow the instructions.";
            motorStopped = false;
            state = 1;  // Set the initial state
            updateUIForState();  // Update the UI for the new state
        }
    }

    // Instruction label
    Text {
        id: instructionLabel
        text: "Configure options and press Start"
        font.pointSize: 20
        color: "white"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: startButton.bottom
        anchors.topMargin: 20
    }

    // Next button
    Button {
        id: nextButton
        text: "Next"
        width: 120
        height: 60
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: instructionLabel.bottom
        anchors.topMargin: 20
        visible: false
        background: Rectangle {
            color: "blue"
            radius: 6
        }
        onClicked: {
            console.log("Next button clicked, current state:", state);
            if (state === 1) {
                instructionLabel.text = "Taring cup, please wait...";
                LoadCellReader.tare();
                state = 2;  // Transition to the next state
                updateUIForState();
            } else if (state === 2) {
                MotorController.stop_motor();
                weightPoller.stop();
                instructionLabel.text = "Ice shaving complete. Add flavor until target weight is reached.";
                state = 3;  // Transition to the next state
                updateUIForState();
            } else if (state === 3) {
                weightPoller.stop();
                instructionLabel.text = "Flavor addition complete. Process finished.";
                state = 4;  // Transition to the final state
                updateUIForState();
            }
        }
    }

    // Weight poller
    Timer {
        id: weightPoller
        interval: 100
        repeat: true
        running: false
        onTriggered: {
            const weight = LoadCellReader.weight || 0
            const target = state === 2 ? AppSettings.sizes[AppState.selectedFlavor][AppState.selectedSize].Ice : AppSettings.sizes[AppState.selectedFlavor][AppState.selectedSize].Flavor
            instructionLabel.text = `Current weight: ${weight.toFixed(2)} oz (Target: ${target.toFixed(2)} oz)`
            if (weight >= target) {
                nextButton.visible = true
            }
        }
    }

    // Exit button
    Button {
        id: exitButton
        text: "Exit"
        width: 120
        height: 60
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        background: Rectangle {
            color: "red"
            radius: 6
        }
        onClicked: Qt.quit()
    }

    function updateUIForState() {
        console.log("DEBUG: Current state:", state);
        if (state === 1) {
            instructionLabel.text = "Place your cup and then press Next.";
            nextButton.text = "Next";
            nextButton.visible = true;
        } else if (state === 2) {
            instructionLabel.text = "Shaving ice... Please wait.";
            nextButton.visible = false;
        } else if (state === 3) {
            instructionLabel.text = "Add flavor until target weight is reached.";
            nextButton.visible = false;
        } else if (state === 4) {
            instructionLabel.text = "Process complete. Enjoy!";
            nextButton.visible = false;
        } else {
            console.log("DEBUG: Unknown state:", state);
        }
    }
}
