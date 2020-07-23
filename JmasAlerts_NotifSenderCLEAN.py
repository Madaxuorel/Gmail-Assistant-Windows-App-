from __future__ import print_function
from plyer import notification


import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def GoogleCreds():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

 
    return service
         
class NotiFromAdress():
    def SendNotif(self, adresses,service):
        self.results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        self.messages = self.results.get('messages', [])
        #Get all messages in UNREAD inbox
        
        for message in self.messages:
            self.content = service.users().messages().get(userId='me', id = message['id']).execute()
            self.headers = self.content['payload']['headers']
            #Get the playload headerfrom the content
            for self.header in self.headers:
                if self.header['name'] == 'From':
                    self.sender = "".join( ("".join(self.header['value'].split("<")[1])).split(">"))
                    if self.sender in adresses:
                        #if the sender is part of the adresses, send noti
                        notification.notify(
                        title='Nouveau mail  de {}'.format(self.sender),
                        message='{}'.format(self.content['snippet']),
                        app_icon= None,  # e.g. 'C:\\icon_32x32.ico'
                        timeout=10,  # seconds
                        )
                    
                        
    
    
def main():
    adresses = ['adamleroux26@gmail.com', 'lerouxadam@eisti.eu']
    service = GoogleCreds()
    action = NotiFromAdress()
    action.SendNotif(adresses,service)   
    
                             
main()
                        
        
        
    
