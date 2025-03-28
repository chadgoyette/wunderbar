/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Controls 2.15
import App 1.0



Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#1c1c1c"
    anchors.fill: parent


    Button {
        id: closeBtn
        x: 581
        width: 154
        height: 70
        text: qsTr("Close")
        background: Rectangle {
            color: "#b00404" // shaded gray background
            radius: 6
        }
        anchors.verticalCenter: parent.verticalCenter
        font.pointSize: 15
        anchors.verticalCenterOffset: 182
        anchors.horizontalCenterOffset: 231
        checkable: true

        Connections {
            function onClicked() {
            stepStack.pop()
            }
        }
    }
    //ComboBox for the flavors
    ComboBox {
        id: flavorCombo
        x: 332
        y: 8
        width: 403
        height: 78

        model: FlavorModel
        textRole: "display"

        // Background color like homepage
        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }

        // Style the currently selected text
        contentItem: Text {
            text: flavorCombo.currentText
            color: "white"                // Change this to any color you like (e.g. "#eaeaea")
            font.pointSize: 20            // Make text larger
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            elide: Text.ElideRight
            anchors.fill: parent
            padding: 10
        }

        Component.onCompleted: {
            if (flavorCombo.count > 0) {
                flavorCombo.currentIndex = 0
                updateSpinboxes(flavorCombo.currentText)
                console.log("Forced flavor selection:", flavorCombo.currentText)
            }
        }

        onCurrentIndexChanged: {
            console.log("Selected flavor:", flavorCombo.currentText)
            updateSpinboxes(flavorCombo.currentText)
        }
    }








    function updateSpinboxes(flavor) {
        console.log("Loading recipe for:", flavor)
        console.log("All flavors:", Object.keys(AppSettings.sizes))

        const sizes = ["Small", "Medium", "Large"];
        const ingredients = ["Flavor", "Yogurt", "Ice"];
        const idMap = {
            "Small": { Flavor: spinBoxSfl, Yogurt: spinBoxSygt, Ice: spinBoxSice },
            "Medium": { Flavor: spinBoxMfl, Yogurt: spinBoxMygt, Ice: spinBoxMice },
            "Large": { Flavor: spinBoxLfl, Yogurt: spinBoxLygt, Ice: spinBoxLice }
        };
        if (!flavor || flavor.length === 0) {
            console.log("No flavor selected, skipping update")
            return
        }

        const recipe = AppSettings.sizes[flavor];
        if (!recipe)
            return;

        for (let size of sizes) {
            const data = recipe[size];
            for (let key of ingredients) {
                let spinBox = idMap[size][key];
                if (spinBox && data && key in data) {
                    spinBox.value = data[key] * 10;  // scale to match SpinBox's integer format

                }
            }
        }
    }
    Component.onCompleted: {
        console.log("Initial flavorCombo.displayText:", flavorCombo.displayText)
        updateSpinboxes(flavorCombo.displayText)
    }


    //Save Button
    Button {
        id: saveBtn
        x: 332
        width: 154
        height: 70
        text: qsTr("Save")
        anchors.verticalCenter: parent.verticalCenter
        font.pointSize: 15
        Connections {
            target: saveBtn
            function onClicked() {
                SettingsManager.save()
            }
        }
        checkable: true
        background: Rectangle {
            color: "#1003e8"
            radius: 6
        }
        anchors.verticalCenterOffset: 182
        anchors.horizontalCenterOffset: 231
    }
    //spin boxes for the ice, yogurt, and flavor
    Item {
        x: 274
        y: 157

        SpinBox {
            id: spinBoxSice
            x: 55
            y: -8
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxSygt
            x: 55
            y: 63
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

           
            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxSfl
            x: 55
            y: 134
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            
            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxMice
            x: 194
            y: -8
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxMygt
            x: 194
            y: 63
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxMfl
            x: 194
            y: 134
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxLice
            x: 335
            y: -8
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxLygt
            x: 335
            y: 63
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }

        SpinBox {
            id: spinBoxLfl
            x: 335
            y: 134
            width: 130
            height: 65
            wrap: false
            stepSize: 1
            spacing: 0
            focusPolicy: Qt.NoFocus
            font.bold: false
            font.pointSize: 20
            property real realValue: value / 10

            

            textFromValue: function(val) {
                return (val / 10).toFixed(1) + " oz"
            }

            valueFromText: function(text) {
                return parseFloat(text) * 10
            }
        }
    }

    Text {
        id: text1
        x: 238
        y: 165
        width: 56
        height: 45
        color: "#eaeaea"
        text: qsTr("Ice")
        font.pixelSize: 35
    }

    Text {
        id: text2
        x: 200
        y: 234
        width: 94
        height: 45
        color: "#eaeaea"
        text: qsTr("Yogurt")
        font.pixelSize: 35
    }

    Text {
        id: text3
        x: 208
        y: 304
        width: 100
        height: 45
        color: "#eaeaea"
        text: qsTr("Flavor")
        font.pixelSize: 35
    }

    Text {
        id: text4
        x: 358
        y: 106
        width: 73
        height: 45
        color: "#eaeaea"
        text: qsTr("Small")
        font.pixelSize: 25
    }

    Text {
        id: text5
        x: 484
        y: 106
        width: 99
        height: 45
        color: "#eaeaea"
        text: qsTr("Medium")
        font.pixelSize: 25
    }

    Text {
        id: text6
        x: 634
        y: 106
        width: 64
        height: 45
        color: "#eaeaea"
        text: qsTr("Large")
        font.pixelSize: 25
    }

    Button {
        id: calBtn
        x: 22
        y: 395
        width: 148
        height: 62
        text: qsTr("Calibration")
        font.pointSize: 15
    }

    SpinBox {
        id: spinBox
        x: 32
        y: 64
        width: 138
        height: 108
        font.pointSize: 35
    }

    Text {
        id: text7
        x: 26
        y: 23
        width: 140
        height: 35
        color: "#eaeaea"
        text: qsTr("Rotor Speed")
        font.pixelSize: 25
        font.styleName: "Bold"
        styleColor: "#eaeaea"
    }
    states: [
        State {
            name: "clicked"
            when: closeBtn.checked
        }
    ]
}
