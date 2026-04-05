import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    required property QtObject windowSelectionDialogModel
    parent: Overlay.overlay
    modal: true
    width: Math.round(parent.width * 0.8)
    height: Math.round(parent.height * 0.8)
    x: Math.round((parent.width - width) * 0.5)
    y: Math.round((parent.height - height) * 0.5)

    onAccepted: windowSelectionDialogModel.accept()
    onRejected: windowSelectionDialogModel.reject()

    ColumnLayout {
        anchors.fill: parent

        ListView {
            id: windowListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: windowSelectionDialogModel.listModel
            currentIndex: windowSelectionDialogModel.listModel.currentIndex

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AlwaysOn
            }

            delegate: ItemDelegate {
                width: windowListView.width
                highlighted: index === windowSelectionDialogModel.listModel.currentIndex

                onClicked: {
                    windowSelectionDialogModel.listModel.currentIndex = index
                    root.accept()
                }

                contentItem: RowLayout {
                    Label {
                        text: model.text || ""
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Label {
                        text: String(model.pid)
                        Layout.preferredWidth: 80
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }
        }
    }
}