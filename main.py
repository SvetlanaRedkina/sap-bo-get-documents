import http.client
import xml.etree.ElementTree as ET

# GET request
connGet = http.client.HTTPConnection("urlAddress", 8080)

headersGet = {
    "Accept": "application/xml"
}

payload = ""

connGet.request("GET", "biprws/logon/long", body=None, headers=headersGet)
responseGet = connGet.getresponse()
resultGet = responseGet.read()
print(resultGet.decode("utf-8"))

root = ET.fromstring(resultGet)
print(root)

for child in root:
    print(child.tag, child.attrib, child.text)

root[0].text = 'yourUsername'
root[3].text = 'yourPassword'

newPayload = ET.tostring(root, encoding='utf-8').decode('utf-8')
print(newPayload)

# POST request
connPost = http.client.HTTPConnection("urlAddress", 8080)

headersPost = {
    "Content-Type": "application/xml"
}

connPost.request("POST", "biprws/logon/long", newPayload, headersPost)
responsePost = connPost.getresponse()
resultPost = responsePost.read()
print(resultPost.decode("utf-8"))

rootToken = ET.fromstring(resultPost)
print(rootToken)

for child in rootToken:
    print(child.tag, child.attrib, child.text)

token = rootToken[3][0][0].text
print(token)

# Get ALL Documents and Folders per Folder knowing Folder Id
connGetDocsAndFolders = http.client.HTTPConnection("urlAddress", 8080)

headersGetDocsAndFolders = {
    "Accept": "application/xml",
    "Content-Type": "application/xml",
    "X-SAP-LogonToken": token,
    "Authorization": "Bearer X-SAP-LogonToken"
}
print(headersGetDocsAndFolders)

payloadXml = "<search>\n <folder>\n <folderId>yourFolderId</folderId>\n <folder>\n <document>\n <folderId>yourFolderId</folderId>\n </document>\n</search>"
print(payloadXml)

connGetDocsAndFolders.request("POST", "/biprws/raylight/v1/searches", payloadXml, headersGetDocsAndFolders)
responseGetDocsAndFolders = connGetDocsAndFolders.getresponse()
resultGetDocsAndFolders = responseGetDocsAndFolders.read()
print(resultGetDocsAndFolders.decode("utf-8"))

