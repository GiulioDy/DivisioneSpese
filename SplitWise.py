import matplotlib.pyplot as plt
import streamlit as st
import json
import os

FILE_DATI = "spese.json"


# --- Funzioni di utilità ---
def salva_dati():
    dati = {"giulio": st.session_state.giulio, "delia": st.session_state.delia}
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)


def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            return json.load(f)
    else:
        return {
            "giulio": {"hotel": [328.81, 316.20, 190], "traghetto": 272},
            "delia": {"regalo Irene": 70}
        }


# --- Inizializzazione session_state ---
if "giulio" not in st.session_state or "delia" not in st.session_state:
    dati = carica_dati()
    st.session_state.giulio = dati["giulio"]
    st.session_state.delia = dati["delia"]


# --- Funzioni per gestione spese ---
def aggiungi_spesa(persona, categoria, importo):
    if categoria in st.session_state[persona]:
        if isinstance(st.session_state[persona][categoria], list):
            st.session_state[persona][categoria].append(importo)
        else:
            st.session_state[persona][categoria] = [st.session_state[persona][categoria], importo]
    else:
        st.session_state[persona][categoria] = importo
    salva_dati()


def rimuovi_categoria(persona, categoria):
    if categoria in st.session_state[persona]:
        del st.session_state[persona][categoria]
    salva_dati()


# --- Titolo ---
st.title("💰 Gestione Spese Giulio & Delia")

# --- Form aggiunta spesa ---
with st.form("aggiungi_form"):
    persona = st.selectbox("A chi aggiungere la spesa?", ["giulio", "delia"])
    categoria = st.text_input("Categoria di spesa")
    importo = st.number_input("Importo (€)", min_value=0.0, step=0.01)
    aggiungi = st.form_submit_button("➕ Aggiungi spesa")

    if aggiungi and categoria and importo > 0:
        aggiungi_spesa(persona, categoria, importo)
        st.success(f"Spesa '{categoria}' di {importo:.2f} € aggiunta a {persona.capitalize()}")

# --- Calcolo somme ---
def calcola_somma(diz):
    return sum(v if isinstance(v, (int, float)) else sum(v) for v in diz.values())


somma_giulio = calcola_somma(st.session_state.giulio)
somma_delia = calcola_somma(st.session_state.delia)

# --- Riepilogo ---
st.subheader("📋 Riepilogo")
st.markdown(f"**Totale spesa:** {somma_giulio + somma_delia:.2f} €")
st.markdown(f"**Spesa Giulio:** {somma_giulio:.2f} €")
st.markdown(f"**Spesa Delia:** {somma_delia:.2f} €")

if somma_giulio > somma_delia:
    st.markdown(f"💡 Delia deve a Giulio: **{(somma_giulio - somma_delia) / 2:.2f} €**")
elif somma_delia > somma_giulio:
    st.markdown(f"💡 Giulio deve a Delia: **{(somma_delia - somma_giulio) / 2:.2f} €**")
else:
    st.markdown("✅ Nessuno deve nulla!")

# --- Grafico ---
etichette = list(set(list(st.session_state.giulio.keys()) + list(st.session_state.delia.keys())))
valori_giulio = [
    st.session_state.giulio.get(cat, 0) if isinstance(st.session_state.giulio.get(cat, 0), (int, float))
    else sum(st.session_state.giulio.get(cat, [])) for cat in etichette
]
valori_delia = [
    st.session_state.delia.get(cat, 0) if isinstance(st.session_state.delia.get(cat, 0), (int, float))
    else sum(st.session_state.delia.get(cat, [])) for cat in etichette
]

x = range(len(etichette))
fig, ax = plt.subplots()
ax.bar([i - 0.2 for i in x], valori_giulio, width=0.4, color='skyblue', label="Giulio")
ax.bar([i + 0.2 for i in x], valori_delia, width=0.4, color='pink', label="Delia")
ax.set_xticks(x)
ax.set_xticklabels(etichette, rotation=45, ha="right")
ax.set_ylabel("Spesa (€)")
ax.set_title("Spese a confronto")
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

st.pyplot(fig)


# --- Modifica e rimozione ---
st.subheader("✏️ Modifica o rimuovi spese")

for persona in ["giulio", "delia"]:
    st.markdown(f"### {persona.capitalize()}")
    categorie = list(st.session_state[persona].keys())

    for cat in categorie:
        valore = st.session_state[persona][cat]
        if isinstance(valore, list):
            totale = sum(valore)
        else:
            totale = valore

        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            nuova_categoria = st.text_input(f"Categoria ({persona})", cat, key=f"cat_{persona}_{cat}")
        with col2:
            nuovo_valore = st.number_input(f"Importo totale", value=float(totale), step=0.01,
                                           key=f"val_{persona}_{cat}")
        with col3:
            if st.button("❌", key=f"del_{persona}_{cat}"):
                rimuovi_categoria(persona, cat)
                st.rerun()

        # Salva modifiche se il nome o il valore cambiano
        if nuova_categoria != cat or nuovo_valore != totale:
            st.session_state[persona].pop(cat)
            st.session_state[persona][nuova_categoria] = nuovo_valore
            salva_dati()
            st.rerun()

