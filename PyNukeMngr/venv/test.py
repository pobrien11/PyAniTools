from PyQt4 import QtGui, QtCore


class Window(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.tree = QtGui.QTreeWidget(self)

        for i in xrange(3):
            parent = QtGui.QTreeWidgetItem(self.tree)
            parent.setText(0, "Parent {}".format(i))
            parent.setFlags(parent.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            for x in xrange(5):
                child = QtGui.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setCheckState(0, QtCore.Qt.Unchecked)
        self.tree.expandAll()
        self.button = QtGui.QPushButton('Print', self)
        self.button.clicked.connect(self.handleButton)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(self.button)

    def handleButton(self):
        iterator = QtGui.QTreeWidgetItemIterator(self.tree, QtGui.QTreeWidgetItemIterator.Checked)
        while iterator.value():
            item = iterator.value()
            print item.text(0)
            iterator += 1

if __name__ == '__main__':

     import sys
     app = QtGui.QApplication(sys.argv)
     window = Window()
     window.resize(300, 300)
     window.show()
     sys.exit(app.exec_())