def generate(url,token,type='0'):
    tokens = str(url).split('/')
    nametoken = tokens[-1]
    name = str(nametoken).split('?')[0]
    itemid = tokens[5]
    core = tokens[8]
    return 'https://vdirect.cu/'+type+'/'+itemid+'/'+core+'/'+token+'/'+name