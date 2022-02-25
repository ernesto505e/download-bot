import re
import warnings
import requests
import urllib.parse
from bs4 import BeautifulSoup

def parse_url(url, warning=True):
    """Parse URLs especially for Google Drive links.
    file_id: ID of file on Google Drive.
    is_download_link: Flag if it is download link of Google Drive.
    """
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    is_gdrive = parsed.hostname in ["drive.google.com", "docs.google.com"]
    is_download_link = parsed.path.endswith("/uc")

    if not is_gdrive:
        return is_gdrive, is_download_link

    file_id = None
    if "id" in query:
        file_ids = query["id"]
        if len(file_ids) == 1:
            file_id = file_ids[0]
    else:
        patterns = [r"^/file/d/(.*?)/view$", r"^/presentation/d/(.*?)/edit$"]
        for pattern in patterns:
            match = re.match(pattern, parsed.path)
            if match:
                file_id = match.groups()[0]
                break

    if warning and not is_download_link:
        warnings.warn(
            "You specified Google Drive Link but it is not the correct link "
            "to download the file. Maybe you should try: {url}".format(
                url="https://drive.google.com/uc?id={}".format(file_id)
            )
        )

    return {'file_id':file_id, 'is_download_link':is_download_link}

def getDownloadUrl(fileid):
    url = 'https://drive.google.com/u/0/uc?id='+fileid+'&export=download'
    session = requests.Session()
    resp = session.get(url)
    soup = BeautifulSoup(resp.text,'html.parser')
    direct = soup.find('a',{'id':'uc-download-link'})['href']
    return 'https://drive.google.com' + direct , session