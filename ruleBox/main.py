import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5
import sys
import os
import threading
import pypinyin
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QDate, Qt, QModelIndex
import shutil

#*******************************************************************************************
class Mylog(object):

    def __init__(self):
        pass



def to_pinyin(word) -> str:
    '''
    function:汉字转拼音
    '''
    pinyin = ''
    for i in pypinyin.lazy_pinyin(word, style=0):
        pinyin = pinyin + ''.join(i)
    return pinyin


#*******************************************************************************************
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1238, 801)
        MainWindow.setFixedSize(1238, 801)
        #MainWindow.setMaximumSize(QtCore.QSize(16777214, 16777215))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tree_show = QtWidgets.QTreeView(self.centralwidget)
        self.tree_show.setGeometry(QtCore.QRect(10, 10, 331, 751))
        self.tree_show.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tree_show.setObjectName("tree_show")

        self.table_show = QtWidgets.QTableView(self.centralwidget)
        self.table_show.setGeometry(QtCore.QRect(350, 60, 881, 701))
        self.table_show.setObjectName("table_show")
        self.table_show.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.btn_query = QtWidgets.QPushButton(self.centralwidget)
        self.btn_query.setGeometry(QtCore.QRect(350, 10, 181, 41))
        self.btn_query.setObjectName("btn_query")
        self.btn_delete = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete.setGeometry(QtCore.QRect(580, 10, 181, 41))
        self.btn_delete.setObjectName("btn_delete")
        self.btn_modify = QtWidgets.QPushButton(self.centralwidget)
        self.btn_modify.setGeometry(QtCore.QRect(820, 10, 181, 41))
        self.btn_modify.setObjectName("btn_modify")
        self.btn_add = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add.setGeometry(QtCore.QRect(1050, 10, 181, 41))
        self.btn_add.setObjectName("btn_add")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1238, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "2D规则运营工具"))
        self.btn_query.setText(_translate("MainWindow", "显示详细信息"))
        self.btn_delete.setText(_translate("MainWindow", "删除"))
        self.btn_modify.setText(_translate("MainWindow", "修改"))
        self.btn_add.setText(_translate("MainWindow", "添加"))
