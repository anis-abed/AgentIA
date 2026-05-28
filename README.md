# 🧠 Agent IA d'Analyse Automatisée de Données

> Solution métier de **Business Intelligence (BI)** combinant une interface conversationnelle, un serveur de contexte standardisé **(MCP)** et un **Large Language Model (LLM)** exécuté entièrement en local.

---

## 🎯 Objectifs du Projet

L'objectif principal de cette application est de **démocratiser l'accès à la Business Intelligence** en supprimant la barrière technique du code (Python, SQL).

- **Prompt-to-Viz** : Permettre à un utilisateur non-technique de générer des visualisations de données complexes (cartes de chaleur, diagrammes, courbes temporelles) via un simple prompt en langage naturel.
- **Gain de Temps & Productivité** : Automatisation complète du cycle traditionnel `Nettoyage → Analyse statistique → Rendu graphique` en moins de 10 secondes.
- **Souveraineté des données** : Exécution de l'IA entièrement en local afin de garantir la **confidentialité absolue** des données manipulées.

---

## 🛠️ Architecture Technique

L'écosystème repose sur une **architecture découplée** assurant modularité et extensibilité.

```
┌─────────────────────┐        ┌──────────────────────┐        ┌─────────────────┐
│   Interface (app.py)│ ──────▶│  MCP Server           │ ──────▶│  Ollama (LLM)   │
│   Streamlit / UI    │        │  (mcp_server.py)      │        │  Gemma 3:1b     │
│   Prompt utilisateur│◀───────│  ETL + Feature Eng.   │◀───────│  JSON strict    │
└─────────────────────┘        └──────────────────────┘        └─────────────────┘
```

### 1. Connecteur Universel MCP — `mcp_server.py`

Ce composant agit comme une **passerelle d'accès** et un outil de traitement en amont (ETL léger) :

| Fonctionnalité | Description |
|---|---|
| **Ingestion Flexible** | Lecture automatisée des flux CSV avec détection à la volée des délimiteurs (`,` `;`) |
| **Data Cleaning** | Élimination des colonnes vides, normalisation sémantique des en-têtes |
| **Feature Engineering Géographique** | Détection et parsing des coordonnées composites (ex: `"48.85,2.35"`) en champs `lat` / `lon` exploitables par Mapbox |

### 2. Interface Utilisateur & Pipeline IA — `app.py`

| Fonctionnalité | Description |
|---|---|
| **Pilotage par Prompt Strict** | Sollicite Gemma 3:1b via Ollama avec un prompt système contraint retournant du **JSON strict** compatible Plotly |
| **Filtrage Dynamique** | Curseur contextuel (Slider) s'adaptant automatiquement à la variable numérique principale |
| **Visualisations Adaptatives** | Génération dynamique du graphique le plus adapté (`map`, `bar`, `pie`, `line`) avec échelle colorimétrique divergente **Rouge-Jaune-Vert (RdYlGn)** |

---

## ⚙️ Contraintes & Choix d'Ingénierie

**Migration Cloud → Local**
Initialement configuré sur l'API OpenAI, le projet a rencontré des limites de quotas et des coûts restreignant la phase de tests intensifs. Le pivot vers **Ollama** a offert une liberté totale d'exécution et une conformité native au **RGPD** (aucune donnée ne quitte la machine).

**Régulation du format de sortie**
Les petits modèles de langage (1b–3b) ont tendance à ajouter du texte conversationnel autour de leurs réponses. L'implémentation d'une capture par **expressions régulières** (`re.search`) sécurise l'extraction du bloc JSON afin d'éviter les plantages de l'application.

---

## 📦 Installation

### Prérequis

- Python **3.9** ou supérieur
- [Ollama](https://ollama.com/) installé avec le modèle `gemma3:1b`

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-username>/<votre-repo>.git
cd <votre-repo>

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Télécharger le modèle LLM
ollama pull gemma3:1b

# 4. Lancer le serveur MCP
python mcp_server.py

# 5. Lancer l'interface utilisateur
streamlit run app.py
```

---

## 🚀 Exemple d'Utilisation

### Dataset : Coordonnées géographiques des départements métropolitains français

**Source CSV :**
```
https://static.data.gouv.fr/resources/coordonnees-geographiques-extremes-des-departements-metropolitains-de-france/20210827-003941/points-extremes-des-departements-metropolitains-de-france.csv
```

**Nom à donner au dataset dans l'interface :**
```
dataset pour tracer les limites des départements
```

**Prompt à tester :**
```
Fais un pie pour les départements.
```

**Résultat attendu :**
L'agent interroge le CSV, nettoie les données, et génère automatiquement un **diagramme en secteurs (pie chart)** représentant la répartition des départements métropolitains — sans écrire une seule ligne de code.

---

## 📁 Structure du Projet

```
.
├── app.py              # Interface Streamlit & pipeline IA
├── mcp_server.py       # Connecteur MCP (ETL + feature engineering)
├── requirements.txt    # Dépendances Python
└── README.md
```

---

## 🔒 Conformité & Confidentialité

Ce projet est conçu dans une logique **privacy-by-design** :
- Aucune donnée ne transite vers un serveur externe
- Le modèle LLM tourne intégralement en local via Ollama
- Compatible avec les environnements soumis au **RGPD**
