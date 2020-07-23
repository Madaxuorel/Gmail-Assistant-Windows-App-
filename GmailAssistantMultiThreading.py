#By Adam Le Roux, Final Version WITH THREADING, requires VENV (JmasAlertsVenv)


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


class Ui_MainWindow(object):
    def __init__(self):
        with open("adresses.txt","r") as save:
            self.adresses = save.read().split(" ") 
        self.threadpool = QThreadPool()
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Gmail Assistant")
        MainWindow.resize(326, 271)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.clearAdressesButt = QtWidgets.QPushButton(self.centralwidget)
        self.clearAdressesButt.move(105,200)
        self.clearAdressesButt.setObjectName("clearAdressesButt")
        #Button which deletes the list of adresses
        self.EnterAdressesButt = QtWidgets.QPushButton(self.centralwidget)
        self.EnterAdressesButt.move(90,80)
        self.EnterAdressesButt.setObjectName("EnterAdresses")
        #Button which opens the window to enter adresses
        self.ActivateNotiButt = QtWidgets.QPushButton(self.centralwidget)
        self.ActivateNotiButt.move(30,140)
        self.ActivateNotiButt.setObjectName("ActivateNotiButt")
        #Button which activates the notifications
        self.Welcomelabel = QtWidgets.QLabel(self.centralwidget)
        self.Welcomelabel.move(70, 10)
        self.Welcomelabel.setObjectName("WelcomeLabel")
        #Wlecome Message
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 326, 18))
        self.menubar.setObjectName("menubar")
        #~~
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        #~~

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #If 'Button' clicked, activate 'Function'
        self.ActivateNotiButt.clicked.connect(self.NotiSender)
        self.EnterAdressesButt.clicked.connect(self.OpenWindowAdresses)
        self.clearAdressesButt.clicked.connect(self.ClearAdresses)
        
    def retranslateUi(self, MainWindow):
        #Links the button to the text
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.EnterAdressesButt.setText(_translate("MainWindow", "Enter your adresses"))
        self.ActivateNotiButt.setText(_translate("MainWindow", "Activate Custom Notis from adresses"))
        self.Welcomelabel.setText(_translate("MainWindow", "Welcome to Gmail Assistant"))
        self.clearAdressesButt.setText(_translate("MainWindow", "Clear Adresses"))
        
    def NotiSender(self):
        #Starts the thread which checks for mail and sends notif
        self.NotiSender = NotiFromAdress()
        self.threadpool.start(self.NotiSender)
        
            
        
    def OpenWindowAdresses(self):
        #GUI of the Window from where you can enter your adresses
        self.WindowAdresses = QMessageBox()
        self.WindowAdresses.setIcon(QMessageBox.Question)#set icon
        self.texteditadresses = QtWidgets.QTextEdit(self.WindowAdresses)
        self.WindowAdresses.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel) #set messages
        self.WindowAdresses.setWindowTitle("Enter your adresses")
        self.WindowAdresses.setText("Please Enter The email adresses for wich you would like to receive notifications")
        self.WindowAdresses.buttonClicked.connect(self.WindowAdresses_Buttons)
        x=self.WindowAdresses.exec_()
        
    def WindowAdresses_Buttons(self, i):
        #Saves the adresses in the list
        if i.text() == 'Save':
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
    ui.setupUi(MainWindow)#the ui is build on the main window
    MainWindow.show()#We show the window
   
    sys.exit(app.exec_())#Executes the prog

