import http.client
import xml.etree.ElementTree as ET
import pandas as pd

# Establish connection to the server
conn_get = http.client.HTTPConnection("urlAddress", 8080)
headers_get = {
    "Accept": "application/xml"
}
payload = ""

# GET the authentication information
conn_get.request("GET", "biprws/logon/long", body=None, headers=headers_get)
response_get = conn_get.getresponse()
result_get = response_get.read()
print(result_get.decode("utf-8"))

# Parse the XML response
root = ET.fromstring(result_get)
for child in root:
    print(child.tag, child.attrib, child.text)

# Modify XML elements with your username and password
root[0].text = 'yourUsername'
root[3].text = 'yourPassword'

# Convert modified XML back to string
new_payload = ET.tostring(root, encoding='utf-8').decode('utf-8')
print(new_payload)

# Establish connection for POST request
conn_post = http.client.HTTPConnection("urlAddress", 8080)
headers_post = {
    "Content-Type": "application/xml"
}

# Get the logon token using POST request
conn_post.request("POST", "biprws/logon/long", new_payload, headers_post)
response_post = conn_post.getresponse()
result_post = response_post.read()
print(result_post.decode("utf-8"))

# Extract token from the POST response
root_token = ET.fromstring(result_post)
token = root_token[3][0][0].text
print(token)

# Establish connection to get documents and folders
conn_get_docs_folders = http.client.HTTPConnection("urlAddress", 8080)
headers_get_docs_folders = {
    "Accept": "application/xml",
    "Content-Type": "application/xml",
    "X-SAP-LogonToken": token,
    "Authorization": "Bearer X-SAP-LogonToken"
}
print(headers_get_docs_folders)

# Define current folder ID and create payload
current_folder_id = 123
payload_xml = f"<search>\n <folder>\n <folderId>{current_folder_id}</folderId>\n <folder>\n <document>\n <folderId>{current_folder_id}</folderId>\n </document>\n</search>"
print(payload_xml)

# Send POST searches to check if folders and documents exist in parent folder
conn_get_docs_folders.request("POST", "/biprws/raylight/v1/searches", payload_xml, headers_get_docs_folders)
response_get_docs_folders = conn_get_docs_folders.getresponse()
result_get_docs_folders = response_get_docs_folders.read()
print(result_get_docs_folders.decode("utf-8"))

# Parse the XML response to extract children details
root = ET.fromstring(result_get_docs_folders)
for child in root:
    print(child.tag, child.attrib, child.text, child.find("id").text, child.find("name").text)

# Initialize lists and dictionary for storing folder and document details
folder_ids = []
folder_names = []
document_ids = []
document_names = []
item_ids = []
document_dict = {}


# Get folder ID, folder name, document ID, and document name
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

# Call the function
post_searches_dict(current_folder_id, headers_get_docs_folders)

# Print folder and document details
print(folder_ids)
print(folder_names)
print(document_ids)
print(document_names)

# Create DataFrame from document dictionary
df = pd.DataFrame(list(document_dict.items()), columns=['Document ID', 'Document Name']).set_index('Document ID')
print(df)

# Initialize lists to store dataprovider ID and universe name
all_dataprovider_ids = []
all_universes = []

# Loop through each document to get dataprovider details
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

    # Loop through dataproviders in each document
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

            # Extract universes from dataprovider details
            for u in root_ids.findall('dataSourceName'):
                if u is not None:
                    universes.append(u.text)

    # Extend the lists with dataprovider IDs and universes' names
    all_dataprovider_ids.append(dataprovider_ids)
    all_universes.append(universes)

# Create a combined dictionary
combined_dict = {
    "document_ids": document_ids,
    "dataprovider_ids": all_dataprovider_ids,
    "universes": all_universes
}

# Create DataFrame from the combined dictionary
df1 = pd.DataFrame(combined_dict)
print(df1)

# Merge DataFrames based on document ID
result = pd.merge(df, df1, left_on = "Document ID", right_on = "document_ids", how = "inner")
result.head(15)

# Save merged DataFrame to Excel
result.to_excel(r"your directory", index=False)
print('Saved to Excel')

# Log off the Platform
conn_logoff = http.client.HTTPConnection("urlAddress", 8080)
headersList_logoff = {
    "Accept": "application/xml",
    "X-SAP-LogonToken": token
}

payload = ""

conn_logoff.request("POST", "/biprws/logoff", payload, headersList_logoff)
response_logoff = conn_logoff.getresponse()
result_logoff = response_logoff.read()

print('The job is complete.')