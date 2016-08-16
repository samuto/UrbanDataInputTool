# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UrbanDataInputDockWidget
                                 A QGIS plugin
 Urban Data Input Tool for QGIS
                             -------------------
        begin                : 2016-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Abhimanyu Acharya/(C) 2016 by Space Syntax Limited’.
        email                : a.acharya@spacesyntax.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from CreateNew_dialog import CreatenewDialog
from . import utility_functions as uf


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'urban_data_input_dockwidget_base.ui'))



class UrbanDataInputDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(UrbanDataInputDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # define globals
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.frontage_layer = None
        self.LU_layer = None
        self.frontagedlg = CreatenewDialog()
        self.legend = self.iface.legendInterface()


        # initialisation

        self.updateFrontageTypes()
        self.pushIDlistWidget.hide()
        self.pushIDcomboBox.hide()
        self.updateIDPushButton.hide()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    #######
    #   Data functions
    #######

    # Update frontage types
    def updateFrontageTypes(self):
        self.frontageslistWidget.clear()
        frontage_list = ['Transparent', 'Semi Transparent', 'Blank',
                          'High Opaque Fence', 'High See Through Fence',
                          'Low Fence']

        self.frontageslistWidget.addItems(frontage_list)

    # Set universal Frontage layer if conditions are satisfied
    def setFrontageLayer(self):
        index = self.useExistingcomboBox.currentIndex()
        self.frontage_layer = self.useExistingcomboBox.itemData(index)
        return self.frontage_layer

    # Get building layer based on name
    def getSelectedLayerPushID(self):
        layer_name = self.pushIDcomboBox.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer

    def addDataFields(self):
        self.tableClear()
        layer = self.setFrontageLayer()
        if layer:
            features = layer.selectedFeatures()
            attrs = []
            for feat in features:
                attr = feat.attributes()
                attrs.append(attr)

            fields = layer.pendingFields()
            field_names = [field.name() for field in fields]

            field_length = len(field_names)
            A1 = field_length - 4
            A2 = field_length - 3
            A3 = field_length - 2

            self.tableWidgetFrontage.setColumnCount(3)
            headers = ["F-ID", "Group", "Type"]
            self.tableWidgetFrontage.setHorizontalHeaderLabels(headers)
            self.tableWidgetFrontage.setRowCount(len(attrs))

            for i, item in enumerate(attrs):
                self.tableWidgetFrontage.setItem(i, 0, QtGui.QTableWidgetItem(str(item[A1])))
                self.tableWidgetFrontage.setItem(i, 1, QtGui.QTableWidgetItem(str(item[A2])))
                self.tableWidgetFrontage.setItem(i, 2, QtGui.QTableWidgetItem(str(item[A3])))

            self.tableWidgetFrontage.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
            self.tableWidgetFrontage.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
            self.tableWidgetFrontage.resizeRowsToContents()

    def tableClear(self):
        self.tableWidgetFrontage.clear()





















