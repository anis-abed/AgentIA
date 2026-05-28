import streamlit as st
import pandas as pd
import plotly.express as px
import json
import ollama
import re
from mcp_server import mcp_api_connector

# Configuration de l'application
st.set_page_config(page_title="Agent IA - Master 1", layout="wide", page_icon="🧠")

# 1. INITIALISATION DE LA SESSION
if 'api_url' not in st.session_state:
    st.session_state.api_url = None
if 'dataset_name' not in st.session_state:
    st.session_state.dataset_name = ""

# 2. FONCTION INTELLIGENCE (L'AGENT IA)
def agent_intelligence(user_query, df, topic):
    # Description rapide des colonnes pour guider l'agent
    columns_list = ", ".join(df.columns)
    
    system_prompt = f"""
    Tu es un ANALYSTE DE DONNÉES.
    Dataset actuel : {topic}
    Colonnes disponibles : {columns_list}

    MISSION : Réponds à la demande de l'utilisateur "{user_query}" au format JSON strict.
    Contrainte de l'insight : Rédige obligatoirement un RÉSUMÉ TRÈS COURT (1 ou 2 phrases maximum).
    
    Format de réponse attendu (JSON uniquement) :
    {{
      "chart_type": "bar|line|pie|map",
      "x_axis": "nom_de_colonne",
      "y_axis": "nom_de_colonne",
      "title": "Titre du graphique",
      "insight": "Ton résumé ultra-court ici."
    }}
    """
    
    try:
        response = ollama.chat(model='gemma3:1b', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_query}
        ])
        content = response['message']['content']
        # Extraction du bloc JSON de la réponse textuelle
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        return json.loads(match.group(1)) if match else None
    except:
        return None

# 3. INTERFACE UTILISATEUR (STREAMLIT UI)
if st.session_state.api_url is None:
    st.title("🤖 Configuration de l'Agent MCP")
    with st.form("setup_form"):
        url = st.text_input("Lien de l'API (CSV) :")
        name = st.text_input("Nom du Projet / Dataset :")
        if st.form_submit_button("Lancer l'Application"):
            if url and name:
                st.session_state.api_url = url
                st.session_state.dataset_name = name
                st.rerun()
else:
    # Bouton de déconnexion/changement de source dans la barre latérale
    if st.sidebar.button("🔄 Changer de source de données"):
        st.session_state.api_url = None
        st.rerun()

    # Appel au serveur MCP pour charger et nettoyer la donnée
    df = mcp_api_connector(st.session_state.api_url)

    if df is not None:
        # --- CONFIGURATION DU FILTRE DYNAMIQUE (SLIDER) ---
        st.sidebar.header("🎚️ Filtres")
        numeric_cols = df.select_dtypes(include=['number']).columns
        # Cible en priorité la colonne "dotation_brute", sinon prend la première colonne numérique
        filter_col = "dotation_brute" if "dotation_brute" in df.columns else (numeric_cols[0] if len(numeric_cols) > 0 else None)
        
        if filter_col:
            # Sécurisation du typage numérique pour le slider
            df[filter_col] = pd.to_numeric(df[filter_col], errors='coerce')
            df = df.dropna(subset=[filter_col])
            
            min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
            slider_range = st.sidebar.slider(f"Plage de {filter_col}", min_val, max_val, (min_val, max_val))
            # Application du filtre au DataFrame
            df = df[(df[filter_col] >= slider_range[0]) & (df[filter_col] <= slider_range[1])]

        # --- CORPS PRINCIPAL DE L'APPLICATION ---
        st.title(f"📊 Dashboard : {st.session_state.dataset_name}")
        
        with st.expander("🔍 Aperçu des données nettoyées (Top 5 lignes)"):
            st.dataframe(df.head(5))

        # Barre de recherche pour le Prompt utilisateur
        query = st.text_input("💬 Que voulez-vous analyser (Prompt) ?")

        if query:
            with st.spinner("L'agent analyse votre demande..."):
                res = agent_intelligence(query, df, st.session_state.dataset_name)
            
            if res:
                # Mapping insensible à la casse des colonnes trouvées par l'IA
                columns_map = {c.lower(): c for c in df.columns}
                col_x = columns_map.get(res.get('x_axis', '').lower(), df.columns[0])
                col_y = columns_map.get(str(res.get('y_axis', '')).lower(), filter_col)

                if col_y:
                    df[col_y] = pd.to_numeric(df[col_y], errors='coerce')

                chart_type = res.get('chart_type', 'bar')

                try:
                    # --- CONSTRUCION ET RENDU DES GRAPHES ---
                    if chart_type == 'map' and 'lat' in df.columns:
                        fig = px.scatter_mapbox(
                            df, lat='lat', lon='lon', 
                            color=col_y, size=col_y, 
                            hover_name=col_x, 
                            color_continuous_scale='RdYlGn',  # Échelle divergente Rouge-Jaune-Vert
                            zoom=8, height=600, 
                            mapbox_style="carto-positron"
                        )
                    elif chart_type == 'pie':
                        fig = px.pie(df.sort_values(by=col_y, ascending=False).head(15), names=col_x, values=col_y, title=res.get('title'))
                    elif chart_type == 'line':
                        fig = px.line(df.sort_values(by=col_x), x=col_x, y=col_y, markers=True, title=res.get('title'))
                    else:
                        fig = px.bar(df.sort_values(by=col_y, ascending=False).head(20), x=col_x, y=col_y, color=col_y, title=res.get('title'))
                    
                    # Affichage du graphe Plotly
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # --- AFFICHAGE DU RÉSUMÉ CONCIS ---
                    st.success(f"**Analyse :** {res.get('insight', 'Aucun résumé généré.')}")
                    
                except Exception as chart_error:
                    st.error(f"Erreur lors de la génération du graphique : {chart_error}")