#*******************************************************************************************
class WindowAction(PyQt5.QtWidgets.QMainWindow):
    
    def __init__(self, rule:object):
        super(WindowAction, self).__init__()
        self.rule:Rule = rule
            

    def click_update(self):
        self.rule.dialog.status = 'update'
        treeSelect = self.get_tree_select()
        if treeSelect == 'None':
            QMessageBox.warning(self,"警告","当前无修改项！",QMessageBox.Yes | QMessageBox.No)
            return
        ret, category, dict_rule = self.check_update_able()
        if not ret:
            QMessageBox.warning(self,"警告","当前选项不支持修改！",QMessageBox.Yes | QMessageBox.No)
            return
        self.rule.dialog.setupTitle('修改规则')
        self.rule.dialog.setupContent(dict_rule)
        self.rule.dialog.ui.combo_category.setEditable(False)
        self.rule.dialog.set_category_combo([category])
        self.rule.dialog.ui.combo_company.setEditable(False)
        self.rule.dialog.set_company_combo([dict_rule['company']])
        self.rule.dialog.ui.combo_dimension.setEditable(False)
        self.rule.dialog.set_dimension_combo()
        self.rule.dialog.ui.combo_status.setEditable(False)
        self.rule.dialog.set_status_combo()
        self.rule.dialog.ui.edit_virusname.setEnabled(False)
        self.rule.dialog.set_virus_name(dict_rule['name'])
        list_date = dict_rule['date'].split('-')
        #print(list_date)
        date=QDate(int(list_date[0]), int(list_date[1]), int(list_date[2]))
        self.rule.dialog.set_date(date)
        self.rule.dialog.set_rule(dict_rule['rule'])
        self.rule.dialog.set_remark(dict_rule['remark'])
        self.rule.dialog.exec() # exec为模态对话框， show为非模态
        

    def check_update_able(self) -> tuple('''bool, str, dict'''):
        '''
        function:检查当前选中的项是否支持修改
        '''
        treeSelect = self.get_tree_select()
        ret, list_category = self.rule.sql.query_category()
        if not ret:
            QMessageBox.warning(self,"警告","check_update_able查询query_category出错！",QMessageBox.Yes | QMessageBox.No)
            return
        for item_category in list_category:
            category_name = item_category['category']
            if category_name == treeSelect:
                # 此时选中的为品类
                return False, None, None
        ret, list_company = self.rule.sql.query_all_company()
        if not ret:
            QMessageBox.warning(self,"警告","check_update_able查询query_all_company出错！",QMessageBox.Yes | QMessageBox.No)
            return
        if treeSelect in list_company:
            # 此时选中的为公司名
            return False, None, None
        else:
            # 此时选中的为病毒名
            category_name = self.rule.ui.tree_show.currentIndex().parent().parent().data()
            company_name = self.rule.ui.tree_show.currentIndex().parent().data()
            for item_category in list_category: 
                if item_category['category'] == category_name:
                    table_name = item_category['tablename']
            ret, list_rule = self.rule.sql.query_rule(table_name, company_name)
            if not ret:
                QMessageBox.warning(self,"警告","check_update_able查询query_virus_by_company出错！",QMessageBox.Yes | QMessageBox.No)
                return
            for item in list_rule:
                if item['name'] == treeSelect:
                    return True, category_name, item
    

    def click_insert(self):
        self.rule.dialog.status = 'insert'
        self.rule.dialog.setupTitle('添加规则')
        self.rule.dialog.setupContent({})
        self.rule.dialog.status = 'insert'

        self.rule.dialog.ui.combo_category.setEditable(True)
        ret, list_category = self.rule.sql.query_category()
        category = []
        if ret:
            for item in list_category:
                category.append(item['category'])
            self.rule.dialog.set_category_combo(category)
        self.rule.dialog.ui.combo_company.setEditable(True)
        self.rule.dialog.ui.combo_dimension.setEditable(False)
        self.rule.dialog.set_dimension_combo()
        self.rule.dialog.ui.combo_status.setEditable(False)
        self.rule.dialog.set_status_combo()
        self.rule.dialog.ui.edit_virusname.setEnabled(True)
        self.rule.dialog.set_virus_name('')
        self.rule.dialog.set_date()
        self.rule.dialog.set_rule('')
        self.rule.dialog.set_remark('')
        self.rule.dialog.exec()


    def check_query_able(self) -> tuple('''bool, str, dict'''):
        '''
        function:检查当前选中的项是否支持显示
        '''
        treeSelect = self.get_tree_select()
        ret, list_category = self.rule.sql.query_category()
        if not ret:
            QMessageBox.warning(self,"警告","check_update_able查询query_category出错！",QMessageBox.Yes | QMessageBox.No)
            return
        for item_category in list_category:
            category_name = item_category['category']
            if category_name == treeSelect:
                # 此时选中的为品类
                return False, None, None
        ret, list_company = self.rule.sql.query_all_company()
        if not ret:
            QMessageBox.warning(self,"警告","check_update_able查询query_all_company出错！",QMessageBox.Yes | QMessageBox.No)
            return
        if treeSelect in list_company:
            # 此时选中的为公司名
            return False, None, None
        else:
            # 此时选中的为病毒名
            category_name = self.rule.ui.tree_show.currentIndex().parent().parent().data()
            company_name = self.rule.ui.tree_show.currentIndex().parent().data()
            for item_category in list_category: 
                if item_category['category'] == category_name:
                    table_name = item_category['tablename']
            ret, list_rule = self.rule.sql.query_rule(table_name, company_name)
            if not ret:
                QMessageBox.warning(self,"警告","check_update_able查询query_virus_by_company出错！",QMessageBox.Yes | QMessageBox.No)
                return
            for item in list_rule:
                if item['name'] == treeSelect:
                    return True, category_name, item


    def click_query(self):
        '''
        function:显示详细信息按钮，用于查询单条规则
        '''
        self.rule.dialog.status = 'show'
        ret, category, dict_rule = self.check_query_able()
        if not ret:
            QMessageBox.warning(self,"警告","当前选项不支持修改！",QMessageBox.Yes | QMessageBox.No)
            return
        self.rule.dialog.setupTitle('详细信息')
        self.rule.dialog.setupContent(dict_rule)
        self.rule.dialog.ui.combo_category.setEditable(False)
        self.rule.dialog.set_category_combo([category])
        self.rule.dialog.ui.combo_company.setEditable(False)
        self.rule.dialog.set_company_combo([dict_rule['company']])
        self.rule.dialog.ui.combo_dimension.setEditable(False)
        self.rule.dialog.set_dimension_combo([dict_rule['dimension']])
        self.rule.dialog.ui.combo_status.setEditable(False)
        self.rule.dialog.set_status_combo([dict_rule['status']])
        self.rule.dialog.ui.edit_virusname.setEnabled(False)
        self.rule.dialog.set_virus_name(dict_rule['name'])
        list_date = dict_rule['date'].split('-')
        #print(list_date)
        date=QDate(int(list_date[0]), int(list_date[1]), int(list_date[2]))
        self.rule.dialog.set_date(date)
        self.rule.dialog.set_rule(dict_rule['rule'])
        self.rule.dialog.set_remark(dict_rule['remark'])
        self.rule.dialog.exec() # exec为模态对话框， show为非模态


    def click_delete(self):
        treeSelect = self.get_tree_select()
        if treeSelect == 'None':
            QMessageBox.warning(self,"警告","当前无删除项！",QMessageBox.Yes | QMessageBox.No)
            return
        ret = QMessageBox.question(self,"标题","确定删除<" + treeSelect + ">吗？",QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            ret, list_category = self.rule.sql.query_category()
            if not ret:
                QMessageBox.warning(self,"警告","click_delete查询query_category出错！",QMessageBox.Yes | QMessageBox.No)
                return
            for item_category in list_category:
                category_name = item_category['category']
                if category_name == treeSelect:
                    # 此时选中的为品类
                    table_name = item_category['tablename']
                    self.rule.sql.delete_category(treeSelect)
                    self.rule.sql.delete_company_by_category(treeSelect)
                    self.rule.sql.delete_table(table_name)
                    self.rule.window.update_tree()
                    return
            ret, list_company = self.rule.sql.query_all_company()
            if not ret:
                QMessageBox.warning(self,"警告","click_delete查询query_all_company出错！",QMessageBox.Yes | QMessageBox.No)
                return
            if treeSelect in list_company:
                # 此时选中的为公司名
                category_name = str(self.rule.ui.tree_show.currentIndex().parent().data())
                for item_category in list_category: 
                    if item_category['category'] == category_name:
                        table_name = item_category['tablename']
                        self.rule.sql.delete_company_by_category_and_company(category_name, treeSelect)
                        self.rule.sql.delete_rule_by_company(table_name, treeSelect)
                        self.rule.window.update_tree()
                        return
            else:
                # 此时选中的为病毒名
                category_name = self.rule.ui.tree_show.currentIndex().parent().parent().data()
                company_name = self.rule.ui.tree_show.currentIndex().parent().data()
                for item_category in list_category: 
                    if item_category['category'] == category_name:
                        table_name = item_category['tablename']
                self.rule.sql.delete_rule_by_company_and_virus(table_name, company_name, treeSelect)
                self.rule.window.update_tree()
                return
        

    def click_tree(self):
        '''
        function:用户点击了树控件中的项
        '''
        self.update_table()
        

    def update_table(self):
        '''
        function:更新表控件
        '''
        self.clear_table()
        treeSelect = self.get_tree_select()
        ret, list_category = self.rule.sql.query_category()
        if not ret:
            QMessageBox.warning(self,"警告","update_table查询query_category出错！",QMessageBox.Yes | QMessageBox.No)
            return
        for item_category in list_category:
            category_name = item_category['category']
            if category_name == treeSelect:
                # 此时选中的为品类
                table_name = item_category['tablename']
                ret, list_rule = self.rule.sql.query_all_rule(table_name)
                if not ret:
                    QMessageBox.warning(self,"警告","update_table查询query_all_rule出错！",QMessageBox.Yes | QMessageBox.No)
                    return
                self.insert_rule_table(list_rule)
                return
        ret, list_company = self.rule.sql.query_all_company()
        if not ret:
            QMessageBox.warning(self,"警告","update_table查询query_all_company出错！",QMessageBox.Yes | QMessageBox.No)
            return
        if treeSelect in list_company:
            # 此时选中的为公司名
            category_name = str(self.rule.ui.tree_show.currentIndex().parent().data())
            for item_category in list_category: 
                if item_category['category'] == category_name:
                    table_name = item_category['tablename']
                    ret, list_rule = self.rule.sql.query_rule(table_name, treeSelect)
                    if not ret:
                        QMessageBox.warning(self,"警告","update_table查询query_rule出错！",QMessageBox.Yes | QMessageBox.No)
                        return
                    self.insert_rule_table(list_rule)
                    return
        else:
            # 此时选中的为病毒名，上溯2层找到根节点数据
            category_name = self.rule.ui.tree_show.currentIndex().parent().parent().data()
            for item_category in list_category: 
                if item_category['category'] == category_name:
                    table_name = item_category['tablename']
                    ret, list_rule = self.rule.sql.query_rule_by_virus(table_name, treeSelect)
                    if not ret:
                        QMessageBox.warning(self,"警告","update_table查询query_rule_by_virus出错！",QMessageBox.Yes | QMessageBox.No)
                        return
                    self.insert_rule_table(list_rule)
                    return



    def clear_table(self):
        '''
        function:清理表控件的所有节点
        '''
        while True:
            rootIndex = self.rule.ui.table_show.model().index(0, 0) 
            if rootIndex.data() != None:
                self.rule.ui.table_show.model().removeRow(rootIndex.row(), rootIndex.parent())
            else:
                break


    def insert_rule_table(self, list_table:list):
        '''
        function:在table表中插入规则
        '''
        for item in list_table:
            self.rule.ui.table_show.model().appendRow([QStandardItem(item['company']),
                                                        QStandardItem(item['name']),
                                                        QStandardItem(item['dimension']),
                                                        QStandardItem(item['status']),
                                                        QStandardItem(item['date']),
                                                        QStandardItem(item['rule']),
                                                        QStandardItem(item['remark'])])


    def update_tree(self):
        '''
        function:更新树控件
        '''
        ret, list_category = self.rule.sql.query_category()
        if not ret:
            QMessageBox.warning(self,"警告","查询品类表出错！",QMessageBox.Yes | QMessageBox.No)
            return
        self.clear_tree()
        for item_category in list_category:
            category_name = item_category['category']
            table_name = item_category['tablename']
            tree_category = self.insert_category_tree(category_name)
            ret, list_company = self.rule.sql.query_company(category_name)
            if not ret:
                QMessageBox.warning(self,"警告","查询公司表出错！",QMessageBox.Yes | QMessageBox.No)
                return
            for item_company in list_company:
                ret, list_virus = self.rule.sql.query_rule(table_name, item_company)
                if not ret:
                    QMessageBox.warning(self,"警告","查询" + table_name + "表出错！",QMessageBox.Yes | QMessageBox.No)
                    return
                if list_virus:
                    tree_company = self.insert_company_tree(item_company, tree_category)
                    for item_virus in list_virus:
                        self.insert_virus_tree(item_virus['name'], tree_company)
                else: # 该公司旗下没有病毒规则信息,则从公司表中删除相关公司信息
                    self.rule.sql.delete_company_by_category_and_company(category_name, item_company)


    def clear_tree(self):
        '''
        function:清理树控件的所有节点
        '''
        while True:
            rootIndex = self.rule.ui.tree_show.model().index(0, 0) 
            if rootIndex.data() != None:
                self.rule.ui.tree_show.model().removeRow(rootIndex.row(), rootIndex.parent())
            else:
                break


    def get_tree_select(self):
        '''
        function:获取树控件当前选择节点的数据
        '''
        currentIndex = self.rule.ui.tree_show.currentIndex()
        return str(currentIndex.data())


    def get_table_select(self):
        '''
        function:清理表控件当前选择的行数据
        '''
        currentIndex = self.rule.ui.table_show.currentIndex()
        #return str(currentIndex.data())
        return self.rule.ui.table_show.model().data()


    def insert_category_tree(self, name) -> QStandardItem:
        '''
        function:在树控件中插入品类
        '''
        category = QStandardItem(name)
        self.rule.ui.tree_show.model().appendRow(category)
        return category


    def insert_company_tree(self, name, category) -> QStandardItem:
        '''
        function:在树控件中插入公司
        '''
        company = QStandardItem(name)
        category.appendRow(company)
        return company


    def insert_virus_tree(self, name, company):
        '''
        function:在树控件中插入规则
        '''
        virus = QStandardItem(name)
        company.appendRow(virus)


#*******************************************************************************************
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(706, 296)
        Dialog.setFixedSize(706, 296)
        self.btn_ok = QtWidgets.QPushButton(Dialog)
        self.btn_ok.setGeometry(QtCore.QRect(210, 250, 75, 31))
        self.btn_ok.setObjectName("btn_ok")
        self.btn_cancel = QtWidgets.QPushButton(Dialog)
        self.btn_cancel.setGeometry(QtCore.QRect(380, 250, 75, 31))
        self.btn_cancel.setObjectName("btn_cancel")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 31, 16))
        self.label.setObjectName("label")
        self.combo_category = QtWidgets.QComboBox(Dialog)
        self.combo_category.setGeometry(QtCore.QRect(60, 10, 211, 22))
        self.combo_category.setObjectName("combo_category")
        self.combo_category.setEditable(True)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 31, 16))
        self.label_2.setObjectName("label_2")
        self.combo_company = QtWidgets.QComboBox(Dialog)
        self.combo_company.setGeometry(QtCore.QRect(60, 50, 211, 22))
        self.combo_company.setObjectName("combo_company")
        self.combo_company.setEditable(True)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 90, 31, 16))
        self.label_3.setObjectName("label_3")
        self.combo_dimension = QtWidgets.QComboBox(Dialog)
        self.combo_dimension.setGeometry(QtCore.QRect(60, 90, 211, 22))
        self.combo_dimension.setObjectName("combo_dimension")
        self.combo_dimension.setEditable(True)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 130, 31, 16))
        self.label_4.setObjectName("label_4")
        self.combo_status = QtWidgets.QComboBox(Dialog)
        self.combo_status.setGeometry(QtCore.QRect(60, 130, 211, 22))
        self.combo_status.setObjectName("combo_status")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(10, 170, 41, 16))
        self.label_5.setObjectName("label_5")
        self.edit_virusname = QtWidgets.QLineEdit(Dialog)
        self.edit_virusname.setGeometry(QtCore.QRect(60, 170, 211, 21))
        self.edit_virusname.setObjectName("edit_virusname")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(10, 210, 41, 16))
        self.label_6.setObjectName("label_6")
        self.dedit_date = QtWidgets.QDateEdit(Dialog)
        self.dedit_date.setGeometry(QtCore.QRect(60, 210, 211, 22))
        self.dedit_date.setObjectName("dedit_date")
        self.dedit_date.setCalendarPopup(True)
        self.dedit_date.setDisplayFormat("yyyy-MM-dd")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(300, 10, 31, 16))
        self.label_7.setObjectName("label_7")
        self.tedit_rule = QtWidgets.QTextEdit(Dialog)
        self.tedit_rule.setGeometry(QtCore.QRect(330, 10, 371, 111))
        self.tedit_rule.setObjectName("tedit_rule")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(300, 130, 31, 16))
        self.label_8.setObjectName("label_8")
        self.tedit_remark = QtWidgets.QTextEdit(Dialog)
        self.tedit_remark.setGeometry(QtCore.QRect(330, 130, 371, 101))
        self.tedit_remark.setObjectName("tedit_remark")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.btn_ok.setText(_translate("Dialog", "确定"))
        self.btn_cancel.setText(_translate("Dialog", "取消"))
        self.label.setText(_translate("Dialog", "品类"))
        self.label_2.setText(_translate("Dialog", "公司"))
        self.label_3.setText(_translate("Dialog", "维度"))
        self.label_4.setText(_translate("Dialog", "状态"))
        self.label_5.setText(_translate("Dialog", "病毒名"))
        self.label_6.setText(_translate("Dialog", "日期"))
        self.label_7.setText(_translate("Dialog", "规则"))
        self.label_8.setText(_translate("Dialog", "备注"))
