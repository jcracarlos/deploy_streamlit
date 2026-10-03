import json
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import streamlit as st

# Configuración de credenciales y conexión a Firestore
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-app-70c78")
dbNames = db.collection("names")


# Función auxiliar para buscar registros por nombre
def loadByName(name):
    names_ref = dbNames.where("name", "==", name)
    currentName = None
    for myname in names_ref.stream():
        currentName = myname
    return currentName


# ---------------------------------------------------------
# UI: Formulario principal para crear registros
# ---------------------------------------------------------
st.header("Nuevo registro")
index = st.text_input("Index")
name = st.text_input("Name")
sex = st.selectbox("Select Sex", ("F", "M", "Other"))
submit = st.button("Crear nuevo registro")

# Procesar creación de registro
if index and name and sex and submit:
    doc_ref = db.collection("names").document(name)
    doc_ref.set({"index": index, "name": name, "sex": sex})
    st.sidebar.write("Registro insertado correctamente")

# ---------------------------------------------------------
# UI: Barra lateral (Sidebar) - Operaciones CRUD
# ---------------------------------------------------------
st.sidebar.subheader("Buscar nombre")
nameSearch = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    doc = loadByName(nameSearch)
    if doc is None:
        st.sidebar.write("Nombre no existe")
    else:
        st.sidebar.write(doc.to_dict())

st.sidebar.markdown("---")

btnEliminar = st.sidebar.button("Eliminar")
if btnEliminar:
    deletename = loadByName(nameSearch)
    if deletename is None:
        st.sidebar.write(f"{nameSearch} no existe")
    else:
        dbNames.document(deletename.id).delete()
        st.sidebar.write(f"{nameSearch} eliminado")

st.sidebar.markdown("---")

newname = st.sidebar.text_input("Actualizar nombre")
btnActualizar = st.sidebar.button("Actualizar")
if btnActualizar:
    updatename = loadByName(nameSearch)
    if updatename is None:
        st.write(f"{nameSearch} no existe")
    else:
        myupdatename = dbNames.document(updatename.id)
        myupdatename.update({"name": newname})

# ---------------------------------------------------------
# UI: Vista principal - Mostrar todos los registros
# ---------------------------------------------------------
names_ref = list(db.collection("names").stream())
names_dict = list(map(lambda x: x.to_dict(), names_ref))
names_dataframe = pd.DataFrame(names_dict)
st.dataframe(names_dataframe)