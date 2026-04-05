import QtQuick
import QtQuick.Controls

Item {
    required property QtObject panelModel
    anchors.fill: parent

    WindowSelectionDialog {
        id: windowSelectionDialog
        windowSelectionDialogModel: panelModel.windowSelectionDialogModel
    }

    Connections {
        target: panelModel

        function onOpenWindowSelectionDialogRequested() {
            windowSelectionDialog.open()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#3F3F3F"

        Rectangle {
            objectName: "overlayTarget"
            anchors.fill: parent
            anchors.margins: 4
            color: "#202020"

            Button {
                anchors.centerIn: parent
                visible: !panelModel.isWindowAttached
                text: "Attach Window"
                onClicked: panelModel.openWindowSelectionDialog()
            }
        }
    }
}