#*******************************************************************************************
class DialogAction(PyQt5.QtWidgets.QDialog):
    data = None  # type: list[str]

    def __init__(self, window):
        super(DialogAction, self).__init__(window)
        self.ui = Ui_Dialog()
        self.window:WindowAction = window
        self.ui.setupUi(self)
        self.setupAction()
        self.status = 'none'


    def setupTitle(self, title):
        '''
        function:设置对话框标题
        '''
        self.setWindowTitle(title)


    def setupContent(self, dict_info):
        pass



    def setupAction(self):
        '''
        function:连接信号槽
        '''
        self.ui.btn_ok.clicked.connect(self.click_comfirm)
        self.ui.btn_cancel.clicked.connect(self.click_cancel)
        self.ui.combo_category.activated.connect(self.select_category)


    def save_info(self) -> bool:
        '''
        function:保存对话框中信息
        '''
        info_category = self.get_category_combo()
        if info_category.isdigit():
            QMessageBox.warning(self,"警告","品类名不能为纯数字！",QMessageBox.Yes | QMessageBox.No)
            return False
        info_company = self.get_company_combo()
        info_dimension = self.get_dimension_combo()
        info_status = self.get_status_combo()
        info_virus = self.get_virus_name()
        if info_virus == '':
            QMessageBox.warning(self,"警告","病毒名不能为空！",QMessageBox.Yes | QMessageBox.No)
            return False
        info_date = self.get_date()
        info_rule = self.get_rule()
        if info_rule == '':
            QMessageBox.warning(self,"警告","规则不能为空！",QMessageBox.Yes | QMessageBox.No)
            return False
        info_remark = self.get_remark()
        self.save_category_table(info_category)
        self.save_company_table(info_category, info_company)
        self.save_rule_table(info_category, info_company, info_dimension, info_status, info_virus, info_date, info_rule, info_remark)
        return True


    def save_category_table(self, category) -> bool:
        '''
        function:保存品类表中的信息
        '''
        ret, list_category = self.window.rule.sql.query_category()
        if not ret:
            print('[error] -> save_category_table:query_category')
            return
        has_category = False
        for item_category in list_category:
            if category == item_category['category']:
                has_category = True
                break
        if not has_category:
            self.window.rule.sql.insert_category({'category':category, 'tablename':to_pinyin(category)})
        else:
            pass # 啥也不干


    def save_company_table(self, category, company):
        '''
        function:保存公司表中的信息
        '''
        ret, list_company = self.window.rule.sql.query_company(category)
        if not ret:
            print('[error] -> save_company_table:query_company')
            return
        has_company = False
        for item_company in list_company:
            if company == item_company:
                has_company = True
                break
        if not has_company:
            self.window.rule.sql.insert_company({'category':category, 'company':company})
        else:
            pass # 啥也不干


    def save_rule_table(self, category, company, dimension, status, virus, date, rule, remark):
        '''
        function:保存规则表中的信息
        '''
        tablename = to_pinyin(category)
        has_table = False
        tables = self.window.rule.sql.query_tables()
        for item_table in tables:
            if tablename == item_table:
                has_table = True
                break
        if has_table:
            ret, list_virus = self.window.rule.sql.query_virus_by_company(tablename, company)
            if not ret:
                QMessageBox.warning(self,"警告","save_rule_table:query_virus_by_company 出错！",QMessageBox.Yes | QMessageBox.No)
                return
            else:
                if list_virus:
                    has_virus = False
                    for vir in list_virus:
                        if vir == virus:
                            has_virus = True
                            break
                    if has_virus:
                        self.window.rule.sql.update_rule(tablename, {'company':company, 
                                                                'name':virus,
                                                                'dimension':dimension,
                                                                'status':status,
                                                                'date':date,
                                                                'rule':rule,
                                                                'remark':remark})
                    else:
                        self.window.rule.sql.insert_rule(tablename, {'company':company, 
                                                                'name':virus,
                                                                'dimension':dimension,
                                                                'status':status,
                                                                'date':date,
                                                                'rule':rule,
                                                                'remark':remark})
                else:
                    self.window.rule.sql.insert_rule(tablename, {'company':company, 
                                                                'name':virus,
                                                                'dimension':dimension,
                                                                'status':status,
                                                                'date':date,
                                                                'rule':rule,
                                                                'remark':remark})
        else:
            self.window.rule.sql.create_rule_table(tablename)
            self.window.rule.sql.insert_rule(tablename, {'company':company, 
                                                         'name':virus,
                                                         'dimension':dimension,
                                                         'status':status,
                                                         'date':date,
                                                         'rule':rule,
                                                         'remark':remark})
        self.window.update_tree()




    def click_comfirm(self):
        '''
        function:确定按钮点击事件
        '''
        if self.status != 'show':
            if self.save_info():
                self.window.clear_table()
        self.close()
        


    def click_cancel(self):
        '''
        function:取消按钮点击事件
        '''
        self.close()


    def set_category_combo(self, list_item):
        '''
        function:在控件设置品类控件的默认值列表
        '''
        self.ui.combo_category.clear()
        self.ui.combo_category.addItems(list_item)


    def get_category_combo(self):
        '''
        function:在控件获取品类控件的值
        '''
        return str(self.ui.combo_category.currentText())


    def select_category(self):
        '''
        function:用户切换品类控件中的值引发的事件
        '''
        category = self.get_category_combo()
        ret, list_company = self.window.rule.sql.query_company(category)
        if not ret:
            print('[error] -> select_category:query_company')
            return
        self.set_company_combo(list_company)


    def set_company_combo(self, list_item):
        '''
        function:在控件设置公司控件的默认值列表
        '''
        self.ui.combo_company.clear()
        self.ui.combo_company.addItems(list_item)


    def get_company_combo(self):
        '''
        function:在控件获取公司控件的值
        '''
        return str(self.ui.combo_company.currentText())


    def set_dimension_combo(self, list_dimension=['打击', '灰度', '标记']):
        '''
        function:在控件设置维度控件的默认值列表
        '''
        self.ui.combo_dimension.clear()
        self.ui.combo_dimension.addItems(list_dimension)


    def get_dimension_combo(self):
        '''
        function:在控件获取维度控件的值
        '''
        return str(self.ui.combo_dimension.currentText())


    def set_status_combo(self, list_status=['生效中', '已撤销']):
        '''
        function:在控件设置状态控件的默认值列表
        '''
        self.ui.combo_status.clear()
        self.ui.combo_status.addItems(list_status)


    def get_status_combo(self): 
        '''
        function:在控件获取状态控件的值
        '''
        return str(self.ui.combo_status.currentText())


    def set_virus_name(self, name):
        '''
        function:在控件设置默认病毒名
        '''
        self.ui.edit_virusname.setText(name)


    def get_virus_name(self):
        '''
        function:在控件获取病毒名
        '''
        return str(self.ui.edit_virusname.text())


    def set_date(self, date=QDate.currentDate()):
        '''
        function:在控件设置日期
        '''
        self.ui.dedit_date.setDate(date)


    def get_date(self):
        '''
        function:在控件获取日期
        '''
        return self.ui.dedit_date.date().toString(Qt.ISODate)


    def set_rule(self, info):
        '''
        function:在控件设置规则信息
        '''
        self.ui.tedit_rule.setText(info)


    def get_rule(self):
        '''
        function:在控件获取规则信息
        '''
        return str(self.ui.tedit_rule.toPlainText())


    def set_remark(self, info):
        '''
        function:在控件设置备注信息
        '''
        self.ui.tedit_remark.setText(info)


    def get_remark(self):
        '''
        function:在控件获取备注信息
        '''
        return str(self.ui.tedit_remark.toPlainText())


