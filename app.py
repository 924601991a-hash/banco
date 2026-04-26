import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# CONFIGURACIÓN FIREBASE
if not firebase_admin._apps:
    try:
        # Aquí usas el archivo que vas a subir a GitHub
        cred = credentials.Certificate('credenciales.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://bancoan-86282-default-rtdb.firebaseio.com/' 
        })
    except:
        st.error("Revisa tu archivo credenciales.json y la URL")

st.set_page_config(page_title="BANCO ONLINE AIEP", page_icon="🏦")

# Conexión a la tabla de usuarios
ref_u = db.reference('usuarios')

st.title("🏦 Sistema Bancario Online")

if 'usuario' not in st.session_state:
    with st.form("login"):
        st.subheader("Ingreso Seguro")
        doc = st.text_input("Documento (Doc)")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("INGRESAR"):
            datos = ref_u.child(doc).get()
            if datos and datos['pin'] == pin:
                st.session_state['usuario'] = datos
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    u = st.session_state['usuario']
    st.sidebar.success(f"Sesión activa: {u['nombre']}")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state['usuario']
        st.rerun()

    # Mostrar Saldo actualizado
    saldo_actual = ref_u.child(u['doc']).child('saldo').get()
    st.header(f"Tu Saldo: ${saldo_actual}")
    
    # Zona de Transferencia
    with st.expander("💸 Enviar dinero a otro usuario"):
        dest = st.text_input("Doc del Destinatario")
        monto = st.number_input("Monto a enviar", min_value=1)
        if st.button("Confirmar Envío"):
            u_dest = ref_u.child(dest).get()
            if u_dest and saldo_actual >= monto:
                # Restar y Sumar en la nube
                ref_u.child(u['doc']).update({'saldo': saldo_actual - monto})
                ref_u.child(dest).update({'saldo': u_dest['saldo'] + monto})
                st.balloons()
                st.success("¡Dinero enviado con éxito!")
                st.rerun()
            else:
                st.error("Saldo insuficiente o el destino no existe")
