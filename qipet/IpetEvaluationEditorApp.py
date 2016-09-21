'''
Created on 26.03.2015

@author: bzfhende
'''
from PyQt4.QtGui import QFrame, QWidget, QLabel,\
    QApplication, QKeySequence, QFileDialog, \
    QVBoxLayout, QHBoxLayout
from qipet.IPetTreeView import IpetTreeView
from qipet.EditableForm import EditableForm
from PyQt4.QtCore import QString, Qt, SIGNAL
from ipet.evaluation.IPETEvalTable import IPETEvaluation, IPETEvaluationColumn
import sys
from ipet.misc import misc
from ipet.evaluation.Aggregation import Aggregation
from ipet.evaluation.IPETFilter import IPETFilterGroup, IPETInstance
from ipet.evaluation.IPETFilter import IPETFilter
from qipet.IpetMainWindow import IpetMainWindow

class IpetEvaluationEditorApp(IpetMainWindow):
    '''
    classdocs
    '''
    addedcolumns = 0
    addedfiltergroups = 0
    addedfilters = 0
    addedaggregations = 0
    addedinstances = 0

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(IpetEvaluationEditorApp, self).__init__(parent)
        
        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle("Evaluation Editor")
        thewidget = QWidget(self)
        self.treewidget = IpetTreeView(self)
        layout = QHBoxLayout()
        layout.addWidget(self.treewidget, 3)
        self.editframe = QFrame(thewidget)
        layout.addWidget(self.editframe, 2)

        self.editframelayout = QVBoxLayout()

        self.editframe.setLayout(self.editframelayout)
    
        thewidget.setLayout(layout)
        self.setCentralWidget(thewidget)
        self.evaluation = None
        self.statusBar().showMessage("Ready", 5000)
        self.filename = None
        
        self.initConnections()
        self.defineActions()
        
    def initConnections(self):
        self.connect(self.treewidget, SIGNAL("itemSelectionChanged()"), self.redrawEditFrameContent)
        
    def setEvaluation(self, evaluation):
        self.evaluation = evaluation
        self.treewidget.populateTree(evaluation)
        self.redrawEditFrameContent()
        
    def defineActions(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        
        filetoolbar = self.addToolBar("File")
        
        loadaction = self.createAction("&Load", self.loadEvaluation, QKeySequence.Open, icon="Load-icon", 
                                       tip="Load evaluation from XML file (current evaluation gets discarded)")
        saveaction = self.createAction("&Save", self.saveEvaluation, QKeySequence.Save, icon="disk-icon", 
                                       tip="Save evaluation to XML format")
        saveasaction = self.createAction("&Save as", self.saveEvaluationAs, QKeySequence.SaveAs, icon="disk-icon", 
                                       tip="Save evaluation to XML format")
        self.addcolaction = self.createAction("Add &Column", self.addColumn, "Alt+C", icon="Letter-C-violet-icon", 
                                         tip="Add new column as a child of the currently selected element")
        self.addfiltergroupaction = self.createAction("Add Filter &Group", self.addFilterGroup, "Alt+G", icon="Letter-G-gold-icon", 
                                         tip="Add new filter group as a child of the current evaluation")
        self.addfilteraction = self.createAction("Add &Filter", self.addFilter, "Alt+H", icon="Letter-F-lg-icon", 
                                            tip="Add filter as a child of the current filter group")
        self.addaggregationaction = self.createAction("Add &Aggregation", self.addAggregation, "Alt+A", icon="Letter-A-dg-icon", 
                                            tip="Add aggregation as a child for the current top level column")
        self.addinstancenaction = self.createAction("Add &Instance", self.addInstance, "Alt+I", icon="Letter-I-blue-icon", 
                                            tip="Add instance as child of the current filter")
        
        deletelementaction = self.createAction("&Delete Element", self.deleteElement, QKeySequence.Delete, "delete-icon", 
                                               tip="Delete currently selected element")
        filemenu.addAction(loadaction)
        filemenu.addAction(saveaction)
        filemenu.addAction(saveasaction)
        filetoolbar.addAction(saveaction)
        filetoolbar.addAction(loadaction)
        filetoolbar.addSeparator()
        filetoolbar.addAction(self.addcolaction)
        filetoolbar.addAction(self.addfiltergroupaction)
        filetoolbar.addAction(self.addfilteraction)
        filetoolbar.addAction(self.addaggregationaction)
        filetoolbar.addAction(self.addinstancenaction)
        filetoolbar.addAction(deletelementaction)
        
    def addNewElementAsChildOfSelectedElement(self, newelement):
        
        selectededitable = self.treewidget.getSelectedEditable()
        selectededitable.addChild(newelement)
        self.reselectAfterInsertOrRemoval(selectededitable)
    
    def reselectAfterInsertOrRemoval(self, newselection):
        self.treewidget.populateTree(self.evaluation)
        
        self.treewidget.setSelectedEditable(newselection)
        
        
    def addColumn(self):
        self.updateStatus("Add column")
        self.addedcolumns += 1
        newcolname = "New Column %d"%self.addedcolumns 
        newcol = IPETEvaluationColumn(name=newcolname)
        self.addNewElementAsChildOfSelectedElement(newcol)
        
    def addFilterGroup(self):
        self.updateStatus("Add filter group")
        self.addedfiltergroups += 1
        newfiltergroupname = "New Group %d"%self.addedfiltergroups
        newfiltergroup = IPETFilterGroup(newfiltergroupname)

        self.addNewElementAsChildOfSelectedElement(newfiltergroup)
        
    
    def addFilter(self):
        self.updateStatus("Add filter")
        self.addedfilters += 1
        evalchildren = self.evaluation.getChildren()

        newfilter = IPETFilter(expression1 = "CHANGE", expression2 = "CHANGE")
        print newfilter.getName()
        self.addNewElementAsChildOfSelectedElement(newfilter)


    def addAggregation(self):
        self.updateStatus("Add aggregation")
        self.addedaggregations += 1
        newaggregationname = "New Aggregation %d"%self.addedaggregations
        newaggregation = Aggregation(newaggregationname)

        self.addNewElementAsChildOfSelectedElement(newaggregation)

    def addInstance(self):
        self.updateStatus("Add instance")
        self.addedinstances += 1
        newinstancename = "new Instance %d"%self.addedinstances
        newinstance = IPETInstance(newinstancename)
        
        self.addNewElementAsChildOfSelectedElement(newinstance)
    
    def deleteElement(self):
        self.updateStatus("Delete Element")
        selectededitable = self.treewidget.getSelectedEditable()
        parentofselectededitable = self.treewidget.getParentOfSelectedEditable()
        if parentofselectededitable is not None:
            children = parentofselectededitable.getChildren()
            index = children.index(selectededitable)
            if index == len(children) - 1:
                newselectededitable = parentofselectededitable
            else:
                newselectededitable = children[index + 1]
            parentofselectededitable.removeChild(selectededitable)
            self.reselectAfterInsertOrRemoval(newselectededitable)
        
    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        
        
    def loadEvaluation(self):
        thedir = unicode(".")
        filename = unicode(QFileDialog.getOpenFileName(self, caption=QString("%s - Load an evaluation"%QApplication.applicationName()),
                                               directory=thedir, filter=unicode("XML files (*.xml)")))
        if filename:
            try:
                ev = IPETEvaluation.fromXMLFile(filename)
                message = "Loaded evaluation from %s"%filename
                self.setEvaluation(ev)
            except Exception:
                message = "Error: Could not load evaluation from file %s"%filename
                
            self.updateStatus(message)
        
        pass
    
    def saveEvaluation(self):
        if self.filename is None:
            filename = unicode(QFileDialog.getSaveFileName(self, caption=QString("%s - Load an evaluation"%QApplication.applicationName()),
                                                           directory = unicode("."), filter=unicode("XML files (*.xml)")))
        else:
            filename = self.filename
        
        if not filename:
            return
        
        misc.saveAsXML(self.evaluation, filename)
        self.filename = filename
        self.updateStatus("Saved evaluation to file %s"%filename)
        
    
    def saveEvaluationAs(self):
        filename = unicode(QFileDialog.getSaveFileName(self, caption=QString("%s - Load an evaluation"%QApplication.applicationName()),
                                                       directory = unicode("."), filter=unicode("XML files (*.xml)")))
        if not filename:
            return
        
        misc.saveAsXML(self.evaluation, filename)
        self.filename = filename
        self.updateStatus("Saved evaluation to file %s"%filename)
        
    def enableOrDisableActions(self):
        for action, addclass in zip([self.addcolaction, self.addfiltergroupaction, self.addfilteraction, self.addaggregationaction, self.addinstancenaction],
                                    [IPETEvaluationColumn(), IPETFilterGroup(), IPETFilter(), Aggregation(), IPETInstance()]):
            if self.treewidget.currentItemAcceptsClassAsChild(addclass):
                action.setEnabled(True)
            else:
                action.setEnabled(False)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            child.widget().deleteLater()


    def redrawEditFrameContent(self):

        if self.treewidget.getSelectedEditable() is not None:
            editable = self.treewidget.getSelectedEditable()
            editframecontent = EditableForm(editable, self.editframe)
            textlabel = QLabel(QString("<b>Edit attributes for %s</b>"%(editable.getName())))
        else:
            editframecontent = QLabel(QString("Select an element from the evaluation"))
            textlabel = QLabel(QString("<b>No element selected</b>"))

        self.clearLayout(self.editframelayout)
        textlabel.setMaximumHeight(20)
        textlabel.setMinimumHeight(20)
        textlabel.setAlignment(Qt.AlignCenter)
        textlabel.setBuddy(editframecontent)
        self.editframelayout.addWidget(textlabel)
        self.editframelayout.addWidget(editframecontent)
        self.connect(editframecontent, SIGNAL(EditableForm.USERINPUT_SIGNAL), self.updateItem)
        self.enableOrDisableActions()
        
    def updateItem(self):
        self.treewidget.updateSelectedItem()
        self.redrawEditFrameContent()
        
    def setExperiment(self, experiment):
        EditableForm.extendAvailableOptions("datakey", experiment.getDatakeys())

    
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    app.setApplicationName("Evaluation editor")
    mainwindow = IpetEvaluationEditorApp()
    try:
        ev = IPETEvaluation.fromXMLFile("test/testevaluate.xml")
        mainwindow.setEvaluation(ev)
    except:
        pass
    mainwindow.show()
    
    sys.exit(app.exec_())
        
    
