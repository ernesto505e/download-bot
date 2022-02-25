from MoodleClient import MoodleClient

BOT_TOKEN = '5010096091:AAE1Y9JfdqgcyCPRatkVzMgm_EVfCslxNxg'
MAX_ZIP_SIZE = 100
ACCES_USERS = ['obisoftdev','shapingdev']
CREDENTIALS = {'username':'obysoft','password':'Obysoft2001@'}
CACHE = {}

def getCache():
    return CACHE[CREDENTIALS['username']]
def saveCache(cache):
    CACHE[CREDENTIALS['username']] = cache

def appendAcc(acc):
    txt = open('accounts.txt','r')
    txtcontent = txt.read()
    txt.close()
    txt = open('accounts.txt','w')
    txt.write(txtcontent+"\n{'username':'"+acc[0]+"','password':'"+acc[1]+"'}")
    txt.close();
    list = loadAccounts()
    createAccountCache(list[-1])

def parsejson(json):
        data = {}
        tokens = str(json).replace('{','').replace('}','').split(',')
        for t in tokens:
            split = str(t).split(':',1)
            data[str(split[0]).replace('"','')] = str(split[1]).replace('"','')
        return data

STEP_CCOUNT = 0

def loadAccounts():
    list = []
    txt = open('accounts.txt','r')
    alljson = txt.read()
    txt.close()
    jsonlist = alljson.replace("'",'"').split('\n')
    for json in jsonlist:
        list.append(parsejson(json))
    return list

def stepAccount():
    global STEP_CCOUNT
    global CREDENTIALS

    list = loadAccounts()
    listlen = len(list)
    STEP_CCOUNT+=1
    if STEP_CCOUNT>=listlen:
        STEP_CCOUNT = 0
    CREDENTIALS = list[STEP_CCOUNT]

def isStep(file_size):
    global CACHE
    global CREDENTIALS
    for c in CACHE:
        moodle_cache = CACHE[c]
        available_storage = moodle_cache['storage_size'] - moodle_cache['storage_current']
        if available_storage>file_size:
            CREDENTIALS = moodle_cache['credentials']
            return True
    return False

def createAccountsCache():
    global CACHE
    accounts = loadAccounts()
    for acc in accounts:
        moodle = MoodleClient(acc['username'],acc['password'])
        loged = moodle.login()
        if loged:
            userdata = moodle.getUserData()
            file_list = moodle.getFiles()
            storage_current = 0
            for f in file_list:
                storage_current += f['size']
            CACHE[acc['username']] = {'userdata':userdata,'storage_size':1024*1024*1000,'storage_current':storage_current,'file_list':file_list,'credentials':acc}
        else:
            CACHE[acc['username']] = None
    pass

def createAccountCache(acc):
        global CACHE
        moodle = MoodleClient(acc['username'],acc['password'])
        loged = moodle.login()
        if loged:
            userdata = moodle.getUserData()
            file_list = moodle.getFiles()
            storage_current = 0
            for f in file_list:
                storage_current += f['size']
            CACHE[acc['username']] = {'userdata':userdata,'storage_size':1024*1024*1000,'storage_current':storage_current,'file_list':file_list,'credentials':acc}
        else:
            CACHE[acc['username']] = {'userdata':{},'storage_size':0,'storage_current':0,'file_list':[],'credentials':{}}

#createAccountsCache();