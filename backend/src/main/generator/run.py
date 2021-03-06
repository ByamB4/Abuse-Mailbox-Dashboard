from pathlib import Path
import configparser, os, email, json

config = configparser.ConfigParser()
PARENT = str(Path(__file__).absolute().parent.parent.parent.parent.parent) + '/'
config.read(PARENT + 'configs/general.ini')
MAIL_ = PARENT + 'backend/src/main/api/resources/mail/'

DEBUG = bool(int(config['general']['DEBUG']))
LOG = bool(int(config['general']['LOGGING']))
CNS = bool(int(config['general']['CONSOLE']))
MAIL_SERVER = config['mail']['MAIL_SERVER']
MAIL_PORT = config['mail']['MAIL_PORT']
FILE_ = PARENT + '/backend/src/main/api/resources/general/full-data.json'

newMails = 0

if LOG: log = open(PARENT + '/logs/general.log', 'a')

def getmails():
    if not os.path.exists(PARENT + 'backend/src/main/api/resources'): os.mkdir(PARENT + 'backend/src/main/api/resources/')
    if not os.path.exists(PARENT + 'backend/src/main/api/resources/mail/'): os.mkdir(PARENT + 'backend/src/main/api/resources/mail/')
    if not os.path.exists(PARENT + 'backend/src/main/api/resources/general/'): os.mkdir(PARENT + 'backend/src/main/api/resources/general/')
    import imaplib, base64
    from email import generator
    if LOG: log.write('[+] Trying to login mail\n')
    if CNS: print('[+] Trying to login mail')

    # You have to configure your local enviroment variables
    email_user = os.environ.get('EMAIL_USERNAME')
    email_pass = os.environ.get('EMAIL_PASSWORD')

    mail = imaplib.IMAP4_SSL(MAIL_SERVER, MAIL_PORT)
    try: mail.login(email_user, email_pass)
    except:
        if LOG: log.write('[-] Login failed\n')
        if CNS: print('[-] Login failed')

    if LOG:
        log.write('[+] Login successfully\n')
        log.write('[+] Trying to get last mails\n')
    if CNS:
        print('[+] Login successfully')
        print('[+] Trying to get last mails')

    mail.select('Inbox')

    type, data = mail.search(None, 'ALL')
    if LOG: log.write(f'[+] {len(data[0].split())} mails found\n')
    if CNS: print(f'[+] {len(data[0].split())} mails found')
    if len(os.listdir(MAIL_)) == 1:
        start = 1
        if LOG: log.write(f'[+] 0 mails in resource\n')
        if CNS: print(f'[+] 0 mails in resource')
    else:
        start = len(os.listdir(MAIL_))
        if LOG: log.write(f'[+] {start} mails in resource\n')
        if CNS: print(f'[+] {start} mails in resource')
    end = len(data[0].split())
    global newMails
    newMails = end - start
    
    for num in range(start + 1, end + 1):
        if LOG: log.write(f'[+] Getting {num}th mail\n')
        if CNS: print(f'[+] Getting {num}th mail')
        try: os.mkdir(MAIL_ + str(num))
        except Exception as e:
            if LOG: log.write(f'[-] Create directory failed: {e}')
            if CNS: print(f'[-] Create directory failed: {e}')
        typ, data = mail.fetch(str(num), '(RFC822)' )
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        with open(MAIL_ + str(num) + '/main-content.elm', 'w') as out:
            gen = generator.Generator(out)
            gen.flatten(email_message)
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart': continue
            if part.get('Content-Disposition') is None: continue
            fileName = part.get_filename()
            if bool(fileName):
                filePath = os.path.join(MAIL_ + str(num), fileName)
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
    if start < end: 
        if CNS: print(f'[+] Getting all mail successfully')
        if LOG: log.write(f'[+] Getting all mail successfully\n')
        readmails()
        createFullData()
    
    if not os.path.exists(FILE_): createFullData()
    
