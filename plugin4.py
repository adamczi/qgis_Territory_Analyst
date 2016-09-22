# -*- coding: utf-8 -*-
"""
/***************************************************************************
 plugin4
                                 A QGIS plugin
 Dynamic attr tables
                              -------------------
        begin                : 2016-08-29
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Adam Borczyk
        email                : ad.borczyk@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QTimer, Qt
from PyQt4.QtGui import QAction, QIcon, QTableWidgetItem, QInputDialog, QHeaderView, QTableView, QStandardItem, QStandardItemModel, QComboBox, QCheckBox, QLabel, QToolBar
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsFeatureRequest, QgsExpression, QgsMapLayer
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from plugin4_dialog import plugin4Dialog
# from plugin4graph import Graph
import plugin4graph
import os.path
## Additional
import numbers
from decimal import Decimal
from fractions import Fraction
from plugin4customTable import QCustomTableWidgetItem
import pyqtgraph



class plugin4:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'plugin4_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference, window on top
        self.dlg = plugin4Dialog(self.iface.mainWindow())
        self.graph = plugin4graph.Graph()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Location Intelligence')

        ## Add to LI tooblar or create if doesn't exist
        toolbarName = 'Location Intelligence'
        self.toolbar = self.iface.mainWindow().findChild(QToolBar,toolbarName)
        print self.toolbar
        if self.toolbar is None:
            self.toolbar = self.iface.addToolBar(toolbarName)
            self.toolbar.setObjectName(toolbarName)

        
        ## Run functions connected to button clicks

        ## Get attributes of chosen file
        self.dlg.pushButton_2.clicked.connect(self.openFile)        

        ## Hide/Show the side panel
        self.dlg.toolButton_4.clicked.connect(self.toggleRightPanel)

        ## Create the graph
        self.dlg.pushButton_3.clicked.connect(self.prepareGraph)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('plugin4', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/plugin4/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Run plugin4'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Plugin4'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        if len(self.toolbar.actions())==0:
            del self.toolbar

    def availableLayers(self):
        """ List layers available to select in the side panel """
        self.dlg.comboBox_chosenFile.clear()
        for i in self.iface.legendInterface().layers():
            if  i.type() == QgsMapLayer.VectorLayer and i.isValid():
                self.dlg.comboBox_chosenFile.addItem(i.name())

    def openFile(self):
        """ Get selected layer name and load its features """
        self.chosenLayer = self.dlg.comboBox_chosenFile.currentText()
        self.dlg.comboBox.clear()
        self.getAttributes()
        self.availableColumns()

    def availableColumns(self):
        """ Lists available numeric columns in the side panel """
        comboBoxOptions = ['Suma', u'Średnia']
        self.dlg.tableWidget_2.setRowCount(len(self.numFields))
        self.dlg.tableWidget_2.setColumnCount(3)

        ## Fill the table
        for i in range(len(self.numFields)):
            checkBoxItem = QCheckBox()
            checkBoxItem.setCheckState(Qt.Unchecked) 
            self.dlg.tableWidget_2.setCellWidget(i,0,checkBoxItem)

            textItem = QLabel()
            textItem.setText(self.numFields.values()[i])
            self.dlg.tableWidget_2.setCellWidget(i,1,textItem)
            
            comboBoxField = QComboBox()
            for j in comboBoxOptions:
                comboBoxField.addItem(j)
            self.dlg.tableWidget_2.setCellWidget(i,2,comboBoxField)

        self.dlg.tableWidget_2.setColumnWidth(0,25)
        self.dlg.tableWidget_2.verticalHeader().setVisible(False)
        self.dlg.tableWidget_2.horizontalHeader().setVisible(False)

        

    def getAttributes(self):
        """ Get layer's headlines and fields information """
        ## Work on layer 'warstwa 1'
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(self.chosenLayer)
        features = layerList[0].getFeatures() 

        ## Get headlines from first feature
        request = QgsFeatureRequest().setFilterFid(0)
        f1 = layerList[0].getFeatures(request).next()
        fields = [c.name() for c in f1.fields().toList()] 

        ## Insert only numerical columns
        self.numFields = {}
        for i in range(len(fields)):
            if layerList[0].pendingFields().field(i).typeName() in ["Real", "Integer"]:
                self.numFields[i] = layerList[0].pendingFields().field(i).name()

        ## Append columns to choose as a group column
        if self.dlg.comboBox.count() == 0:
            self.dlg.comboBox.addItems(fields)

        return features, layerList, fields

    def groupBy(self):
        """ Check which field to group with and preserve sorting when refreshing """
        try:
            ## Get inf about how columns were sorted 
            qTable = self.dlg.tableWidget
            self.sortedColumn = qTable.horizontalHeader().sortIndicatorSection()
            self.sortedColumnOrder = qTable.horizontalHeader().sortIndicatorOrder()
            ## And clear table before refreshing
            qTable.clear()

            selectedFields = []
            for c in range(len(self.numFields)):
                if self.dlg.tableWidget_2.cellWidget(c,0).isChecked():
                    selectedFields.append(self.dlg.tableWidget_2.cellWidget(c,1).text())
            
            self.selectedHeaders = selectedFields

            ## Run a function to fill the table
            self.insertToTable(self.dlg.comboBox.currentIndex(), selectedFields)
        except AttributeError:
            self.iface.messageBar().pushMessage("Error", u"Brak załadowanych danych", level=QgsMessageBar.CRITICAL, duration=4)

    def insertToTable(self, field, selectedFields):
        """ Get values from the shapefile and insert it to the table """
        qTable = self.dlg.tableWidget

        getAttributes = self.getAttributes()
        features = getAttributes[0]
        layerList = getAttributes[1]
        fields = getAttributes[2]

        ## Clear feature selection if there was any
        layerList[0].setSelectedFeatures([])


        self.values = []
        self.groups = []

        ## Get group names
        idx = layerList[0].fieldNameIndex(fields[field])
        self.groups = layerList[0].uniqueValues(idx)

        ## Create as many lists as selected fields to later store values for each group
        for fieldElement in range(len(selectedFields)):
            self.values.append([])
            for groupElement in range(len(self.groups)):
                self.values[fieldElement].append([])
                ## Returns empty lists for values of each group, all that as an element of a list of len(selectedFields)
        
        ## Disable sorting for a while so the values get assigned in a correct order
        qTable.setSortingEnabled(False)

        ## For each feature
        for f in features:
            ## check group 1, 2 ... n
            for g in range(len(self.groups)):
                ## if feature in group[n] append it to correct list
                if f.attributes()[field] == self.groups[g]:
                    for selected_field in range(len(selectedFields)):                    
                        self.values[selected_field][g].append(f.attributes()[fields.index(selectedFields[selected_field])])     

        ## Prepare table size
        labels = [u'Region']
        labels += selectedFields

        # for label in range(1,len(labels)):
        #     labels[label] += '(',self.dlg.tableWidget_2.cellWidget(label-1,2).currentText(),')'

        qTable.setRowCount(len(self.groups))
        qTable.setColumnCount(len(selectedFields)+1)

        
        
        try:
            ## Insert data
            for row in range(len(self.groups)):

                ## Add group name field
                group = QTableWidgetItem(str(self.groups[row]))
                qTable.setItem(row,0,group) 

                ## Add data into columns
                for column in range(1,qTable.columnCount()):
                    self.currentColumn = selectedFields[column-1]
                    ## Check selected sum/average value by name of the field
                    for available_field in range(len(self.numFields)):
                        if self.dlg.tableWidget_2.cellWidget(available_field,1).text() == selectedFields[column-1]:

                            ## Calculate sum or average
                            if self.dlg.tableWidget_2.cellWidget(available_field,2).currentIndex() == 0:
                                item = QCustomTableWidgetItem(str(round(sum(self.values[column-1][row],2))))
                            else:
                                item = QCustomTableWidgetItem(str(round((sum(self.values[column-1][row])/len(self.values[column-1][row])),2)))
                                                            
                            ## Set item
                            qTable.setItem(row,column,item)
                    
        except TypeError:
            self.iface.messageBar().pushMessage("Error", u"Jedna z wybranych kolumn zawiera puste komórki ("+self.currentColumn+")", level=QgsMessageBar.WARNING, duration=4)
                    
        ## Apply previous sorting
        qTable.setSortingEnabled(True)
        if self.sortedColumn < qTable.columnCount:
            qTable.horizontalHeader().setSortIndicator(self.sortedColumn, self.sortedColumnOrder)
        else:
            qTable.horizontalHeader().setSortIndicator(0, 0)

        ## Finalize table
        qTable.setHorizontalHeaderLabels(labels)
        qTable.resizeColumnsToContents()
     

    def toggleRightPanel(self):
        """ Show/hide the file panel """
        self.dlg.frame.setHidden(not self.dlg.frame.isHidden())

        label = '<<' if self.dlg.frame.isHidden() == True else '>>'
        self.dlg.toolButton_4.setText(label)
        
        # print self.dlg.frame.isHidden()

        # # self.dlg.updateGeometry()
        # mainWindowHeight = self.dlg.geometry().height()
        # frameSize = self.dlg.mainFrame.size().width()

        # if self.dlg.frame.isHidden():
        #     self.dlg.resize(self.dlg.mainFrame.size().width(), mainWindowHeight)
        # else:
        #     self.dlg.resize(self.dlg.mainFrame.size().width()+300, mainWindowHeight)
        # # mainWindowWidth = self.dlg.geometry().width()

    def rowSelection(self):
        """ Highlights selected groups on map """ 
        qTable = self.dlg.tableWidget
        indexes = qTable.selectionModel().selectedRows()
        
        ## Get selected group name
        for index in sorted(indexes):
            selectedGroup = qTable.item(index.row(),0).text()

        groupName = self.dlg.comboBox.currentText()
        expr = QgsExpression( "\"%s\"='%s'" % (groupName, selectedGroup))

        ## Get layer's features based on expression
        layerList = QgsMapLayerRegistry.instance().mapLayersByName(self.chosenLayer)    
        features = layerList[0].getFeatures(QgsFeatureRequest(expr))

        ## Select features using IDs of 'features'
        ids = [i.id() for i in features]
        layerList[0].selectByIds(ids)

    def prepareGraph(self):
        """ Prepare data to use """
        try:
            self.x = list(enumerate(self.groups))
            self.y = []
            selectedColumns = []
            ## If no or only 'Region' column loaded
            if self.dlg.tableWidget.columnCount() in (0,1):
                return
            else: 
                ## Check which columns are selected and get the first one if many
                for index in self.dlg.tableWidget.selectedIndexes():
                    if index.column() != 0:
                        selectedColumns.append(index.column())

            ## In case none or Region column checked and the button was pressed
            try:
                columnToGraph = min(selectedColumns)-1
            except ValueError, NameError:
                columnToGraph = 0
            self.graphTitle = self.selectedHeaders[columnToGraph]

            ## Select data
            for row in range(len(self.groups)):
                for available_field in range(len(self.numFields)):
                    if self.dlg.tableWidget_2.cellWidget(available_field,1).text() == self.selectedHeaders[columnToGraph]:
                        if self.dlg.tableWidget_2.cellWidget(available_field,2).currentIndex() == 0:
                            self.y.append(round(sum(self.values[columnToGraph][row])))
                        else:
                            self.y.append(round(sum(self.values[columnToGraph][row])/len(self.values[columnToGraph][row]),2))

            self.buildGraph()

        except IndexError, UnboundLocalError:
            self.iface.messageBar().pushMessage("Error", u"Po zaimportowaniu wybierz grupę i odśwież dane", level=QgsMessageBar.CRITICAL, duration=4)
        except AttributeError:
            self.iface.messageBar().pushMessage("Error", u"Brak załadowanych danych", level=QgsMessageBar.CRITICAL, duration=4)


    def buildGraph(self):
        """ Add data to the graph """
        pyqtgraph.setConfigOption('background', (230,230,230))
        pyqtgraph.setConfigOption('foreground', (100,100,100))
        dataColor = (102,178,255)
        dataBorderColor = (180,220,255)
        barGraph = self.graph.graphicsView
        barGraph.clear()
        barGraph.addItem(pyqtgraph.BarGraphItem(x=range(len(self.x)), height=self.y, width=0.5, brush=dataColor, pen=dataBorderColor))
        barGraph.addItem(pyqtgraph.GridItem())
        barGraph.getAxis('bottom').setTicks([self.x])
        barGraph.setTitle(title=self.graphTitle)

        self.showGraph()

    def showGraph(self):
        """ Just show the graph """
        self.graph.show()
       

    def run(self):
        """ Functions that run every time the dialog shows up """
        ## Refresh available layers in case new were added to the map
        self.availableLayers() 

        ## Show the main window
        self.dlg.show()

        ## Select features matching clicked row group name
        self.dlg.tableWidget.verticalHeader().sectionClicked.connect(self.rowSelection)

        ## "Odswiez", add/refresh data
        self.dlg.pushButton.clicked.connect(self.groupBy)