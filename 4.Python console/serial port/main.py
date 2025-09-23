# This is a sample Python script.
import math
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
import sys

import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from phsio import Ui_MainWindow
# from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import pyqtgraph as pg
from serial import Serial
import serial.tools.list_ports
from random import randint
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
import _thread

from scipy import signal
b, a = signal.butter(5, 0.05,'highpass',fs=250)
zi = signal.lfilter_zi(b, a)

#全局变量默认值设置
com_temp_change=36
com_temp_source=0x00#默认为Pad加热
ECG_Source_Change=0x01#默认为内部电极
Com_Open_Flag = False  # 串口打开标志
current_Stop_Bit=serial.STOPBITS_ONE
current_parity=serial.PARITY_NONE

# 获取串口数据
def Com_Data_Rsv(threadName):
    while True:
        while Com_Open_Flag:
            data = ecg_serial.read_all()
            if data == b'':
                continue
            else:
                # print("receive : ", data)
                window.Set_Display_Data(data)



class SerialPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #增加永久状态栏信息
        self.statuslabel=QtWidgets.QLabel()
        self.statuslabel.setText('Copy right by EE')
        self.ui.statusbar.addPermanentWidget(self.statuslabel)

        #全局绘图设置：抗锯齿
        pg.setConfigOptions(antialias=True,foreground ='r')
        #设置坐标轴的文本
        font=QFont()
        font.setPixelSize(14)
        #绘图显示窗口定义
        # self.x = list(range(100)) # X轴坐标
        # self.y = [randint(0 , 100) for _ in range(100)] # Y轴坐标
        self.x = list(range(50)) # X轴坐标
        self.y = [randint(0 , 0) for _ in range(50)] # Y轴坐标

        self.x1 = list(range(30)) # X轴坐标
        self.y1 = [randint(0 , 0) for _ in range(10)] # Y轴坐标


        self.x2 = list(range(30)) # X轴坐标
        self.y2 = [randint(0 , 0) for _ in range(10)] # Y轴坐标

        #Animal_Temp_View窗口设置
        self.ui.Animal_Temp_View.setBackground('w')
        Animal_Temp_View_pen = pg.mkPen(color='b', width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.Animal_Temp_View.setLabel('bottom', 'time', **styles)
        self.ui.Animal_Temp_View.setLabel('left', 'Temp (℃)', **styles)
        self.ui.Animal_Temp_View.showGrid(x=True, y=True)
        #设置坐标轴的样式
        self.ui.Animal_Temp_View.getAxis("left").setFont(font)
        self.ui.Animal_Temp_View.getAxis("left").setTextPen('k')
        self.ui.Animal_Temp_View.getAxis("bottom").setTextPen('k')
        # self.ui.Animal_Temp_View.setTitle('Animal_Temp', color = 'r' , size = '10pt')

        #Pad_Temp_View窗口设置
        self.ui.Pad_Temp_View.setBackground('w')
        # pen = pg.mkPen(color=(255, 0, 0), width = 5)
        Pad_Temp_View_pen = pg.mkPen(color='b', width=5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.Pad_Temp_View.setLabel('bottom', 'time', **styles)
        self.ui.Pad_Temp_View.setLabel('left', 'Temp (℃)', **styles)
        self.ui.Pad_Temp_View.showGrid(x=True, y=True)
        #设置坐标轴的样式
        self.ui.Pad_Temp_View.getAxis("left").setFont(font)
        self.ui.Pad_Temp_View.getAxis("left").setTextPen('k')
        self.ui.Pad_Temp_View.getAxis("bottom").setTextPen('k')
        # self.ui.Pad_Temp_View.setTitle('Pad_Temp', color = 'r' , size = '10pt')

        #Spo2窗口设置
        self.ui.Spo2.setBackground('w')
        # pen = pg.mkPen(color=(255, 0, 0), width = 5)
        Spo2_pen = pg.mkPen(color='b', width=5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.Spo2.setLabel('bottom', 'time', **styles)
        self.ui.Spo2.setLabel('left', '%', **styles)
        self.ui.Spo2.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.Spo2.getAxis("left").setFont(font)
        self.ui.Spo2.getAxis("left").setTextPen('k')
        self.ui.Spo2.getAxis("bottom").setTextPen('k')
        # self.ui.Spo2.setTitle('Spo2', color = 'r' , size = '10pt')

        #Resp窗口设置
        self.ui.Resp.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.Resp.setLabel('bottom', 'time', **styles)
        self.ui.Resp.setLabel('left', 'mV', **styles)
        self.ui.Resp.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.Resp.getAxis("left").setFont(font)
        self.ui.Resp.getAxis("left").setTextPen('k')
        self.ui.Resp.getAxis("bottom").setTextPen('k')
        # self.ui.Resp.setTitle('Resp', color = 'r' , size = '10pt')

        #ECG_I窗口设置
        self.ui.ECG_I.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_I.setLabel('bottom', 'time', **styles)
        self.ui.ECG_I.setLabel('left', 'mV', **styles)
        self.ui.ECG_I.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_I.getAxis("left").setFont(font)
        self.ui.ECG_I.getAxis("left").setTextPen('k')
        self.ui.ECG_I.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_I.setTitle('ECG_I', color = 'r' , size = '10pt')

        #ECG_II窗口设置
        self.ui.ECG_II.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_II.setLabel('bottom', 'time', **styles)
        self.ui.ECG_II.setLabel('left', 'mV', **styles)
        self.ui.ECG_II.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_II.getAxis("left").setFont(font)
        self.ui.ECG_II.getAxis("left").setTextPen('k')
        self.ui.ECG_II.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_II.setTitle('ECG_II', color = 'r' , size = '10pt')

        #ECG_III窗口设置
        self.ui.ECG_III.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_III.setLabel('bottom', 'time', **styles)
        self.ui.ECG_III.setLabel('left', 'mV', **styles)
        self.ui.ECG_III.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_III.getAxis("left").setFont(font)
        self.ui.ECG_III.getAxis("left").setTextPen('k')
        self.ui.ECG_III.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_III.setTitle('ECG_III', color = 'r' , size = '10pt')

        #ECG_AVL窗口设置
        self.ui.ECG_AVL.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_AVL.setLabel('bottom', 'time', **styles)
        self.ui.ECG_AVL.setLabel('left', 'mV', **styles)
        self.ui.ECG_AVL.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_AVL.getAxis("left").setFont(font)
        self.ui.ECG_AVL.getAxis("left").setTextPen('k')
        self.ui.ECG_AVL.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_AVL.setTitle('ECG_AVL', color = 'r' , size = '10pt')

        #ECG_AVR窗口设置
        self.ui.ECG_AVR.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_AVR.setLabel('bottom', 'time', **styles)
        self.ui.ECG_AVR.setLabel('left', 'mV', **styles)
        self.ui.ECG_AVR.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_AVR.getAxis("left").setFont(font)
        self.ui.ECG_AVR.getAxis("left").setTextPen('k')
        self.ui.ECG_AVR.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_AVR.setTitle('ECG_AVR', color = 'r' , size = '10pt')

        #ECG_AVF窗口设置
        self.ui.ECG_AVF.setBackground('w')
        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        styles = {'color': '#f00', 'font-size': '20px'}  # 设置标签的颜色和大小
        # self.ui.ECG_AVF.setLabel('bottom', 'time', **styles)
        self.ui.ECG_AVF.setLabel('left', 'mV', **styles)
        self.ui.ECG_AVF.showGrid(x=True, y=True)
        # 设置坐标轴的样式
        self.ui.ECG_AVF.getAxis("left").setFont(font)
        self.ui.ECG_AVF.getAxis("left").setTextPen('k')
        self.ui.ECG_AVF.getAxis("bottom").setTextPen('k')
        # self.ui.ECG_AVF.setTitle('ECG_AVF', color = 'r' , size = '10pt')

        #添加legend
        # self.ui.ECG_I.addLegend(offset=(30, 30))
        #创建PlotDataItem
        self.Animal_Temp_View = self.ui.Animal_Temp_View.plot(pen = Animal_Temp_View_pen,name='Animal_Temp',viewBox='ViewBox')
        self.Pad_Temp_View = self.ui.Pad_Temp_View.plot(pen=Pad_Temp_View_pen,
                                                              name='Animal_Temp', viewBox='ViewBox')
        self.Spo2_View = self.ui.Spo2.plot(pen=Spo2_pen,
                                                              name='spo2', viewBox='ViewBox')
        #添加ROI
        # lr = pg.LinearRegionItem([100, 200])
        # lr.setZValue(-10)
        # self.ui.ECG_I.addItem(lr)
        self.create_time() #创建时间

        # 定义串口对象
        self.port_list=list(serial.tools.list_ports.comports())
        if len(self.port_list) ==0:
            self.ui.statusbar.showMessage(f'No available SerialCom')
        # 读取串口信息，并选择第一个串口
        for com_port in range(0,len(self.port_list)):
            #选择显示COM name or description
            # self.ui.Com1.addItem(self.port_list[com_port].name)
            # self.ui.Com2.addItem(self.port_list[com_port].name)
            self.ui.Com1.addItem(self.port_list[com_port].description)
            self.ui.Com2.addItem(self.port_list[com_port].description)
            # 打印串口号后面的字符
            # print(str(self.port_list[com_port].description))

    # 创建50s的定时时间
    def create_time(self):
        self.timer = QTimer()  # 创建时间类
        self.timer.setInterval(25)  # 设置内部定时为50
        # self.timer.timeout.connect(self.update_plot_data)  # 50s时间一到则调用update_plot_data函数
        self.timer.timeout.connect(self.Set_Display_Data)
        self.timer.start()  # 开始计时

    def update_plot_data(self):
        # self.x = self.x[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
        # self.x.append(self.x[-1] + 1)  # 增加一个数，增加的数值为最后一个数+1
        #
        # self.y = self.y[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
        # z = randint(0, 100)  # 取一个随机数，赋值给z
        # self.y.append(z)  # 将z添加到列表y的最后一个数
        #
        # self.Animal_Temp_View.setData(self.x, self.y)  # 更新x轴和y轴的数据
        # #将最新的数据更新至对应的label
        self.ui.Ani_Temp.setText(str(self.y[-1]))

    def Set_Display_Data(self):
        self.timer.stop()  # stop计时
        if Com_Open_Flag:
            # self.data = ecg_serial.read_all()
            self.data = spo2_serial.read_all() #由于处理速度不够，只取第一个数据，相当于抽取滤波器
            # # self.data = spo2_serial.readline()
            # print(self.data)
            if self.data == b'':
                 z=0
            else :
                try:
                    if self.data[2] == 1:
                        try:
                            # print(self.data[2])
                            self.x = self.x[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                            self.x.append(self.x[-1] + 1)  # 增加一个数，增加的数值为最后一个数+1
                            self.y = self.y[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                            # z = int.from_bytes(bytes(Data[0:2]), 'little')
                            self.data = self.data[3:]
                            # print(self.data)
                            self.data=(self.data[0]<<16)|(self.data[1]<<8)|(self.data[2])
                            # self.data =(self.data[1]<<8)| (self.data[2])
                            self.data = 0.000000572 * self.data
                            z = float(self.data)
                            # print("z : ", z)
                            # if z =='':
                            #     z=0
                            self.y.append(z)  # 将z添加到列表y的最后一个数
                            z1, _ = signal.lfilter(b, a, self.y, zi=zi * self.y[0])
                            # self.Spo2_View.setData(self.x, self.y)
                            self.Spo2_View.setData(self.x, z1)
                            # 将最新的数据更新至对应的label
                        except:
                            print("some error")
                            z = 0
                            self.y.append(z)  # 将z添加到列表y的最后一个数
                    if self.data[2] == 2:
                        try:
                        # print(self.data[2])
                             self.x2 = self.x2[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                             self.x2.append(self.x2[-1] + 1)  # 增加一个数，增加的数值为最后一个数+1
                             self.y2 = self.y2[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                             # z = int.from_bytes(bytes(Data[0:2]), 'little')
                             self.data=self.data[3:]
                             # print(self.data)
                             # self.data=(self.data[0]<<16)|(self.data[1]<<8)|(self.data[2])
                             self.data=(self.data[0]<<8)|(self.data[1])
                             self.data=0.0008*self.data
                             self.data =(1/((1/3380)*math.log(((3.28/(self.data/10000)-10000))/10000)+(1/(25+273.15)))-273.15)
                             z2=float(self.data)
                             # print("z : ", z)
                             # if z =='':
                             #     z=0
                             self.y2.append(z2)  # 将z添加到列表y的最后一个数
                             self.Animal_Temp_View.setData(self.x2, self.y2)
                             # 将最新的数据更新至对应的label
                             self.ui.Ani_Temp.setStyleSheet("color: red")
                             self.ui.Ani_Temp.setText(str(self.y2[-1]))
                        except:
                            print("some error")
                            z2=0
                            self.y2.append(z2)  # 将z添加到列表y的最后一个数
                    else:

                        if self.data[2] == 3:
                            try:
                            # print(self.data[2])
                                 self.x1 = self.x1[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                                 self.x1.append(self.x1[-1] + 1)  # 增加一个数，增加的数值为最后一个数+1
                                 self.y1 = self.y1[1:]  # 去掉列表第一个数，取出除第一个数之外的所有数
                                 # z = int.from_bytes(bytes(Data[0:2]), 'little')
                                 self.data=self.data[3:]
                                 # print(self.data)
                                 self.data=(self.data[0]<<16)|(self.data[1]<<8)|(self.data[2])
                                 #self.data=(self.data[0]<<8)|(self.data[1])
                                 self.data=0.0078125*self.data
                                 z1=float(self.data)
                                 # print("z : ", z)
                                 # if z =='':
                                 #     z=0
                                 self.y1.append(z1)  # 将z添加到列表y的最后一个数
                                 self.Pad_Temp_View.setData(self.x1, self.y1)
                                 # 将最新的数据更新至对应的label
                                 self.ui.Pad_Temp.setStyleSheet("color: red")
                                 self.ui.Pad_Temp.setText(str(self.y1[-1]))
                            except:
                                print("some error")
                                z1=0
                                self.y1.append(z1)  # 将z添加到列表y的最后一个数
                except:
                    print("index out of range")
        self.timer.start()  # 开始计时



    #Open_Com为按键单击事件的槽函数
    def Open_Com(self):
        try:
            global ecg_serial,spo2_serial  # 全局变量，需要加global
            global Com_Open_Flag,current_Stop_Bit,current_parity
            print("点击了打开串口按钮")
            if self.ui.Conn_Button.text() == "Connect":
                print(self.ui.Com1.currentText())
                print(self.ui.Com2.currentText())
                #判断停止位
                if self.ui.Stop_Bit.currentText()== "STOPBITS_ONE":
                    current_Stop_Bit=serial.STOPBITS_ONE
                else:
                    if self.ui.Check_Bit.currentText()== "STOPBITS_TWO":
                        current_Stop_Bit = serial.STOPBITS_TWO
                # 判断校验位
                if self.ui.Check_Bit.currentText()== "PARITY_NONE":
                    current_parity=serial.PARITY_NONE
                else:
                    if self.ui.Check_Bit.currentText()== "PARITY_EVEN":
                        current_parity = serial.PARITY_EVEN
                    else:
                        if self.ui.Check_Bit.currentText() == "PARITY_ODD":
                            current_parity = serial.PARITY_ODD

                #利用正则表达式从description中提取出port
                ecg_port=re.findall('.*\((.*)\)',self.ui.Com1.currentText())
                spo2_port = re.findall('.*\((.*)\)', self.ui.Com2.currentText())

                # ecg_serial = serial.Serial(self.ui.Com1.currentText(), int(self.ui.Baud_Rate.currentText()),
                #                               bytesize =serial.EIGHTBITS,parity=current_parity,stopbits=current_Stop_Bit,timeout=0.1)
                # spo2_serial = serial.Serial(self.ui.Com2.currentText(), int(self.ui.Baud_Rate.currentText()),
                #                               bytesize=serial.EIGHTBITS, parity=current_parity, stopbits=current_Stop_Bit,
                #                               timeout=0.1)
                #[0]代表去掉结果中的括号（结果会自带括号）
                ecg_serial = serial.Serial(ecg_port[0], int(self.ui.Baud_Rate.currentText()),
                                              bytesize =serial.EIGHTBITS,parity=current_parity,stopbits=current_Stop_Bit,timeout=0.1)
                spo2_serial = serial.Serial(spo2_port[0], int(self.ui.Baud_Rate.currentText()),
                                              bytesize=serial.EIGHTBITS, parity=current_parity, stopbits=current_Stop_Bit,
                                              timeout=0.1)


                #设置波特率等选项变化状态
                if ecg_serial.isOpen():
                    self.ui.statusbar.showMessage(f'{self.ui.Com1.currentText()}  Connected')
                    print("open ecg_serial success")
                    Com_Open_Flag = True
                    self.ui.Conn_Button.setText("Disconnect")
                    self.ui.Baud_Rate.setEnabled(False)  # 串口号和波特率变为不可选择
                    self.ui.Com1.setEnabled(False)
                    self.ui.Stop_Bit.setEnabled(False)
                    self.ui.Check_Bit.setEnabled(False)
                else:
                    print("open failed")

                if spo2_serial.isOpen():
                    self.ui.statusbar.showMessage(f'{self.ui.Com2.currentText()}  Connected')
                    print("open spo2_serial success")
                    Com_Open_Flag = True
                    self.ui.Conn_Button.setText("Disconnect")
                    self.ui.Baud_Rate.setEnabled(False)  # 串口号和波特率变为不可选择
                    self.ui.Com2.setEnabled(False)
                    self.ui.Stop_Bit.setEnabled(False)
                    self.ui.Check_Bit.setEnabled(False)
                else:
                    print("open failed")

            else:
                Com_Open_Flag = False
                self.ui.Conn_Button.setText("Connect")
                self.ui.statusbar.showMessage(f'Com DisConnected')
                ecg_serial.close()
                spo2_serial.close()
                self.ui.Baud_Rate.setEnabled(True)  # 串口号和波特率变为可选择
                self.ui.Com1.setEnabled(True)
                self.ui.Com2.setEnabled(True)
                self.ui.Stop_Bit.setEnabled(True)
                self.ui.Check_Bit.setEnabled(True)

        except :
            self.ui.statusbar.showMessage(f'Serial Com occurs some errors:may com not chosed,or com is using by others')


    def Temp_Change(self):
        global com_temp_change,com_temp_source,ECG_Source_Change
        print("Temp_Set Change!")
        com_temp_change=self.ui.Temp_Set.currentText()
        self.ui.statusbar.showMessage(f'Temp set to {self.ui.Temp_Set.currentText()} ℃')
        self.Com_Send_Cmd()


    def Temp_Source_Change(self):
        global com_temp_change, com_temp_source, ECG_Source_Change
        print("Temp_Source Change!")
        #判断多选框的勾选状态
        if self.ui.Pad_Button.isChecked()== True :
             self.ui.statusbar.showMessage(f'Temp_Source changed to Pad ')
             com_temp_source=0x00
             self.Com_Send_Cmd()
        else:
             self.ui.statusbar.showMessage(f'Temp_Source changed to Animal ')
             com_temp_source = 0x01
             self.Com_Send_Cmd()

        #传递温度设置值给MCU
        # if self.ui.Temp_Set.text() == "Connect":



    def ECG_Source_Change(self):
        global com_temp_change, com_temp_source, ECG_Source_Change
        print("ECG_Source Change!")
        if self.ui.Ext_checkBox.isChecked()== True :
            ECG_Source_Change=0x00
            self.ui.statusbar.showMessage(f'ECG_Source changed to Ext')
            self.Com_Send_Cmd()
        else:
            ECG_Source_Change =0x01
            self.ui.statusbar.showMessage(f'ECG_Source changed to Int')
            self.Com_Send_Cmd()
        #传递温度设置值给MCU
        # if self.ui.Temp_Set.text() == "Connect":

    #下发控制字命令
    # 发送相应的控制指令 AA 55 为spo2串口头，05为上位机下发的控制字，第三个字节为控温对象（00为Pad，01为Animal），
    # 第四个为设置温度，第五个字节为电极对象(00为外部电极，01为内部电极)
    def Com_Send_Cmd(self):
        Cmd='AA55050' + str(com_temp_source) + str(com_temp_change)+ '0' +str(ECG_Source_Change)
        if Com_Open_Flag ==True:
            spo2_serial.write(bytes.fromhex(Cmd))
        else :
            self.ui.statusbar.showMessage(f'Spo2 serial com not open,so cmd is not work')


    # def on_timeout(self):
    #     rcv_data = self.COM.readAll()
    #     if len(rcv_data) >= 2:
    #         print(int.from_bytes(bytes(rcv_data[0:2]), 'little'))


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = SerialPlot()
    # 设置fusion风格
    app.setStyle(QStyleFactory.create('fusion'))
    # window.ui.statusbar.showMessage(f'Connected')
    window.setWindowIcon(QIcon("./Rat.png"))

    _thread.start_new_thread(Com_Data_Rsv, ("Thread-1",))

    #正常窗口
    window.show()
    #最大化窗口
    window.showMaximized()

    sys.exit(app.exec())



