import requests
import os
import textwrap
import re
import json

from bs4 import BeautifulSoup

class MoodleClient(object):
    def __init__(self, user,passw):
        self.username = user
        self.password = passw
        self.session = requests.Session()
        self.path = 'https://evea.uh.cu/'
        self.userdata = ''

    def getsession(self):
        return self.session    

    def getUserData(self):
        tokenUrl = self.path+'login/token.php?service=moodle_mobile_app&username='+self.username+'&password='+self.password
        resp = self.session.get(tokenUrl)
        return self.parsejson(resp.text)

    def getDirectUrl(self,url):
        tokens = str(url).split('/')
        direct = self.path+'webservice/pluginfile.php/'+tokens[4]+'/user/private/'+tokens[-1]+'?token='+self.data['token']
        return direct

    def login(self):
        login = self.path+'login/index.php'
        resp = self.session.get(login)
        cookie = resp.cookies.get_dict()
        soup = BeautifulSoup(resp.text,'html.parser')
        anchor = soup.find('input',attrs={'name':'anchor'})['value']
        logintoken = soup.find('input',attrs={'name':'logintoken'})['value']
        username = self.username
        password = self.password
        payload = {'anchor': '', 'logintoken': logintoken,'username': username, 'password': password, 'rememberusername': 1}
        loginurl = self.path+'login/index.php'
        resp2 = self.session.post(loginurl, data=payload)
        counter = 0
        for i in resp2.text.splitlines():
            if "loginerrors" in i or (0 < counter <= 3):
                counter += 1
                print(i)
        if counter>0:
            print('No pude iniciar sesion')
            return False
        else:
            print('E iniciado sesion con exito')
            self.userdata = self.getUserData()
            return True

    def upload_file(self,file,saved = False):
        fileurl = self.path+'user/files.php'
        resp = self.session.get(fileurl)
        print('Resp: '+str(resp))
        soup = BeautifulSoup(resp.text,'html.parser')
        sesskey  =  soup.find('input',attrs={'name':'sesskey'})['value']
        print('Sesskey: '+str(sesskey))
        _qf__core_user_form_private_files = 1
        files_filemanager = soup.find('input',attrs={'name':'files_filemanager'})['value']
        print('files_filemanager: '+str(files_filemanager))
        returnurl = fileurl
        print('Returnurl: '+str(returnurl))
        submitbutton = soup.find('input',attrs={'name':'submitbutton'})['value']
        print('Submitbutton: '+str(submitbutton))
        #usertext =  soup.find('span',attrs={'class':'usertext mr-1'}).contents[0]
        #print('Usertext: '+str(usertext))
        query = self.extractQuery(soup.find('object',attrs={'type':'text/html'})['data'])
        print('Query: '+str(query))
        client_id = self.getclientid(resp.text)
        print('Client_id: '+str(client_id))
        of = open(file,'rb')
        upload_file = {
            'repo_upload_file':(file,of,'application/octet-stream'),
            }
        upload_data = {
            'title':(None,''),
            'author':(None,'ObysoftDev'),
            'license':(None,'allrightsreserved'),
            'itemid':(None,query['itemid']),
            'repo_id':(None,4),
            'p':(None,''),
            'page':(None,''),
            'env':(None,query['env']),
            'sesskey':(None,sesskey),
            'client_id':(None,client_id),
            'maxbytes':(None,query['maxbytes']),
            'areamaxbytes':(None,query['areamaxbytes']),
            'ctx_id':(None,query['ctx_id']),
            'savepath':(None,'/')}
        post_file_url = self.path+'repository/repository_ajax.php?action=upload'
        resp2 = self.session.post(post_file_url, files=upload_file,data=upload_data)
        of.close()

        data = self.parsejson(resp2.text)

        #save file
        if saved:
            saveUrl = self.path+'lib/ajax/service.php?sesskey='+sesskey+'&info=core_form_dynamic_form'
            savejson = [{"index":0,"methodname":"core_form_dynamic_form","args":{"formdata":"sesskey="+sesskey+"&_qf__core_user_form_private_files="+_qf__core_user_form_private_files+"&files_filemanager="+query['itemid']+"","form":"core_user\\form\\private_files"}}]
            headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/javascript, */*; q=0.01'}
            resp3 = self.session.post(saveUrl, json=savejson,headers=headers)

        url = data['url']
        data['url'] = str(url).replace('\\','')
        data['ctxid'] = query['ctx_id']
        data['userdata'] = self.userdata
        ffname = str(str(data['url']).split('/')[-1]).replace('?forcedownload=1','')
        #data['directurl'] = str(data['url']).replace('draftfile.php','webservice/draftfile.php')+'?token='+data['userdata']['token']
        data['directurl'] = data['url']
        return data

    def parsejson(self,json):
        data = {}
        tokens = str(json).replace('{','').replace('}','').split(',')
        for t in tokens:
            split = str(t).split(':',1)
            data[str(split[0]).replace('"','')] = str(split[1]).replace('"','')
        return data

    def getclientid(self,html):
        index = str(html).index('client_id')
        max = 25
        ret = html[index:(index+max)]
        return str(ret).replace('client_id":"','')

    def extractQuery(self,url):
        tokens = str(url).split('?')[1].split('&')
        retQuery = {}
        for q in tokens:
            qspl = q.split('=')
            retQuery[qspl[0]] = qspl[1]
        return retQuery

    def getFiles(self):
        urlfiles = self.path+'user/files.php'
        resp = self.session.get(urlfiles)
        soup = BeautifulSoup(resp.text,'html.parser')
        sesskey  =  soup.find('input',attrs={'name':'sesskey'})['value']
        client_id = self.getclientid(resp.text)
        filepath = '/'
        query = self.extractQuery(soup.find('object',attrs={'type':'text/html'})['data'])
        payload = {'sesskey': sesskey, 'client_id': client_id,'filepath': filepath, 'itemid': query['itemid']}
        postfiles = self.path+'repository/draftfiles_ajax.php?action=list'
        resp = self.session.post(postfiles,data=payload)
        dec = json.JSONDecoder()
        jsondec = dec.decode(resp.text)
        return jsondec['list']
   
    def delteFile(self,name):
        urlfiles = self.path+'user/files.php'
        resp = self.session.get(urlfiles)
        soup = BeautifulSoup(resp.text,'html.parser')
        _qf__core_user_form_private_files = soup.find('input',{'name':'_qf__core_user_form_private_files'})['value']
        files_filemanager = soup.find('input',attrs={'name':'files_filemanager'})['value']
        sesskey  =  soup.find('input',attrs={'name':'sesskey'})['value']
        client_id = self.getclientid(resp.text)
        filepath = '/'
        query = self.extractQuery(soup.find('object',attrs={'type':'text/html'})['data'])
        payload = {'sesskey': sesskey, 'client_id': client_id,'filepath': filepath, 'itemid': query['itemid'],'filename':name}
        postdelete = self.path+'repository/draftfiles_ajax.php?action=delete'
        resp = self.session.post(postdelete,data=payload)

        #save file
        saveUrl = self.path+'lib/ajax/service.php?sesskey='+sesskey+'&info=core_form_dynamic_form'
        savejson = [{"index":0,"methodname":"core_form_dynamic_form","args":{"formdata":"sesskey="+sesskey+"&_qf__core_user_form_private_files="+_qf__core_user_form_private_files+"&files_filemanager="+query['itemid']+"","form":"core_user\\form\\private_files"}}]
        headers = {'Content-type': 'application/json', 'Accept': 'application/json, text/javascript, */*; q=0.01'}
        resp3 = self.session.post(saveUrl, json=savejson,headers=headers)

        return resp3

client = MoodleClient('obysoft','Obysoft2001@')
loged = client.login()
if loged:
   data =  client.upload_file('requirements.txt')
   print(data)