from django.shortcuts import render
from django.views.generic import View
from pathlib import Path
from json import load, dumps
from os import environ, listdir
from .generator import run

PARENT = str(Path(__file__).absolute().parent.parent.parent.parent) + '/'
FILE_ = PARENT + 'backend/src/main/api/resources/general/full-data.json'
MAIL_ = PARENT + 'backend/src/main/api/resources/mail'

class HomeView(View):
    def get(self, request, *args, **kwargs):
        try: data = self.readData()
        except:
            print('[-] Full data json not found')
            print('[+] Trying to refresh everything')
            run.getmails()
            data = self.readData()
        # Begin GET handlers
        if request.GET.get('exportData') == "True": print('[-] Dont need now')
        if request.GET.get('syncData') == 'True':
            print('[+] Syncing data')
            run.getmails()
            data = self.readData()
        if request.GET.get('sendMail'):
            _ = request.GET.get('sendMail')
            if _ == 'sendMailTop1': recipient = list(data['FROMS'])[0]
            elif _ == 'sendMailTop2': recipient = list(data['FROMS'])[1]
            elif _ == 'sendMailTop3': recipient = list(data['FROMS'])[2]
            self.sendMail(recipient)
        # End GET handlers
        fields = {
            'title': 'Нүүр хуудас',
            'total_mail': data['TOTAL_MAIL'],
            'unique_mail': data['UNIQUE_MAIL']
        }
        try:
            if len(data['NEW_MAILS']) > 0: fields['total_new_mails'] = len(data['NEW_MAILS'])
            fields['new_mails'] = {}
            for _ in data['NEW_MAILS']:
                fields['new_mails'][_] = {}
                fields['new_mails'][_]['date'] = data['NEW_MAILS'][_]['DATE'][:10]
                fields['new_mails'][_]['subject'] = data['NEW_MAILS'][_]['SUBJECT'] 
            import itertools
            fields['new_mails'] = dict(itertools.islice(fields['new_mails'].items(), 3))
        except: pass
        return render(request, 'index.html', {'fields': fields})

    def readData(self):
        return load(open(str(Path(__file__).parent) + '/api/resources/general/full-data.json'))

    def sendMail(self, recipient):
        print(f'[+] Trying to send mail to: {recipient}')
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        import smtplib

        username = environ.get('EMAIL_USERNAME')
        password = environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = environ.get('EMAIL_USERNAME')
        msg['Subject'] = 'Testing subject'
        body = 'Testing body'
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        sendMailServer = smtplib.SMTP('outlook.office365.com', 587)
        sendMailServer.starttls()

        sendMailServer.login(username, password)
        # Your mail address
        email_send = 'byambatest7@gmail.com' 
        sendMailServer.sendmail(username, email_send, text)
        sendMailServer.quit()
        print(f'[+] Successfully sent to: {email_send}')

class ActionView(View):
    
    def get(self, request, *args, **kwargs):
        # Begin GET handlers
        if request.GET.get('action'):
            _ = request.GET.get('action')
            if _.startswith('sendQuickMail'): self.sendQuickMail(_.split('-')[1])
            elif _.startswith('sendCustomMail'): self.sendCustomMail(_)
            elif _.startswith('sendToSomeone'): self.sendToSomeone(_.split('-')[1], request.GET.get('to'))
            elif _.startswith('done'): self.finish(_.split('-')[1])
        if request.GET.get('syncData') == 'True':
            print('[+] Syncing data')
            run.getmails()
        # End GET handlers
        try: data = self.readData()
        except:
            print('[-] Full data json not found')
            print('[+] Trying to refresh everything')
            run.getmails()
            data = self.readData()
        fields = {
            'title': 'Actionable Box',
            'fixed_mails': data['FIXED_MAILS'],
            'quick_mails': data['SEND_QUICK_MAILS'],
            'forwarded_mails': data['FORWARDED_MAILS'],
            # To do
            # 'no_action_mail': data['NO_ACTION_MAILS'] 
        }
        try:
            if len(data['NEW_MAILS']) > 0: fields['total_new_mails'] = len(data['NEW_MAILS'])
            fields['new_mails'] = {}
            for _ in data['NEW_MAILS']:
                fields['new_mails'][_] = {}
                fields['new_mails'][_]['date'] = data['NEW_MAILS'][_]['DATE'][:10]
                fields['new_mails'][_]['subject'] = data['NEW_MAILS'][_]['SUBJECT']
            import itertools
            fields['new_mails'] = dict(itertools.islice(fields['new_mails'].items(), 3))
        except: pass
        
        return render(request, 'action-full.html', {'fields': fields})
    def sendQuickMail(self, index):
        data = self.readData()
        # number of other field
        index = str(len(listdir(MAIL_)) - int(index))        
        recipient = data[index]['FROM']
        print(f"[+] Trying to send quick mail to: {recipient}")
        
        # Delete me in production
        print(f"[+] In debug mode sending to: 'byambatest7@gmail.com'")
        email_send = 'byambatest7@gmail.com' 
        
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        import smtplib

        username = environ.get('EMAIL_USERNAME')
        password = environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = environ.get('EMAIL_USERNAME')
        msg['Subject'] = 'Testing subject'
        body = 'Testing body'
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        sendMailServer = smtplib.SMTP('outlook.office365.com', 587)
        sendMailServer.starttls()

        sendMailServer.login(username, password)
        sendMailServer.sendmail(username, email_send, text)
        sendMailServer.quit()
        print(f'[+] Successfully sent to: {recipient}')
        data[index]['SENDQUICK'] = 'True'
        data['SEND_QUICK_MAILS'] += 1
        open(FILE_, 'w').write(dumps(data))

    def sendCustomMail(self, recipient):
        print('-' * 50)
        print(f'[+] Send custom mail to do: {recipient}')
        print('-' * 50)
    def sendToSomeone(self, index, to):
        data = self.readData()
        index = str(len(listdir(MAIL_)) - int(index))
        
        body = data[index]['SUBJECT']
        print(f"[+] Trying to forward mail to: {to}")
        
        email_send = to
        
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        import smtplib

        username = environ.get('EMAIL_USERNAME')
        password = environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = environ.get('EMAIL_USERNAME')
        msg['Subject'] = 'Forwarded mail'
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        sendMailServer = smtplib.SMTP('outlook.office365.com', 587)
        sendMailServer.starttls()

        sendMailServer.login(username, password)
        sendMailServer.sendmail(username, email_send, text)
        sendMailServer.quit()
        print(f'[+] Successfully forward to: {to}')
        data[index]['FORWARDMAIL'] = 'True'
        data[index]['FORWARDEDTO'] = to
        data['FORWARDED_MAILS'] += 1
        open(FILE_, 'w').write(dumps(data))

    def finish(self, index):
        data = self.readData()
        index = str(len(listdir(MAIL_)) - int(index))
        if not 'DONE' in data[index]:
            data[index]['DONE'] = 'True'
            data['FIXED_MAILS'] += 1
            print(f'[+] Done ')
            open(FILE_, 'w').write(dumps(data))

    def readData(self):
        return load(open(FILE_))
        