#*******************************************************************************************
class Sqlite(object):
    def __init__(self):
        self.connect = None
        self.cursor = None
        self.init()
        pass


    def init(self):
        '''
        function:检查数据库是否存在，品类表、公司表是否创建
        '''
        print('init')
        self.check_sql()
        self.connect_sql()
        self.check_category_table()
        self.check_company_table()
        


    def check_sql(self):
        '''
        function:检查数据库是否存在
        '''
        if not os.path.exists("./DB"):
            os.mkdir("./DB")
            file = open('./DB/data.db','w')
            file.close()
        else:
            if not os.path.exists("./DB/data.db"):
                file = open('./DB/data.db','w')
                file.close()
        self.backup_sql()


    def backup_sql(self):
        '''
        function:备份数据库
        '''
        try:
            if os.path.exists('./DB/1.db'):
                os.remove('./DB/1.db')
            if os.path.exists('./DB/2.db'):
                os.rename('./DB/2.db', './DB/1.db')
            if os.path.exists('./DB/3.db'):
                os.rename('./DB/3.db', './DB/2.db')
            if os.path.exists('./DB/4.db'):
                os.rename('./DB/4.db', './DB/3.db')
            if os.path.exists('./DB/5.db'):
                os.rename('./DB/5.db', './DB/4.db')
            shutil.copy('./DB/data.db', './DB/5.db')
        except Exception as err:
            print('[error] -> backup_sql:' + str(err))


    def check_category_table(self):
        '''
        function:检查品类表是否存在
        '''
        list_tables = self.query_tables()
        if 'TB_CATEGORY' not in list_tables:
            self.create_category_table()


    def check_company_table(self):
        '''
        function:检查公司表是否存在
        '''
        list_tables = self.query_tables()
        if 'TB_COMPANY' not in list_tables:
            self.create_company_table()


    def excute(self, sql):
        '''
        function:无返回执行sql
        '''
        print('excute sql == ' + sql)
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as err:
            print('[error] -> excute:sql=' + sql + ' error=' + str(err))
            return False
        return True


    def excute_for_result(self, sql):
        '''
        function:有返回执行sql
        '''
        values = None
        print('excute_for_result sql == ' + sql)
        try:
            values = self.cursor.execute(sql)
            self.connect.commit()
        except Exception as err:
            print('[error] -> excute_for_result:sql=' + sql + ' error=' + str(err))
            return False, str(err)
        return True, values


    def connect_sql(self):
        '''
        function:连接数据库
        '''
        try:
            self.connect = sqlite3.connect('./DB/data.db')
            self.cursor = self.connect.cursor()
        except Exception as err:
            print('[error] -> connect:' + str(err))
            return False, str(err)
        print('connect successfully')
        return True, ''


    def create_rule_table(self, tablename) -> bool:
        '''
        function:创建规则表
        '''
        sql = 'CREATE TABLE ' + tablename + '(company varchar(50),\
                                                name varchar(30),\
                                                dimension varchar(20),\
                                                status varchar(20),\
                                                date varchar(20),\
                                                rule varchar(500),\
                                                remark varchar(1000));'
        return self.excute(sql)
        

    def create_category_table(self) -> bool:
        '''
        function:创建品类表
        '''
        sql = 'CREATE TABLE TB_CATEGORY(category varchar(50), tablename varchar(50));'
        return self.excute(sql)


    def create_company_table(self) -> bool:
        '''
        function:创建公司表
        '''
        sql = 'CREATE TABLE TB_COMPANY(category varchar(50), company varchar(50));'
        return self.excute(sql)



    def insert_rule(self, table, info:dict) -> bool:
        '''
        function:插入规则数据
        '''
        sql = 'INSERT INTO ' + table + '(company, name, dimension, status, date, rule, remark) VALUES("'\
                                                                             + info['company'] + '","'\
                                                                             + info['name'] + '","'\
                                                                             + info['dimension'] + '","'\
                                                                             + info['status'] + '","'\
                                                                             + info['date'] + '","'\
                                                                             + info['rule'] + '","'\
                                                                             + info['remark'] + '");'
        return self.excute(sql)


    def insert_category(self, info:dict) -> bool:
        '''
        function:插入品类表名数据
        '''
        sql = 'INSERT INTO TB_CATEGORY(category, tablename) VALUES("' + info['category'] + '", "' + info['tablename'] + '");'
        return self.excute(sql)


    def insert_company(self, info:dict) -> bool:
        '''
        function:插入品类表名数据
        '''
        sql = 'INSERT INTO TB_COMPANY(category, company) VALUES("' + info['category'] + '", "' + info['company'] + '");'
        return self.excute(sql)


    def delete_table(self, table) -> bool:
        '''
        function:删除数据表
        '''
        sql = 'DROP TABLE ' + table + ';'
        return self.excute(sql)
        

    def delete_category(self, category) -> bool:
        '''
        function:删除品类信息
        '''
        sql = 'DELETE FROM TB_CATEGORY WHERE category="' + category + '";'
        return self.excute(sql)


    def delete_rule_by_company_and_virus(self, table, company, virus) -> bool:
        '''
        function:删除指定公司下面的指定病毒名的规则信息
        '''
        sql = 'DELETE FROM ' + table + ' WHERE name="' + virus + '" and company="' + company + '";'
        return self.excute(sql)


    def delete_rule_by_company(self, table, company) -> bool:
        '''
        function:删除指定公司下面的所有规则信息
        '''
        sql = 'DELETE FROM ' + table + ' WHERE company="' + company + '";'
        return self.excute(sql)


    def delete_company_by_category_and_company(self, category, company) -> bool:
        '''
        function:删除指定品类下的指定公司的信息
        '''
        sql = 'DELETE FROM TB_COMPANY WHERE company="' + company + '" and category="' + category + '";'
        return self.excute(sql)


    def delete_company_by_category(self, category) -> bool:
        '''
        function:删除指定品类下的所有公司信息
        '''
        sql = 'DELETE FROM TB_COMPANY WHERE category="' + category + '";'
        return self.excute(sql)


    def update_rule(self, table, info) -> bool:
        '''
        function:修改规则信息,注意病毒名是不能修改的
        '''
        sql = 'UPDATE ' + table + ' SET company="' + info['company']\
                                                    + '", dimension="' + info['dimension']\
                                                    + '", status="' + info['status']\
                                                    + '", date="' + info['date']\
                                                    + '", rule="' + info['rule']\
                                                    + '", remark="' + info['remark']\
                                                    + '" WHERE name="' + info['name'] + '";'
        return self.excute(sql)


    def query_tables(self) -> list:
        '''
        function:查询数据表
        '''
        list_tables = []
        sql = "select name from sqlite_master where type='table' order by name;"
        try:
            self.cursor.execute(sql)
            for value in self.cursor.fetchall():
                list_tables.append(value[0])
        except:
            return []
        return list_tables


    def query_category(self) -> tuple('''bool, list'''):
        '''
        function:查询品类表数据
        '''
        list_category = []
        sql = 'select * from TB_CATEGORY;'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_category.append({'category':value[0], 'tablename':value[1]})
        return bools, list_category


    def query_company(self, category) -> tuple('''bool, list'''):
        '''
        function:查询指定品类的公司数据
        '''
        list_company = []
        sql = 'select * from TB_COMPANY where category="' + category + '";'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_company.append(value[1])
        return bools, list_company


    def query_virus_by_company(self, table, company):
        '''
        function:在指定规则表查询指定公司旗下的病毒名列表
        '''
        list_rule = []
        sql = 'select * from ' + table + ' where company="' + company + '";'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_rule.append(value[1])
        return bools, list_rule


    def query_rule(self, table, company) -> tuple('''bool, list'''):
        '''
        function:查询指定公司的规则数据
        '''
        list_rule = []
        sql = 'select * from ' + table + ' where company="' + company + '";'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_rule.append({'company':value[0], 'name':value[1], 'dimension':value[2], 'status':value[3], 'date':value[4], 'rule':value[5], 'remark':value[6]})
        return bools, list_rule


    def query_all_rule(self, tablename) -> tuple('''bool, list'''):
        '''
        function:查询指定表的所有规则数据
        '''
        list_rule = []
        sql = 'select * from ' + tablename + ';'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_rule.append({'company':value[0], 'name':value[1], 'dimension':value[2], 'status':value[3], 'date':value[4], 'rule':value[5], 'remark':value[6]})
        return bools, list_rule

    def query_all_company(self) -> tuple('''bool, list'''):
        '''
        function:查询所有公司数据
        '''
        list_company = []
        sql = 'select * from TB_COMPANY;'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                if value[1] not in list_company:
                    list_company.append(value[1])
        return bools, list_company


    def query_rule_by_virus(self, tablename, virus) -> tuple('''bool, list'''):
        '''
        function:在指定表中查询指定病毒名的规则
        '''
        list_rule = []
        sql = 'select * from ' + tablename + ' where name="' + virus + '";'
        bools, values = self.excute_for_result(sql)
        if bools:
            for value in values:
                list_rule.append({'company':value[0], 'name':value[1], 'dimension':value[2], 'status':value[3], 'date':value[4], 'rule':value[5], 'remark':value[6]})
        return bools, list_rule


    def check_table(self):
        '''
        function:检查各个数据表中是否有多余数据
        '''


