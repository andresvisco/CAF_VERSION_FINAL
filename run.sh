export CLIENT_ID="fc7601ad-5176-4772-8817-9a1ef5234234"
export CLIENT_SECRET="UP78Q~qOL7g.ddsZpUFfTRfJKNSHr~rLErs2ndnm"
export TENANT_ID="bc82c546-fd13-43aa-9027-3272991956fc"
export api_key_consultas="x5zh3zigHARlAbBSB89Skrip9baAZ5qA"
export api_key_resumir="KWpnGhGZ4eta3Eg2JB5Td2F1wMx9dEuf"
export conn_string_blob="DefaultEndpointsProtocol=https;AccountName=storageaccpocgreencafcr;AccountKey=HmNZ7h+8q9KdQgfcTUWgqe3Yj+AwpoBodOdDtnCkxESB85bUUwD9L1Ww89Vkof+FtWAxYMmG9i7p+AStbIyhzw==;EndpointSuffix=core.windows.net"
export endpointaz_endpoint_az="https://login.microsoftonline.com/bc82c546-fd13-43aa-9027-3272991956fc/oauth2/v2.0/authorize"

python -m streamlit run ui/app.py --server.port 8000 --server.address 0.0.0.0