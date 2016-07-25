# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UrbanDataInputDockWidget
                                 A QGIS plugin
 Urban Data Input Tool for QGIS
                             -------------------
        begin                : 2016-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Abhimanyu Acharya/ Space Syntax Limited
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
from PyQt4.QtCore import pyqtSignal

# Initialize Qt resources from file resources.py



import os.path
from . import utility_functions as uf
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from CreateNew_dialog import CreatenewDialog
import processing



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

        self.dlg = CreatenewDialog()

        # set up GUI operation signals
        self.dlg.closePopUpButton.clicked.connect(self.closePopUp)
        self.pushButtonNewFile.clicked.connect(self.newFileDialog)
        self.dlg.createNewFileCheckBox.stateChanged.connect(self.updateLayers)
        self.startpushButton.clicked.connect(self.loadFrontageLayer)
        self.updateFacadeButton.clicked.connect(self.updateSelectedFrontageAttribute)
        self.updateIDPushButton.clicked.connect(self.pushID)
        self.iface.mapCanvas().selectionChanged.connect(self.addDataFields)
        self.iface.legendInterface().itemRemoved.connect(self.updateLayers)
        self.iface.legendInterface().itemAdded.connect(self.updateLayers)
        self.dlg.pushButtonNewFileDLG.clicked.connect(self.newFrontageLayer)
        self.dlg.pushButtonSelectLocation.clicked.connect(self.selectSaveLocation)
        self.iface.legendInterface().itemRemoved.connect(self.enablePushIDcombo)
        self.iface.legendInterface().itemAdded.connect(self.enablePushIDcombo)
        self.iface.projectRead.connect(self.enablePushIDcombo)
        self.iface.newProjectCreated.connect(self.enablePushIDcombo)
        self.pushIDcomboBox.currentIndexChanged.connect(self.updatepushWidgetList)
        self.useExistingcomboBox.currentIndexChanged.connect(self.loadFrontageLayer)
        self.hideshowButton.clicked.connect(self.hideFeatures)
        self.iface.legendInterface().itemRemoved.connect(self.ifFrontageLayer)
        self.iface.legendInterface().itemAdded.connect(self.ifFrontageLayer)
        self.iface.projectRead.connect(self.ifFrontageLayer)
        self.iface.newProjectCreated.connect(self.ifFrontageLayer)



        # initialisation
        self.ifFrontageLayer()
        self.updateLayersPushID()
        self.updateFrontageTypes()




        # add button icons

        #initial button state



        # override setting
        QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        QSettings().setValue('/qgis/crs/enable_use_project_crs', True)

    def closeEvent(self, event):
        # disconnect interface signals
        try:
            self.iface.projectRead.disconnect(self.updateLayers)
            self.iface.newProjectCreated.disconnect(self.updateLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.updateLayers)
            self.iface.legendInterface().itemAdded.disconnect(self.updateLayers)
            self.iface.projectRead.disconnect(self.updateFrontageTypes)
            self.iface.newProjectCreated.disconnect(self.updateFrontageTypes)
            self.iface.legendInterface().itemRemoved.disconnect(self.enablePushIDcombo)
            self.iface.legendInterface().itemAdded.disconnect(self.enablePushIDcombo)
            self.iface.projectRead.disconnect(self.enablePushIDcombo)
            self.iface.newProjectCreated.disconnect(self.enablePushIDcombo)



        except:
            pass

        self.closingPlugin.emit()
        event.accept()


    #######
    #   Data functions
    #######



    def closePopUp(self):
        self.dlg.close()


    def getSelectedLayer(self):
        layer_name = self.dlg.selectLUCombo.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer


    def selectSaveLocation(self):
        filename = QFileDialog.getSaveFileName(self, "Select Save Location ","", '*.shp')
        self.dlg.lineEditFrontages.setText(filename)


    def newFileDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.dlg.selectLUCombo.clear()
            pass

    def ifFrontageLayer(self):
        self.useExistingcomboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        layer_list1 = []
        for lyr in layers:
            if lyr.type() == QgsMapLayer.VectorLayer and lyr.geometryType() == QGis.Line:
                layer_list.append(lyr)
                print layer_list


            for layer1 in layer_list:
                fieldlist = uf.getFieldNames(layer1)
                print fieldlist
                if 'Group' in fieldlist and 'Type' in fieldlist:
                    frontageLayer = layer1
                    layer_list1.append(frontageLayer.name())
                    self.useExistingcomboBox.setEditable(True)
                    print layer_list1

                else:
                    self.useExistingcomboBox.setEditable(False)

        self.useExistingcomboBox.addItems(layer_list1)

        global frontageLayer

    def updateLayers(self):
        self.dlg.selectLUCombo.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []

        if self.dlg.createNewFileCheckBox.checkState() == 2:

            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                    layer_list.append(layer.name())
                    self.dlg.selectLUCombo.setEditable(True)

            self.dlg.selectLUCombo.addItems(layer_list)


    def updateLayersPushID(self):
        self.pushIDcomboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                self.pushIDcomboBox.setEditable(True)
                layer_list.append(layer.name())

        self.pushIDcomboBox.addItems(layer_list)

    def enablePushIDcombo(self):
        layers = self.iface.legendInterface().layers()

        if self.useExistingcomboBox.isEditable() == True:
            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                    self.pushIDcomboBox.setEditable(True)
                    self.updateLayersPushID()

        elif self.useExistingcomboBox.isEditable() == False:
            self.pushIDcomboBox.clear()
            self.pushIDcomboBox.setEditable(False)




    def updateFrontageTypes(self):
        self.frontageslistWidget.clear()
        frontage_list = ['Transparent', 'Semi Transparent', 'Blank',
                          'High Opaque Fence', 'High See Through Fence',
                          'Low Fence']

        self.frontageslistWidget.addItems(frontage_list)


    def getSelectedLayerLoad(self):
        layer_name = self.useExistingcomboBox.currentText()
        layer1 = uf.getLegendLayerByName(self.iface, layer_name)
        finalLayer = layer1
        return finalLayer



    def getSelectedLayerPushID(self):
        layer_name = self.pushIDcomboBox.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer

    def globalFrontageLayer(self):
        layer1 = self.getSelectedLayerPushID()
        gFLayer = layer1
        return gFLayer

    def globalBuildingLayer(self):
        layer1= self.getSelectedLayerPushID()
        buldingLayer = layer1
        return buldingLayer

    def addDataFields(self):
        self.tableClear()
        layer = frontageLayer

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
            headers = ["F-ID","Group","Type"]
            self.tableWidgetFrontage.setHorizontalHeaderLabels(headers)
            self.tableWidgetFrontage.setRowCount(len(attrs))

            for i, item in enumerate(attrs):
                self.tableWidgetFrontage.setItem(i, 0, QtGui.QTableWidgetItem(str(item[A1])))
                self.tableWidgetFrontage.setItem(i, 1, QtGui.QTableWidgetItem(str(item[A2])))
                self.tableWidgetFrontage.setItem(i, 2, QtGui.QTableWidgetItem(str(item[A3])))

            self.tableWidgetFrontage.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.tableWidgetFrontage.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
            self.tableWidgetFrontage.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
            self.tableWidgetFrontage.resizeRowsToContents()

    def tableClear(self):
        self.tableWidgetFrontage.clear()





        #######
        #   Frontages
        #######
    def newFrontageLayer(self):
        if self.dlg.createNewFileCheckBox.checkState() == 0:

            if self.dlg.lineEditFrontages.text() != "":
                path = self.dlg.lineEditFrontages.text()
                filename = os.path.basename(path)
                location = os.path.abspath(path)

                destCRS = self.canvas.mapRenderer().destinationCrs()
                vl = QgsVectorLayer("LineString?crs=" + destCRS.toWkt(), "memory:Frontages", "memory")
                QgsMapLayerRegistry.instance().addMapLayer(vl)

                QgsVectorFileWriter.writeAsVectorFormat(vl, location, "CP1250", None, "ESRI Shapefile")

                QgsMapLayerRegistry.instance().removeMapLayers([vl.id()])

                input2 = self.iface.addVectorLayer(location, filename, "ogr")

                if not input2:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer failed to load!' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                else:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer loaded:' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                input2.startEditing()

                edit1 = input2.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input2.commitChanges()



                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                self.dlg.close()


            else:
                destCRS = self.canvas.mapRenderer().destinationCrs()
                vl = QgsVectorLayer("LineString?crs=" + destCRS.toWkt(), "memory:Frontages", "memory")
                QgsMapLayerRegistry.instance().addMapLayer(vl)

                vl.startEditing()

                edit1 = vl.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                vl.commitChanges()

                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                self.dlg.close()


        elif self.dlg.createNewFileCheckBox.checkState() == 2:
            if self.dlg.lineEditFrontages.text() != "":
                path = self.dlg.lineEditFrontages.text()
                filename = os.path.basename(path)
                location = os.path.abspath(path)

                input1 = self.getSelectedLayer()

                processing.runandload("qgis:polygonstolines", input1, "Lines from polygons")

                input2 = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Lines from polygons" or lyr.name() == "LINES FROM POLYGONS":
                        input2 = lyr
                        break

                processing.runandload("qgis:explodelines", input2, "Exploded")

                input3 = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Exploded" or lyr.name() == "EXPLODED":
                        input3 = lyr
                        break

                QgsMapLayerRegistry.instance().removeMapLayer(input2)

                QgsVectorFileWriter.writeAsVectorFormat(input3, location, "CP1250", None, "ESRI Shapefile")

                QgsMapLayerRegistry.instance().removeMapLayer(input3)

                input4 = self.iface.addVectorLayer(location, filename, "ogr")


                if not input4:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer failed to load!' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                else:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer loaded:' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                input4.startEditing()

                edit1 = input4.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input4.commitChanges()
                input4.startEditing()

                features = input4.getFeatures()
                i = 0
                for feat in features:
                    feat['F_ID'] = i
                    i += 1
                    input4.updateFeature(feat)

                input4.commitChanges()

                self.dlg.lineEditFrontages.clear()

                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                self.dlg.close()


            else:
                input1 = self.getSelectedLayer()

                processing.runandload("qgis:polygonstolines", input1, "Lines from polygons")

                input2 = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Lines from polygons" or lyr.name() == "LINES FROM POLYGONS":
                        input2 = lyr
                        break

                processing.runandload("qgis:explodelines", input2, "Exploded")

                input3 = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Exploded" or lyr.name() == "EXPLODED":
                        input3 = lyr
                        break

                QgsMapLayerRegistry.instance().removeMapLayer(input2)

                input3.setLayerName("memory:Frontages")

                edit1 = input3.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input3.commitChanges()
                input3.startEditing()

                features = input3.getFeatures()
                i = 0
                for feat in features:
                    feat['F_ID'] = i
                    i += 1
                    input3.updateFeature(feat)

                input3.commitChanges()

                self.dlg.lineEditFrontages.clear()


                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                self.dlg.close()


    # Load File

    def loadFrontageLayer(self):
        input = frontageLayer

        input.startEditing()

        plugin_path = os.path.dirname(__file__)
        qml_path = plugin_path + "/frontagesThematic.qml"
        input.loadNamedStyle(qml_path)

        input.featureAdded.connect(self.logFeatureAdded)
        input.selectionChanged.connect(self.addDataFields)

        # Draw/Update Feature
    def logFeatureAdded(self, fid):
        QgsMessageLog.logMessage("feature added, id = " + str(fid))

        mc = self.canvas
        v_layer = frontageLayer
        features = v_layer.getFeatures()
        i = 0
        for feat in features:
            feat['F_ID'] = i
            i += 1
            v_layer.updateFeature(feat)

        data = v_layer.dataProvider()

        update1 = data.fieldNameIndex("Group")
        update2 = data.fieldNameIndex("Type")
        self.updateLength()

        if self.frontageslistWidget.currentRow() == 0:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Transparent", True)

        if self.frontageslistWidget.currentRow() == 1:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Semi Transparent", True)

        if self.frontageslistWidget.currentRow() == 2:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Blank", True)

        if self.frontageslistWidget.currentRow() == 3:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "High Opaque Fence", True)

        if self.frontageslistWidget.currentRow() == 4:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "High See Through Fence", True)

        if self.frontageslistWidget.currentRow() == 5:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "Low Fence", True)
            
    def updateLength(self):
        mc = self.canvas
        layer = frontageLayer

        v_layer = layer
        features = v_layer.getFeatures()

        for feat in features:
            geom = feat.geometry()
            feat['Length'] = geom.length()
            v_layer.updateFeature(feat)

    def updateSelectedFrontageAttribute(self):
        QApplication.beep()
        mc = self.canvas
        layer = frontageLayer

        features = layer.selectedFeatures()

        if self.frontageslistWidget.currentRow() == 0:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Transparent"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 1:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Semi Transparent"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 2:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Blank"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 3:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "High Opaque Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 4:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "High See Through Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 5:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "Low Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()



    def hideFeatures(self):
        mc = self.canvas
        layer = frontageLayer

        if self.hideshowButton.isChecked():
            plugin_path = os.path.dirname(__file__)
            qml_path = plugin_path + "/frontagesThematic_NULL.qml"
            layer.loadNamedStyle(qml_path)
            mc.refresh()

        else:
            plugin_path = os.path.dirname(__file__)
            qml_path = plugin_path + "/frontagesThematic.qml"
            layer.loadNamedStyle(qml_path)
            mc.refresh()


    def updatepushWidgetList(self):
        if self.pushIDcomboBox.isEditable()== True:
            self.pushIDlistWidget.clear()
            buildinglayer = self.getSelectedLayerPushID()
            if buildinglayer:
                features = buildinglayer.getFeatures()
                attrs = []
                for feat in features:
                    attr = feat.attributes()
                    attrs.append(attr)

                fields = buildinglayer.pendingFields()
                field_names = [field.name() for field in fields]
                self.pushIDlistWidget.addItems(field_names)

        elif self.pushIDcomboBox.isEditable()== False:
            self.pushIDlistWidget.clear()


    def pushID(self):
        buildinglayer = self.getSelectedLayerPushID()

        mc = self.canvas
        frontlayer = frontageLayer

        frontlayer.startEditing()

        buildingID = self.pushIDlistWidget.currentItem().text()
        print buildingID
        newColumn = "Building_" + buildingID
        frontlayer_pr = frontlayer.dataProvider()
        frontlayer_pr.addAttributes([QgsField( newColumn, QVariant.Int)])
        frontlayer.commitChanges()
        frontlayer.startEditing()
        frontlayer_caps = frontlayer_pr.capabilities()

        for buildfeat in buildinglayer.getFeatures():
            for frontfeat in frontlayer.getFeatures():
                if frontfeat.geometry().intersects(buildfeat.geometry()) == True:
                    frontlayer.startEditing()

                    if frontlayer_caps & QgsVectorDataProvider.ChangeAttributeValues:
                        frontfeat[newColumn] = buildfeat[buildingID]
                        frontlayer.updateFeature(frontfeat)
                        frontlayer.commitChanges()
