class Rule(object):

    def __init__(self):
        self.application = PyQt5.QtWidgets.QApplication(sys.argv)
        self.sql = Sqlite()
        self.ui = Ui_MainWindow()
        self.window = WindowAction(self)
        self.window.setWindowIcon(PyQt5.QtGui.QIcon('icon.png'))
        self.ui.setupUi(self.window)
        self.setup_action()
        self.setup_treeModel()
        self.setup_tableModel()
        self.dialog = DialogAction(self.window)
        self.window.show()
        sys.exit(self.application.exec_())


    def setup_action(self):
        self.ui.btn_add.clicked.connect(self.window.click_insert)
        self.ui.btn_delete.clicked.connect(self.window.click_delete)
        self.ui.btn_modify.clicked.connect(self.window.click_update)
        self.ui.btn_query.clicked.connect(self.window.click_query)
        self.ui.tree_show.clicked.connect(self.window.click_tree)


    def setup_treeModel(self):
        self.ui.tree_show.setModel(PyQt5.QtGui.QStandardItemModel(self.ui.tree_show))
        self.ui.tree_show.model().setHorizontalHeaderLabels(['Item'])
        self.ui.tree_show.setColumnWidth(0, 200)
        self.window.update_tree()


    def setup_tableModel(self):
        self.ui.table_show.setModel(PyQt5.QtGui.QStandardItemModel(self.ui.table_show))
        self.ui.table_show.model().setHorizontalHeaderLabels(['公司', '病毒名', '维度', '状态', '日期', '规则', '备注'])
        self.ui.table_show.setColumnWidth(0, 100)
        self.ui.table_show.setColumnWidth(1, 230)
        self.ui.table_show.setColumnWidth(2, 70)
        self.ui.table_show.setColumnWidth(3, 70)
        self.ui.table_show.setColumnWidth(4, 70)
        self.ui.table_show.setColumnWidth(5, 200)
        self.ui.table_show.setColumnWidth(6, 200)



if __name__ == '__main__':
    Rule()

