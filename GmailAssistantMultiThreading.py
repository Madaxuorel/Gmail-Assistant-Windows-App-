#Copyright (c) 2020 Adam Le Roux

from __future__ import print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThreadPool, QRunnable
from PyQt5.QtWidgets import QMessageBox
from plyer import notification
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from time import sleep
version="1.1"

class Ui_MainWindow(object):
    def __init__(self):
        with open("adresses.txt","r") as save:
            self.adresses = save.read().split(" ") 
        self.threadpool = QThreadPool()
        
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Gmail Assistant")
        MainWindow.resize(436, 301)
        
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.infoadressesbutton = QtWidgets.QToolButton(MainWindow)
        self.infoadressesbutton.move(290,40)
        self.infoadressesbutton.resize(20,34)
        self.infoadressesbutton.setObjectName("infoadressesbutton")
        #Button which show the current adresses
        self.clearAdressesButt = QtWidgets.QPushButton(self.centralwidget)
        self.clearAdressesButt.move(165,200)
        self.clearAdressesButt.setObjectName("clearAdressesButt")
        #Button which deletes the list of adresses
        self.EnterAdressesButt = QtWidgets.QPushButton(self.centralwidget)
        self.EnterAdressesButt.move(140,40)
        self.EnterAdressesButt.setObjectName("EnterAdresses")
        #Button which opens the window to enter adresses
        self.ActivateNotiButt = QtWidgets.QPushButton(self.centralwidget)
        self.ActivateNotiButt.move(90,100)
        self.ActivateNotiButt.setObjectName("ActivateNotiButt")
        #Button which activates the notifications
        self.Welcomelabel = QtWidgets.QLabel(self.centralwidget)
        self.Welcomelabel.move(120, 10)
        self.Welcomelabel.setObjectName("WelcomeLabel")
        #Wlecome Message
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 326, 18))
        self.menubar.setObjectName("menubar")
        
        self.ActivateNotiExcept = QtWidgets.QPushButton(self.centralwidget)
        self.ActivateNotiExcept.move(0,140)
        self.ActivateNotiExcept.setObjectName("ActivateNotiExcept")
        #~~
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        #~~
        self.versionLabel = QtWidgets.QLabel(self.centralwidget)
        self.versionLabel.move(330,250)
        self.versionLabel.setObjectName("versionLabel")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #If 'Button' clicked, activate 'Function'
        self.ActivateNotiButt.clicked.connect(self.NotiSender)
        self.EnterAdressesButt.clicked.connect(self.OpenWindowAdresses)
        self.clearAdressesButt.clicked.connect(self.ClearAdresses)
        self.infoadressesbutton.clicked.connect(self.InfosAdressesWindow)
        self.ActivateNotiExcept.clicked.connect(self.NotiExcept)
        
    def retranslateUi(self, MainWindow):
        #Links the button to the text
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.EnterAdressesButt.setText(_translate("MainWindow", "Enter your adresses"))
        self.ActivateNotiButt.setText(_translate("MainWindow", "Activate notification for the adresses"))
        self.Welcomelabel.setText(_translate("MainWindow", "Welcome to Gmail Assistant"))
        self.clearAdressesButt.setText(_translate("MainWindow", "Clear Adresses"))
        self.infoadressesbutton.setText(_translate("MainWindow","?"))
        self.versionLabel.setText(_translate("MainWindow","Version {}".format(version)))
        self.ActivateNotiExcept.setText(_translate("MainWindow","Activate notification for all messages except for the adresses"))
        
    def NotiSender(self):
        try:
            self.NotiExcept.stop()
        except AttributeError as e:
            pass
        
        #Starts the thread which checks for mail and sends notif
        self.NotiSender = NotiFromAdress()
        self.threadpool.start(self.NotiSender)
        self.InfoNotiFrom = QMessageBox()
        self.InfoNotiFrom.setIcon(QMessageBox.Information)
        self.InfoNotiFrom.setText("You will now receive notifications for unread emails from the adresses you chose")
        x=self.InfoNotiFrom.exec_()
        
            
        
    def OpenWindowAdresses(self):
        #GUI of the Window from where you can enter your adresses
        self.WindowAdresses = QMessageBox()
        self.WindowAdresses.setIcon(QMessageBox.Question)#set icon
        self.WindowAdresses.setBaseSize(100, 200)
        self.texteditadresses = QtWidgets.QTextEdit(self.WindowAdresses)
        self.texteditadresses.setGeometry(20,80,150,50)
        self.WindowAdresses.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel) #set messages
        self.WindowAdresses.setWindowTitle("Enter your adresses")
        self.WindowAdresses.setText("Please Enter The email adresses for wich you would like to receive notifications")
        self.WindowAdresses.buttonClicked.connect(self.WindowAdresses_Buttons)
        x=self.WindowAdresses.exec_()
        
    def WindowAdresses_Buttons(self, i):
        #Saves the adresses in the list
        if i.text() == 'Save':
            if self.texteditadresses.toPlainText() in self.adresses:
                self.SameAdress()
                n=1
            else:
                n=0
            
            if  " " in self.texteditadresses.toPlainText() or  "\n" in self.texteditadresses.toPlainText() or n==1:
                print("non")
            else:
                self.adresses.append(self.texteditadresses.toPlainText())
            
        with open("adresses.txt","w") as save:
            for adress in self.adresses:
                save.write("{} ".format(adress))
        print(self.adresses)
        
    def ClearAdresses(self):
        #Clears the list
        self.adresses = []
        with open("adresses.txt","w") as save:
            save.write("")
    
    def SameAdress(self):
        self.SameAdressWindow = QMessageBox()
        self.SameAdressWindow.setIcon(QMessageBox.Warning)
        self.SameAdressWindow.setText("This adress in already registered")
        x=self.SameAdressWindow.exec_()
        
        
    def InfosAdressesWindow(self):
        self.InfosAdressesWindow = QMessageBox()
        self.InfosAdressesWindow.setIcon(QMessageBox.Information)
        self.InfosAdressesWindow.setStandardButtons(QMessageBox.Ok)
        self.InfosAdressesWindow.setWindowTitle("Your saved adresses")
        if self.adresses == []:
            self.adressesStringed = ""
        else:
            self.adressesStringed = " ".join(self.adresses)
        if self.adressesStringed == "":
            self.InfosAdressesWindow.setText("You have no saved adresses, you can add adresses by clicking the Enter your adresses button")
        else:
            self.InfosAdressesWindow.setText("Theses are your saved adresses :\n {}".format(self.adressesStringed))
        x=self.InfosAdressesWindow.exec_()
    
    def NotiExcept(self):
        try:
            self.NotiSender.stop()
        except AttributeError as e:
            pass
        self.NotiExcept = NotiExceptAdress()
        self.threadpool.start(self.NotiExcept)
        self.InfoNotiExcept = QMessageBox()
        self.InfoNotiExcept.setIcon(QMessageBox.Information)
        self.InfoNotiExcept.setText("You will now receive notifications for all unread emails from everyone except the adresses you chose")
        x=self.InfoNotiExcept.exec_()
        
      
      
      
