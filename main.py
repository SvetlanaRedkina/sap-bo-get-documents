import http.client
import xml.etree.ElementTree as ET

# GET request
conn_get = http.client.HTTPConnection("urlAddress", 8080)

headers_get = {
    "Accept": "application/xml"
}

payload = ""

conn_get.request("GET", "biprws/logon/long", body=None, headers=headers_get)
response_get = conn_get.getresponse()
result_get = response_get.read()
print(result_get.decode("utf-8"))

root = ET.fromstring(result_get)
print(root)

for child in root:
    print(child.tag, child.attrib, child.text)

root[0].text = 'yourUsername'
root[3].text = 'yourPassword'

new_payload = ET.tostring(root, encoding='utf-8').decode('utf-8')
print(new_payload)

# POST request
conn_post = http.client.HTTPConnection("urlAddress", 8080)

headers_post = {
    "Content-Type": "application/xml"
}

conn_post.request("POST", "biprws/logon/long", new_payload, headers_post)
response_post = conn_post.getresponse()
result_post = response_post.read()
print(result_post.decode("utf-8"))

root_token = ET.fromstring(result_post)
print(root_token)

for child in root_token:
    print(child.tag, child.attrib, child.text)

token = root_token[3][0][0].text
print(token)

# Get ALL Documents and Folders per Folder knowing Folder Id
conn_get_docs_folders = http.client.HTTPConnection("urlAddress", 8080)

headers_get_docs_folders = {
    "Accept": "application/xml",
    "Content-Type": "application/xml",
    "X-SAP-LogonToken": token,
    "Authorization": "Bearer X-SAP-LogonToken"
}
print(headers_get_docs_folders)

payload_xml = "<search>\n <folder>\n <folderId>yourFolderId</folderId>\n <folder>\n <document>\n <folderId>yourFolderId</folderId>\n </document>\n</search>"
print(payload_xml)

conn_get_docs_folders.request("POST", "/biprws/raylight/v1/searches", payload_xml, headers_get_docs_folders)
response_get_docs_folders = conn_get_docs_folders.getresponse()
result_get_docs_folders = response_get_docs_folders.read()
print(result_get_docs_folders.decode("utf-8"))

