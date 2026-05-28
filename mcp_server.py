import pandas as pd
import streamlit as st

def mcp_api_connector(url):
    """
    Connecteur Universel MCP : Récupère, Nettoie et Type les données.
    Inclut une détection intelligente des coordonnées (nommées ou fusionnées).
    """
    try:
        # User-Agent pour éviter les blocages de certains serveurs API
        storage_options = {'User-Agent': 'Mozilla/5.0'}
        
        # Lecture flexible avec détection automatique du séparateur (virgule, point-virgule, etc.)
        df = pd.read_csv(url, storage_options=storage_options, sep=None, engine='python')
        
        # 1. Nettoyage de base
        # Supprimer les colonnes 100% vides
        df = df.dropna(axis=1, how='all')
        # Supprimer les espaces inutiles dans les noms de colonnes
        df.columns = [c.strip() for c in df.columns]

        # 2. IDENTIFICATION GÉOGRAPHIQUE INTELLIGENTE
        lat_cols = [c for c in df.columns if c.lower().startswith('lat')]
        lon_cols = [c for c in df.columns if c.lower().startswith('lon') or c.lower().startswith('log')]

        # --- CAS A : Les colonnes Latitude et Longitude sont déjà séparées ---
        if lat_cols and lon_cols:
            df['lat'] = pd.to_numeric(df[lat_cols[0]], errors='coerce')
            df['lon'] = pd.to_numeric(df[lon_cols[0]], errors='coerce')
        
        # --- CAS B : Détection par Analyse de Contenu (ex: colonne "wgs84" ou "position") ---
        else:
            for col in df.columns:
                # On récupère le premier échantillon non nul pour tester le format
                non_null_samples = df[col].dropna()
                if not non_null_samples.empty:
                    sample = str(non_null_samples.iloc[0])
                    
                    # Heuristique : Si la cellule contient une virgule (ex: "48.85,2.35")
                    if "," in sample:
                        parts = sample.split(',')
                        if len(parts) >= 2:
                            try:
                                # On vérifie si les deux parties sont bien des nombres
                                float(parts[0].strip())
                                float(parts[1].strip())
                                
                                # Si le test réussit, on extrait les coordonnées
                                coords = df[col].astype(str).str.split(',', expand=True)
                                df['lat'] = pd.to_numeric(coords[0], errors='coerce')
                                df['lon'] = pd.to_numeric(coords[1], errors='coerce')
                                
                                # On s'arrête dès qu'une colonne valide est trouvée
                                break 
                            except (ValueError, IndexError):
                                continue

        # 3. NETTOYAGE FINAL DES COORDONNÉES
        # Si on a réussi à créer les colonnes standardisées 'lat' et 'lon'
        if 'lat' in df.columns and 'lon' in df.columns:
            # On supprime les lignes où la conversion a échoué (NaN)
            df = df.dropna(subset=['lat', 'lon'])
        
        return df

    except Exception as e:
        st.error(f"❌ Erreur de connexion ou de traitement : {e}")
        return None