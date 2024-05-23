import streamlit as st
from consulta_prompt_flow import PromptFlowClient
import json
import pandas as pd
import pdfkit
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from run_indexer import run_indexer
from datetime import datetime
import os
import msal
import requests

# Configuración de Azure AD
CLIENT_ID = st.secrets.CLIENT_ID  # Reemplaza con tu Application (client) ID
CLIENT_SECRET = st.secrets.CLIENT_SECRET
TENANT_ID = st.secrets.TENANT_ID
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_PATH = ''
SCOPE = ['User.Read']

# Creación de un objeto de aplicación
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

def get_auth_url():
    return msal_app.get_authorization_request_url(SCOPE, redirect_uri=f"https://cafversionfinalgit-cb8cein65fjssb9hafhnhv.streamlit.app/{REDIRECT_PATH}")

def get_token_from_code(auth_code):
    return msal_app.acquire_token_by_authorization_code(auth_code, scopes=SCOPE, redirect_uri=f"https://cafversionfinalgit-cb8cein65fjssb9hafhnhv.streamlit.app/{REDIRECT_PATH}")

def get_user_profile(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    return response.json()

def get_logout_url():
    return f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=https://cafversionfinalgit-cb8cein65fjssb9hafhnhv.streamlit.app/'
# Manejo de la autenticación en Streamlit
if 'token' not in st.session_state:
    st.session_state["token"] = None

if st.session_state.token:
    user_profile = get_user_profile(st.session_state["token"])
    
    st.write(f"Bienvenido, {user_profile.get('displayName')}")
    st.write(f"Correo electrónico: {user_profile.get('mail')}")
    if st.button("Cerrar sesión"):
        st.session_state["token"] = None
        logout_url = get_logout_url()
        st.markdown(f"[Cerrar sesión con Azure AD]({logout_url})")
        st.stop()
    
    
    # Configuración del client
    # e de
    #  Azure Blob Storage

    if "file" not in st.session_state:
        st.session_state["file"] = None
    if "connection_string" not in st.session_state:
        st.session_state["connection_string"] = st.secrets.blob.conn_string
        
    if "container_name" not in st.session_state:
        st.session_state["container_name"] = "fondos"

    if "blob_service_client" not in st.session_state:
        st.session_state["blob_service_client"] = BlobServiceClient.from_connection_string(st.session_state["connection_string"])
        
        

    def guardar_datos_siga(json_data, tipo):
        if tipo == "contrato":
            st.session_state["data_siga"] = json_data
            return (st.session_state["data_siga"])
        else:
            st.session_state["data_siga_carta"] = json_data 
        
        # print(st.session_state["data_siga"])
            return (st.session_state["data_siga_carta"])

    @st.cache_resource
    def guardar_archivo_en_blob(uploaded_file):
        connection_string = st.session_state["connection_string"]
        

        result = None
            # Upload the file to Azure Blob Storagvector-1713303042620-amsapoc-v1-indexere
        blob_client = st.session_state["blob_service_client"].get_blob_client(container=st.session_state["container_name"], blob=uploaded_file.name)
        if not blob_client.exists():
            result = blob_client.upload_blob(uploaded_file, overwrite=True)
            st.success("Archivo cargado exitosamente")
            try:
                
                run_indexer("vector-1715202020188")
                return True
            except Exception as e:
                st.error(e)
                return False
        else:
            st.warning("El archivo ya está cargado en el blob.")
            return True
        
        
            
            

        
        
    @st.cache_data
    def get_blob_names():
        connection_string = st.session_state["connection_string"]
        
        container_client = st.session_state["blob_service_client"].get_container_client(st.session_state["container_name"])
        blob_list = container_client.list_blobs()
        return [blob.name[:22] for blob in blob_list]


    # Crear la barra lateral de navegación
    st.sidebar.image("logo.png", width=250)
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Ir a", [
        "Consultas", 
        "Resumen Tipo"])

    if page == "Consultas":
        st.title("Página de Consultas")
        consulta = st.text_input("Ingrese consulta")
        if st.button("Enviar"):
            endpoint_url = "https://cafpocfondos-project-consultas.eastus.inference.ml.azure.com/score"
            pfc = PromptFlowClient(endpoint_url)
            response = pfc.send_query(consulta)
            response_json = json.loads(response)
            
            st.success(response_json.get("output"))
        # Aquí puedes agregar el código para la página de consultas
    elif page == "Resumen Tipo":
        st.title("Resumen de Fondos Tipo")
        
        
        st.subheader("Seleccione fondo a Resumir.")
        st.session_state["file"]=st.selectbox("Selecciona un archivo", get_blob_names())
        
        uploaded_file = st.file_uploader("Cargar archivo", type=["pdf"])
        if st.button("Cargar") and "file" not in st.session_state:
        
        
            if uploaded_file is not None:
                st.session_state["file"] = uploaded_file.name
                guardar_archivo_en_blob(uploaded_file)
                st.success("Archivo cargado exitosamente")
            
                st.markdown(''':green[Fondo seleccionado: ] :blue[<b>'''+st.session_state["file"]+'''</b>]''', unsafe_allow_html=True)
        
        
        if st.button("Resumir"):
            endpoint_url = "https://cafpocfondos-project-v3.eastus.inference.ml.azure.com/score"
            pfc = PromptFlowClient(endpoint_url)
            response = pfc.send_text(st.session_state["file"], "cafpocfondos-project-v3-1", st.secrets.resumir.api_key)
            json_response_raw = json.loads(response)
            json_response_prett = json_response_raw["output"]
            st.session_state["Resumen A"] = json_response_prett
            st.success(st.session_state["Resumen A"])
            print(st.session_state["Resumen A"])
        
        if st.button("Guardar Resumen"):
            # Convert markdown to PDF
            resultado_pdf = pdfkit.from_string(str(st.session_state["Resumen A"]), st.session_state["file"])
            # print(resultado_pdf)
            st.success("Resumen guardado exitosamente")

    
    
else:
    auth_url = get_auth_url()
    st.markdown(f"[Iniciar sesión con Azure AD]({auth_url})")
    
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        token_response = get_token_from_code(auth_code)
        st.session_state["token"] = token_response["access_token"] if "access_token" in token_response else None
        st.rerun()
