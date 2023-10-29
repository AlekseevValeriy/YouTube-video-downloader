from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit
import sys

class QLineEditMaskDemo(QWidget) :
    def __init__(self):
        super(QLineEditMaskDemo, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Use mask to limit the input of QLineEdit controls')
        self.resize(500, 150)

        formLayout = QFormLayout()  #Form layout

        ipLineEdit = QLineEdit()  # ip input box
        macLineEdit = QLineEdit()  # MAC address input box
        dateLineEdit = QLineEdit()  # Date Enter Box
        licenseLineEdit = QLineEdit()  #

        # Set the input data format, with "_", ASCII numeric characters are allowed to enter, but not required (0-9)
        ipLineEdit.setInputMask('000.000.000.000;_')

        # Set the input data format, with "_" place, the hexadecimal format character is necessary to enter (A-F, A-F, 0-9)
        macLineEdit.setInputMask('HH:HH:HH:HH:HH:HH;_')

        # Set the input data format, for example: 2019-12-12
        dateLineEdit.setInputMask('0000-00-00')
        dateLineEdit.setText('1999')

        # Set the input data format, with "#", ">" means that all alphabet characters are capitalized.
        licenseLineEdit.setInputMask('>AAAAA-AAAAA-AAAAA-AAAAA-AAAAA;#')

        # #   Add to form layout,
        formLayout.addRow('Number mask', ipLineEdit)
        formLayout.addRow('Mac Mask', macLineEdit)
        formLayout.addRow('Date Mask', dateLineEdit)
        formLayout.addRow('License Mask', licenseLineEdit)

        self.setLayout(formLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QLineEditMaskDemo()
    main.show()
    sys.exit(app.exec_())