class NotiFromAdress(QRunnable):
    #THREAD 2
        
    def run(self):
        self.cont = 1 #For the while loop
        self.adresses = []#Create an empty 'Adresses' list
        self.service = build('gmail','v1',credentials = InstalledAppFlow.from_client_secrets_file('credentials.json', 'https://mail.google.com/').run_local_server(port=0))
        #Gets the google gmail api service (code from the python quickstart on gmail api)
        
        with open("Adresses.txt","r") as save:
            self.adresses = save.read().split(" ")
            print("received adresses in thread 2 = {}".format(self.adresses))
        #opens and reads the saved adresses        
            
        while self.cont:
            self.results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
            self.messages = self.results.get('messages', [])
            #Get all messages in UNREAD inbox
        
            for message in self.messages:
                self.content = self.service.users().messages().get(userId='me', id = message['id']).execute()
                self.headers = self.content['payload']['headers']
                #Get the playload headerfrom the content
                for self.header in self.headers:
                    if self.header['name'] == 'From':
                        self.sender = "".join( ("".join(self.header['value'].split("<")[1])).split(">"))
                        if self.sender in self.adresses:
                        #if the sender is part of the adresses, send noti
                            notification.notify(
                            title='Nouveau mail  de {}'.format(self.sender),
                            message='{}'.format(self.content['snippet']),
                            app_icon= None,  # e.g. 'C:\\icon_32x32.ico'
                            timeout=10,  # seconds
                            )     
            sleep(600)
    
    def stop(self):
        self.threadactive = False
            
class NotiExceptAdress(QRunnable):
    #THREAD 3
        
    def run(self):
        self.cont = 1 #For the while loop
        self.adresses = []#Create an empty 'Adresses' list
        self.service = build('gmail','v1',credentials = InstalledAppFlow.from_client_secrets_file('credentials.json', 'https://mail.google.com/').run_local_server(port=0))
        #Gets the google gmail api service (code from the python quickstart on gmail api)
        
        with open("Adresses.txt","r") as save:
            self.adresses = save.read().split(" ")
            print("received adresses in thread 2 = {}".format(self.adresses))
        #opens and reads the saved adresses        
            
        while self.cont:
            self.results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
            self.messages = self.results.get('messages', [])
            #Get all messages in UNREAD inbox
        
            for message in self.messages:
                self.content = self.service.users().messages().get(userId='me', id = message['id']).execute()
                self.headers = self.content['payload']['headers']
                #Get the playload headerfrom the content
                for self.header in self.headers:
                    if self.header['name'] == 'From':
                        self.sender = "".join( ("".join(self.header['value'].split("<")[1])).split(">"))
                        if self.sender not in self.adresses:
                        #if the sender is part of the adresses, send noti
                            notification.notify(
                            title='Nouveau mail  de {}'.format(self.sender),
                            message='{}'.format(self.content['snippet']),
                            app_icon= None,  # e.g. 'C:\\icon_32x32.ico'
                            timeout=10,  # seconds
                            )     
            sleep(600)
    def stop(self):
        self.threadactive=False 
 

def GoogleCreds():
            
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 'https://mail.google.com/')
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    with open("service.txt","w") as servicetxt:
        servicetxt.write(service)
    


if __name__ == "__main__":
    import sys
    #THREAD 1
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow() #Creates the main Window
    ui = Ui_MainWindow()#the ui is an ui ~~
    #ui.setWindowIcon(QtGui.QIcon('Gmail_Assistant.ico'))
    ui.setupUi(MainWindow)#the ui is build on the main window
    MainWindow.show()#We show the window
   
    sys.exit(app.exec_())#Executes the prog

