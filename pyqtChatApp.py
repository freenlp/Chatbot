#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from PyQt4.QtCore import *
from PyQt4 import QtCore, QtGui
from msgList import MsgList
from flowlayout import FlowLayout
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
sys.path.append("qa")
from qa.prediction import QaEngine

DEFAULT_HEAD = 'icons/qq.png'

class TextEdit(QtGui.QTextEdit, QObject):
    entered = pyqtSignal()
    def __init__(self, parent = None):
        super(TextEdit, self).__init__(parent)
    
    def keyPressEvent(self, e):
        if (e.key() == Qt.Key_Return) and (e.modifiers() == Qt.ControlModifier):
            self.entered.emit()# ctrl+return 输入
            self.clear()
        super(TextEdit, self).keyPressEvent(e)


class MsgInput(QtGui.QWidget, QObject):
    # 自定义的内容输入控件，支持图像和文字的输入，文字输入按回车确认。
    textEntered = pyqtSignal(str)
    imgEntered = pyqtSignal(str)

    btnSize = 35
    teditHeight = 200

    def __init__(self, parent=None):
        super(MsgInput, self).__init__(parent)
        self.setContentsMargins(3, 3, 3, 3)

        self.textEdit = TextEdit()
        self.textEdit.setMaximumHeight(self.teditHeight)
        self.setMaximumHeight(self.teditHeight+self.btnSize)
        self.textEdit.setFont(QtGui.QFont("Times",20,QtGui.QFont.Normal))
        self.textEdit.entered.connect(self.sendText)

        sendTxt = QtGui.QPushButton(u'发送')
        sendTxt.setFont(QtGui.QFont("Microsoft YaHei",15,QtGui.QFont.Bold))
        sendTxt.setFixedHeight(self.btnSize)
        sendTxt.clicked.connect(self.sendText)

        hl = FlowLayout()
        hl.addWidget(sendTxt)
        hl.setMargin(0)

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl)
        vl.addWidget(self.textEdit)
        vl.setMargin(0)
        self.setLayout(vl)

    def sendText(self):
        txt = self.textEdit.toPlainText()
        if len(txt) > 0:
            self.textEntered.emit(txt)
        self.textEdit.clear()


class PyqtChatApp(QtGui.QSplitter):
    """聊天界面，QSplitter用于让界面可以鼠标拖动调节"""
    def __init__(self, q=None):
        super(PyqtChatApp, self).__init__(Qt.Horizontal)

        self.setWindowTitle('pyChat')  # window标题
        # self.setMinimumSize(500, 500)   # 窗口最小大小

        self.msgList = MsgList()
        self.msgList.setDisabled(False)  # 刚打开时没有聊天显示内容才对
        self.msgInput = MsgInput()
        self.msgInput.textEntered.connect(self.sendTextMsg)

        # queue
        self.queue = q

        # 3d render
        self.frame = QtGui.QFrame()
        self.vl = QtGui.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren.AddActor(actor)

        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.frame.setParent(self)
        self.iren.Initialize()

        # set layout
        rSpliter = QtGui.QSplitter(Qt.Vertical, self)
        # self.frame.setParent(rSpliter)
        self.msgList.setParent(rSpliter)
        self.msgInput.setParent(rSpliter)
        #setup qa
        self.qa = QaEngine()
        # qa.prediction(question)

    def setDemoMsg(self):
        self.msgList.clear()

    def qa_process(self, txt):
        print("qa resived" + txt)
        answer = self.qa.prediction(txt)
        return answer

    def send_to_queue(self, msg):
        if self.queue is not None:
            self.queue.put(msg)

    @pyqtSlot(str)
    def sendTextMsg(self,txt):
        print(txt)
        # display to chat
        self.msgList.addTextMsg(txt, False)
        # qa process
        qa_txt = self.qa_process(txt)
        # send to queue
        msg = [txt, qa_txt]
        self.send_to_queue(msg)
        self.msgList.addTextMsg(qa_txt, True)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pchat = PyqtChatApp()
    pchat.show()
    sys.exit(app.exec_())
