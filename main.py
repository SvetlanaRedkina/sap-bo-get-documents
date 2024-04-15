import http.client
import xml.etree.ElementTree as ET
import pandas as pd

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

payload_xml = ("<search>\n <folder>\n <folderId>yourFolderId</folderId>\n <folder>\n <document>\n "
               "<folderId>yourFolderId</folderId>\n </document>\n</search>")
print(payload_xml)

conn_get_docs_folders.request("POST", "/biprws/raylight/v1/searches", payload_xml, headers_get_docs_folders)
response_get_docs_folders = conn_get_docs_folders.getresponse()
result_get_docs_folders = response_get_docs_folders.read()
print(result_get_docs_folders.decode("utf-8"))

current_folder_id = 107

root = ET.fromstring(result_get_docs_folders)
print(root)
for child in root:
    print(child.tag, child.attrib, child.text, child.find("id").text, child.find("name").text)

folder_ids = []
folder_names = []
document_ids = []
document_names = []
item_ids = []
document_dict = {}


# Get all Documents, including Documents of the Child-Folders
def post_searches(parent_folder_id, headers):
    conn = http.client.HTTPConnection("urlAddress", 8080)

    payload = (f"<search>\n <folder>\n <folderId>{parent_folder_id}</folderId>\n <folder>\n <document>\n "
               f"<folderId>{parent_folder_id}</folderId>\n </document>\n</search>")
    conn.request("POST", "/biprws/raylight/v1/searches", payload, headers)
    response = conn.getresponse()
    response_bytes = response.read()
    result = response_bytes.decode("utf-8")

    root = ET.fromstring(result)

    for item in root:
        if item.tag == "folder":
            folder_id = item.find("id").text
            folder_ids.append(folder_id)
            folder_name = item.find("name").text
            folder_names.append(folder_name)
            print(item.tag, folder_id, folder_name)
            post_searches(folder_id, headers)
        elif item.tag == "document":
            document_id = item.find("id").text
            document_name = item.find("name").text
            document_names.append(document_name)
            document_ids.append(document_id)
            print(item.tag, document_id, document_name)
        else:
            item_id = item.find("id").text
            item_ids.append(item_id)
            print(item.tag, item_id)

# Call the function and print out the result
post_searches(current_folder_id, headers_get_docs_folders)
print(folder_ids)
print(folder_names)
print(document_ids)
print(document_names)

def post_searches_dict(parent_folder_id, headers):
    conn = http.client.HTTPConnection("urlAddress", 8080)

    payload = f"<search>\n <folder>\n <folderId>{parent_folder_id}</folderId>\n <folder>\n <document>\n <folderId>{parent_folder_id}</folderId>\n </document>\n</search>"
    conn.request("POST", "/biprws/raylight/v1/searches", payload, headers)
    response = conn.getresponse()
    response_bytes = response.read()
    result = response_bytes.decode("utf-8")

    root = ET.fromstring(result)

    for item in root:
        if item.tag == "folder":
            folder_id = item.find("id").text
            folder_name = item.find("name").text
            print(item.tag, folder_id, folder_name)
            post_searches_dict(folder_id, headers)
        elif item.tag == "document":
            document_id = item.find("id").text
            document_name = item.find("name").text
            print(item.tag, document_id, document_name)
            document_ids.append(document_id)
            document_names.append(document_name)
            document_dict[document_id] = document_name
        else:
            item_id = item.find("id").text
            print(item.tag, item_id)

post_searches_dict(current_folder_id, headers_get_docs_folders)

print(folder_ids)
print(folder_names)
print(document_ids)
print(document_names)
print(document_dict)


df = pd.DataFrame(list(document_dict.items()), columns=['Document ID', 'Document Name']).set_index('Document ID')
print(df)

all_dataprovider_ids = []
all_universes = []

conn_dataproviders_dict = http.client.HTTPConnection("urlAddress", 8080)
headers_dataproviders = {
    "Accept": "application/xml",
    "X-SAP-LogonToken": token,
    "Authorization": "Bearer X-SAP-LogonToken"
}
payload_dataproviders = ""

for document_id in document_ids:
    url = f"/biprws/raylight/v1/documents/{document_id}/dataproviders"
    conn_dataproviders_dict.request("GET", url, payload_dataproviders, headers_dataproviders)
    response_dataproviders = conn_dataproviders_dict.getresponse()
    result_dataproviders = response_dataproviders.read()

    root = ET.fromstring(result_dataproviders)

    dataprovider_ids = []
    universes = []

    for r in root.findall('dataprovider'):
        dataprovider_id = r.find('id')
        if dataprovider_id is not None:
            dataprovider_ids.append(dataprovider_id.text)

            conn_dataprovider_ids = http.client.HTTPConnection("urlAddress", 8080)
            headers_dataproviders_ids = {
                "Accept": "application/xml",
                "X-SAP-LogonToken": token,
                "Authorization": "Bearer X-SAP-LogonToken"
            }
            payload_dataproviders_ids = ""

            url_i = f"/biprws/raylight/v1/documents/{document_id}/dataproviders/{dataprovider_id.text}"
            conn_dataprovider_ids.request("GET", url_i, payload_dataproviders_ids, headers_dataproviders_ids)
            response_dataproviders_ids = conn_dataprovider_ids.getresponse()
            result_dataproviders_ids = response_dataproviders_ids.read()
            root_ids = ET.fromstring(result_dataproviders_ids)

            for u in root_ids.findall('dataSourceName'):
                if u is not None:
                    universes.append(u.text)

    all_dataprovider_ids.append(dataprovider_ids)
    all_universes.append(universes)

combined_dict = {
    "document_ids": document_ids,
    "dataprovider_ids": all_dataprovider_ids,
    "universes": all_universes
}

print(combined_dict)

df1 = pd.DataFrame(combined_dict)
print(df1)

result = pd.merge(df, df1, left_on = "Document ID", right_on = "document_ids", how = "inner")
result.head(15)
result.to_excel(f"your directory", index=False)

