from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui
from PyQt5.QtChart import *
from PyQt5 import QtCore
import csv
import time
import u3
d = u3.U3()


# Global variables
TEST_TIME = 30          # This sets the test time in seconds, 
                        # You can change the  test time as you want
MAX_PSI_FOR_SENSOR = 300 # 300 PSI is the max psi that our team's pressure transducer can measure.
                         # You can change this value with the max psi that your pressure trasndcuer can measure.
HOLD_PSI = 40           # 40 PSI is where we want to hold.

# (Components)    (LabJack)     (Relay)
#   pump          	FIO4    	input4 
#   s1	            FIO5	    input5
#   s2	            FIO6	    input6  
#   pressure trans  AIN0        -


# converting voltage to PSI 
def convert(x):
    psi = 0
    if x<0.5:   # if voltage is lower than 0.5V, then PSI = 0 (which is min PSI)
        psi = 0
    elif x >= 4.5: # if voltage is higher than 4.5V, then PSI is max)
        psi = MAX_PSI_FOR_SENSOR
    else:  # else, the voltage and psi are in linear (from Manual: 0 psi = 0.5V, 50 psi = 2.5V, 100 psi = 4.5V)
        psi = (x-0.5)/(4/MAX_PSI_FOR_SENSOR)
    return psi


# averaging voltage, psi for every second
def avg():
    volt = 0
    psi = 0
    
    for i in range(10): # get psi data every 0.1 s, and collect 10 of it then average it
       volt += d.getAIN(0)  #It's reading the data from AIN0 port. Make sure to check your pressure transducer is connected to AIN0 port.
       psi += convert(d.getAIN(0))
       time.sleep(0.1) # 0.1s sleep
    return [volt/10, psi/10]

# read the psi for every 0.01 second
def read_psi():
    psi=convert(d.getAIN(0))
    return psi



