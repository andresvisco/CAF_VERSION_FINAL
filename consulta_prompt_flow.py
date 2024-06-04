import urllib.request
import json
import os
import ssl
import streamlit as st 


class PromptFlowClient:
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        
    def send_query(self, query):
        
        data = {"question": query}

        body = str.encode(json.dumps(data))

        url = self.endpoint_url
        
        api_key = os.environ["api_key_consultas"]
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'cafpocfondos-project-consultas' }

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            return result
        except urllib.error.HTTPError as error:
            st.write("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            st.write(error.info())
            st.write(error.read().decode("utf8", 'ignore'))
        
        
    def send_text(self, filename, flujo, api_key):
        flujo= flujo
        api_key = api_key
        # print(flujo)
        data = {"question": filename}

        body = str.encode(json.dumps(data))

        url = self.endpoint_url 
        
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': str(flujo)}
        

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            return result
        except urllib.error.HTTPError as error:
            st.write("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            st.write(error.info())
            st.write(error.read().decode("utf8", 'ignore'))
    
    
    