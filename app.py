import time
import json
import pathlib
import os
import streamlit as st
import plotly.graph_objects as go
import googlemaps
import pandas as pd
from dotenv import dotenv_values

config = dotenv_values(".env")
# Sua chave de API do Google Maps
API_KEY = config["API_MAPS"]
gmaps = googlemaps.Client(key=API_KEY)


# gerar resultados
def gerar_resultados(lugares):
    resultados = []
    lugares_detalhes = {}
    for lugar in lugares.get("results", []):
        nome = lugar.get("name", "Não disponível")
        endereco = lugar.get("formatted_address", "Não disponível")
        
        place_id = lugar.get("place_id", "")
        # verificar se existe um arquivo json com detalhes da empresa
        if pathlib.Path(
            f"detalhes_empresas_{palavra_chave}_{localizacao}.json"
        ).exists():
            with open(f"detalhes_empresas_{palavra_chave}_{localizacao}.json") as f:
                lugar_detalhes = json.load(f)
            
            telefone = lugar_detalhes[f"{place_id}"].get(
                "formatted_phone_number", "Não disponível"
            )
            #obter horários de funcionamento e converter
            horarios = lugar_detalhes[f"{place_id}"].get("opening_hours", {})
            if horarios:
                horario = ""
                for dia in horarios.get("weekday_text", []):
                    horario += f"{dia}\n"
                    
            else:
                horario = "Não disponível"
                
        else:
            # Obter detalhes adicionais do lugar usando o place_id
            lugar_detalhes = gmaps.place(place_id=place_id)
            lugar = lugar_detalhes["result"]
            # salvar detalhes em objeto com a chave com nome
            lugares_detalhes[place_id] = lugar

            telefone = lugar.get("formatted_phone_number", "Não disponível")

        resultados.append(
            {
                "Nome": nome,
                "Telefone": telefone,
                "Endereço": endereco,
                "Horário de Funcionamento": horario,
            }
        )
    if lugares_detalhes:
        with open(f"detalhes_empresas_{palavra_chave}_{localizacao}.json", "w") as f:
            json.dump(lugares_detalhes, f)
    return resultados


def buscar_empresas(palavra_chave, localizacao, raio=5000):
    try:
        # Find files matching the pattern
        arquivos = list(
            pathlib.Path(".").glob(f"empresas_{palavra_chave}_{localizacao}*.json")
        )

        if arquivos:  # Check if any files were found
            if len(arquivos) > 1:
                # If multiple files exist, get the most recent one
                arquivo = sorted(arquivos, key=os.path.getmtime, reverse=True)[0]
            else:
                arquivo = arquivos[0]

            with open(arquivo) as f:
                lugares = json.load(f)

            return gerar_resultados(lugares)

        # If no files found, proceed with API call
        geocode_result = gmaps.geocode(localizacao)
        if not geocode_result:
            st.error("Localização não encontrada.")
            return []

        # Rest of your existing API call code...
    except FileNotFoundError:

        geocode_result = gmaps.geocode(localizacao)
        if not geocode_result:
            st.error("Localização não encontrada.")
            return []

        coordenadas = geocode_result[0]["geometry"]["location"]
        lat_lng = f"{coordenadas['lat']},{coordenadas['lng']}"
        lugares = gmaps.places(query=palavra_chave, location=lat_lng, radius=raio)
        # salvar lugarem em um arquivo json com timestamp atual

        with open(f"empresas_{palavra_chave}_{localizacao}.json", "w") as f:
            json.dump(lugares, f)

        return gerar_resultados(lugares)


# Interface do Streamlit
st.title("Busca de Empresas no Google Maps")
st.markdown(
    "Este aplicativo usa a API Places para buscar empresas baseadas em palavras-chave e localizações."
)

# Formulário para entrada de dados
palavra_chave = st.text_input(
    "Digite a palavra-chave (ex: 'postos de combustível')", "postos de combustível"
)
localizacao = st.text_input(
    "Digite a localização (ex: 'Campo Grande, MS')", "Campo Grande, MS"
)
raio = st.slider("Raio de busca (em metros)", 1000, 20000, 5000)

# Botão para iniciar a busca
if st.button("Buscar"):
    with st.spinner("Buscando empresas..."):
        empresas = buscar_empresas(palavra_chave, localizacao, raio)

    if empresas:
        # carregar um mapa com as localizações encontradas conforme o arquivo
        with open(f"empresas_{palavra_chave}_{localizacao}.json") as f:
            lugares = json.load(f)
        # colocar legenda com o nome das empresas nos pontos do mapa com plotly
        fig = go.Figure()
        for lugar in lugares.get("results", []):
            coordenadas = lugar["geometry"]["location"]
            nome = lugar.get("name", "Não disponível")
            fig.add_trace(
                go.Scattermapbox(
                    lat=[coordenadas["lat"]],
                    lon=[coordenadas["lng"]],
                    mode="markers",
                    marker=go.scattermapbox.Marker(size=14),
                    text=nome,
                    name=nome,
                    hoverinfo="text",
                    showlegend=False,
                    legendgroup="group1",
                    legendgrouptitle_text="Empresas",
                    legendrank=1,
                    legendwidth=100,
                )
            )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(
                    lat=lugares["results"][0]["geometry"]["location"]["lat"],
                    lon=lugares["results"][0]["geometry"]["location"]["lng"],
                ),
                zoom=12.5,
                pitch=0,
                bearing=0,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
            theme="streamlit",
            height=500,
            width=500,
        )
        st.markdown(
            f"**{len(empresas)} empresas encontradas para '{palavra_chave}' em '{localizacao}'**"
        )

        st.subheader("Resultados")
        st.markdown(
            "Clique em uma empresa para ver mais informações sobre ela. Clique novamente para fechar."
        )
        for empresa in empresas:
            with st.expander(f"{empresa['Nome']}"):
                st.markdown(f"**Endereço:** {empresa['Endereço']}")
                st.markdown(f"**Telefone:** {empresa['Telefone']}")
                st.markdown(f"**Horário de Funcionamento:**")
                st.markdown(empresa["Horário de Funcionamento"])

        st.success(f"{len(empresas)} empresas encontradas.")
        # Mostrar os resultados em uma tabela
        df = pd.DataFrame(empresas)
        st.dataframe(df)

        # Opção para baixar os dados em CSV
        csv = df.to_csv(index=False, encoding="utf-8")
        st.download_button("Baixar resultados em CSV", csv, "empresas.csv", "text/csv")
        # Opção para baixar os dados em JSON
        json_data = json.dumps(empresas, ensure_ascii=False)
        st.download_button("Baixar resultados em JSON", json_data, "empresas.json")
    else:
        st.warning("Nenhuma empresa encontrada para os critérios especificados.")