class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("mygui2.ui",self)
        self.show()
        
        # Initially, all the components are off 
        # Components status: 0=Off, 1=On
        self.solenoid_1 = 0
        self.solenoid_2 = 0
        self.pump = 0
        d.setFIOState(4, state=0)   # PUMP    FIO4 off 
        d.setFIOState(5, state=0)   # S1      FIO5 off
        d.setFIOState(6, state=0)   # S2      FIO6 off

        # 1. Connect 
        self.pushButton_1.clicked.connect(self.connect1)        #1. LabJack connect button
        self.pushButton_2.clicked.connect(self.connect2)        #2. Relay Switch connect button
        self.pushButton_3.clicked.connect(self.connect3)        #3. Solenoid valves connect button
        self.pushButton_next.clicked.connect(self.next1)        #4. Next button
        self.pushButton_cancel.clicked.connect(self.cancel)     #5. Cancel button

        # 2. Fill 
        self.pushButton_back.clicked.connect(self.back1)        #1. Back button
        self.pushButton_fill.clicked.connect(self.fill)         #2. Fill Button
        self.pushButton_next2.clicked.connect(self.next2)       #3. Next button
        self.pushButton_cancel2.clicked.connect(self.cancel)    #4. Cancel button
        self.pushButton_set.clicked.connect(self.setFillTime)   #5. Set Button   

        self.FILL_TIME = 0    

        self.current_file = "pressureLoop6.jpg"                 #6. Upload image
        pixmap = QtGui.QPixmap(self.current_file)
        pixmap = pixmap.scaled(self.width(),self.height())
        self.label_pic.setPixmap(pixmap)
        self.label_pic.setMinimumSize(1,1)

        self.label_stat1_2.setStyleSheet("color: red; font: bold")
        self.label_stat2_2.setStyleSheet("color: red; font: bold")
        self.label_stat3_2.setStyleSheet("color: red; font: bold")

        self.piclabel_1.setStyleSheet("color: red; font: bold")
        self.piclabel_2.setStyleSheet("color: red; font: bold")
        self.piclabel_3.setStyleSheet("color: red; font: bold")

        # 3. Test
        self.pushButton_back2.clicked.connect(self.back2)       #1. Back button
        self.pushButton_test.clicked.connect(self.test)         #2. Test button
        self.pushButton_cancel3.clicked.connect(self.cancel)    #3. Finish button
        self.pushButton_save.clicked.connect(self.save)         #4. Save button
        # self.pushButton_set_2.clicked.connect(self.setTestTime) #5. Set Button 
        # self.TEST_TIME = 0 

        self.data_list = []  # data_list to write csv file

        self.chart = QChart()                                   #6. Chart settings
        self.chart.setTitle("Pressure Data Plot")

        self.axisX = QValueAxis()   # X axis
        self.axisX.setRange(0,TEST_TIME)   # 0 ~ 'TEST_TIME' seconds
        self.axisX.setTitleText("Time (s)")

        self.axisY = QValueAxis()   # Y axis
        self.axisY.setRange(0,MAX_PSI_FOR_SENSOR)   # 0 ~ 'MAX_PSI_FOR_SENSOR' psi
        self.axisY.setTitleText("Pressure (psi)")

        self.chart.setAxisX(self.axisX)
        self.chart.setAxisY(self.axisY)

        w_graph = self.horizontalFrame_graph.width()
        h_graph = self.horizontalFrame_graph.height()

        self.chart_view = QChartView(self.chart)
        self.chart_view.setFixedWidth(w_graph)
        self.chart_view.setFixedHeight(h_graph)
        self.chart_view.setParent(self.horizontalFrame_graph)

        # 4. Manual Control
        self.pushButton_back_4.clicked.connect(self.back3)      #1. Back button
        self.pushButton_cancel4.clicked.connect(self.cancel)    #2. Cancel button

        self.pushButton_sw1.clicked.connect(self.sw1)           #3. SW1 = Solenoid valve #1
        self.pushButton_sw2.clicked.connect(self.sw2)           #4. SW2 = Solenoid valve #2
        self.pushButton_sw3.clicked.connect(self.sw3)           #5. SW3 = pump
                
        self.label_pic_4.setPixmap(pixmap)                      #7. Upload image
        self.label_pic_4.setMinimumSize(1,1)

        self.label_pic4_1.setText("OFF")
        self.label_pic4_2.setText("OFF")
        self.label_pic4_3.setText("OFF")
        self.label_pic4_1.setStyleSheet("color: red; font: bold")
        self.label_pic4_2.setStyleSheet("color: red; font: bold")
        self.label_pic4_3.setStyleSheet("color: red; font: bold")

        self.label_sw_stat1.setText("OFF")
        self.label_sw_stat2.setText("OFF")
        self.label_sw_stat3.setText("OFF")
        self.label_sw_stat1.setStyleSheet("color: red; font: bold")
        self.label_sw_stat2.setStyleSheet("color: red; font: bold")
        self.label_sw_stat3.setStyleSheet("color: red; font: bold")
        
    # 1. Functions use in Connect page
    def connect1(self): # Labjack connection
        self.label_conn1_2.setText("Connected")
        self.label_conn1_2.setStyleSheet("color: green; font: bold")

        self.pushButton_2.setEnabled(True)

    def connect2(self): # Relay Switch connection
        self.label_conn2_2.setText("Connected")
        self.label_conn1_3.setText("Connected")

        self.label_conn2_2.setStyleSheet("color: green; font: bold")
        self.label_conn1_3.setStyleSheet("color: green; font: bold")

        self.pushButton_3.setEnabled(True)

    def connect3(self): # Solenoid valves connection
        self.label_conn1.setText("Connected")
        self.label_conn2.setText("Connected")
        self.label_conn3.setText("Connected")
        self.label_conn1.setStyleSheet("color: green; font: bold")
        self.label_conn2.setStyleSheet("color: green; font: bold")
        self.label_conn3.setStyleSheet("color: green; font: bold")

        self.label_stat1.setText("OFF")
        self.label_stat2.setText("OFF")
        self.label_stat3.setText("OFF")
        self.label_stat1.setStyleSheet("color: red; font: bold")
        self.label_stat2.setStyleSheet("color: red; font: bold")
        self.label_stat3.setStyleSheet("color: red; font: bold")

        # for 4.Manual Control
        self.label_conn4_1.setText("Connected")
        self.label_conn4_2.setText("Connected")
        self.label_conn4_3.setText("Connected")
        self.label_conn4_1.setStyleSheet("color: green; font: bold")
        self.label_conn4_2.setStyleSheet("color: green; font: bold")
        self.label_conn4_3.setStyleSheet("color: green; font: bold")

        self.pushButton_next.setEnabled(True)
        self.pushButton_set.setEnabled(True)

    def next1(self): # Next button 
        self.tabWidget.setCurrentIndex(1)

    def cancel(self):  # Cancel button 
        d.setFIOState(4, state=0)   # PUMP    FIO4 off 
        d.setFIOState(5, state=0)   # S1      FIO5 off
        d.setFIOState(6, state=0)   # S2      FIO6 off
        self.close()

    # 2. Functions use in Fill page
    def back1(self):        # Back Button 
        self.tabWidget.setCurrentIndex(0)

    def setFillTime(self):  # Set Button
        self.FILL_TIME = self.spinBox.value()
        self.pushButton_fill.setEnabled(True)

    def fill(self):         # Fill button
        self.label_stat1_2.setText("ON")
        self.label_stat2_2.setText("ON")
        self.label_stat3_2.setText("ON")

        self.label_stat1_2.setStyleSheet("color: green; font: bold")
        self.label_stat2_2.setStyleSheet("color: green; font: bold")
        self.label_stat3_2.setStyleSheet("color: green; font: bold")

        self.piclabel_1.setText("ON")
        self.piclabel_2.setText("ON")
        self.piclabel_3.setText("ON")

        self.piclabel_1.setStyleSheet("color: green; font: bold")
        self.piclabel_2.setStyleSheet("color: green; font: bold")
        self.piclabel_3.setStyleSheet("color: green; font: bold")

        # Fill: s1, s3, pump on
        d.setFIOState(4, state=1)   # PUMP    FIO4 on 
        d.setFIOState(5, state=1)   # S1      FIO5 on
        d.setFIOState(6, state=1)   # S2      FIO6 on

        x = 0
        while x <= 100: # 10s = 100 * 0.1s
            sleep_time = self.FILL_TIME/100
            time.sleep(sleep_time)
            self.progressBar_fill.setValue(x)
            x+=1

        # Stop: s1, s2, pump off
        d.setFIOState(4, state=0)   # PUMP    FIO4 off 
        d.setFIOState(5, state=0)   # S1      FIO5 off
        d.setFIOState(6, state=0)   # S2      FIO6 off

        
        # Pressurize: s1 & pump on, s2 off
        d.setFIOState(4, state=1)   # PUMP    FIO4 on
        d.setFIOState(5, state=1)   # S1      FIO5 on
        d.setFIOState(6, state=0)   # S2      FIO6 off

        current_psi = 0
        while (current_psi < HOLD_PSI):
            current_psi=read_psi()

        d.setFIOState(4, state=0)   # PUMP    FIO4 on
        d.setFIOState(5, state=0)   # S1      FIO5 off
        d.setFIOState(6, state=0)   # S2      FIO6 off


        self.label_stat1_2.setText("OFF")
        self.label_stat2_2.setText("OFF")
        self.label_stat3_2.setText("OFF")

        self.label_stat1_2.setStyleSheet("color: red; font: bold")
        self.label_stat2_2.setStyleSheet("color: red; font: bold")
        self.label_stat3_2.setStyleSheet("color: red; font: bold")



        self.piclabel_1.setText("OFF")
        self.piclabel_2.setText("OFF")
        self.piclabel_3.setText("OFF")

        self.piclabel_1.setStyleSheet("color: red; font: bold")
        self.piclabel_2.setStyleSheet("color: red; font: bold")
        self.piclabel_3.setStyleSheet("color: red; font: bold")

        self.msgBox_fill = QMessageBox()
        self.msgBox_fill.setIcon(QMessageBox.Information)
        self.msgBox_fill.setWindowTitle("Fill Done")
        self.msgBox_fill.setText("Fill is done.\nYou can now do a pressure test.")
        self.msgBox_fill.exec()
        
        self.pushButton_next2.setEnabled(True)
        self.pushButton_test.setEnabled(True)

    def next2(self):    # Next button 
        self.tabWidget.setCurrentIndex(2)

    # 3. Functions use in Test page
    def back2(self):    # Back Button 
        self.tabWidget.setCurrentIndex(1)

    def test(self):     # Test Button
        self.series = QLineSeries()

       
        # #AVG_PSI
        t = 0
        while t<=TEST_TIME:    #change time
            avg_volt_psi = avg()
            psi = avg_volt_psi[1]   #get PSI

            self.series.append(t,psi)   #update PSI data
            self.label_psi.setText("%.2f" % psi)

            self.chart.addSeries(self.series)   #update chart
            self.series.attachAxis(self.axisX)
            self.series.attachAxis(self.axisY)           
            qApp.processEvents()
            self.data_list.append(psi)          #add psi data to data_list
            
            t+=1

        self.msgBox_test = QMessageBox()
        self.msgBox_test.setIcon(QMessageBox.Information)
        self.msgBox_test.setWindowTitle("Test Done")
        self.msgBox_test.setText("Pressure test is done.\nYou can now save the data.")
        self.msgBox_test.exec()

        self.pushButton_save.setEnabled(True)
        self.pushButton_cancel3.setEnabled(True)

    def save(self):    # Save Button
        f = open('C:/Users/Admin/Downloads/pressure_data.csv', 'w')
        f.write('Time (s),Pressure (PSI) \n')
        
        t=0
        while t<=TEST_TIME:
            f.write("%d, " % t)
            f.write("%.2f \n" % self.data_list[t])            
            t+=1
        f.close()

        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle("Saved")
        self.msgBox.setText("Pressure data is saved in\n\'C:/Users/Admin/Downloads/pressure_data.csv\'")
        self.msgBox.exec()

  
        
    # 4. Functions in Manual Control page
    def back3(self):    # Back Button 
        self.tabWidget.setCurrentIndex(2)

    def sw1(self):      # sw1 Button
        if self.solenoid_1 == 0:
            d.setFIOState(5, state=1)   # S1      FIO5 on
            self.solenoid_1 = 1
            self.label_sw_stat1.setText("ON")
            self.label_sw_stat1.setStyleSheet("color: green; font: bold")
            self.label_pic4_1.setText("ON")     #label on pic
            self.label_pic4_1.setStyleSheet("color: green; font: bold") 
        else:
            d.setFIOState(5, state=0)   # S1      FIO5 off
            self.solenoid_1 = 0
            self.label_sw_stat1.setText("OFF")
            self.label_sw_stat1.setStyleSheet("color: red; font: bold")
            self.label_pic4_1.setText("OFF")     #label on pic
            self.label_pic4_1.setStyleSheet("color: red; font: bold") 

    def sw2(self):      # sw2 Button 
        if self.solenoid_2 == 0:
            d.setFIOState(6, state=1)   # S2      FIO6 on
            self.solenoid_2 = 1
            self.label_sw_stat2.setText("ON")
            self.label_sw_stat2.setStyleSheet("color: green; font: bold")
            self.label_pic4_2.setText("ON")     #label on pic
            self.label_pic4_2.setStyleSheet("color: green; font: bold")  
        else:
            d.setFIOState(6, state=0)   # S2      FIO6 off
            self.solenoid_2 = 0
            self.label_sw_stat2.setText("OFF")
            self.label_sw_stat2.setStyleSheet("color: red; font: bold")
            self.label_pic4_2.setText("OFF")     #label on pic
            self.label_pic4_2.setStyleSheet("color: red; font: bold")  

    def sw3(self):      # sw3 Button 
        if self.pump == 0:
            d.setFIOState(4, state=1)   # S3      FIO7 on
            self.pump = 1
            self.label_sw_stat3.setText("ON")
            self.label_sw_stat3.setStyleSheet("color: green; font: bold")    
            self.label_pic4_3.setText("ON")     #label on pic
            self.label_pic4_3.setStyleSheet("color: green; font: bold")     
        else:
            d.setFIOState(4, state=0)   # S4      FIO7 off
            self.pump = 0
            self.label_sw_stat3.setText("OFF")
            self.label_sw_stat3.setStyleSheet("color: red; font: bold")
            self.label_pic4_3.setText("OFF")     #label on pic
            self.label_pic4_3.setStyleSheet("color: red; font: bold")  
    
   

def main():
    app = QApplication([])
    window = MyGUI()
    window.setWindowTitle("Pressure Test App")
    app.exec_()




if __name__ == '__main__':
    main()