def readmails():
    import eml_parser, datetime, re
    from email import policy
    from email.parser import BytesParser

    def json_serial(obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()
            return serial
    
    KNOWN = ['sold@swiftdsl.com.au', 'cert@cert.ee', 'incident-report@bitninja.io', 'network-abuse@hetzner.com', 'antipiracy@p2p.markmonitor.com', 'mcgrawhill.antipiracy@p2p.markmonitor.com', 'p2p@copyright.ip-echelon.com', 'cert@cert.br', 'autogenerated@blocklist.de', 'root@ssd2-cpanel.vhosting-it.com', 'root@ssd1-cpanel.vhosting-it.com', 'abuse-notify@tepucom.nl', 'unitel-request@mail.shadowserver.org', 'unitel-bounces@mail.shadowserver.org', 'botnet.tracker@gmail.com', 'fail2ban-no-reply@dns01.keymachine.de']
    ep = eml_parser.eml_parser
    end = len(os.listdir(MAIL_))
    for _ in range(1, end + 1):
        if os.path.exists(MAIL_ + '/' + str(_) + '/processed-data.json'): continue
        try:
            if LOG: log.write(f'[+] Reading: {_}\n')
            if CNS: print(f'[+] Reading: {_}')
            with open(MAIL_ + '/' + str(_) + '/main-content.elm', 'rb') as f: raw_email = f.read()
            parsed_eml = ep.decode_email_b(raw_email)
            parsed_json = json.loads(json.dumps(parsed_eml, default=json_serial))
            FROM = parsed_json['header']['from']
            SUBJECT = parsed_json['header']['subject']
            DATE = parsed_json['header']['date']
            CATEGORY, OUR_ADDRESS, VICTIM_ADDRESS = '', '', ''
            if FROM in KNOWN:
                with open(MAIL_ + '/' + str(_) + '/main-content.elm', 'rb') as f:
                    msg = BytesParser(policy=policy.default).parse(f)
                try: TEXT = msg.get_body(preferencelist=('plain')).get_content()
                except: pass
                if FROM == 'sold@swiftdsl.com.au':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'cert@cert.ee':
                    if 'phishing' in TEXT: CATEGORY = 'phishing'
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[1]
                    VICTIM_ADDRESS = re.findall( r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'incident-report@bitninja.io':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
                    if 'botnet' in TEXT: CATEGORY = 'botnet'
                elif FROM == 'network-abuse@hetzner.com':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
                    if 'Netscan' in SUBJECT: CATEGORY = 'scan'
                elif FROM in 'p2p.markmonitor.com':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'p2p@copyright.ip-echelon.com':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'cert@cert.br':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
                    print(OUR_ADDRESS)
                elif FROM == 'autogenerated@blocklist.de':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
                    if 'ssh' in SUBJECT: CATEGORY = 'ssh'
                elif FROM == 'root@ssd2-cpanel.vhosting-it.com':
                    if 'DOS' in TEXT: CATEGORY = 'DOS'
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'root@ssd1-cpanel.vhosting-it.com':
                    if 'DOS' in TEXT: CATEGORY = 'DOS'
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                elif FROM == 'abuse-notify@tepucom.nl':
                    CATEGORY = 'wp-admin'
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
                elif FROM == 'botnet.tracker@gmail.com':
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', TEXT)[0]
                    if 'scan' in TEXT: CATEGORY = 'scan'
                elif FROM == 'fail2ban-no-reply@dns01.keymachine.de':
                    CATEGORY = 'scan'
                    OUR_ADDRESS = re.findall(r'[0-9]+(?:\.[0-9]+){3}', SUBJECT)[0]
            else:
                if LOG: log.write('[-] Unknown mail\n')
                if CNS: print('[-] Unknown mail')
            if CNS:
                print('-' * 20)
                outdata = {}
                outdata['FROM'] = FROM
                outdata['SUBJECT'] = SUBJECT
                outdata['DATE'] = DATE
                if CATEGORY != '':
                    outdata['CATEGORY'] = CATEGORY
                if OUR_ADDRESS != '':
                    outdata['OUR_ADDRESS'] = OUR_ADDRESS
                if VICTIM_ADDRESS != '':
                    outdata['VICTIM_ADDRESS'] = VICTIM_ADDRESS
                print(outdata)
                open(MAIL_ + str(_) + '/processed-data.json', 'w').write(json.dumps(outdata))
                print('-' * 20)
        except Exception as e:
            if LOG: log.write(f'[-] Error: {e}\n')
            if CNS: print(f'[-] Error: {_}')
    if CNS: print(f'[+] Reading all mail successfully')
    if LOG: log.write(f'[+] Reading all mail successfully\n')

def createFullData():
    if LOG: log.write('[+] Refreshing full-data.json\n')
    if CNS: print('[+] Refreshing full-data.json')
    data = {}
    length = len(os.listdir(MAIL_))
    OUR_IPS_, VICTIM_IPS_, FROMS_, CATEGORY_, SUBJECT_, DATE_ = [], [], [], [], [], []
    try:
        has = True
        old = open(FILE_)
        old = json.load(old)
    except:
        has = False
    for _ in range(1, length + 1):
        try:
            proc = open(MAIL_  + str(_) + '/processed-data.json')
            proc = json.load(proc)
            data[str(_)] = {}
            data[str(_)]['FROM'] = proc['FROM']
            FROMS_.append(proc['FROM'])
            data[str(_)]['SUBJECT'] = proc['SUBJECT']
            SUBJECT_.append(proc['SUBJECT'])
            data[str(_)]['DATE'] = proc['DATE']
            DATE_.append(proc['DATE'])
            try: 
                data[str(_)]['CATEGORY'] = proc['CATEGORY']
                CATEGORY_.append(proc['CATEGORY'])
            except: pass
            try: 
                data[str(_)]['OUR_ADDRESS'] = proc['OUR_ADDRESS']
                OUR_IPS_.append(proc['OUR_ADDRESS'])
            except: pass
            try:
                data[str(_)]['VICTIM_IPS'] = proc['VICTIM_ADDRESS']
                VICTIM_IPS_.append(proc['VICTIM_ADDRESS'])
            except: pass
            if has: 
                data[str(_)]['SENDQUICK'] = old[str(_)]['SENDQUICK']
                data[str(_)]['FORWARDMAIL'] = old[str(_)]['FORWARDMAIL']
                data[str(_)]['FORWARDEDTO'] = old[str(_)]['FORWARDEDTO']
                data[str(_)]['DONE'] = old[str()]['DONE']
        except: pass
    if newMails > 0:
        data['NEW_MAILS'] = {}
        for _ in range(length - 1, length - newMails - 1, -1):
            try:
                proc = open(MAIL_  + str(_) + '/processed-data.json')
                proc = json.load(proc)
                data['NEW_MAILS'][str(_)] = {}
                data['NEW_MAILS'][str(_)]['FROM'] = proc['FROM']
                data['NEW_MAILS'][str(_)]['SUBJECT'] = proc['SUBJECT']
                data['NEW_MAILS'][str(_)]['DATE'] = proc['DATE']
            except: pass

    from collections import Counter, OrderedDict
    x = dict(Counter(OUR_IPS_))
    OUR_IPS_ = sorted(x.items(), key=lambda x: x[1], reverse=True)
    x = dict(Counter(VICTIM_IPS_))
    VICTIM_IPS_ = sorted(x.items(), key=lambda x: x[1], reverse=True)
    x = dict(Counter(FROMS_))
    FROMS_ = sorted(x.items(), key=lambda x: x[1], reverse=True)
    x = dict(Counter(CATEGORY_))
    CATEGORY_ = sorted(x.items(), key=lambda x: x[1], reverse=True)
    x = dict(Counter(SUBJECT_))
    SUBJECT_ = sorted(x.items(), key=lambda x: x[1], reverse=True)

    data['TOTAL_MAIL'] = length
    data['UNIQUE_MAIL'] = len(set(FROMS_))
    data['OUR_IPS'] = dict(OUR_IPS_)
    data['VICTIM_IPS'] = dict(VICTIM_IPS_)
    data['FROMS'] = dict(FROMS_)
    data['CATEGORY'] = dict(CATEGORY_)
    data['DATE'] = {}
    if has:
        data['FIXED_MAILS'] = old['FIXED_MAILS']
        data['SEND_QUICK_MAILS'] = old['SEND_QUICK_MAILS']
        data['FORWARDED_MAILS'] = old['FORWARDED_MAILS']
        data['NO_ACTION_MAILS'] = old['NO_ACTION_MAILS']
    else:
        data['FIXED_MAILS'] = 0
        data['SEND_QUICK_MAILS'] = 0
        data['FORWARDED_MAILS'] = 0
        data['NO_ACTION_MAILS'] = 0
    # Begin Date
    dct, tst = {}, {}
    ans = [''.join(_[:10].split('-')) for _ in DATE_]
    for _ in set(ans): dct[_] = ans.count(_)
    for _ in [_ for _ in list(sorted(dct.keys()))[::-1][:30][::-1]]: data['DATE'][_[:4]+'-'+_[4:6]+'-'+_[6:8]] = dct[_]
    # End Date
    open(FILE_, 'w').write(json.dumps(data))
    if LOG: log.write('[+] Writing full-data.json\n')
    if CNS: print('[+] Writing full-data.json')
    
getmails()
