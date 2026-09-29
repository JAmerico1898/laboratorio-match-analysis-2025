import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
#from PIL import image
import numpy as np
import pandas as pd
#from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import plotly.express as px
import io
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar
from sklearn.decomposition import PCA
from PIL import Image
#from pandas.plotting import table
import seaborn as sns
from matplotlib import cm
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
from scipy.stats import zscore
from fpdf import FPDF
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# Convert GitHub blob URLs to raw URLs
#def convert_to_raw_url(github_url):
#    return github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

# Dictionary of club images with corrected raw URLs

import streamlit as st

# Dictionary of club image paths
club_image_paths = {
    'Vasco da Gama': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Vasco%20da%20Gama.png",
    'Athletico Paranaense': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Athletico%20Paranaense.png",
    'Atletico GO': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Atletico%20GO.png",
    'Atletico MG': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Atletico%20MG.png",
    'Bahia': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Bahia.png",
    'Botafogo RJ': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Botafogo%20RJ.png",
    'Ceara': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Ceara.png",
    'Corinthians': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Corinthians.png",
    'Criciuma': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Criciuma.png",
    'Cruzeiro': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Cruzeiro.png",
    'Cuiaba': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Cuiaba.png",
    'Flamengo': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Flamengo.png",
    'Fluminense': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Fluminense.png",
    'Fortaleza': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Fortaleza.png",
    'Gremio': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Gremio.png",
    'Internacional': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Internacional.png",
    'Juventude': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Juventude.png",
    'Mirassol': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Mirassol.png",
    'Palmeiras': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Palmeiras.png",
    'Red Bull Bragantino': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Red%20Bull%20Bragantino.png",
    'Santos': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Santos.png",
    'Sao Paulo': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Sao%20Paulo.png",
    'Sport': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Sport.png",
    'Vitoria': "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/4b50b7d4de0678a4ac101386ce1d3299cff23d03/Vitoria.png",
}


# GitHub raw URL
image_url = "https://raw.githubusercontent.com/JAmerico1898/match-oppositionanalysis/2ebc80e41a6adebaefc0c5c6b8cbd876f69b0c1d/Brasileirão.jpg"


st.markdown("<h2 style='text-align: center;'>Desempenho Esportivo dos Clubes</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Série A - 2024</h3>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center;'>(dados Opta)</h6>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="{image_url}" width="150">
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Initialize session state variables if they don’t exist
if "step" not in st.session_state:
    st.session_state.step = "start"  # Initial state
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

# Define button click handlers
def click_club_analysis():
    st.session_state.step = "club_analysis"
    st.session_state.selected_option = None

def click_opponent_analysis():
    st.session_state.step = "opponent_analysis"
    st.session_state.selected_option = None

# Function for the second level options (Clube vs Clube, etc.)
def select_option(option):
    st.session_state.selected_option = option

# Define custom CSS for button styling
st.markdown("""
<style>
    /* Default button style (light gray) */
    .stButton > button {
        background-color: #f0f2f6 !important;
        color: #31333F !important;
        border-color: #d2d6dd !important;
    }
    
    /* Selected button style (red) */
    .selected-button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-color: #FF0000 !important;
    }
    
    /* For second level buttons */
    div[data-testid="stButton"] button.option-selected {
        background-color: #FF4B4B !important;
        color: white !important;
        border-color: #FF0000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Create three columns for the initial choices
col1, col2, col3 = st.columns([4, 1, 4])

# Render buttons based on current state
with col1:
    if st.session_state.step == "club_analysis":
        # Display selected (red) button for club analysis
        st.markdown(
            """
            <div data-testid="stButton">
                <button class="selected-button" style="width:100%; padding:0.5rem; font-weight:400;">
                    Análise do Clube
                </button>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # Display default (gray) button
        st.button("Análise do Clube", key="club_btn", use_container_width=True, on_click=click_club_analysis)

with col3:
    if st.session_state.step == "opponent_analysis":
        # Display selected (red) button for opponent analysis
        st.markdown(
            """
            <div data-testid="stButton">
                <button class="selected-button" style="width:100%; padding:0.5rem; font-weight:400;">
                    Análise do Adversário
                </button>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # Display default (gray) button
        st.button("Análise do Adversário", key="opponent_btn", use_container_width=True, on_click=click_opponent_analysis)
                
# Step 1: Clube Analysis
if st.session_state.step == "club_analysis":
    
    # Custom CSS for better formatting
    st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stAlert {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ff4b4b;
        }
        .info-box {
            background-color: #e6f3ff;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #4B8BF5;
            margin-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        .katex {
            font-size: 1.1em;
        }
    </style>
    """, unsafe_allow_html=True)
    
    
    st.markdown("""
    <div class="info-box">
    <h4>Permite a análise do Clube em 5 dimensões:</h4>
    <p><b>1. Clube vs Clube:</b> Compara o jogo selecionado em relação aos demais jogos da equipe na competição.</p>
    <p><b>2. Clube na Rodada:</b> Compara a partida escolhida da equipe com as demais partidas da mesma rodada na competição. Cada partida aparece duas vezes, destacando ora uma equipe, ora a outra.</p>
    <p><b>3. Clube na Competição:</b> Compara o desempenho da equipe com as demais equipes da competição, por meio de uma média móvel de 5 jogos.</p>
    <p><b>4. 2025 vs 2024:</b> Compara o desempenho da equipe em 2025 com seu desempenho em 2024, por meio de uma média móvel de 5 jogos.</p>
    <p><b>5. Performance:</b> Analisa o DESEMPENHO ESPORTIVO da equipe com base nos (até) últimos 5 jogos disputados em CASA e FORA. 
    A análise destaca as diferentes fases do jogo por meio dos atributos: Defesa, Transição Defensiva, Transição Ofensiva, Ataque e Criação de Chances.
    Além disso, permite ao usuário analisar as 6 métricas em que a equipe mais se destacou positivamente e negativamente.</p>
    <p><b>Nota:</b> Todas as métricas estão normalizadas. os valores representam a diferença da métrica para a média, dividida pelo desvio-padrão.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h5 style='text-align: center;'><br>Digite o nome do Clube!</h5>", unsafe_allow_html=True)

    df = pd.read_csv("performance_team.csv")
    df.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
    
    clubes = ['Vasco da Gama', 'Atletico MG', 'Bahia', 
              'Botafogo RJ', 'Ceara', 'Corinthians', 'Cruzeiro', 
              'Flamengo', 'Fluminense', 'Fortaleza', 'Gremio', 
              'Internacional', 'Juventude', 'Mirassol', 'Palmeiras', 
              'Red Bull Bragantino', 'Santos', 'Sao Paulo', 'Sport', 'Vitoria'
             ]
    
    clube = st.selectbox("", options=clubes)

    st.markdown("<h5 style='text-align: center;'>Escolha sua Opção</h5>", unsafe_allow_html=True)

    # Define button styles for selected/unselected states
    selected_style = """
    <style>
    div[data-testid="stButton"] button.option-selected {
        background-color: #FF4B4B !important;
        color: white !important;
        border-color: #FF0000 !important;
    }
    </style>
    """
    st.markdown(selected_style, unsafe_allow_html=True)

    # Create two rows with two buttons each
    col1, col2, col3 = st.columns([4, 1, 4])
    with col1:
        # Use different button styles based on selection status
        if st.session_state.selected_option == "Clube vs Clube":
            # Create a custom HTML button when selected
            st.markdown(
                f"""
                <div data-testid="stButton">
                    <button class="option-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                        Clube vs Clube
                    </button>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.button("Clube vs Clube", type='secondary', use_container_width=True, 
                    on_click=select_option, args=("Clube vs Clube",))
            
    with col3:
        # Use different button styles based on selection status
        if st.session_state.selected_option == "Clube na Rodada":
            # Create a custom HTML button when selected
            st.markdown(
                f"""
                <div data-testid="stButton">
                    <button class="option-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                        Clube na Rodada
                    </button>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.button("Clube na Rodada", type='secondary', use_container_width=True, 
                    on_click=select_option, args=("Clube na Rodada",))

    col4, col5, col6 = st.columns([4, 1, 4])
    with col4:
        # Use different button styles based on selection status
        if st.session_state.selected_option == "Clube na Competição":
            # Create a custom HTML button when selected
            st.markdown(
                f"""
                <div data-testid="stButton">
                    <button class="option-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                        Clube na Competição
                    </button>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.button("Clube na Competição", type='secondary', use_container_width=True, 
                    on_click=select_option, args=("Clube na Competição",))

    with col6:
        # Use different button styles based on selection status
        if st.session_state.selected_option == "2025 vs 2024":
            # Create a custom HTML button when selected
            st.markdown(
                f"""
                <div data-testid="stButton">
                    <button class="option-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                        2025 vs 2024
                    </button>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.button("2025 vs 2024", type='secondary', use_container_width=True, 
                    on_click=select_option, args=("2025 vs 2024",))

    col7, col8, col9 = st.columns([2.2, 4, 2.2])
    with col8:
        # Use different button styles based on selection status
        if st.session_state.selected_option == "Análise de Performance":
            # Create a custom HTML button when selected
            st.markdown(
                f"""
                <div data-testid="stButton">
                    <button class="option-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                        Análise de Performance
                    </button>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.button("Análise de Performance", type='secondary', use_container_width=True, 
                    on_click=select_option, args=("Análise de Performance",))


    # Handle button selection logic
    if st.session_state.selected_option:
        st.write("---")
        st.markdown(f"<h3 style='text-align: center;'><b>{st.session_state.selected_option}</b></h3>", unsafe_allow_html=True)
        st.write("---")

        # Instructions based on selection
        if st.session_state.selected_option == "Clube vs Clube":
            # Your existing code here
            pass
    
            if clube:
                
                # Select a club
                club_selected = clube

                # Get the image URL for the selected club
                image_url = club_image_paths[club_selected]

                # Center-align and display the image
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center;">
                        <img src="{image_url}" width="150">
                    </div>
                    """,
                    unsafe_allow_html=True
                )                

                #Determinar o Jogo
                df1 = df.loc[(df['clube']==clube)]
                partidas = df1['partida'].unique()
                st.markdown("<h4 style='text-align: center;'><br>Escolha a Partida!</h4>", unsafe_allow_html=True)
                partida = st.selectbox("", options=partidas)
                st.write("---")
                
                if partida:
                    
                    df2 = df1.loc[(df1['partida']==partida)]
                    data = df2['data']
                    data_value = data.iloc[0]

                    #Plotar Primeiro Gráfico - Dispersão das métricas do clube em eixo único:

                    st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Como performou o {clube} comparado às demais partidas na competição?<br>
                        <span style='color: black;'>{partida}</span><br>
                        <span style='color: black;'>{data_value}</span>
                    </h3>
                    """,
                    unsafe_allow_html=True
                    )

                    #Collecting data to plot
                    metrics = df1.iloc[:, np.r_[11:16]].reset_index(drop=True)
                    metrics_defesa = metrics.iloc[:, 0].tolist()
                    metrics_transição_defensiva = metrics.iloc[:, 1].tolist()
                    metrics_transição_ofensiva = metrics.iloc[:, 2].tolist()
                    metrics_ataque = metrics.iloc[:, 3].tolist()
                    metrics_criação_chances = metrics.iloc[:, 4].tolist()
                    metrics_y = [0] * len(metrics_defesa)

                    # The specific data point you want to highlight
                    highlight = df1[(df1['clube']==clube)&(df1['partida']==partida)]
                    highlight = highlight.iloc[:, np.r_[11:16]].reset_index(drop=True)
                    highlight_defesa = highlight.iloc[:, 0].tolist()
                    highlight_transição_defensiva = highlight.iloc[:, 1].tolist()
                    highlight_transição_ofensiva = highlight.iloc[:, 2].tolist()
                    highlight_ataque = highlight.iloc[:, 3].tolist()
                    highlight_criação_chances = highlight.iloc[:, 4].tolist()
                    highlight_y = 0

                    # Computing the selected game specific values
                    highlight_defesa_value = pd.DataFrame(highlight_defesa).reset_index(drop=True)
                    highlight_transição_defensiva_value = pd.DataFrame(highlight_transição_defensiva).reset_index(drop=True)
                    highlight_transição_ofensiva_value = pd.DataFrame(highlight_transição_ofensiva).reset_index(drop=True)
                    highlight_ataque_value = pd.DataFrame(highlight_ataque).reset_index(drop=True)
                    highlight_criação_chances_value = pd.DataFrame(highlight_criação_chances).reset_index(drop=True)

                    highlight_defesa_value = highlight_defesa_value.iat[0,0]
                    highlight_transição_defensiva_value = highlight_transição_defensiva_value.iat[0,0]
                    highlight_transição_ofensiva_value = highlight_transição_ofensiva_value.iat[0,0]
                    highlight_ataque_value = highlight_ataque_value.iat[0,0]
                    highlight_criação_chances_value = highlight_criação_chances_value.iat[0,0]

                    # Computing the min and max value across all lists using a generator expression
                    min_value = min(min(lst) for lst in [metrics_defesa, metrics_transição_defensiva, 
                                                        metrics_transição_ofensiva, metrics_ataque, 
                                                        metrics_criação_chances])
                    min_value = min_value - 0.1
                    max_value = max(max(lst) for lst in [metrics_defesa, metrics_transição_defensiva, 
                                                        metrics_transição_ofensiva, metrics_ataque, 
                                                        metrics_criação_chances])
                    max_value = max_value + 0.1

                    # Create two subplots vertically aligned with separate x-axes
                    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
                    #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                    # Building the Extended Title"
                    rows_count = df1.shape[0]
                    
                    # Function to determine game's rank in attribute in league
                    def get_partida_rank(partida, temporada, column_name, dataframe):
                        # Filter the dataframe for the specified Temporada
                        filtered_df = dataframe[dataframe['Temporada'] == 2024]
                        
                        # Rank partidas based on the specified column in descending order
                        filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                        
                        # Find the rank of the specified partida
                        partida_row = filtered_df[filtered_df['partida'] == partida]
                        if not partida_row.empty:
                            return int(partida_row['Rank'].iloc[0])
                        else:
                            return None

                    # Determining partida's rank in attribute in league
                    defesa_ranking_value = (get_partida_rank(partida, 2024, "Defesa", df1))

                    # Data to plot
                    output_str = f"({defesa_ranking_value}/{rows_count})"
                    full_title_defesa = f"Defesa {output_str} {highlight_defesa_value}"

                    # Building the Extended Title"
                    # Determining partida's rank in attribute in league
                    transição_defensiva_ranking_value = (get_partida_rank(partida, 2024, "Transição defensiva", df1))

                    output_str = f"({transição_defensiva_ranking_value}/{rows_count})"
                    full_title_transição_defensiva = f"Transição defensiva {output_str} {highlight_transição_defensiva_value}"
                    
                    # Building the Extended Title"
                    # Determining partida's rank in attribute in league
                    transição_ofensiva_ranking_value = (get_partida_rank(partida, 2024, "Transição ofensiva", df1))

                    output_str = f"({transição_ofensiva_ranking_value}/{rows_count})"
                    full_title_transição_ofensiva = f"Transição ofensiva {output_str} {highlight_transição_ofensiva_value}"

                    # Building the Extended Title"
                    # Determining partida's rank in attribute in league
                    ataque_ranking_value = (get_partida_rank(partida, 2024, "Ataque", df1))#.astype(int)

                    output_str = f"({ataque_ranking_value}/{rows_count})"
                    full_title_ataque = f"Ataque {output_str} {highlight_ataque_value}"

                    # Building the Extended Title"
                    # Determining partida's rank in attribute in league
                    criação_chances_ranking_value = (get_partida_rank(partida, 2024, "Criação de chances", df1))#.astype(int)

                    output_str = f"({criação_chances_ranking_value}/{rows_count})"
                    full_title_criação_chances = f"Criação de chances {output_str} {highlight_criação_chances_value}"

                    ##############################################################################################################
                    ##############################################################################################################
                    ##############################################################################################################
                    ##############################################################################################################
                    #From Claude version2

                    def calculate_ranks(values):
                        """Calculate ranks for a given metric, with highest values getting rank 1"""
                        return pd.Series(values).rank(ascending=False).astype(int).tolist()

                    def prepare_data(tabela_a, metrics_cols):
                        """Prepare the metrics data dictionary with all required data"""
                        metrics_data = {}
                        
                        for col in metrics_cols:
                            # Store the metric values
                            metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                            # Calculate and store ranks
                            metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                            # Store partida names
                            metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        
                        return metrics_data

                    def create_partida_attributes_plot(tabela_a, partida, min_value, max_value):
                        """
                        Create an interactive plot showing partida attributes with hover information
                        
                        Parameters:
                        tabela_a (pd.DataFrame): DataFrame containing all partida data
                        partida (str): Name of the partida to highlight
                        min_value (float): Minimum value for x-axis
                        max_value (float): Maximum value for x-axis
                        """
                        # List of metrics to plot
                        metrics_list = [
                            'Defesa', 'Transição defensiva', 'Transição ofensiva',
                            'Ataque','Criação de chances'
                        ]
                        
                        # Prepare all the data
                        metrics_data = prepare_data(tabela_a, metrics_list)
                        
                        # Calculate highlight data
                        highlight_data = {
                            f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            for metric in metrics_list
                        }
                        
                        # Calculate highlight ranks
                        highlight_ranks = {
                            metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                            for metric in metrics_list
                        }
                        
                        # Total number of partidas
                        total_partidas = len(tabela_a)
                        
                        # Create subplots
                        fig = make_subplots(
                            rows=7, 
                            cols=1,
                            subplot_titles=[
                                f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_partidas}) {highlight_data[f'highlight_{metric}']:.2f}"
                                for metric in metrics_list
                            ],
                            vertical_spacing=0.05
                        )

                        # Update subplot titles font size and color
                        for i in fig['layout']['annotations']:
                            i['font'] = dict(size=17, color='black')

                        # Add traces for each metric
                        for idx, metric in enumerate(metrics_list, 1):
                            # Add scatter plot for all partidas
                            fig.add_trace(
                                go.Scatter(
                                    x=metrics_data[f'metrics_{metric}'],
                                    y=[0] * len(metrics_data[f'metrics_{metric}']),
                                    mode='markers',
                                    name = f"Demais partidas do {clube}</span>",
                                    marker=dict(color='deepskyblue', size=8),
                                    text=[f"{rank}/{total_partidas}" for rank in metrics_data[f'ranks_{metric}']],
                                    customdata=metrics_data[f'partida_names_{metric}'],
                                    hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                    showlegend=True if idx == 1 else False
                                ),
                                row=idx, 
                                col=1
                            )
                            
                            # Add highlighted partida point
                            fig.add_trace(
                                go.Scatter(
                                    x=[highlight_data[f'highlight_{metric}']],
                                    y=[0],
                                    mode='markers',
                                    name=partida,
                                    marker=dict(color='blue', size=12),
                                    hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_partidas}<br>Value: %{{x:.2f}}<extra></extra>',
                                    showlegend=True if idx == 1 else False
                                ),
                                row=idx, 
                                col=1
                            )

                        # Get the total number of metrics (subplots)
                        n_metrics = len(metrics_list)

                        # Update layout for each subplot
                        for i in range(1, n_metrics + 1):
                            if i == n_metrics:  # Only for the last subplot
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='black',
                                    zerolinewidth=1,
                                    showline=False,
                                    ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                    tickvals=[min_value/2, 0, max_value/2],
                                    tickmode='array',
                                    ticks="outside",
                                    ticklen=2,
                                    tickfont=dict(size=16),
                                    tickangle=0,
                                    side='bottom',
                                    automargin=False,
                                    row=i, 
                                    col=1
                                )
                                # Adjust layout for the last subplot
                                fig.update_layout(
                                    xaxis_tickfont_family="Arial",
                                    margin=dict(b=0)  # Reduce bottom margin
                                )
                            else:  # For all other subplots
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='grey',
                                    zerolinewidth=1,
                                    showline=False,
                                    showticklabels=False,  # Hide tick labels
                                    row=i, 
                                    col=1
                                )  # Reduces space between axis and labels

                            # Update layout for the entire figure
                            fig.update_yaxes(
                                showticklabels=False,
                                showgrid=False,
                                showline=False,
                                row=i, 
                                col=1
                            )

                        # Update layout for the entire figure
                        fig.update_layout(
                            height=650,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=+0.02,
                                xanchor="center",
                                x=0.5,
                                font=dict(size=16)
                            ),
                            margin=dict(t=100)
                        )

                        # Add x-axis label at the bottom
                        fig.add_annotation(
                            text="Desvio-padrão",
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.15,
                            showarrow=False,
                            font=dict(size=16, color='black')
                        )

                        return fig

                    # Calculate min and max values with some padding
                    min_value_test = min([
                    min(metrics_defesa), min(metrics_transição_defensiva), min(metrics_transição_ofensiva),
                    min(metrics_ataque), min(metrics_criação_chances)
                    ])  # Add padding of 0.5

                    max_value_test = max([
                    max(metrics_defesa), max(metrics_transição_defensiva), max(metrics_transição_ofensiva),
                    max(metrics_ataque), max(metrics_criação_chances)
                    ])  # Add padding of 0.5

                    min_value = -max(abs(min_value_test), max_value_test) -0.03
                    max_value = -min_value

                    # Create the plot
                    fig = create_partida_attributes_plot(
                        tabela_a=df1,  # Your main dataframe
                        partida=partida,  # Name of partida to highlight
                        min_value= min_value,  # Minimum value for x-axis
                        max_value= max_value    # Maximum value for x-axis
                    )

                    st.plotly_chart(fig, use_container_width=True)

                ##################################################################################################################### 
                #####################################################################################################################
                #################################################################################################################################
                #################################################################################################################################
                #################################################################################################################################

                    #INSERIR ANÁLISE POR ATRIBUTO

                    atributos = ["Defesa", "Transição defensiva", "Transição ofensiva", 
                                    "Ataque", "Criação de chances"]

                    st.markdown("---")
                    st.markdown(
                        "<h3 style='text-align: center; color:black; '>Se quiser aprofundar, escolha o Atributo</h3>",
                        unsafe_allow_html=True
                    )
                    
                    atributo = st.selectbox("", options=atributos, index = None, placeholder = "Escolha o Atributo!")
                    if atributo == ("Defesa"):
                        
                        #Plotar Primeiro Gráfico - Dispersão das partidas do mesmo clube em eixo único:

                        # Dynamically create the HTML string with the 'partida' variable
                        title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h4 style='text-align: center; color: deepskyblue;'>A Defesa do {clube}<br>em relação aos demais jogos do clube na competição</h4>",
                                    unsafe_allow_html=True
                                    )
                        st.markdown(title_html, unsafe_allow_html=True)
                        st.markdown("---")

                        attribute_chart_z = df1
                        # Collecting data
                        attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['clube']==clube)]
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[17:25]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_participação_7 = metrics.iloc[:, 6].tolist()
                        metrics_participação_8 = metrics.iloc[:, 7].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                        highlight = highlight.iloc[:, np.r_[17:25]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_participação_7 = highlight.iloc[:, 6].tolist()
                        highlight_participação_8 = highlight.iloc[:, 7].tolist()
                        highlight_y = 0

                        # Computing the selected player specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                        highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                        highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                        highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                        highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6, 
                                                            metrics_participação_7, metrics_participação_8])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6, 
                                                            metrics_participação_7, metrics_participação_8])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine partida's rank in attribute in league
                        def get_partida_rank(partida, temporada, column_name, dataframe):
                            # Filter the dataframe for the specified Temporada
                            filtered_df = dataframe[dataframe['Temporada'] == 2024]
                            
                            # Rank partidas based on the specified column in descending order
                            filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified partida
                            partida_row = filtered_df[filtered_df['partida'] == partida]
                            if not partida_row.empty:
                                return int(partida_row['Rank'].iloc[0])
                            else:
                                return None

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_1_ranking_value = (get_partida_rank(partida, 2024, "PPDA", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"PPDA {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_2_ranking_value = (get_partida_rank(partida, 2024, "Intensidade defensiva", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"Intensidade defensiva {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_3_ranking_value = (get_partida_rank(partida, 2024, "Duelos defensivos vencidos (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"Duelos defensivos vencidos (%) {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_4_ranking_value = (get_partida_rank(partida, 2024, "Altura defensiva (m)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"Altura defensiva (m) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_5_ranking_value = (get_partida_rank(partida, 2024, "Velocidade do passe adversário", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"Velocidade do passe adversário {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário no último terço (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"Entradas do adversário no último terço (%) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_7_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário na área (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_7_ranking_value}/{rows_count})"
                        full_title_participação_7 = f"Entradas do adversário na área (%) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_8_ranking_value = (get_partida_rank(partida, 2024, "xT adversário", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_8_ranking_value}/{rows_count})"
                        full_title_participação_8 = f"xT adversário {output_str} {highlight_participação_4_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['partida'].tolist()
                            
                            return metrics_data

                        def create_player_attributes_plot(tabela_a, partida, min_value, max_value):
                            """
                            Create an interactive plot showing player attributes with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            partida (str): Name of the player to highlight
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            metrics_list = ["PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                    "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                    "Entradas do adversário na área (%)", "xT adversário"
                            ]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of players
                            total_players = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=8, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Add scatter plot for all players
                                fig.add_trace(
                                    go.Scatter(
                                        x=metrics_data[f'metrics_{metric}'],
                                        y=[0] * len(metrics_data[f'metrics_{metric}']),
                                        mode='markers',
                                        name = f'Demais partidas do {clube}',
                                        marker=dict(color='deepskyblue', size=8),
                                        text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                        customdata=metrics_data[f'player_names_{metric}'],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=partida,
                                        marker=dict(color='blue', size=12),
                                        hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )

                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=800,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.25,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.16,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6),
                        min(metrics_participação_7), min(metrics_participação_8),
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6),
                        max(metrics_participação_7), max(metrics_participação_8),
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_player_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            partida=partida,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.write("---")

                        st.markdown("""
                                    ### DEFESA - métricas
                                - **PPDA**: “Passes por Ação Defensiva”. Mede a intensidade da pressão defensiva calculando o número de passes permitidos por um time antes de tentar uma ação defensiva. Quanto menor o PPDA, maior a intensidade da pressão defensiva. A análise é limitada aos 60% iniciais do campo do oponente.
                                - **Intensidade defensiva**: Número de duelos defensivos, duelos livres, interceptações, desarmes e faltas quando a posse é do adversário, ajustado pela posse do adversário. Mede quão ativamente um time se envolve em ações defensivas em relação à quantidade de tempo que o adversário tem a bola.
                                - **Duelos defensivos vencidos (%)**: Porcentagem de duelos defensivos no solo que interrompem com sucesso a progressão de um oponente ou recuperam a posse de bola. Mede a eficácia de um time em desafios defensivos no solo.
                                - **Altura defensiva (m)**: Altura média no campo, medida em metros, das ações defensivas de um time.
                                - **Velocidade do passe do adversário**: Velocidade com que o time adversário move a bola por meio de passes. Isso pode ser influenciado pelo estilo de jogo do adversário, como ataque direto ou futebol baseado em posse de bola.
                                - **Entradas do adversário no último terço (%)**: Porcentagem de posses do time adversário que progridem com sucesso para o terço final do campo. Informa a efetividade do adversário em penetrar na configuração defensiva e avançar em direção ao gol.
                                - **Entradas do adversário na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário. Informa a efetividade do adversário em penetrar na configuração defensiva e criar oportunidades de gol.
                                - **xT Adversário**: Ameaça esperada baseada em ações (xT) por 100 passes bem-sucedidos do adversário originados de dentro da área defensiva da equipe. 
                                """)

                        #####################################################################################################################
                        #####################################################################################################################
                        ##################################################################################################################### 
                        #####################################################################################################################
                        
                    elif atributo == ("Transição defensiva"):
                        
                        #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                        # Dynamically create the HTML string with the 'partida' variable
                        title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>A Transição Defensiva em relação aos demais jogos do {clube}</h3>",
                                    unsafe_allow_html=True
                                    )
                        st.markdown(title_html, unsafe_allow_html=True)
                        st.write("---")
                        attribute_chart_z = df1
                        # Collecting data
                        attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['clube']==clube)]
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[25:33]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_participação_7 = metrics.iloc[:, 6].tolist()
                        metrics_participação_8 = metrics.iloc[:, 7].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                        highlight = highlight.iloc[:, np.r_[25:33]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_participação_7 = highlight.iloc[:, 6].tolist()
                        highlight_participação_8 = highlight.iloc[:, 7].tolist()
                        highlight_y = 0

                        # Computing the selected player specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                        highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                        highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                        highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                        highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6,
                                                            metrics_participação_7, metrics_participação_8 
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6,
                                                            metrics_participação_7, metrics_participação_8
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9) = plt.subplots(9, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine partida's rank in attribute in league
                        def get_partida_rank(partida, temporada, column_name, dataframe):
                            # Filter the dataframe for the specified Temporada
                            filtered_df = dataframe[dataframe['Temporada'] == 2024]
                            
                            # Rank partidas based on the specified column in descending order
                            filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified partida
                            partida_row = filtered_df[filtered_df['partida'] == partida]
                            if not partida_row.empty:
                                return int(partida_row['Rank'].iloc[0])
                            else:
                                return None

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_1_ranking_value = (get_partida_rank(partida, 2024, "Perdas de posse na linha baixa", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"Perdas de posse na linha baixa {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_2_ranking_value = (get_partida_rank(partida, 2024, "Altura da perda de posse (m)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"Altura da perda de posse (m) {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_3_ranking_value = (get_partida_rank(partida, 2024, "Recuperações de posse em 5s (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"Recuperações de posse em 5s (%) {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_4_ranking_value = (get_partida_rank(partida, 2024, "Tempo médio ação defensiva (s)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"Tempo médio ação defensiva (s) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_5_ranking_value = (get_partida_rank(partida, 2024, "Tempo médio para recuperação de posse (s)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"Tempo médio para recuperação de posse (s) {output_str} {highlight_participação_5_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário no último terço em 10s da recuperação da posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"Entradas do adversário no último terço em 10s da recuperação da posse {output_str} {highlight_participação_6_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_7_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário na área em 10s da recuperação da posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_7_ranking_value}/{rows_count})"
                        full_title_participação_7 = f"Entradas do adversário na área em 10s da recuperação da posse {output_str} {highlight_participação_7_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_8_ranking_value = (get_partida_rank(partida, 2024, "xG do adversário em 10s da recuperação da posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_8_ranking_value}/{rows_count})"
                        full_title_participação_8 = f"xG do adversário em 10s da recuperação da posse {output_str} {highlight_participação_8_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['partida'].tolist()
                            
                            return metrics_data

                        def create_player_attributes_plot(tabela_a, partida, min_value, max_value):
                            """
                            Create an interactive plot showing player attributes with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            partida (str): Name of the player to highlight
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            metrics_list = ["Perdas de posse na linha baixa",
                                        "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                        "Tempo médio para recuperação de posse (s)",
                                        "Entradas do adversário no último terço em 10s da recuperação da posse",
                                        "Entradas do adversário na área em 10s da recuperação da posse", 
                                        "xG do adversário em 10s da recuperação da posse"
                            ]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of players
                            total_players = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=8, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Add scatter plot for all players
                                fig.add_trace(
                                    go.Scatter(
                                        x=metrics_data[f'metrics_{metric}'],
                                        y=[0] * len(metrics_data[f'metrics_{metric}']),
                                        mode='markers',
                                        name = f'Demais partidas do {clube}',
                                        marker=dict(color='deepskyblue', size=8),
                                        text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                        customdata=metrics_data[f'player_names_{metric}'],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=partida,
                                        marker=dict(color='blue', size=12),
                                        hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )

                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=800,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.25,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.15,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6),
                        min(metrics_participação_7), min(metrics_participação_8)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6),
                        max(metrics_participação_7), max(metrics_participação_8)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_player_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            partida=partida,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.write("---")
                        st.markdown("""
                                    ### TRANSIÇÃO DEFENSIVA - métricas
                                - **Perda de posse na linha baixa**: Perdas de posse devido a passes errados (Turnovers), erros de domínio ou duelos ofensivos perdidos, nos 40% defensivos da equipe, ajustados pela posse.Turnovers elevados indicam a frequência com que um time perde a posse em áreas perigosas.
                                - **Altura da perda de posse (m)**: Altura média no campo, medida em metros, onde ocorrem perdas de posse.
                                - **Recuperações de posse em 5s %**: Porcentagem de recuperações de bola que ocorrem em até 5 segundos após a perda da posse. Destaca a capacidade de um time recuperar rapidamente o controle da bola após perdê-la, geralmente por meio de estratégias eficazes de pressão e contrapressão.
                                - **Tempo médio ação defensiva (s)**: Tempo que o time leva para executar uma ação defensiva, após perder a posse de bola. Reflete a capacidade de resposta e o tempo de reação de um time em situações defensivas.
                                - **Tempo médio para recuperação de posse (s)**: Tempo que o time leva para recuperar a posse da bola após perdê-la.
                                - **Entradas do adversário no último terço em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso no último terço em até 10 segundos após a recuperação da posse. Informa a capacidade do adversário em penetrar na configuração defensiva e avançar em direção ao gol.
                                - **Entradas do adversário na área em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso na área em até 10 segundos após a recuperação da posse. Informa a efetividade do adversário em penetrar na configuração defensiva e criar potenciais oportunidades gol.
                                - **xG do adversário em 10s da recuperação da posse**: Gols esperados não-pênaltis (xG) acumulados dos chutes do adversário que ocorrem dentro de 10 segundos após a recuperação da posse de bola. Informa a qualidade das chances de gol que o adversário cria rapidamente após recuperar a bola.
                                """)

                        #################################################################################################################################
                        #################################################################################################################################
                        ##################################################################################################################### 
                        #####################################################################################################################

                    elif atributo == ("Transição ofensiva"):
                        
                        #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                        # Dynamically create the HTML string with the 'partida' variable
                        title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>A Transição Ofensiva em relação aos demais jogos do {clube}</h3>",
                                    unsafe_allow_html=True
                                    )
                        st.markdown(title_html, unsafe_allow_html=True)
                        st.write("---")

                        attribute_chart_z = df1
                        # Collecting data
                        attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['clube']==clube)]
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[33:41]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_participação_7 = metrics.iloc[:, 6].tolist()
                        metrics_participação_8 = metrics.iloc[:, 7].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                        highlight = highlight.iloc[:, np.r_[33:41]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_participação_7 = highlight.iloc[:, 6].tolist()
                        highlight_participação_8 = highlight.iloc[:, 7].tolist()
                        highlight_y = 0

                        # Computing the selected player specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                        highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                        highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                        highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                        highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6, 
                                                            metrics_participação_7, metrics_participação_8])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6, 
                                                            metrics_participação_7, metrics_participação_8])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine partida's rank in attribute in league
                        def get_partida_rank(partida, temporada, column_name, dataframe):
                            # Filter the dataframe for the specified Temporada
                            filtered_df = dataframe[dataframe['Temporada'] == 2024]
                            
                            # Rank partidas based on the specified column in descending order
                            filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified partida
                            partida_row = filtered_df[filtered_df['partida'] == partida]
                            if not partida_row.empty:
                                return int(partida_row['Rank'].iloc[0])
                            else:
                                return None

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_1_ranking_value = (get_partida_rank(partida, 2024, "Recuperações de posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"Recuperações de posse {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_2_ranking_value = (get_partida_rank(partida, 2024, "Altura da recuperação de posse (m)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"Altura da recuperação de posse (m) {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_3_ranking_value = (get_partida_rank(partida, 2024, "Posse mantida em 5s", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"Posse mantida em 5s {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_4_ranking_value = (get_partida_rank(partida, 2024, "Posse mantida em 5s (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"Posse mantida em 5s (%) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_5_ranking_value = (get_partida_rank(partida, 2024, "Entradas no último terço em 10s", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"Entradas no último terço em 10s {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas na área em 10s", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"Entradas na área em 10s {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_7_ranking_value = (get_partida_rank(partida, 2024, "xG em 10s da recuperação da posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_7_ranking_value}/{rows_count})"
                        full_title_participação_7 = f"xG em 10s da recuperação da posse {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_8_ranking_value = (get_partida_rank(partida, 2024, "xT em 10s da recuperação da posse", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_8_ranking_value}/{rows_count})"
                        full_title_participação_8 = f"xT em 10s da recuperação da posse {output_str} {highlight_participação_4_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['partida'].tolist()
                            
                            return metrics_data

                        def create_player_attributes_plot(tabela_a, partida, min_value, max_value):
                            """
                            Create an interactive plot showing player attributes with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            partida (str): Name of the player to highlight
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            metrics_list = ["Recuperações de posse", "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                    "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                    "xT em 10s da recuperação da posse"
                            ]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of players
                            total_players = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=9, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Add scatter plot for all players
                                fig.add_trace(
                                    go.Scatter(
                                        x=metrics_data[f'metrics_{metric}'],
                                        y=[0] * len(metrics_data[f'metrics_{metric}']),
                                        mode='markers',
                                        name = f'Demais partidas do {clube}',
                                        marker=dict(color='deepskyblue', size=8),
                                        text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                        customdata=metrics_data[f'player_names_{metric}'],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=partida,
                                        marker=dict(color='blue', size=12),
                                        hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )

                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=800,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.06,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6),
                        min(metrics_participação_7), min(metrics_participação_8),
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6),
                        max(metrics_participação_7), max(metrics_participação_8),
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_player_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            partida=partida,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.write("---")
                        st.markdown("""
                                    ### TRANSIÇÃO OFENSIVA - métricas
                                - **Recuperações de posse**: Número de vezes que um time recupera a posse da bola após perdê-la.
                                - **Altura da recuperação de posse (m)**: Altura média no campo, medida em metros, onde ocorrem as recuperações da posse.
                                - **Posse mantida em 5s**: Número de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após ganhar o controle inicialmente. Informa sobre a capacidade da equipe reter a posse sob pressão e evitar turnovers imediatos. É um indicador de controle de bola eficaz e compostura na manutenção da posse.
                                - **Posse mantida em 5s (%)**: Porcentagem de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após retomar o controle inicialmente. Informa sobre a efetividade da equipe reter a posse sob pressão e evitar turnovers imediatos. É um indicador de controle de bola eficaz e compostura na manutenção da posse.
                                - **Entradas no último terço em 10s**: Número de vezes que um time move a bola com sucesso para o terço final do campo dentro de 10 segundos após recuperar a posse. Indica a rapidez da equipe em criar potenciais oportunidades de gol após recuperar a bola.
                                - **Entradas na área em 10s**: Número de vezes que uma equipe move a bola com sucesso para a área do adversário dentro de 10 segundos após recuperar a posse. Informa sobre a eficácia da transição da defesa para o ataque e indica a rapidez da equipe em criar potenciais oportunidades na área após recuperar a bola.
                                - **xG em 10s da recuperação da posse**: Gols esperados (não-pênaltis) acumulados (xG) de chutes feitos dentro de 10 segundos após uma equipe recuperar a posse. Informa sobre a qualidade das chances de pontuação criadas rapidamente após recuperar a bola.
                                - **xT em 10s da recuperação da posse**: Ameaça esperada acumulada (xT) gerada por ações dentro de 10 segundos após um time recuperar a posse de bola. Informa sobre o perigo criado rapidamente após recuperar a bola. Fornece insights sobre a eficácia de contra-ataque de um time.
                                """)

                        #####################################################################################################################
                        #####################################################################################################################
                        ##################################################################################################################### 
                        #####################################################################################################################

                    elif atributo == ("Ataque"):
                        
                        #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                        # Dynamically create the HTML string with the 'partida' variable
                        title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>O Ataque em relação aos demais jogos do {clube}</h3>",
                                    unsafe_allow_html=True
                                    )
                        st.markdown(title_html, unsafe_allow_html=True)
                        st.write("---")

                        attribute_chart_z = df1
                        # Collecting data
                        attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['clube']==clube)]
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[41:47]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                        highlight = highlight.iloc[:, np.r_[41:47]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_y = 0

                        # Computing the selected player specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine partida's rank in attribute in league
                        def get_partida_rank(partida, temporada, column_name, dataframe):
                            # Filter the dataframe for the specified Temporada
                            filtered_df = dataframe[dataframe['Temporada'] == 2024]
                            
                            # Rank partidas based on the specified column in descending order
                            filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified partida
                            partida_row = filtered_df[filtered_df['partida'] == partida]
                            if not partida_row.empty:
                                return int(partida_row['Rank'].iloc[0])
                            else:
                                return None

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_1_ranking_value = (get_partida_rank(partida, 2024, "Field tilt (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"Field tilt (%) {output_str} {highlight_participação_1_value}"
                        
                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_2_ranking_value = (get_partida_rank(partida, 2024, "Bola longa (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"Bola longa (%) {output_str} {highlight_participação_2_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_3_ranking_value = (get_partida_rank(partida, 2024, "Velocidade do passe", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"Velocidade do passe {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_4_ranking_value = (get_partida_rank(partida, 2024, "Entradas no último terço (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"Entradas no último terço (%) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_5_ranking_value = (get_partida_rank(partida, 2024, "Entradas na área (%)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"Entradas na área (%) {output_str} {highlight_participação_5_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_6_ranking_value = (get_partida_rank(partida, 2024, "xT (Ameaça esperada)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"xT (Ameaça esperada) {output_str} {highlight_participação_6_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['partida'].tolist()
                            
                            return metrics_data

                        def create_player_attributes_plot(tabela_a, partida, min_value, max_value):
                            """
                            Create an interactive plot showing player attributes with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            partida (str): Name of the player to highlight
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            metrics_list = ["Field tilt (%)", "Bola longa (%)", 
                                    "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                    "xT (Ameaça esperada)"
                            ]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of players
                            total_players = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=9, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Add scatter plot for all players
                                fig.add_trace(
                                    go.Scatter(
                                        x=metrics_data[f'metrics_{metric}'],
                                        y=[0] * len(metrics_data[f'metrics_{metric}']),
                                        mode='markers',
                                        name = f'Demais partidas do {clube}',
                                        marker=dict(color='deepskyblue', size=8),
                                        text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                        customdata=metrics_data[f'player_names_{metric}'],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=partida,
                                        marker=dict(color='blue', size=12),
                                        hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )

                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=800,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=0.16,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=0.23,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_player_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            partida=partida,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.write("---")
                        st.markdown("""
                                    ### ATAQUE - métricas
                                - **Field tilt (%)**: Porcentagem de tempo que a bola está na metade de ataque do campo para um time específico em comparação com seu adversário. Ajuda a entender qual time é mais dominante em termos de controle territorial e pressão de ataque durante uma partida.
                                - **Bola longa %**: Porcentagem de passes que são bolas longas, que são definidas como passes que percorrem uma distância significativa para chegar aos atacantes rapidamente. Informa sobre o estilo de jogo de uma equipe, indicando uma preferência por uma abordagem mais direta para avançar a bola no campo.
                                - **Velocidade do passe**: Velocidade com que a equipe move a bola por meio de passes. Uma velocidade de passe mais alta indicam uma estratégia para interromper a organização defensiva do adversário e criar oportunidades de gol.
                                - **Entradas no último terço (%)**: Porcentagem de posses da equipe que progridem com sucesso para o terço final do campo. Informa a efetividade da equipeem penetrar na configuração defensiva e avançar em direção ao gol.
                                - **Entradas na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário. Informa a efetividade da equipeem penetrar na configuração defensiva e criar oportunidades de gol.
                                - **xT (ameaça esperada)**: Mede o quanto as ações com bola contribuem para a chance de um time marcar. Informa sobre o o impacto potencial e o perigo criado pelas ações da equipe ao avançar a bola e criar oportunidades de gol.
                                """)

                        #####################################################################################################################
                        #####################################################################################################################
                        ##################################################################################################################### 
                        #####################################################################################################################

                    elif atributo == ("Criação de chances"):
                        
                        #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                        # Dynamically create the HTML string with the 'partida' variable
                        title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>Criação de Chances em relação aos demais jogos do {clube}</h3>",
                                    unsafe_allow_html=True
                                    )
                        st.markdown(title_html, unsafe_allow_html=True)
                        st.write("---")

                        attribute_chart_z = df1
                        # Collecting data
                        attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['clube']==clube)]
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[47:54]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_participação_7 = metrics.iloc[:, 6].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                        highlight = highlight.iloc[:, np.r_[47:54]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_participação_7 = highlight.iloc[:, 6].tolist()
                        highlight_y = 0

                        # Computing the selected player specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                        highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                        highlight_participação_7_value = highlight_participação_7_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6,
                                                            metrics_participação_7 
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6,
                                                            metrics_participação_7
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine partida's rank in attribute in league
                        def get_partida_rank(partida, temporada, column_name, dataframe):
                            # Filter the dataframe for the specified Temporada
                            filtered_df = dataframe[dataframe['Temporada'] == 2024]
                            
                            # Rank partidas based on the specified column in descending order
                            filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified partida
                            partida_row = filtered_df[filtered_df['partida'] == partida]
                            if not partida_row.empty:
                                return int(partida_row['Rank'].iloc[0])
                            else:
                                return None

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_1_ranking_value = (get_partida_rank(partida, 2024, "Toques na área", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"Toques na área {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_2_ranking_value = (get_partida_rank(partida, 2024, "Finalizações (pEntrada na área, %)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"Finalizações (pEntrada na área, %) {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_3_ranking_value = (get_partida_rank(partida, 2024, "Finalizações (exceto pênaltis)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"Finalizações (exceto pênaltis) {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_4_ranking_value = (get_partida_rank(partida, 2024, "Grandes oportunidades", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"Grandes oportunidades {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_5_ranking_value = (get_partida_rank(partida, 2024, "xG (exceto pênaltis)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"xG (exceto pênaltis) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_6_ranking_value = (get_partida_rank(partida, 2024, "Gols (exceto pênaltis)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"Gols (exceto pênaltis) {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining partida's rank in attribute in league
                        participação_7_ranking_value = (get_partida_rank(partida, 2024, "xG (pFinalização)", attribute_chart_z1))

                        # Data to plot
                        output_str = f"({participação_7_ranking_value}/{rows_count})"
                        full_title_participação_7 = f"xG (pFinalização) {output_str} {highlight_participação_4_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['partida'].tolist()
                            
                            return metrics_data

                        def create_player_attributes_plot(tabela_a, partida, min_value, max_value):
                            """
                            Create an interactive plot showing player attributes with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            partida (str): Name of the player to highlight
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            metrics_list = ["Toques na área", "Finalizações (pEntrada na área, %)",
                                    "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                    "Gols (exceto pênaltis)", "xG (pFinalização)"
                            ]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of players
                            total_players = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=9, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Add scatter plot for all players
                                fig.add_trace(
                                    go.Scatter(
                                        x=metrics_data[f'metrics_{metric}'],
                                        y=[0] * len(metrics_data[f'metrics_{metric}']),
                                        mode='markers',
                                        name = f'Demais partidas do {clube}',
                                        marker=dict(color='deepskyblue', size=8),
                                        text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                        customdata=metrics_data[f'player_names_{metric}'],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=partida,
                                        marker=dict(color='blue', size=12),
                                        hovertemplate=f'{partida}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )

                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=700,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=0.0,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=0.09,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6),
                        min(metrics_participação_7)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6),
                        max(metrics_participação_7)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_player_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            partida=partida,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.write("---")
                        st.markdown("""
                                    ### CRIAÇÃO DE CHANCES - métricas
                                - **Toques na área**: Número de vezes que a equipe faz contato com a bola dentro da área do adversário. Informa sobre a atividade da equipe na zona de ataque mais perigosa do campo.
                                - **Finalizações (pEntrada na área, %)**: Porcentagem de vezes que uma entrada na área do adversário resulta em um chute. Indica com que frequência a penetração na área leva a uma tentativa de gol.
                                - **Finalizações (exceto pênaltis)**: Número total de finalizações da equipe, excluindo pênaltis. Informa sobre o desempenho da equipe em finalizações, exceto pênaltis.
                                - **Grandes oportunidades**: Número de finalizações em posições ou situações com alta probabilidade de gol. Finalizações em geral próximas ao gol, com menos defensores no caminho e de posições mais centrais.
                                - **xG (exceto pênaltis)**: Gols esperados, excluindo pênaltis. Quantifica a qualidade das chances de gol que um time tem, excluindo pênaltis. Sugere quantos gols o time deve marcar com base na qualidade de suas finalizações, exceto pênaltis.
                                - **Gols (exceto pênaltis)**: Número total de gols que a equipe marca, excluindo pênaltis.
                                - **xG (pFinalização)**: Gols esperados acumulados sem pênaltis (xG) divididos pelo número de finalizações. Informa sobre a qualidade média de cada chute da equipe e fornece insights sobre a eficiência e o perigo das oportunidades de chute da equipe.
                                """)

    #####################################################################################################################
    #####################################################################################################################
    ##################################################################################################################### 
    #####################################################################################################################
    ##################################################################################################################### 
    #####################################################################################################################
    #####################################################################################################################
    #####################################################################################################################
    #####################################################################################################################

        elif st.session_state.selected_option == "Clube na Rodada":

            # Select a club
            club_selected = clube

            # Get the image URL for the selected club
            image_url = club_image_paths[club_selected]

            # Center-align and display the image
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{image_url}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )                

            # Add further instructions here        
            #Determinar o Jogo
            df1 = df.loc[(df['clube']==clube)]
            partidas = df1['partida'].unique()
            st.markdown("<h4 style='text-align: center;'><br>Escolha a Partida!</h4>", unsafe_allow_html=True)
            partida = st.selectbox("", options=partidas)

            st.write("---")

            dfa = pd.read_csv("performance_round.csv")
            dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

            dfb = dfa.loc[(dfa['partida']==partida) & (dfa['clube']==clube)]
            data = dfb['data']
            data_value = data.iloc[0]
            rodada = dfb['rodada']
            rodada_value = rodada.iloc[0]
            dfc = dfa.loc[dfa['rodada'] == rodada_value]

            #Plotar Primeiro Gráfico - Dispersão das métricas do clube em eixo único:

            st.markdown(
            f"""
            <h3 style='text-align: center; color: blue;'>
            Como performou o {clube} <br>comparado às demais partidas da rodada?<br>
            <span style='color: black;'>{partida}</span><br>
            <span style='color: black;'>Rodada {rodada_value} - {data_value}</span>
            </h3>
            """,
            unsafe_allow_html=True
            )

            #Collecting data to plot
            metrics = dfc.iloc[:, np.r_[11:16]].reset_index(drop=True)
            metrics_defesa = metrics.iloc[:, 0].tolist()
            metrics_transição_defensiva = metrics.iloc[:, 1].tolist()
            metrics_transição_ofensiva = metrics.iloc[:, 2].tolist()
            metrics_ataque = metrics.iloc[:, 3].tolist()
            metrics_criação_chances = metrics.iloc[:, 4].tolist()
            metrics_y = [0] * len(metrics_defesa)

            # The specific data point you want to highlight
            highlight = dfb[(dfb['clube']==clube)&(dfb['partida']==partida)]
            highlight = highlight.iloc[:, np.r_[11:16]].reset_index(drop=True)
            highlight_defesa = highlight.iloc[:, 0].tolist()
            highlight_transição_defensiva = highlight.iloc[:, 1].tolist()
            highlight_transição_ofensiva = highlight.iloc[:, 2].tolist()
            highlight_ataque = highlight.iloc[:, 3].tolist()
            highlight_criação_chances = highlight.iloc[:, 4].tolist()
            highlight_y = 0

            # Computing the selected game specific values
            highlight_defesa_value = pd.DataFrame(highlight_defesa).reset_index(drop=True)
            highlight_transição_defensiva_value = pd.DataFrame(highlight_transição_defensiva).reset_index(drop=True)
            highlight_transição_ofensiva_value = pd.DataFrame(highlight_transição_ofensiva).reset_index(drop=True)
            highlight_ataque_value = pd.DataFrame(highlight_ataque).reset_index(drop=True)
            highlight_criação_chances_value = pd.DataFrame(highlight_criação_chances).reset_index(drop=True)

            highlight_defesa_value = highlight_defesa_value.iat[0,0]
            highlight_transição_defensiva_value = highlight_transição_defensiva_value.iat[0,0]
            highlight_transição_ofensiva_value = highlight_transição_ofensiva_value.iat[0,0]
            highlight_ataque_value = highlight_ataque_value.iat[0,0]
            highlight_criação_chances_value = highlight_criação_chances_value.iat[0,0]

            # Computing the min and max value across all lists using a generator expression
            min_value = min(min(lst) for lst in [metrics_defesa, metrics_transição_defensiva, 
                                            metrics_transição_ofensiva, metrics_ataque, 
                                            metrics_criação_chances])
            min_value = min_value - 0.1
            max_value = max(max(lst) for lst in [metrics_defesa, metrics_transição_defensiva, 
                                            metrics_transição_ofensiva, metrics_ataque, 
                                            metrics_criação_chances])
            max_value = max_value + 0.1

            # Create two subplots vertically aligned with separate x-axes
            fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
            #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

            # Building the Extended Title"
            rows_count = dfc.shape[0]

            # Function to determine game's rank in attribute in league
            def get_partida_rank(partida, temporada, column_name, dataframe):
                # Filter the dataframe for the specified Temporada
                filtered_df = dataframe[dataframe['Temporada'] == 2024]

                # Rank partidas based on the specified column in descending order
                filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')

                # Find the rank of the specified partida
                partida_row = filtered_df[filtered_df['partida'] == partida]
                if not partida_row.empty:
                    return int(partida_row['Rank'].iloc[0])
                else:
                    return None

                # Determining partida's rank in attribute in league
                defesa_ranking_value = (get_partida_rank(partida, 2024, "Defesa", dfc))

                # Data to plot
                output_str = f"({defesa_ranking_value}/{rows_count})"
                full_title_defesa = f"Defesa {output_str} {highlight_defesa_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                transição_defensiva_ranking_value = (get_partida_rank(partida, 2024, "Transição defensiva", dfc))

                output_str = f"({transição_defensiva_ranking_value}/{rows_count})"
                full_title_transição_defensiva = f"Transição defensiva {output_str} {highlight_transição_defensiva_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                transição_ofensiva_ranking_value = (get_partida_rank(partida, 2024, "Transição ofensiva", dfc))

                output_str = f"({transição_ofensiva_ranking_value}/{rows_count})"
                full_title_transição_ofensiva = f"Transição ofensiva {output_str} {highlight_transição_ofensiva_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                ataque_ranking_value = (get_partida_rank(partida, 2024, "Ataque", dfc))#.astype(int)

                output_str = f"({ataque_ranking_value}/{rows_count})"
                full_title_ataque = f"Ataque {output_str} {highlight_ataque_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                criação_chances_ranking_value = (get_partida_rank(partida, 2024, "Criação de chances", dfc))#.astype(int)

                output_str = f"({criação_chances_ranking_value}/{rows_count})"
                full_title_criação_chances = f"Criação de chances {output_str} {highlight_criação_chances_value}"

            ##############################################################################################################
            ##############################################################################################################
            ##############################################################################################################
            ##############################################################################################################
            #From Claude version2

            def calculate_ranks(values):
                """Calculate ranks for a given metric, with highest values getting rank 1"""
                return pd.Series(values).rank(ascending=False).astype(int).tolist()

            def prepare_data(tabela_a, metrics_cols):
                """Prepare the metrics data dictionary with all required data"""
                metrics_data = {}

                for col in metrics_cols:
                    # Store the metric values
                    metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                    # Calculate and store ranks
                    metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                    # Store partida names
                    metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                    # Store club names - assuming there's a 'clube' column
                    metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()

                return metrics_data

            def get_club_from_fixture(fixture, selected_clube=None):
                """
                Extract club names from fixture string
                If selected_clube is provided and matches one of the clubs, return that club
                Otherwise return the first club
                """
                parts = fixture.split(" x ")
                # Extract first club (remove the score)
                first_club_parts = parts[0].strip().split(" ")
                first_club = " ".join(first_club_parts[:-1])
                
                # Extract second club (remove the score)
                second_club_parts = parts[1].strip().split(" ")
                second_club = " ".join(second_club_parts[1:])
                
                if selected_clube == first_club or selected_clube == second_club:
                    return selected_clube
                
                return first_club

            def create_partida_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                """
                Create an interactive plot showing partida attributes with hover information

                Parameters:
                tabela_a (pd.DataFrame): DataFrame containing all partida data
                partida (str): Name of the partida to highlight
                selected_club (str, optional): Name of the club to highlight, if None first club is used
                min_value (float): Minimum value for x-axis
                max_value (float): Maximum value for x-axis
                """
                # Get the specific club from the fixture to highlight
                highlight_clube = get_club_from_fixture(partida, selected_clube)
                
                # List of metrics to plot
                metrics_list = [
                    'Defesa', 'Transição defensiva', 'Transição ofensiva',
                    'Ataque','Criação de chances'
                ]

                # Prepare all the data
                metrics_data = prepare_data(tabela_a, metrics_list)

                # Calculate highlight data - filter by both partida and club
                highlight_data = {}
                highlight_ranks = {}
                
                for metric in metrics_list:
                    # Find the row that matches both partida and clube
                    match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                    if not match_rows.empty:
                        highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                        # Calculate rank
                        highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                    else:
                        # Fallback if no match
                        highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                        highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])

                # Total number of partidas
                total_partidas = len(tabela_a)

                # Create subplots
                fig = make_subplots(
                    rows=9, 
                    cols=1,
                    subplot_titles=[
                        f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_partidas}) {highlight_data[f'highlight_{metric}']:.2f}"
                        for metric in metrics_list
                    ],
                    vertical_spacing=0.04
                )

                # Update subplot titles font size and color
                for i in fig['layout']['annotations']:
                    i['font'] = dict(size=17, color='black')

                # Add traces for each metric
                for idx, metric in enumerate(metrics_list, 1):
                    # Add scatter plot for all partidas
                    fig.add_trace(
                        go.Scatter(
                            x=metrics_data[f'metrics_{metric}'],
                            y=[0] * len(metrics_data[f'metrics_{metric}']),
                            mode='markers',
                            name = f"Demais partidas da Rodada <span style='color: deepskyblue; weight=bold'>{rodada_value}</span>",
                            marker=dict(color='deepskyblue', size=8),
                            text=[f"{rank}/{total_partidas}" for rank in metrics_data[f'ranks_{metric}']],
                            customdata=list(zip(
                                metrics_data[f'partida_names_{metric}'], 
                                metrics_data[f'clube_names_{metric}']
                            )),
                            hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )
                    
                    # Add highlighted partida point
                    fig.add_trace(
                        go.Scatter(
                            x=[highlight_data[f'highlight_{metric}']],
                            y=[0],
                            mode='markers',
                            name=highlight_clube,
                            marker=dict(color='blue', size=12),
                            hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_partidas}<br>Value: %{{x:.2f}}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )

                # Get the total number of metrics (subplots)
                n_metrics = len(metrics_list)

                # Update layout for each subplot
                for i in range(1, n_metrics + 1):
                    if i == n_metrics:  # Only for the last subplot
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='black',
                            zerolinewidth=1,
                            showline=False,
                            ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                            tickvals=[min_value/2, 0, max_value/2],
                            tickmode='array',
                            ticks="outside",
                            ticklen=2,
                            tickfont=dict(size=16),
                            tickangle=0,
                            side='bottom',
                            automargin=False,
                            row=i, 
                            col=1
                        )
                        # Adjust layout for the last subplot
                        fig.update_layout(
                            xaxis_tickfont_family="Arial",
                            margin=dict(b=0)  # Reduce bottom margin
                        )
                    else:  # For all other subplots
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='grey',
                            zerolinewidth=1,
                            showline=False,
                            showticklabels=False,  # Hide tick labels
                            row=i, 
                            col=1
                        )  # Reduces space between axis and labels

                    # Update layout for the entire figure
                    fig.update_yaxes(
                        showticklabels=False,
                        showgrid=False,
                        showline=False,
                        row=i, 
                        col=1
                    )

                # Update layout for the entire figure
                fig.update_layout(
                    height=700,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=0.25,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=16)
                    ),
                    margin=dict(t=100)
                )

                # Add x-axis label at the bottom
                fig.add_annotation(
                    text="Desvio-padrão",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.32,
                    showarrow=False,
                    font=dict(size=16, color='black')
                )

                return fig

            # Calculate min and max values with some padding
            min_value_test = min([
            min(metrics_defesa), min(metrics_transição_defensiva), min(metrics_transição_ofensiva),
            min(metrics_ataque), min(metrics_criação_chances)
            ])  # Add padding of 0.5

            max_value_test = max([
            max(metrics_defesa), max(metrics_transição_defensiva), max(metrics_transição_ofensiva),
            max(metrics_ataque), max(metrics_criação_chances)
            ])  # Add padding of 0.5

            min_value = -max(abs(min_value_test), max_value_test) -0.03
            max_value = -min_value

            # Create the plot
            fig = create_partida_attributes_plot(
                tabela_a=dfc,           # Your main dataframe
                partida=partida,        # Name of partida to highlight (e.g., "Cuiaba 1 x 2 Vasco da Gama")
                selected_clube=clube,   # Name of the club to highlight (e.g., "Vasco da Gama" or "Cuiaba")
                min_value=min_value,    # Minimum value for x-axis
                max_value=max_value     # Maximum value for x-axis
            )

            st.plotly_chart(fig, use_container_width=True)

            ##################################################################################################################### 
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################


            #INSERIR ANÁLISE POR ATRIBUTO

            atributos = ["Defesa", "Transição defensiva", "Transição ofensiva", 
                            "Ataque", "Criação de chances"]

            st.markdown("---")
            st.markdown(
                "<h3 style='text-align: center; color:black; '>Se quiser aprofundar, escolha o Atributo</h3>",
                unsafe_allow_html=True
            )

            atributo = st.selectbox("", options=atributos, index = None, key=10, placeholder = "Escolha o Atributo!")
            if atributo == ("Defesa"):
                
                #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                # Dynamically create the HTML string with the 'partida' variable
                title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                # Use the dynamically created HTML string in st.markdown
                st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>A Defesa em relação aos demais jogos da Rodada</h3>",
                            unsafe_allow_html=True
                            )
                st.markdown(title_html, unsafe_allow_html=True)
                st.write("---")

                attribute_chart_z = dfc
                # Collecting data
                attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['rodada']==rodada_value)]
                #Collecting data to plot
                metrics = attribute_chart_z1.iloc[:, np.r_[17:25]].reset_index(drop=True)
                metrics_participação_1 = metrics.iloc[:, 0].tolist()
                metrics_participação_2 = metrics.iloc[:, 1].tolist()
                metrics_participação_3 = metrics.iloc[:, 2].tolist()
                metrics_participação_4 = metrics.iloc[:, 3].tolist()
                metrics_participação_5 = metrics.iloc[:, 4].tolist()
                metrics_participação_6 = metrics.iloc[:, 5].tolist()
                metrics_participação_7 = metrics.iloc[:, 6].tolist()
                metrics_participação_8 = metrics.iloc[:, 7].tolist()
                metrics_y = [0] * len(metrics_participação_1)

                # The specific data point you want to highlight
                highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                highlight = highlight.iloc[:, np.r_[17:25]].reset_index(drop=True)
                highlight_participação_1 = highlight.iloc[:, 0].tolist()
                highlight_participação_2 = highlight.iloc[:, 1].tolist()
                highlight_participação_3 = highlight.iloc[:, 2].tolist()
                highlight_participação_4 = highlight.iloc[:, 3].tolist()
                highlight_participação_5 = highlight.iloc[:, 4].tolist()
                highlight_participação_6 = highlight.iloc[:, 5].tolist()
                highlight_participação_7 = highlight.iloc[:, 6].tolist()
                highlight_participação_8 = highlight.iloc[:, 7].tolist()
                highlight_y = 0

                # Computing the selected player specific values
                highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                # Computing the min and max value across all lists using a generator expression
                min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6, 
                                                    metrics_participação_7, metrics_participação_8])
                min_value = min_value - 0.1
                max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6, 
                                                    metrics_participação_7, metrics_participação_8])
                max_value = max_value + 0.1

                # Create two subplots vertically aligned with separate x-axes
                fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                # Building the Extended Title"
                rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                
                # Function to determine partida's rank in attribute in league
                def get_partida_rank(partida, temporada, column_name, dataframe):
                    # Filter the dataframe for the specified Temporada
                    filtered_df = dataframe[dataframe['Temporada'] == 2024]
                    
                    # Rank partidas based on the specified column in descending order
                    filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                    
                    # Find the rank of the specified partida
                    partida_row = filtered_df[filtered_df['partida'] == partida]
                    if not partida_row.empty:
                        return int(partida_row['Rank'].iloc[0])
                    else:
                        return None

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_1_ranking_value = (get_partida_rank(partida, 2024, "PPDA", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_1_ranking_value}/{rows_count})"
                full_title_participação_1 = f"PPDA {output_str} {highlight_participação_1_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_2_ranking_value = (get_partida_rank(partida, 2024, "Intensidade defensiva", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_2_ranking_value}/{rows_count})"
                full_title_participação_2 = f"Intensidade defensiva {output_str} {highlight_participação_2_value}"
                
                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_3_ranking_value = (get_partida_rank(partida, 2024, "Duelos defensivos vencidos (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_3_ranking_value}/{rows_count})"
                full_title_participação_3 = f"Duelos defensivos vencidos (%) {output_str} {highlight_participação_3_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_4_ranking_value = (get_partida_rank(partida, 2024, "Altura defensiva (m)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_4_ranking_value}/{rows_count})"
                full_title_participação_4 = f"Altura defensiva (m) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_5_ranking_value = (get_partida_rank(partida, 2024, "Velocidade do passe adversário", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_5_ranking_value}/{rows_count})"
                full_title_participação_5 = f"Velocidade do passe adversário {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário no último terço (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_6_ranking_value}/{rows_count})"
                full_title_participação_6 = f"Entradas do adversário no último terço (%) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_7_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário na área (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_7_ranking_value}/{rows_count})"
                full_title_participação_7 = f"Entradas do adversário na área (%) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_8_ranking_value = (get_partida_rank(partida, 2024, "xT adversário", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_8_ranking_value}/{rows_count})"
                full_title_participação_8 = f"xT adversário {output_str} {highlight_participação_4_value}"

                ##############################################################################################################
                ##############################################################################################################
                #From Claude version2

                def calculate_ranks(values):
                    """Calculate ranks for a given metric, with highest values getting rank 1"""
                    return pd.Series(values).rank(ascending=False).astype(int).tolist()

                def prepare_data(tabela_a, metrics_cols):
                    """Prepare the metrics data dictionary with all required data"""
                    metrics_data = {}
                    
                    for col in metrics_cols:
                        # Store the metric values
                        metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                        # Calculate and store ranks
                        metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                        # Store partida names
                        metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        # Store clube names - assuming there's a 'clube' column
                        metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()
                    
                    return metrics_data

                def get_clube_from_partida(partida, selected_clube=None):
                    """
                    Extract clube names from partida string
                    If selected_clube is provided and matches one of the clubes, return that clube
                    Otherwise return the first clube
                    """
                    parts = partida.split(" x ")
                    # Extract first clube (remove the score)
                    first_clube_parts = parts[0].strip().split(" ")
                    first_clube = " ".join(first_clube_parts[:-1])
                    
                    # Extract second clube (remove the score)
                    second_clube_parts = parts[1].strip().split(" ")
                    second_clube = " ".join(second_clube_parts[1:])
                    
                    if selected_clube == first_clube or selected_clube == second_clube:
                        return selected_clube
                    
                    return first_clube

                def create_player_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                    """
                    Create an interactive plot showing player attributes with hover information
                    
                    Parameters:
                    tabela_a (pd.DataFrame): DataFrame containing all player data
                    partida (str): Name of the partida to highlight (e.g., "Cuiaba 1 x 2 Vasco da Gama")
                    selected_clube (str, optional): Name of the clube to highlight, if None first clube is used
                    min_value (float): Minimum value for x-axis
                    max_value (float): Maximum value for x-axis
                    """
                    # Get the specific clube from the partida to highlight
                    highlight_clube = get_clube_from_partida(partida, selected_clube)
                    
                    # List of metrics to plot
                    metrics_list = ["PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                            "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                            "Entradas do adversário na área (%)", "xT adversário"
                    ]

                    # Prepare all the data
                    metrics_data = prepare_data(tabela_a, metrics_list)
                    
                    # Calculate highlight data - filter by both partida and clube
                    highlight_data = {}
                    highlight_ranks = {}
                    
                    for metric in metrics_list:
                        # Find the row that matches both partida and clube
                        match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                        if not match_rows.empty:
                            highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                            # Calculate rank
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                        else:
                            # Fallback if no match
                            highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])
                    
                    # Total number of players
                    total_players = len(tabela_a)
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=9, 
                        cols=1,
                        subplot_titles=[
                            f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                            for metric in metrics_list
                        ],
                        vertical_spacing=0.04
                    )

                    # Update subplot titles font size and color
                    for i in fig['layout']['annotations']:
                        i['font'] = dict(size=17, color='black')

                    # Add traces for each metric
                    for idx, metric in enumerate(metrics_list, 1):
                        # Add scatter plot for all players
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_data[f'metrics_{metric}'],
                                y=[0] * len(metrics_data[f'metrics_{metric}']),
                                mode='markers',
                                name = f'Demais partidas do {clube}',
                                marker=dict(color='deepskyblue', size=8),
                                text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                customdata=list(zip(
                                    metrics_data[f'partida_names_{metric}'],
                                    metrics_data[f'clube_names_{metric}']
                                )),
                                hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                        
                        # Add highlighted player point
                        fig.add_trace(
                            go.Scatter(
                                x=[highlight_data[f'highlight_{metric}']],
                                y=[0],
                                mode='markers',
                                name=highlight_clube,
                                marker=dict(color='blue', size=12),
                                hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )

                    # Get the total number of metrics (subplots)
                    n_metrics = len(metrics_list)

                    # Update layout for each subplot
                    for i in range(1, n_metrics + 1):
                        if i == n_metrics:  # Only for the last subplot
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='black',
                                zerolinewidth=1,
                                showline=False,
                                ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                tickvals=[min_value/2, 0, max_value/2],
                                tickmode='array',
                                ticks="outside",
                                ticklen=2,
                                tickfont=dict(size=16),
                                tickangle=0,
                                side='bottom',
                                automargin=False,
                                row=i, 
                                col=1
                            )
                            # Adjust layout for the last subplot
                            fig.update_layout(
                                xaxis_tickfont_family="Arial",
                                margin=dict(b=0)  # Reduce bottom margin
                            )
                        else:  # For all other subplots
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='grey',
                                zerolinewidth=1,
                                showline=False,
                                showticklabels=False,  # Hide tick labels
                                row=i, 
                                col=1
                            )  # Reduces space between axis and labels

                        # Update layout for the entire figure
                        fig.update_yaxes(
                            showticklabels=False,
                            showgrid=False,
                            showline=False,
                            row=i, 
                            col=1
                        )

                    # Update layout for the entire figure
                    fig.update_layout(
                        height=800,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=16)
                        ),
                        margin=dict(t=100)
                    )

                    # Add x-axis label at the bottom
                    fig.add_annotation(
                        text="Desvio-padrão",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=-0.06,
                        showarrow=False,
                        font=dict(size=16, color='black')
                    )

                    return fig

                # Calculate min and max values with some padding
                min_value_test = min([
                min(metrics_participação_1), min(metrics_participação_2), 
                min(metrics_participação_3), min(metrics_participação_4),
                min(metrics_participação_5), min(metrics_participação_6),
                min(metrics_participação_7), min(metrics_participação_8),
                ])  # Add padding of 0.5

                max_value_test = max([
                max(metrics_participação_1), max(metrics_participação_2), 
                max(metrics_participação_3), max(metrics_participação_4),
                max(metrics_participação_5), max(metrics_participação_6),
                max(metrics_participação_7), max(metrics_participação_8),
                ])  # Add padding of 0.5

                min_value = -max(abs(min_value_test), max_value_test) -0.03
                max_value = -min_value

                # Create the plot
                fig = create_player_attributes_plot(
                    tabela_a=attribute_chart_z1,  # Your main dataframe
                    partida=partida,              # Name of partida to highlight (e.g., "Cuiaba 1 x 2 Vasco da Gama")
                    selected_clube=clube,         # Name of the clube to highlight (e.g., "Vasco da Gama" or "Cuiaba")
                    min_value=min_value,          # Minimum value for x-axis
                    max_value=max_value           # Maximum value for x-axis
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### DEFESA - métricas
                        - **PPDA**: “Passes por ação defensiva”. Mede a intensidade da pressão defensiva calculando o número de passes permitidos por um time antes de tentar uma ação defensiva. Quanto menor o PPDA, maior a intensidade da pressão defensiva. A análise é limitada aos 60% iniciais do campo do oponente.  A análise é limitada aos 60% iniciais do campo do oponente.
                        - **Intensidade defensiva**: Número de duelos defensivos, duelos livres, interceptações, desarmes e faltas quando a posse é do adversário, ajustado pela posse do adversário.
                        - **Duelos defensivos vencidos (%)**: Porcentagem de duelos defensivos no solo que interrompem com sucesso a progressão de um oponente ou recuperam a posse de bola.
                        - **Altura defensiva (m)**: Altura média no campo, medida em metros, das ações defensivas de um time.
                        - **Velocidade do passe do adversário**: Velocidade com que o time adversário move a bola por meio de passes. Isso pode ser influenciado pelo estilo de jogo do adversário, como ataque direto ou futebol baseado em posse de bola.
                        - **Entradas do adversário no último terço (%)**: Porcentagem de posses do time adversário que progridem com sucesso para o terço final do campo.
                        - **Entradas do adversário na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT Adversário**: Ameaça esperada baseada em ações (xT) por 100 passes bem-sucedidos do adversário originados de dentro da área defensiva da equipe. 
                        """)
                
                #####################################################################################################################
                #####################################################################################################################
                ##################################################################################################################### 
                #####################################################################################################################
                
            elif atributo == ("Transição defensiva"):
                
                #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                # Dynamically create the HTML string with the 'partida' variable
                title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                # Use the dynamically created HTML string in st.markdown
                st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>Transição Defensiva em relação aos demais jogos da Rodada</h3>",
                            unsafe_allow_html=True
                            )
                st.markdown(title_html, unsafe_allow_html=True)
                st.write("---")

                attribute_chart_z = dfc
                # Collecting data
                attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['rodada']==rodada_value)]
                #Collecting data to plot
                metrics = attribute_chart_z1.iloc[:, np.r_[25:33]].reset_index(drop=True)
                metrics_participação_1 = metrics.iloc[:, 0].tolist()
                metrics_participação_2 = metrics.iloc[:, 1].tolist()
                metrics_participação_3 = metrics.iloc[:, 2].tolist()
                metrics_participação_4 = metrics.iloc[:, 3].tolist()
                metrics_participação_5 = metrics.iloc[:, 4].tolist()
                metrics_participação_6 = metrics.iloc[:, 5].tolist()
                metrics_participação_7 = metrics.iloc[:, 6].tolist()
                metrics_participação_8 = metrics.iloc[:, 7].tolist()
                metrics_y = [0] * len(metrics_participação_1)

                # The specific data point you want to highlight
                highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                highlight = highlight.iloc[:, np.r_[25:33]].reset_index(drop=True)
                highlight_participação_1 = highlight.iloc[:, 0].tolist()
                highlight_participação_2 = highlight.iloc[:, 1].tolist()
                highlight_participação_3 = highlight.iloc[:, 2].tolist()
                highlight_participação_4 = highlight.iloc[:, 3].tolist()
                highlight_participação_5 = highlight.iloc[:, 4].tolist()
                highlight_participação_6 = highlight.iloc[:, 5].tolist()
                highlight_participação_7 = highlight.iloc[:, 6].tolist()
                highlight_participação_8 = highlight.iloc[:, 7].tolist()
                highlight_y = 0

                # Computing the selected player specific values
                highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                # Computing the min and max value across all lists using a generator expression
                min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6,
                                                    metrics_participação_7, metrics_participação_8 
                                                    ])
                min_value = min_value - 0.1
                max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6,
                                                    metrics_participação_7, metrics_participação_8
                                                    ])
                max_value = max_value + 0.1

                # Create two subplots vertically aligned with separate x-axes
                fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8) = plt.subplots(8, 1)
                #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                # Building the Extended Title"
                rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                
                # Function to determine partida's rank in attribute in league
                def get_partida_rank(partida, temporada, column_name, dataframe):
                    # Filter the dataframe for the specified Temporada
                    filtered_df = dataframe[dataframe['Temporada'] == 2024]
                    
                    # Rank partidas based on the specified column in descending order
                    filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                    
                    # Find the rank of the specified partida
                    partida_row = filtered_df[filtered_df['partida'] == partida]
                    if not partida_row.empty:
                        return int(partida_row['Rank'].iloc[0])
                    else:
                        return None

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_1_ranking_value = (get_partida_rank(partida, 2024, "Perdas de posse na linha baixa", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_1_ranking_value}/{rows_count})"
                full_title_participação_1 = f"Perdas de posse na linha baixa {output_str} {highlight_participação_1_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_2_ranking_value = (get_partida_rank(partida, 2024, "Altura da perda de posse (m)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_2_ranking_value}/{rows_count})"
                full_title_participação_2 = f"Altura da perda de posse (m) {output_str} {highlight_participação_2_value}"
                
                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_3_ranking_value = (get_partida_rank(partida, 2024, "Recuperações de posse em 5s (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_3_ranking_value}/{rows_count})"
                full_title_participação_3 = f"Recuperações de posse em 5s (%) {output_str} {highlight_participação_3_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_4_ranking_value = (get_partida_rank(partida, 2024, "Tempo médio ação defensiva (s)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_4_ranking_value}/{rows_count})"
                full_title_participação_4 = f"Tempo médio ação defensiva (s) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_5_ranking_value = (get_partida_rank(partida, 2024, "Tempo médio para recuperação de posse (s)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_5_ranking_value}/{rows_count})"
                full_title_participação_5 = f"Tempo médio para recuperação de posse (s) {output_str} {highlight_participação_5_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário no último terço em 10s da recuperação da posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_6_ranking_value}/{rows_count})"
                full_title_participação_6 = f"Entradas do adversário no último terço em 10s da recuperação da posse {output_str} {highlight_participação_6_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_7_ranking_value = (get_partida_rank(partida, 2024, "Entradas do adversário na área em 10s da recuperação da posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_7_ranking_value}/{rows_count})"
                full_title_participação_7 = f"Entradas do adversário na área em 10s da recuperação da posse {output_str} {highlight_participação_7_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_8_ranking_value = (get_partida_rank(partida, 2024, "xG do adversário em 10s da recuperação da posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_8_ranking_value}/{rows_count})"
                full_title_participação_8 = f"xG do adversário em 10s da recuperação da posse {output_str} {highlight_participação_8_value}"

                ##############################################################################################################
                ##############################################################################################################
                #From Claude version2

                def calculate_ranks(values):
                    """Calculate ranks for a given metric, with highest values getting rank 1"""
                    return pd.Series(values).rank(ascending=False).astype(int).tolist()

                def prepare_data(tabela_a, metrics_cols):
                    """Prepare the metrics data dictionary with all required data"""
                    metrics_data = {}
                    
                    for col in metrics_cols:
                        # Store the metric values
                        metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                        # Calculate and store ranks
                        metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                        # Store partida names
                        metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        # Store clube names
                        metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()
                    
                    return metrics_data

                def get_clube_from_partida(partida, selected_clube=None):
                    """
                    Extract clube names from partida string
                    If selected_clube is provided and matches one of the clubes, return that clube
                    Otherwise return the first clube
                    """
                    parts = partida.split(" x ")
                    # Extract first clube (remove the score)
                    first_clube_parts = parts[0].strip().split(" ")
                    first_clube = " ".join(first_clube_parts[:-1])
                    
                    # Extract second clube (remove the score)
                    second_clube_parts = parts[1].strip().split(" ")
                    second_clube = " ".join(second_clube_parts[1:])
                    
                    if selected_clube == first_clube or selected_clube == second_clube:
                        return selected_clube
                    
                    return first_clube

                def create_player_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                    """
                    Create an interactive plot showing player attributes with hover information
                    
                    Parameters:
                    tabela_a (pd.DataFrame): DataFrame containing all player data
                    partida (str): Name of the partida to highlight
                    selected_clube (str, optional): Name of the clube to highlight
                    min_value (float): Minimum value for x-axis
                    max_value (float): Maximum value for x-axis
                    """
                    # Get the specific clube from the partida to highlight
                    highlight_clube = get_clube_from_partida(partida, selected_clube)
                    
                    # List of metrics to plot
                    metrics_list = ["Perdas de posse na linha baixa",
                                "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                "Tempo médio para recuperação de posse (s)",
                                "Entradas do adversário no último terço em 10s da recuperação da posse",
                                "Entradas do adversário na área em 10s da recuperação da posse", 
                                "xG do adversário em 10s da recuperação da posse"
                    ]

                    # Prepare all the data
                    metrics_data = prepare_data(tabela_a, metrics_list)
                    
                    # Calculate highlight data - filter by both partida and clube
                    highlight_data = {}
                    highlight_ranks = {}
                    
                    for metric in metrics_list:
                        # Find the row that matches both partida and clube
                        match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                        if not match_rows.empty:
                            highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                            # Calculate rank
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                        else:
                            # Fallback if no match
                            highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])
                    
                    # Total number of players
                    total_players = len(tabela_a)
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=9, 
                        cols=1,
                        subplot_titles=[
                            f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                            for metric in metrics_list
                        ],
                        vertical_spacing=0.04
                    )

                    # Update subplot titles font size and color
                    for i in fig['layout']['annotations']:
                        i['font'] = dict(size=17, color='black')

                    # Add traces for each metric
                    for idx, metric in enumerate(metrics_list, 1):
                        # Add scatter plot for all players
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_data[f'metrics_{metric}'],
                                y=[0] * len(metrics_data[f'metrics_{metric}']),
                                mode='markers',
                                name = f'Demais partidas do {clube}',
                                marker=dict(color='deepskyblue', size=8),
                                text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                customdata=list(zip(
                                    metrics_data[f'partida_names_{metric}'],
                                    metrics_data[f'clube_names_{metric}']
                                )),
                                hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                        
                        # Add highlighted player point
                        fig.add_trace(
                            go.Scatter(
                                x=[highlight_data[f'highlight_{metric}']],
                                y=[0],
                                mode='markers',
                                name=highlight_clube,
                                marker=dict(color='blue', size=12),
                                hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )

                    # Get the total number of metrics (subplots)
                    n_metrics = len(metrics_list)

                    # Update layout for each subplot
                    for i in range(1, n_metrics + 1):
                        if i == n_metrics:  # Only for the last subplot
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='black',
                                zerolinewidth=1,
                                showline=False,
                                ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                tickvals=[min_value/2, 0, max_value/2],
                                tickmode='array',
                                ticks="outside",
                                ticklen=2,
                                tickfont=dict(size=16),
                                tickangle=0,
                                side='bottom',
                                automargin=False,
                                row=i, 
                                col=1
                            )
                            # Adjust layout for the last subplot
                            fig.update_layout(
                                xaxis_tickfont_family="Arial",
                                margin=dict(b=0)  # Reduce bottom margin
                            )
                        else:  # For all other subplots
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='grey',
                                zerolinewidth=1,
                                showline=False,
                                showticklabels=False,  # Hide tick labels
                                row=i, 
                                col=1
                            )  # Reduces space between axis and labels

                        # Update layout for the entire figure
                        fig.update_yaxes(
                            showticklabels=False,
                            showgrid=False,
                            showline=False,
                            row=i, 
                            col=1
                        )

                    # Update layout for the entire figure
                    fig.update_layout(
                        height=800,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=16)
                        ),
                        margin=dict(t=100)
                    )

                    # Add x-axis label at the bottom
                    fig.add_annotation(
                        text="Desvio-padrão",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=-0.06,
                        showarrow=False,
                        font=dict(size=16, color='black')
                    )

                    return fig

                # Calculate min and max values with some padding
                min_value_test = min([
                min(metrics_participação_1), min(metrics_participação_2), 
                min(metrics_participação_3), min(metrics_participação_4),
                min(metrics_participação_5), min(metrics_participação_6),
                min(metrics_participação_7), min(metrics_participação_8)
                ])  # Add padding of 0.5

                max_value_test = max([
                max(metrics_participação_1), max(metrics_participação_2), 
                max(metrics_participação_3), max(metrics_participação_4),
                max(metrics_participação_5), max(metrics_participação_6),
                max(metrics_participação_7), max(metrics_participação_8)
                ])  # Add padding of 0.5

                min_value = -max(abs(min_value_test), max_value_test) -0.03
                max_value = -min_value

                # Create the plot
                fig = create_player_attributes_plot(
                    tabela_a=attribute_chart_z1,  # Your main dataframe
                    partida=partida,              # Name of partida to highlight
                    selected_clube=clube,         # Name of the clube to highlight
                    min_value=min_value,          # Minimum value for x-axis
                    max_value=max_value           # Maximum value for x-axis
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### TRANSIÇÃO DEFENSIVA - métricas
                        - **Perda de posse na linha baixa**: Perdas de posse devido a passes errados, erros de domínio ou duelos ofensivos perdidos, nos 40% defensivos da equipe, ajustados pela posse.
                        - **Altura da perda de posse (m)**: Altura média no campo, medida em metros, onde ocorrem perdas de posse.
                        - **Recuperações de posse em 5s %**: Porcentagem de recuperações de bola que ocorrem em até 5 segundos após a perda da posse.
                        - **Tempo médio ação defensiva (s)**: Tempo que o time leva para executar uma ação defensiva, após perder a posse de bola.
                        - **Tempo médio para recuperação de posse (s)**: Tempo que o time leva para recuperar a posse da bola após perdê-la.
                        - **Entradas do adversário no último terço em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso no último terço em até 10 segundos após a recuperação da posse.
                        - **Entradas do adversário na área em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso na área em até 10 segundos após a recuperação da posse.
                        - **xG do adversário em 10s da recuperação da posse**: Gols esperados não-pênaltis (xG) acumulados dos chutes do adversário que ocorrem dentro de 10 segundos após a recuperação da posse de bola.
                        """)

                #################################################################################################################################
                #################################################################################################################################
                ##################################################################################################################### 
                #####################################################################################################################

            elif atributo == ("Transição ofensiva"):
                
                #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                # Dynamically create the HTML string with the 'partida' variable
                title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                # Use the dynamically created HTML string in st.markdown
                st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>A Transição Ofensiva do {clube}<br>em relação aos demais jogos da Rodada</h3>",
                            unsafe_allow_html=True
                            )
                st.markdown(title_html, unsafe_allow_html=True)
                st.write("---")

                attribute_chart_z = dfc
                # Collecting data
                attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['rodada']==rodada_value)]
                #Collecting data to plot
                metrics = attribute_chart_z1.iloc[:, np.r_[33:41]].reset_index(drop=True)
                metrics_participação_1 = metrics.iloc[:, 0].tolist()
                metrics_participação_2 = metrics.iloc[:, 1].tolist()
                metrics_participação_3 = metrics.iloc[:, 2].tolist()
                metrics_participação_4 = metrics.iloc[:, 3].tolist()
                metrics_participação_5 = metrics.iloc[:, 4].tolist()
                metrics_participação_6 = metrics.iloc[:, 5].tolist()
                metrics_participação_7 = metrics.iloc[:, 6].tolist()
                metrics_participação_8 = metrics.iloc[:, 7].tolist()
                metrics_y = [0] * len(metrics_participação_1)

                # The specific data point you want to highlight
                highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                highlight = highlight.iloc[:, np.r_[33:41]].reset_index(drop=True)
                highlight_participação_1 = highlight.iloc[:, 0].tolist()
                highlight_participação_2 = highlight.iloc[:, 1].tolist()
                highlight_participação_3 = highlight.iloc[:, 2].tolist()
                highlight_participação_4 = highlight.iloc[:, 3].tolist()
                highlight_participação_5 = highlight.iloc[:, 4].tolist()
                highlight_participação_6 = highlight.iloc[:, 5].tolist()
                highlight_participação_7 = highlight.iloc[:, 6].tolist()
                highlight_participação_8 = highlight.iloc[:, 7].tolist()
                highlight_y = 0

                # Computing the selected player specific values
                highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)
                highlight_participação_8_value = pd.DataFrame(highlight_participação_8).reset_index(drop=True)

                highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                highlight_participação_7_value = highlight_participação_7_value.iat[0,0]
                highlight_participação_8_value = highlight_participação_8_value.iat[0,0]

                # Computing the min and max value across all lists using a generator expression
                min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6, 
                                                    metrics_participação_7, metrics_participação_8])
                min_value = min_value - 0.1
                max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6, 
                                                    metrics_participação_7, metrics_participação_8])
                max_value = max_value + 0.1

                # Create two subplots vertically aligned with separate x-axes
                fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                # Building the Extended Title"
                rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                
                # Function to determine partida's rank in attribute in league
                def get_partida_rank(partida, temporada, column_name, dataframe):
                    # Filter the dataframe for the specified Temporada
                    filtered_df = dataframe[dataframe['Temporada'] == 2024]
                    
                    # Rank partidas based on the specified column in descending order
                    filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                    
                    # Find the rank of the specified partida
                    partida_row = filtered_df[filtered_df['partida'] == partida]
                    if not partida_row.empty:
                        return int(partida_row['Rank'].iloc[0])
                    else:
                        return None

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_1_ranking_value = (get_partida_rank(partida, 2024, "Recuperações de posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_1_ranking_value}/{rows_count})"
                full_title_participação_1 = f"Recuperações de posse {output_str} {highlight_participação_1_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_2_ranking_value = (get_partida_rank(partida, 2024, "Altura da recuperação de posse (m)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_2_ranking_value}/{rows_count})"
                full_title_participação_2 = f"Altura da recuperação de posse (m) {output_str} {highlight_participação_2_value}"
                
                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_3_ranking_value = (get_partida_rank(partida, 2024, "Posse mantida em 5s", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_3_ranking_value}/{rows_count})"
                full_title_participação_3 = f"Posse mantida em 5s {output_str} {highlight_participação_3_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_4_ranking_value = (get_partida_rank(partida, 2024, "Posse mantida em 5s (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_4_ranking_value}/{rows_count})"
                full_title_participação_4 = f"Posse mantida em 5s (%) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_5_ranking_value = (get_partida_rank(partida, 2024, "Entradas no último terço em 10s", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_5_ranking_value}/{rows_count})"
                full_title_participação_5 = f"Entradas no último terço em 10s {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_6_ranking_value = (get_partida_rank(partida, 2024, "Entradas na área em 10s", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_6_ranking_value}/{rows_count})"
                full_title_participação_6 = f"Entradas na área em 10s {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_7_ranking_value = (get_partida_rank(partida, 2024, "xG em 10s da recuperação da posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_7_ranking_value}/{rows_count})"
                full_title_participação_7 = f"xG em 10s da recuperação da posse {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_8_ranking_value = (get_partida_rank(partida, 2024, "xT em 10s da recuperação da posse", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_8_ranking_value}/{rows_count})"
                full_title_participação_8 = f"xT em 10s da recuperação da posse {output_str} {highlight_participação_4_value}"

                ##############################################################################################################
                ##############################################################################################################
                #From Claude version2

                def calculate_ranks(values):
                    """Calculate ranks for a given metric, with highest values getting rank 1"""
                    return pd.Series(values).rank(ascending=False).astype(int).tolist()

                def prepare_data(tabela_a, metrics_cols):
                    """Prepare the metrics data dictionary with all required data"""
                    metrics_data = {}
                    
                    for col in metrics_cols:
                        # Store the metric values
                        metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                        # Calculate and store ranks
                        metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                        # Store partida names
                        metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        # Store clube names
                        metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()
                    
                    return metrics_data

                def get_clube_from_partida(partida, selected_clube=None):
                    """
                    Extract clube names from partida string
                    If selected_clube is provided and matches one of the clubes, return that clube
                    Otherwise return the first clube
                    """
                    parts = partida.split(" x ")
                    # Extract first clube (remove the score)
                    first_clube_parts = parts[0].strip().split(" ")
                    first_clube = " ".join(first_clube_parts[:-1])
                    
                    # Extract second clube (remove the score)
                    second_clube_parts = parts[1].strip().split(" ")
                    second_clube = " ".join(second_clube_parts[1:])
                    
                    if selected_clube == first_clube or selected_clube == second_clube:
                        return selected_clube
                    
                    return first_clube

                def create_player_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                    """
                    Create an interactive plot showing player attributes with hover information
                    
                    Parameters:
                    tabela_a (pd.DataFrame): DataFrame containing all player data
                    partida (str): Name of the partida to highlight
                    selected_clube (str, optional): Name of the clube to highlight
                    min_value (float): Minimum value for x-axis
                    max_value (float): Maximum value for x-axis
                    """
                    # Get the specific clube from the partida to highlight
                    highlight_clube = get_clube_from_partida(partida, selected_clube)
                    
                    # List of metrics to plot
                    metrics_list = ["Recuperações de posse", "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                            "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                            "xT em 10s da recuperação da posse"
                    ]

                    # Prepare all the data
                    metrics_data = prepare_data(tabela_a, metrics_list)
                    
                    # Calculate highlight data - filter by both partida and clube
                    highlight_data = {}
                    highlight_ranks = {}
                    
                    for metric in metrics_list:
                        # Find the row that matches both partida and clube
                        match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                        if not match_rows.empty:
                            highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                            # Calculate rank
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                        else:
                            # Fallback if no match
                            highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])
                    
                    # Total number of players
                    total_players = len(tabela_a)
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=9, 
                        cols=1,
                        subplot_titles=[
                            f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                            for metric in metrics_list
                        ],
                        vertical_spacing=0.04
                    )

                    # Update subplot titles font size and color
                    for i in fig['layout']['annotations']:
                        i['font'] = dict(size=17, color='black')

                    # Add traces for each metric
                    for idx, metric in enumerate(metrics_list, 1):
                        # Add scatter plot for all players
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_data[f'metrics_{metric}'],
                                y=[0] * len(metrics_data[f'metrics_{metric}']),
                                mode='markers',
                                name = f'Demais partidas do {clube}',
                                marker=dict(color='deepskyblue', size=8),
                                text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                customdata=list(zip(
                                    metrics_data[f'partida_names_{metric}'],
                                    metrics_data[f'clube_names_{metric}']
                                )),
                                hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                        
                        # Add highlighted player point
                        fig.add_trace(
                            go.Scatter(
                                x=[highlight_data[f'highlight_{metric}']],
                                y=[0],
                                mode='markers',
                                name=highlight_clube,
                                marker=dict(color='blue', size=12),
                                hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )

                    # Get the total number of metrics (subplots)
                    n_metrics = len(metrics_list)

                    # Update layout for each subplot
                    for i in range(1, n_metrics + 1):
                        if i == n_metrics:  # Only for the last subplot
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='black',
                                zerolinewidth=1,
                                showline=False,
                                ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                tickvals=[min_value/2, 0, max_value/2],
                                tickmode='array',
                                ticks="outside",
                                ticklen=2,
                                tickfont=dict(size=16),
                                tickangle=0,
                                side='bottom',
                                automargin=False,
                                row=i, 
                                col=1
                            )
                            # Adjust layout for the last subplot
                            fig.update_layout(
                                xaxis_tickfont_family="Arial",
                                margin=dict(b=0)  # Reduce bottom margin
                            )
                        else:  # For all other subplots
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='grey',
                                zerolinewidth=1,
                                showline=False,
                                showticklabels=False,  # Hide tick labels
                                row=i, 
                                col=1
                            )  # Reduces space between axis and labels

                        # Update layout for the entire figure
                        fig.update_yaxes(
                            showticklabels=False,
                            showgrid=False,
                            showline=False,
                            row=i, 
                            col=1
                        )

                    # Update layout for the entire figure
                    fig.update_layout(
                        height=800,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=16)
                        ),
                        margin=dict(t=100)
                    )

                    # Add x-axis label at the bottom
                    fig.add_annotation(
                        text="Desvio-padrão",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=-0.06,
                        showarrow=False,
                        font=dict(size=16, color='black')
                    )

                    return fig

                # Calculate min and max values with some padding
                min_value_test = min([
                min(metrics_participação_1), min(metrics_participação_2), 
                min(metrics_participação_3), min(metrics_participação_4),
                min(metrics_participação_5), min(metrics_participação_6),
                min(metrics_participação_7), min(metrics_participação_8),
                ])  # Add padding of 0.5

                max_value_test = max([
                max(metrics_participação_1), max(metrics_participação_2), 
                max(metrics_participação_3), max(metrics_participação_4),
                max(metrics_participação_5), max(metrics_participação_6),
                max(metrics_participação_7), max(metrics_participação_8),
                ])  # Add padding of 0.5

                min_value = -max(abs(min_value_test), max_value_test) -0.03
                max_value = -min_value

                # Create the plot
                fig = create_player_attributes_plot(
                    tabela_a=attribute_chart_z1,  # Your main dataframe
                    partida=partida,              # Name of partida to highlight
                    selected_clube=clube,         # Name of the clube to highlight
                    min_value=min_value,          # Minimum value for x-axis
                    max_value=max_value           # Maximum value for x-axis
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### TRANSIÇÃO OFENSIVA - métricas
                        - **Recuperações de posse**: Número de vezes que um time recupera a posse da bola após perdê-la.
                        - **Altura da recuperação de posse (m)**: Altura média no campo, medida em metros, onde ocorrem as recuperações da posse.
                        - **Posse mantida em 5s**: Número de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após ganhar o controle inicialmente.
                        - **Posse mantida em 5s (%)**: Porcentagem de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após retomar o controle inicialmente.
                        - **Entradas no último terço em 10s**: Número de vezes que um time move a bola com sucesso para o terço final do campo dentro de 10 segundos após recuperar a posse.
                        - **Entradas na área em 10s**: Número de vezes que uma equipe move a bola com sucesso para a área do adversário dentro de 10 segundos após recuperar a posse.
                        - **xG em 10s da recuperação da posse**: Gols esperados (não-pênaltis) acumulados (xG) de chutes feitos dentro de 10 segundos após uma equipe recuperar a posse.
                        - **xT em 10s da recuperação da posse**: Ameaça esperada acumulada (xT) gerada por ações dentro de 10 segundos após um time recuperar a posse de bola.
                        """)

                #####################################################################################################################
                #####################################################################################################################
                ##################################################################################################################### 
                #####################################################################################################################

            elif atributo == ("Ataque"):
                
                #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                # Dynamically create the HTML string with the 'partida' variable
                title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                # Use the dynamically created HTML string in st.markdown
                st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>O Ataque do {clube} <br>em relação aos demais jogos da Rodada</h3>",
                            unsafe_allow_html=True
                            )
                st.markdown(title_html, unsafe_allow_html=True)
                st.write("---")

                attribute_chart_z = dfc
                # Collecting data
                attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['rodada']==rodada_value)]
                #Collecting data to plot
                metrics = attribute_chart_z1.iloc[:, np.r_[41:47]].reset_index(drop=True)
                metrics_participação_1 = metrics.iloc[:, 0].tolist()
                metrics_participação_2 = metrics.iloc[:, 1].tolist()
                metrics_participação_3 = metrics.iloc[:, 2].tolist()
                metrics_participação_4 = metrics.iloc[:, 3].tolist()
                metrics_participação_5 = metrics.iloc[:, 4].tolist()
                metrics_participação_6 = metrics.iloc[:, 5].tolist()
                metrics_y = [0] * len(metrics_participação_1)

                # The specific data point you want to highlight
                highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                highlight = highlight.iloc[:, np.r_[41:47]].reset_index(drop=True)
                highlight_participação_1 = highlight.iloc[:, 0].tolist()
                highlight_participação_2 = highlight.iloc[:, 1].tolist()
                highlight_participação_3 = highlight.iloc[:, 2].tolist()
                highlight_participação_4 = highlight.iloc[:, 3].tolist()
                highlight_participação_5 = highlight.iloc[:, 4].tolist()
                highlight_participação_6 = highlight.iloc[:, 5].tolist()
                highlight_y = 0

                # Computing the selected player specific values
                highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

                highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

                # Computing the min and max value across all lists using a generator expression
                min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6
                                                    ])
                min_value = min_value - 0.1
                max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6
                                                    ])
                max_value = max_value + 0.1

                # Create two subplots vertically aligned with separate x-axes
                fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                # Building the Extended Title"
                rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                
                # Function to determine partida's rank in attribute in league
                def get_partida_rank(partida, temporada, column_name, dataframe):
                    # Filter the dataframe for the specified Temporada
                    filtered_df = dataframe[dataframe['Temporada'] == 2024]
                    
                    # Rank partidas based on the specified column in descending order
                    filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                    
                    # Find the rank of the specified partida
                    partida_row = filtered_df[filtered_df['partida'] == partida]
                    if not partida_row.empty:
                        return int(partida_row['Rank'].iloc[0])
                    else:
                        return None

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_1_ranking_value = (get_partida_rank(partida, 2024, "Field tilt (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_1_ranking_value}/{rows_count})"
                full_title_participação_1 = f"Field tilt (%) {output_str} {highlight_participação_1_value}"
                
                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_2_ranking_value = (get_partida_rank(partida, 2024, "Bola longa (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_2_ranking_value}/{rows_count})"
                full_title_participação_2 = f"Bola longa (%) {output_str} {highlight_participação_2_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_3_ranking_value = (get_partida_rank(partida, 2024, "Velocidade do passe", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_3_ranking_value}/{rows_count})"
                full_title_participação_3 = f"Velocidade do passe {output_str} {highlight_participação_3_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_4_ranking_value = (get_partida_rank(partida, 2024, "Entradas no último terço (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_4_ranking_value}/{rows_count})"
                full_title_participação_4 = f"Entradas no último terço (%) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_5_ranking_value = (get_partida_rank(partida, 2024, "Entradas na área (%)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_5_ranking_value}/{rows_count})"
                full_title_participação_5 = f"Entradas na área (%) {output_str} {highlight_participação_5_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_6_ranking_value = (get_partida_rank(partida, 2024, "xT (Ameaça esperada)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_6_ranking_value}/{rows_count})"
                full_title_participação_6 = f"xT (Ameaça esperada) {output_str} {highlight_participação_6_value}"

                ##############################################################################################################
                ##############################################################################################################
                #From Claude version2

                def calculate_ranks(values):
                    """Calculate ranks for a given metric, with highest values getting rank 1"""
                    return pd.Series(values).rank(ascending=False).astype(int).tolist()

                def prepare_data(tabela_a, metrics_cols):
                    """Prepare the metrics data dictionary with all required data"""
                    metrics_data = {}
                    
                    for col in metrics_cols:
                        # Store the metric values
                        metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                        # Calculate and store ranks
                        metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                        # Store partida names
                        metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        # Store clube names
                        metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()
                    
                    return metrics_data

                def get_clube_from_partida(partida, selected_clube=None):
                    """
                    Extract clube names from partida string
                    If selected_clube is provided and matches one of the clubes, return that clube
                    Otherwise return the first clube
                    """
                    parts = partida.split(" x ")
                    # Extract first clube (remove the score)
                    first_clube_parts = parts[0].strip().split(" ")
                    first_clube = " ".join(first_clube_parts[:-1])
                    
                    # Extract second clube (remove the score)
                    second_clube_parts = parts[1].strip().split(" ")
                    second_clube = " ".join(second_clube_parts[1:])
                    
                    if selected_clube == first_clube or selected_clube == second_clube:
                        return selected_clube
                    
                    return first_clube

                def create_player_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                    """
                    Create an interactive plot showing player attributes with hover information
                    
                    Parameters:
                    tabela_a (pd.DataFrame): DataFrame containing all player data
                    partida (str): Name of the partida to highlight
                    selected_clube (str, optional): Name of the clube to highlight
                    min_value (float): Minimum value for x-axis
                    max_value (float): Maximum value for x-axis
                    """
                    # Get the specific clube from the partida to highlight
                    highlight_clube = get_clube_from_partida(partida, selected_clube)
                    
                    # List of metrics to plot
                    metrics_list = ["Field tilt (%)", "Bola longa (%)", 
                            "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                            "xT (Ameaça esperada)"
                    ]

                    # Prepare all the data
                    metrics_data = prepare_data(tabela_a, metrics_list)
                    
                    # Calculate highlight data - filter by both partida and clube
                    highlight_data = {}
                    highlight_ranks = {}
                    
                    for metric in metrics_list:
                        # Find the row that matches both partida and clube
                        match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                        if not match_rows.empty:
                            highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                            # Calculate rank
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                        else:
                            # Fallback if no match
                            highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])
                    
                    # Total number of players
                    total_players = len(tabela_a)
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=9, 
                        cols=1,
                        subplot_titles=[
                            f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                            for metric in metrics_list
                        ],
                        vertical_spacing=0.04
                    )

                    # Update subplot titles font size and color
                    for i in fig['layout']['annotations']:
                        i['font'] = dict(size=17, color='black')

                    # Add traces for each metric
                    for idx, metric in enumerate(metrics_list, 1):
                        # Add scatter plot for all players
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_data[f'metrics_{metric}'],
                                y=[0] * len(metrics_data[f'metrics_{metric}']),
                                mode='markers',
                                name = f'Demais partidas do {clube}',
                                marker=dict(color='deepskyblue', size=8),
                                text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                customdata=list(zip(
                                    metrics_data[f'partida_names_{metric}'],
                                    metrics_data[f'clube_names_{metric}']
                                )),
                                hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                        
                        # Add highlighted player point
                        fig.add_trace(
                            go.Scatter(
                                x=[highlight_data[f'highlight_{metric}']],
                                y=[0],
                                mode='markers',
                                name=highlight_clube,
                                marker=dict(color='blue', size=12),
                                hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )

                    # Get the total number of metrics (subplots)
                    n_metrics = len(metrics_list)

                    # Update layout for each subplot
                    for i in range(1, n_metrics + 1):
                        if i == n_metrics:  # Only for the last subplot
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='black',
                                zerolinewidth=1,
                                showline=False,
                                ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                tickvals=[min_value/2, 0, max_value/2],
                                tickmode='array',
                                ticks="outside",
                                ticklen=2,
                                tickfont=dict(size=16),
                                tickangle=0,
                                side='bottom',
                                automargin=False,
                                row=i, 
                                col=1
                            )
                            # Adjust layout for the last subplot
                            fig.update_layout(
                                xaxis_tickfont_family="Arial",
                                margin=dict(b=0)  # Reduce bottom margin
                            )
                        else:  # For all other subplots
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='grey',
                                zerolinewidth=1,
                                showline=False,
                                showticklabels=False,  # Hide tick labels
                                row=i, 
                                col=1
                            )  # Reduces space between axis and labels

                        # Update layout for the entire figure
                        fig.update_yaxes(
                            showticklabels=False,
                            showgrid=False,
                            showline=False,
                            row=i, 
                            col=1
                        )

                    # Update layout for the entire figure
                    fig.update_layout(
                        height=650,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=0.10,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=16)
                        ),
                        margin=dict(t=100)
                    )

                    # Add x-axis label at the bottom
                    fig.add_annotation(
                        text="Desvio-padrão",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.20,
                        showarrow=False,
                        font=dict(size=16, color='black')
                    )

                    return fig

                # Calculate min and max values with some padding
                min_value_test = min([
                min(metrics_participação_1), min(metrics_participação_2), 
                min(metrics_participação_3), min(metrics_participação_4),
                min(metrics_participação_5), min(metrics_participação_6)
                ])  # Add padding of 0.5

                max_value_test = max([
                max(metrics_participação_1), max(metrics_participação_2), 
                max(metrics_participação_3), max(metrics_participação_4),
                max(metrics_participação_5), max(metrics_participação_6)
                ])  # Add padding of 0.5

                min_value = -max(abs(min_value_test), max_value_test) -0.03
                max_value = -min_value

                # Create the plot
                fig = create_player_attributes_plot(
                    tabela_a=attribute_chart_z1,  # Your main dataframe
                    partida=partida,              # Name of partida to highlight
                    selected_clube=clube,         # Name of the clube to highlight
                    min_value=min_value,          # Minimum value for x-axis
                    max_value=max_value           # Maximum value for x-axis
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### ATAQUE - métricas
                        - **Field tilt (%)**: Porcentagem de tempo que a bola está na metade de ataque do campo para um time específico em comparação com seu adversário.
                        - **Bola longa %**: Porcentagem de passes que são bolas longas, que são definidas como passes que percorrem uma distância significativa para chegar aos atacantes rapidamente.
                        - **Velocidade do passe**: Velocidade com que a equipe move a bola por meio de passes.
                        - **Entradas no último terço (%)**: Porcentagem de posses da equipe que progridem com sucesso para o terço final do campo.
                        - **Entradas na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT (ameaça esperada)**: Mede o quanto as ações com bola contribuem para a chance de um time marcar.
                        """)

            #####################################################################################################################
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################

            elif atributo == ("Criação de chances"):
           
                #Plotar Primeiro Gráfico - Dispersão dos partida da mesma posição na 2024 em eixo único:

                # Dynamically create the HTML string with the 'partida' variable
                title_html = f"<h3 style='text-align: center; color: blue;'>{partida}</h3>"
                # Use the dynamically created HTML string in st.markdown
                st.markdown(f"<h3 style='text-align: center; color: deepskyblue;'>Criação de Chances do {clube}<br>em relação aos demais jogos da Rodada</h3>",
                            unsafe_allow_html=True
                            )
                st.markdown(title_html, unsafe_allow_html=True)
                st.write("---")

                attribute_chart_z = dfc
                # Collecting data
                attribute_chart_z1 = attribute_chart_z[(attribute_chart_z['rodada']==rodada_value)]
                #Collecting data to plot
                metrics = attribute_chart_z1.iloc[:, np.r_[47:54]].reset_index(drop=True)
                metrics_participação_1 = metrics.iloc[:, 0].tolist()
                metrics_participação_2 = metrics.iloc[:, 1].tolist()
                metrics_participação_3 = metrics.iloc[:, 2].tolist()
                metrics_participação_4 = metrics.iloc[:, 3].tolist()
                metrics_participação_5 = metrics.iloc[:, 4].tolist()
                metrics_participação_6 = metrics.iloc[:, 5].tolist()
                metrics_participação_7 = metrics.iloc[:, 6].tolist()
                metrics_y = [0] * len(metrics_participação_1)

                # The specific data point you want to highlight
                highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)&(attribute_chart_z1['partida']==partida)]
                highlight = highlight.iloc[:, np.r_[47:54]].reset_index(drop=True)
                highlight_participação_1 = highlight.iloc[:, 0].tolist()
                highlight_participação_2 = highlight.iloc[:, 1].tolist()
                highlight_participação_3 = highlight.iloc[:, 2].tolist()
                highlight_participação_4 = highlight.iloc[:, 3].tolist()
                highlight_participação_5 = highlight.iloc[:, 4].tolist()
                highlight_participação_6 = highlight.iloc[:, 5].tolist()
                highlight_participação_7 = highlight.iloc[:, 6].tolist()
                highlight_y = 0

                # Computing the selected player specific values
                highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)
                highlight_participação_7_value = pd.DataFrame(highlight_participação_7).reset_index(drop=True)

                highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                highlight_participação_6_value = highlight_participação_6_value.iat[0,0]
                highlight_participação_7_value = highlight_participação_7_value.iat[0,0]

                # Computing the min and max value across all lists using a generator expression
                min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6,
                                                    metrics_participação_7 
                                                    ])
                min_value = min_value - 0.1
                max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                    metrics_participação_3, metrics_participação_4,
                                                    metrics_participação_5, metrics_participação_6,
                                                    metrics_participação_7
                                                    ])
                max_value = max_value + 0.1

                # Create two subplots vertically aligned with separate x-axes
                fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
                #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                # Building the Extended Title"
                rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                
                # Function to determine partida's rank in attribute in league
                def get_partida_rank(partida, temporada, column_name, dataframe):
                    # Filter the dataframe for the specified Temporada
                    filtered_df = dataframe[dataframe['Temporada'] == 2024]
                    
                    # Rank partidas based on the specified column in descending order
                    filtered_df['Rank'] = filtered_df[column_name].rank(ascending=False, method='min')
                    
                    # Find the rank of the specified partida
                    partida_row = filtered_df[filtered_df['partida'] == partida]
                    if not partida_row.empty:
                        return int(partida_row['Rank'].iloc[0])
                    else:
                        return None

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_1_ranking_value = (get_partida_rank(partida, 2024, "Toques na área", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_1_ranking_value}/{rows_count})"
                full_title_participação_1 = f"Toques na área {output_str} {highlight_participação_1_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_2_ranking_value = (get_partida_rank(partida, 2024, "Finalizações (pEntrada na área, %)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_2_ranking_value}/{rows_count})"
                full_title_participação_2 = f"Finalizações (pEntrada na área, %) {output_str} {highlight_participação_2_value}"
                
                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_3_ranking_value = (get_partida_rank(partida, 2024, "Finalizações (exceto pênaltis)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_3_ranking_value}/{rows_count})"
                full_title_participação_3 = f"Finalizações (exceto pênaltis) {output_str} {highlight_participação_3_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_4_ranking_value = (get_partida_rank(partida, 2024, "Grandes oportunidades", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_4_ranking_value}/{rows_count})"
                full_title_participação_4 = f"Grandes oportunidades {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_5_ranking_value = (get_partida_rank(partida, 2024, "xG (exceto pênaltis)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_5_ranking_value}/{rows_count})"
                full_title_participação_5 = f"xG (exceto pênaltis) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_6_ranking_value = (get_partida_rank(partida, 2024, "Gols (exceto pênaltis)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_6_ranking_value}/{rows_count})"
                full_title_participação_6 = f"Gols (exceto pênaltis) {output_str} {highlight_participação_4_value}"

                # Building the Extended Title"
                # Determining partida's rank in attribute in league
                participação_7_ranking_value = (get_partida_rank(partida, 2024, "xG (pFinalização)", attribute_chart_z1))

                # Data to plot
                output_str = f"({participação_7_ranking_value}/{rows_count})"
                full_title_participação_7 = f"xG (pFinalização) {output_str} {highlight_participação_4_value}"

                ##############################################################################################################
                ##############################################################################################################
                #From Claude version2

                def calculate_ranks(values):
                    """Calculate ranks for a given metric, with highest values getting rank 1"""
                    return pd.Series(values).rank(ascending=False).astype(int).tolist()

                def prepare_data(tabela_a, metrics_cols):
                    """Prepare the metrics data dictionary with all required data"""
                    metrics_data = {}
                    
                    for col in metrics_cols:
                        # Store the metric values
                        metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                        # Calculate and store ranks
                        metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                        # Store partida names
                        metrics_data[f'partida_names_{col}'] = tabela_a['partida'].tolist()
                        # Store clube names
                        metrics_data[f'clube_names_{col}'] = tabela_a['clube'].tolist()
                    
                    return metrics_data

                def get_clube_from_partida(partida, selected_clube=None):
                    """
                    Extract clube names from partida string
                    If selected_clube is provided and matches one of the clubes, return that clube
                    Otherwise return the first clube
                    """
                    parts = partida.split(" x ")
                    # Extract first clube (remove the score)
                    first_clube_parts = parts[0].strip().split(" ")
                    first_clube = " ".join(first_clube_parts[:-1])
                    
                    # Extract second clube (remove the score)
                    second_clube_parts = parts[1].strip().split(" ")
                    second_clube = " ".join(second_clube_parts[1:])
                    
                    if selected_clube == first_clube or selected_clube == second_clube:
                        return selected_clube
                    
                    return first_clube

                def create_player_attributes_plot(tabela_a, partida, selected_clube=None, min_value=None, max_value=None):
                    """
                    Create an interactive plot showing player attributes with hover information
                    
                    Parameters:
                    tabela_a (pd.DataFrame): DataFrame containing all player data
                    partida (str): Name of the partida to highlight
                    selected_clube (str, optional): Name of the clube to highlight
                    min_value (float): Minimum value for x-axis
                    max_value (float): Maximum value for x-axis
                    """
                    # Get the specific clube from the partida to highlight
                    highlight_clube = get_clube_from_partida(partida, selected_clube)
                    
                    # List of metrics to plot
                    metrics_list = ["Toques na área", "Finalizações (pEntrada na área, %)",
                            "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                            "Gols (exceto pênaltis)", "xG (pFinalização)"
                    ]

                    # Prepare all the data
                    metrics_data = prepare_data(tabela_a, metrics_list)
                    
                    # Calculate highlight data - filter by both partida and clube
                    highlight_data = {}
                    highlight_ranks = {}
                    
                    for metric in metrics_list:
                        # Find the row that matches both partida and clube
                        match_rows = tabela_a[(tabela_a['partida'] == partida) & (tabela_a['clube'] == highlight_clube)]
                        if not match_rows.empty:
                            highlight_data[f'highlight_{metric}'] = match_rows[metric].iloc[0]
                            # Calculate rank
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[match_rows.index].iloc[0])
                        else:
                            # Fallback if no match
                            highlight_data[f'highlight_{metric}'] = tabela_a[tabela_a['partida'] == partida][metric].iloc[0]
                            highlight_ranks[metric] = int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['partida'] == partida].index[0])
                    
                    # Total number of players
                    total_players = len(tabela_a)
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=9, 
                        cols=1,
                        subplot_titles=[
                            f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_players}) {highlight_data[f'highlight_{metric}']:.2f}"
                            for metric in metrics_list
                        ],
                        vertical_spacing=0.04
                    )

                    # Update subplot titles font size and color
                    for i in fig['layout']['annotations']:
                        i['font'] = dict(size=17, color='black')

                    # Add traces for each metric
                    for idx, metric in enumerate(metrics_list, 1):
                        # Add scatter plot for all players
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_data[f'metrics_{metric}'],
                                y=[0] * len(metrics_data[f'metrics_{metric}']),
                                mode='markers',
                                name = f'Demais partidas do {clube}',
                                marker=dict(color='deepskyblue', size=8),
                                text=[f"{rank}/{total_players}" for rank in metrics_data[f'ranks_{metric}']],
                                customdata=list(zip(
                                    metrics_data[f'partida_names_{metric}'],
                                    metrics_data[f'clube_names_{metric}']
                                )),
                                hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                        
                        # Add highlighted player point
                        fig.add_trace(
                            go.Scatter(
                                x=[highlight_data[f'highlight_{metric}']],
                                y=[0],
                                mode='markers',
                                name=highlight_clube,
                                marker=dict(color='blue', size=12),
                                hovertemplate=f'{partida}<br>{highlight_clube}<br>Rank: {highlight_ranks[metric]}/{total_players}<br>Value: %{{x:.2f}}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )

                    # Get the total number of metrics (subplots)
                    n_metrics = len(metrics_list)

                    # Update layout for each subplot
                    for i in range(1, n_metrics + 1):
                        if i == n_metrics:  # Only for the last subplot
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='black',
                                zerolinewidth=1,
                                showline=False,
                                ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                tickvals=[min_value/2, 0, max_value/2],
                                tickmode='array',
                                ticks="outside",
                                ticklen=2,
                                tickfont=dict(size=16),
                                tickangle=0,
                                side='bottom',
                                automargin=False,
                                row=i, 
                                col=1
                            )
                            # Adjust layout for the last subplot
                            fig.update_layout(
                                xaxis_tickfont_family="Arial",
                                margin=dict(b=0)  # Reduce bottom margin
                            )
                        else:  # For all other subplots
                            fig.update_xaxes(
                                range=[min_value, max_value],
                                showgrid=False,
                                zeroline=True,
                                zerolinecolor='grey',
                                zerolinewidth=1,
                                showline=False,
                                showticklabels=False,  # Hide tick labels
                                row=i, 
                                col=1
                            )  # Reduces space between axis and labels

                        # Update layout for the entire figure
                        fig.update_yaxes(
                            showticklabels=False,
                            showgrid=False,
                            showline=False,
                            row=i, 
                            col=1
                        )

                    # Update layout for the entire figure
                    fig.update_layout(
                        height=700,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=0.0,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=16)
                        ),
                        margin=dict(t=100)
                    )

                    # Add x-axis label at the bottom
                    fig.add_annotation(
                        text="Desvio-padrão",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.09,
                        showarrow=False,
                        font=dict(size=16, color='black')
                    )

                    return fig

                # Calculate min and max values with some padding
                min_value_test = min([
                min(metrics_participação_1), min(metrics_participação_2), 
                min(metrics_participação_3), min(metrics_participação_4),
                min(metrics_participação_5), min(metrics_participação_6),
                min(metrics_participação_7)
                ])  # Add padding of 0.5

                max_value_test = max([
                max(metrics_participação_1), max(metrics_participação_2), 
                max(metrics_participação_3), max(metrics_participação_4),
                max(metrics_participação_5), max(metrics_participação_6),
                max(metrics_participação_7)
                ])  # Add padding of 0.5

                min_value = -max(abs(min_value_test), max_value_test) -0.03
                max_value = -min_value

                # Create the plot
                fig = create_player_attributes_plot(
                    tabela_a=attribute_chart_z1,  # Your main dataframe
                    partida=partida,              # Name of partida to highlight
                    selected_clube=clube,         # Name of the clube to highlight
                    min_value=min_value,          # Minimum value for x-axis
                    max_value=max_value           # Maximum value for x-axis
                )

                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### CRIAÇÃO DE CHANCES - métricas
                        - **Toques na área**: Número de vezes que a equipe faz contato com a bola dentro da área do adversário.
                        - **Finalizações (pEntrada na área, %)**: Porcentagem de vezes que uma entrada na área do adversário resulta em um chute.
                        - **Finalizações (exceto pênaltis)**: Número total de finalizações da equipe, excluindo pênaltis.
                        - **Grandes oportunidades**: Número de finalizações em posições ou situações com alta probabilidade de gol.
                        - **xG (exceto pênaltis)**: Gols esperados, excluindo pênaltis. Quantifica a qualidade das chances de gol que um time tem, excluindo pênaltis.
                        - **Gols (exceto pênaltis)**: Número total de gols que a equipe marca, excluindo pênaltis.
                        - **xG (pFinalização)**: Gols esperados acumulados sem pênaltis (xG) divididos pelo número de finalizações.
                        """)

            #####################################################################################################################
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################

        elif st.session_state.selected_option == "Clube na Competição":

            # Select a club
            club_selected = clube

            # Get the image URL for the selected club
            image_url = club_image_paths[club_selected]

            # Center-align and display the image
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{image_url}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )                

            # Add further instructions here
            dfa = pd.read_csv("performance_round.csv")
            dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
            st.markdown("---")
            st.markdown(
                f"""
                <h3 style='text-align: center; color: blue;'>
                    Desempenho dos clubes <br>({clube} em destaque)<br>
                    Média móvel de 5 jogos
                </h3>
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='display: inline-flex; align-items: center;'>
                        <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                        <span style="color: blue;">{clube}</span>
                    </span>
                    <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                        <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                        <span>Demais clubes</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("---")

            def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                """
                Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                
                Parameters:
                dfa (pd.DataFrame): DataFrame with club performance data
                selected_clube (str): Name of the club to highlight
                attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                """
                # If no attributes provided, use columns 10-14
                if attributes is None:
                    attributes = dfa.columns[11:16]
                
                # Get all unique clubs and rounds
                all_clubs = dfa['clube'].unique()
                max_round = min(dfa['rodada'].max(), 38)
                
                # Prepare figure with subplots - vertical layout
                fig = make_subplots(
                    rows=len(attributes), 
                    cols=1,
                    subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                    shared_xaxes=True,
                    vertical_spacing=0.05
                )
                
                # Store moving averages for all clubs to calculate rankings later
                all_club_data = {}
                for attr in attributes:
                    all_club_data[attr] = {}
                
                # First pass: Calculate and store all moving averages
                for clube in all_clubs:
                    club_data = dfa[dfa['clube'] == clube]
                    
                    for i, attr in enumerate(attributes, 1):
                        # Initialize arrays for x and y values
                        rounds = []
                        moving_avgs = []
                        
                        # Calculate progressive means for rounds 1-4
                        for r in range(1, min(5, max_round + 1)):
                            club_rounds = club_data[club_data['rodada'] <= r]
                            if not club_rounds.empty:
                                rounds.append(r)
                                avg_value = club_rounds[attr].mean()
                                moving_avgs.append(avg_value)
                                
                                # Store the moving average for later ranking calculation
                                if r not in all_club_data[attr]:
                                    all_club_data[attr][r] = {}
                                all_club_data[attr][r][clube] = avg_value
                        
                        # Calculate 5-round moving averages for round 5 onwards
                        for r in range(5, max_round + 1):
                            club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                            if len(club_rounds) > 0:
                                rounds.append(r)
                                avg_value = club_rounds[attr].mean()
                                moving_avgs.append(avg_value)
                                
                                # Store the moving average for later ranking calculation
                                if r not in all_club_data[attr]:
                                    all_club_data[attr][r] = {}
                                all_club_data[attr][r][clube] = avg_value
                        
                        # Set line properties based on whether this is the selected club
                        line_width = 2 if clube == selected_clube else 0.4
                        line_color = 'blue' if clube == selected_clube else 'gray'
                        show_legend = True if clube == selected_clube else False
                        
                        # Store for second pass
                        if 'data_for_plots' not in locals():
                            data_for_plots = {}
                        if attr not in data_for_plots:
                            data_for_plots[attr] = {}
                        if clube not in data_for_plots[attr]:
                            data_for_plots[attr][clube] = {}
                        
                        data_for_plots[attr][clube]['rounds'] = rounds
                        data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                        data_for_plots[attr][clube]['line_width'] = line_width
                        data_for_plots[attr][clube]['line_color'] = line_color
                        data_for_plots[attr][clube]['show_legend'] = show_legend
                
                # Find global min and max values for each attribute to set y-axis ranges with extra padding
                y_ranges = {}
                for attr in attributes:
                    all_values = []
                    for club_data in all_club_data[attr].values():
                        all_values.extend(list(club_data.values()))
                        
                    if all_values:
                        # Add larger padding (20%) to min/max values to prevent data loss
                        min_val = min(all_values)
                        max_val = max(all_values)
                        padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                        y_ranges[attr] = [min_val - padding, max_val + padding]
                    else:
                        y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                        
                # Second pass: Calculate rankings based on moving averages and create plots
                for i, attr in enumerate(attributes, 1):
                    # Calculate rankings for each round based on stored moving averages
                    rankings_by_round = {}
                    for round_num in all_club_data[attr]:
                        # Get all clubs' values for this round and attribute
                        round_values = all_club_data[attr][round_num]
                        # Convert to Series and rank
                        import pandas as pd
                        rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                        rankings_by_round[round_num] = rankings
                    
                    # Now create the actual traces with correct rankings
                    for clube in all_clubs:
                        if clube not in data_for_plots[attr]:
                            continue  # Skip if no data
                            
                        rounds = data_for_plots[attr][clube]['rounds']
                        moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                        line_width = data_for_plots[attr][clube]['line_width']
                        line_color = data_for_plots[attr][clube]['line_color']
                        show_legend = data_for_plots[attr][clube]['show_legend']
                        
                        # Get rankings for each round
                        rankings = []
                        for r in rounds:
                            if r in rankings_by_round and clube in rankings_by_round[r]:
                                rankings.append(int(rankings_by_round[r][clube]))
                            else:
                                rankings.append("-")
                        
                        # Add trace with correct rankings
                        fig.add_trace(
                            go.Scatter(
                                x=rounds,
                                y=moving_avgs,
                                mode='lines',
                                name=clube if clube == selected_clube else None,
                                line=dict(width=line_width, color=line_color),
                                customdata=rankings,  # Pass correct rankings as custom data
                                hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                            ),
                            row=i,
                            col=1
                        )
                
                # Update subplot titles to remove 'undefined' and set color to black
                for i, title in enumerate(fig['layout']['annotations']):
                    if i < len(attributes):  # Only update the actual subplot titles
                        title['text'] = attributes[i].replace("_", " ").capitalize()
                        title['font'] = dict(color="black", size=18)
                        
                # Update layout for vertical arrangement - no legend
                fig.update_layout(
                    height=400 * len(attributes),
                    width=800,
                    showlegend=False,  # Disable legend completely
                    margin=dict(l=20, r=20, t=20, b=30)
                )
                
                # Update axes for vertical layout
                for i in range(1, len(attributes) + 1):
                    # Only show x-axis title for the last subplot
                    if i == len(attributes):
                        fig.update_xaxes(
                            title_text="Rodada", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1
                        )
                    else:
                        fig.update_xaxes(showticklabels=True, row=i, col=1)
                        
                    # Add y-axis title to each subplot and set y-axis range
                    fig.update_yaxes(
                        title_text="Valor do Atributo", 
                        title_font=dict(color="black", size=18  ),
                        row=i, 
                        col=1,
                        range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                    )
                
                return fig

            fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
            st.plotly_chart(fig, use_container_width=True)


            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            #INSERIR ANÁLISE POR ATRIBUTO

            atributos = ["Defesa", "Transição defensiva", "Transição ofensiva", 
                            "Ataque", "Criação de chances"]

            st.markdown("---")
            st.markdown(
                "<h3 style='text-align: center; color:black; '>Se quiser aprofundar, escolha o Atributo</h3>",
                unsafe_allow_html=True
            )
            atributo = st.selectbox("", options=atributos, index = None, placeholder = "Escolha o Atributo!")
            if atributo == ("Defesa"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Desempenho dos clubes <br>({clube} em destaque)<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube}</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                            <span>Demais clubes</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data
                    selected_clube (str): Name of the club to highlight
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    
                    # If no attributes provided, use columns 16-24
                    if attributes is None:
                        attributes = dfa.columns[17:25]
                    
                    # Get all unique clubs and rounds
                    all_clubs = dfa['clube'].unique()
                    max_round = min(dfa['rodada'].max(), 38)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Store moving averages for all clubs to calculate rankings later
                    all_club_data = {}
                    for attr in attributes:
                        all_club_data[attr] = {}
                    
                    # First pass: Calculate and store all moving averages
                    for clube in all_clubs:
                        club_data = dfa[dfa['clube'] == clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Set line properties based on whether this is the selected club
                            line_width = 2 if clube == selected_clube else 0.4
                            line_color = 'blue' if clube == selected_clube else 'gray'
                            show_legend = True if clube == selected_clube else False
                            
                            # Store for second pass
                            if 'data_for_plots' not in locals():
                                data_for_plots = {}
                            if attr not in data_for_plots:
                                data_for_plots[attr] = {}
                            if clube not in data_for_plots[attr]:
                                data_for_plots[attr][clube] = {}
                            
                            data_for_plots[attr][clube]['rounds'] = rounds
                            data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                            data_for_plots[attr][clube]['line_width'] = line_width
                            data_for_plots[attr][clube]['line_color'] = line_color
                            data_for_plots[attr][clube]['show_legend'] = show_legend
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        all_values = []
                        for club_data in all_club_data[attr].values():
                            all_values.extend(list(club_data.values()))
                            
                        if all_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(all_values)
                            max_val = max(all_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                            
                    # Second pass: Calculate rankings based on moving averages and create plots
                    for i, attr in enumerate(attributes, 1):
                        # Calculate rankings for each round based on stored moving averages
                        rankings_by_round = {}
                        for round_num in all_club_data[attr]:
                            # Get all clubs' values for this round and attribute
                            round_values = all_club_data[attr][round_num]
                            # Convert to Series and rank
                            import pandas as pd
                            rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                            rankings_by_round[round_num] = rankings
                        
                        # Now create the actual traces with correct rankings
                        for clube in all_clubs:
                            if clube not in data_for_plots[attr]:
                                continue  # Skip if no data
                                
                            rounds = data_for_plots[attr][clube]['rounds']
                            moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                            line_width = data_for_plots[attr][clube]['line_width']
                            line_color = data_for_plots[attr][clube]['line_color']
                            show_legend = data_for_plots[attr][clube]['show_legend']
                            
                            # Get rankings for each round
                            rankings = []
                            for r in rounds:
                                if r in rankings_by_round and clube in rankings_by_round[r]:
                                    rankings.append(int(rankings_by_round[r][clube]))
                                else:
                                    rankings.append("-")
                            
                            # Add trace with correct rankings
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=clube if clube == selected_clube else None,
                                    line=dict(width=line_width, color=line_color),
                                    customdata=rankings,  # Pass correct rankings as custom data
                                    hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                    showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                            
                    # Update layout for vertical arrangement - no legend
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800,
                        showlegend=False,  # Disable legend completely
                        margin=dict(l=20, r=20, t=20, b=30)
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor da Métrica", 
                            title_font=dict(color="black", size=18  ),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### DEFESA - métricas
                        - **PPDA**: “Passes por ação defensiva”. Mede a intensidade da pressão defensiva calculando o número de passes permitidos por um time antes de tentar uma ação defensiva. Quanto menor o PPDA, maior a intensidade da pressão defensiva. A análise é limitada aos 60% iniciais do campo do oponente.
                        - **Intensidade defensiva**: Número de duelos defensivos, duelos livres, interceptações, desarmes e faltas quando a posse é do adversário, ajustado pela posse do adversário.
                        - **Duelos defensivos vencidos (%)**: Porcentagem de duelos defensivos no solo que interrompem com sucesso a progressão de um oponente ou recuperam a posse de bola.
                        - **Altura defensiva (m)**: Altura média no campo, medida em metros, das ações defensivas de um time.
                        - **Velocidade do passe do adversário**: Velocidade com que o time adversário move a bola por meio de passes. Isso pode ser influenciado pelo estilo de jogo do adversário, como ataque direto ou futebol baseado em posse de bola.
                        - **Entradas do adversário no último terço (%)**: Porcentagem de posses do time adversário que progridem com sucesso para o terço final do campo.
                        - **Entradas do adversário na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT Adversário**: Ameaça esperada baseada em ações (xT) por 100 passes bem-sucedidos do adversário originados de dentro da área defensiva da equipe. 
                        """)
                
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            elif atributo == ("Transição defensiva"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Desempenho dos clubes <br>({clube} em destaque)<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube}</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                            <span>Demais clubes</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data
                    selected_clube (str): Name of the club to highlight
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 25-33
                    if attributes is None:
                        attributes = dfa.columns[25:33]
                    
                    # Get all unique clubs and rounds
                    all_clubs = dfa['clube'].unique()
                    max_round = min(dfa['rodada'].max(), 38)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Store moving averages for all clubs to calculate rankings later
                    all_club_data = {}
                    for attr in attributes:
                        all_club_data[attr] = {}
                    
                    # First pass: Calculate and store all moving averages
                    for clube in all_clubs:
                        club_data = dfa[dfa['clube'] == clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Set line properties based on whether this is the selected club
                            line_width = 2 if clube == selected_clube else 0.4
                            line_color = 'blue' if clube == selected_clube else 'gray'
                            show_legend = True if clube == selected_clube else False
                            
                            # Store for second pass
                            if 'data_for_plots' not in locals():
                                data_for_plots = {}
                            if attr not in data_for_plots:
                                data_for_plots[attr] = {}
                            if clube not in data_for_plots[attr]:
                                data_for_plots[attr][clube] = {}
                            
                            data_for_plots[attr][clube]['rounds'] = rounds
                            data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                            data_for_plots[attr][clube]['line_width'] = line_width
                            data_for_plots[attr][clube]['line_color'] = line_color
                            data_for_plots[attr][clube]['show_legend'] = show_legend
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        all_values = []
                        for club_data in all_club_data[attr].values():
                            all_values.extend(list(club_data.values()))
                            
                        if all_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(all_values)
                            max_val = max(all_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                            
                    # Second pass: Calculate rankings based on moving averages and create plots
                    for i, attr in enumerate(attributes, 1):
                        # Calculate rankings for each round based on stored moving averages
                        rankings_by_round = {}
                        for round_num in all_club_data[attr]:
                            # Get all clubs' values for this round and attribute
                            round_values = all_club_data[attr][round_num]
                            # Convert to Series and rank
                            import pandas as pd
                            rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                            rankings_by_round[round_num] = rankings
                        
                        # Now create the actual traces with correct rankings
                        for clube in all_clubs:
                            if clube not in data_for_plots[attr]:
                                continue  # Skip if no data
                                
                            rounds = data_for_plots[attr][clube]['rounds']
                            moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                            line_width = data_for_plots[attr][clube]['line_width']
                            line_color = data_for_plots[attr][clube]['line_color']
                            show_legend = data_for_plots[attr][clube]['show_legend']
                            
                            # Get rankings for each round
                            rankings = []
                            for r in rounds:
                                if r in rankings_by_round and clube in rankings_by_round[r]:
                                    rankings.append(int(rankings_by_round[r][clube]))
                                else:
                                    rankings.append("-")
                            
                            # Add trace with correct rankings
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=clube if clube == selected_clube else None,
                                    line=dict(width=line_width, color=line_color),
                                    customdata=rankings,  # Pass correct rankings as custom data
                                    hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                    showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                            
                    # Update layout for vertical arrangement - no legend
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800,
                        showlegend=False,  # Disable legend completely
                        margin=dict(l=20, r=20, t=20, b=30)
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor da Métrica", 
                            title_font=dict(color="black", size=18  ),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.write("---")
                st.markdown("""
                            ### TRANSIÇÃO DEFENSIVA - métricas
                        - **Perda de posse na linha baixa**: Perdas de posse devido a passes errados, erros de domínio ou duelos ofensivos perdidos, nos 40% defensivos da equipe, ajustados pela posse.
                        - **Altura da perda de posse (m)**: Altura média no campo, medida em metros, onde ocorrem perdas de posse.
                        - **Recuperações de posse em 5s %**: Porcentagem de recuperações de bola que ocorrem em até 5 segundos após a perda da posse.
                        - **Tempo médio ação defensiva (s)**: Tempo que o time leva para executar uma ação defensiva, após perder a posse de bola.
                        - **Tempo médio para recuperação de posse (s)**: Tempo que o time leva para recuperar a posse da bola após perdê-la.
                        - **Entradas do adversário no último terço em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso no último terço em até 10 segundos após a recuperação da posse.
                        - **Entradas do adversário na área em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso na área em até 10 segundos após a recuperação da posse.
                        - **xG do adversário em 10s da recuperação da posse**: Gols esperados não-pênaltis (xG) acumulados dos chutes do adversário que ocorrem dentro de 10 segundos após a recuperação da posse de bola.
                        """)
                
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            elif atributo == ("Transição ofensiva"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Desempenho dos clubes <br>({clube} em destaque)<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube}</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                            <span>Demais clubes</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data
                    selected_clube (str): Name of the club to highlight
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 33-41
                    if attributes is None:
                        attributes = dfa.columns[33:41]
                    
                    # Get all unique clubs and rounds
                    all_clubs = dfa['clube'].unique()
                    max_round = min(dfa['rodada'].max(), 38)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Store moving averages for all clubs to calculate rankings later
                    all_club_data = {}
                    for attr in attributes:
                        all_club_data[attr] = {}
                    
                    # First pass: Calculate and store all moving averages
                    for clube in all_clubs:
                        club_data = dfa[dfa['clube'] == clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Set line properties based on whether this is the selected club
                            line_width = 2 if clube == selected_clube else 0.4
                            line_color = 'blue' if clube == selected_clube else 'gray'
                            show_legend = True if clube == selected_clube else False
                            
                            # Store for second pass
                            if 'data_for_plots' not in locals():
                                data_for_plots = {}
                            if attr not in data_for_plots:
                                data_for_plots[attr] = {}
                            if clube not in data_for_plots[attr]:
                                data_for_plots[attr][clube] = {}
                            
                            data_for_plots[attr][clube]['rounds'] = rounds
                            data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                            data_for_plots[attr][clube]['line_width'] = line_width
                            data_for_plots[attr][clube]['line_color'] = line_color
                            data_for_plots[attr][clube]['show_legend'] = show_legend
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        all_values = []
                        for club_data in all_club_data[attr].values():
                            all_values.extend(list(club_data.values()))
                            
                        if all_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(all_values)
                            max_val = max(all_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                            
                    # Second pass: Calculate rankings based on moving averages and create plots
                    for i, attr in enumerate(attributes, 1):
                        # Calculate rankings for each round based on stored moving averages
                        rankings_by_round = {}
                        for round_num in all_club_data[attr]:
                            # Get all clubs' values for this round and attribute
                            round_values = all_club_data[attr][round_num]
                            # Convert to Series and rank
                            import pandas as pd
                            rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                            rankings_by_round[round_num] = rankings
                        
                        # Now create the actual traces with correct rankings
                        for clube in all_clubs:
                            if clube not in data_for_plots[attr]:
                                continue  # Skip if no data
                                
                            rounds = data_for_plots[attr][clube]['rounds']
                            moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                            line_width = data_for_plots[attr][clube]['line_width']
                            line_color = data_for_plots[attr][clube]['line_color']
                            show_legend = data_for_plots[attr][clube]['show_legend']
                            
                            # Get rankings for each round
                            rankings = []
                            for r in rounds:
                                if r in rankings_by_round and clube in rankings_by_round[r]:
                                    rankings.append(int(rankings_by_round[r][clube]))
                                else:
                                    rankings.append("-")
                            
                            # Add trace with correct rankings
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=clube if clube == selected_clube else None,
                                    line=dict(width=line_width, color=line_color),
                                    customdata=rankings,  # Pass correct rankings as custom data
                                    hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                    showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                            
                    # Update layout for vertical arrangement - no legend
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800,
                        showlegend=False,  # Disable legend completely
                        margin=dict(l=20, r=20, t=20, b=30)
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor da Métrica", 
                            title_font=dict(color="black", size=18  ),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)
                
                st.write("---")
                st.markdown("""
                            ### TRANSIÇÃO OFENSIVA - métricas
                        - **Recuperações de posse**: Número de vezes que um time recupera a posse da bola após perdê-la.
                        - **Altura da recuperação de posse (m)**: Altura média no campo, medida em metros, onde ocorrem as recuperações da posse.
                        - **Posse mantida em 5s**: Número de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após ganhar o controle inicialmente.
                        - **Posse mantida em 5s (%)**: Porcentagem de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após retomar o controle inicialmente.
                        - **Entradas no último terço em 10s**: Número de vezes que um time move a bola com sucesso para o terço final do campo dentro de 10 segundos após recuperar a posse.
                        - **Entradas na área em 10s**: Número de vezes que uma equipe move a bola com sucesso para a área do adversário dentro de 10 segundos após recuperar a posse.
                        - **xG em 10s da recuperação da posse**: Gols esperados (não-pênaltis) acumulados (xG) de chutes feitos dentro de 10 segundos após uma equipe recuperar a posse.
                        - **xT em 10s da recuperação da posse**: Ameaça esperada acumulada (xT) gerada por ações dentro de 10 segundos após um time recuperar a posse de bola.
                        """)

            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            elif atributo == ("Ataque"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Desempenho dos clubes <br>({clube} em destaque)<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube}</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                            <span>Demais clubes</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data
                    selected_clube (str): Name of the club to highlight
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 41:47
                    if attributes is None:
                        attributes = dfa.columns[np.r_[41:47]]
                    
                    # Get all unique clubs and rounds
                    all_clubs = dfa['clube'].unique()
                    max_round = min(dfa['rodada'].max(), 38)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Store moving averages for all clubs to calculate rankings later
                    all_club_data = {}
                    for attr in attributes:
                        all_club_data[attr] = {}
                    
                    # First pass: Calculate and store all moving averages
                    for clube in all_clubs:
                        club_data = dfa[dfa['clube'] == clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Set line properties based on whether this is the selected club
                            line_width = 2 if clube == selected_clube else 0.4
                            line_color = 'blue' if clube == selected_clube else 'gray'
                            show_legend = True if clube == selected_clube else False
                            
                            # Store for second pass
                            if 'data_for_plots' not in locals():
                                data_for_plots = {}
                            if attr not in data_for_plots:
                                data_for_plots[attr] = {}
                            if clube not in data_for_plots[attr]:
                                data_for_plots[attr][clube] = {}
                            
                            data_for_plots[attr][clube]['rounds'] = rounds
                            data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                            data_for_plots[attr][clube]['line_width'] = line_width
                            data_for_plots[attr][clube]['line_color'] = line_color
                            data_for_plots[attr][clube]['show_legend'] = show_legend
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        all_values = []
                        for club_data in all_club_data[attr].values():
                            all_values.extend(list(club_data.values()))
                            
                        if all_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(all_values)
                            max_val = max(all_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                            
                    # Second pass: Calculate rankings based on moving averages and create plots
                    for i, attr in enumerate(attributes, 1):
                        # Calculate rankings for each round based on stored moving averages
                        rankings_by_round = {}
                        for round_num in all_club_data[attr]:
                            # Get all clubs' values for this round and attribute
                            round_values = all_club_data[attr][round_num]
                            # Convert to Series and rank
                            import pandas as pd
                            rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                            rankings_by_round[round_num] = rankings
                        
                        # Now create the actual traces with correct rankings
                        for clube in all_clubs:
                            if clube not in data_for_plots[attr]:
                                continue  # Skip if no data
                                
                            rounds = data_for_plots[attr][clube]['rounds']
                            moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                            line_width = data_for_plots[attr][clube]['line_width']
                            line_color = data_for_plots[attr][clube]['line_color']
                            show_legend = data_for_plots[attr][clube]['show_legend']
                            
                            # Get rankings for each round
                            rankings = []
                            for r in rounds:
                                if r in rankings_by_round and clube in rankings_by_round[r]:
                                    rankings.append(int(rankings_by_round[r][clube]))
                                else:
                                    rankings.append("-")
                            
                            # Add trace with correct rankings
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=clube if clube == selected_clube else None,
                                    line=dict(width=line_width, color=line_color),
                                    customdata=rankings,  # Pass correct rankings as custom data
                                    hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                    showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                            
                    # Update layout for vertical arrangement - no legend
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800,
                        showlegend=False,  # Disable legend completely
                        margin=dict(l=20, r=20, t=20, b=30)
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor da Métrica", 
                            title_font=dict(color="black", size=18  ),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### ATAQUE - métricas
                        - **Field tilt (%)**: Porcentagem de tempo que a bola está na metade de ataque do campo para um time específico em comparação com seu adversário.
                        - **Bola longa %**: Porcentagem de passes que são bolas longas, que são definidas como passes que percorrem uma distância significativa para chegar aos atacantes rapidamente.
                        - **Velocidade do passe**: Velocidade com que a equipe move a bola por meio de passes.
                        - **Entradas no último terço (%)**: Porcentagem de posses da equipe que progridem com sucesso para o terço final do campo.
                        - **Entradas na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT (ameaça esperada)**: Mede o quanto as ações com bola contribuem para a chance de um time marcar.
                        """)
                
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            elif atributo == ("Criação de chances"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: blue;'>
                        Desempenho dos clubes <br>({clube} em destaque)<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube}</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: rgba(150,150,150,0.3); margin-right: 8px;'></span>
                            <span>Demais clubes</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_attribute_moving_averages(dfa, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for all clubs, highlighting the selected club.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data
                    selected_clube (str): Name of the club to highlight
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 47-54
                    if attributes is None:
                        attributes = dfa.columns[47:54]
                    
                    # Get all unique clubs and rounds
                    all_clubs = dfa['clube'].unique()
                    max_round = min(dfa['rodada'].max(), 38)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Store moving averages for all clubs to calculate rankings later
                    all_club_data = {}
                    for attr in attributes:
                        all_club_data[attr] = {}
                    
                    # First pass: Calculate and store all moving averages
                    for clube in all_clubs:
                        club_data = dfa[dfa['clube'] == clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    
                                    # Store the moving average for later ranking calculation
                                    if r not in all_club_data[attr]:
                                        all_club_data[attr][r] = {}
                                    all_club_data[attr][r][clube] = avg_value
                            
                            # Set line properties based on whether this is the selected club
                            line_width = 2 if clube == selected_clube else 0.4
                            line_color = 'blue' if clube == selected_clube else 'gray'
                            show_legend = True if clube == selected_clube else False
                            
                            # Store for second pass
                            if 'data_for_plots' not in locals():
                                data_for_plots = {}
                            if attr not in data_for_plots:
                                data_for_plots[attr] = {}
                            if clube not in data_for_plots[attr]:
                                data_for_plots[attr][clube] = {}
                            
                            data_for_plots[attr][clube]['rounds'] = rounds
                            data_for_plots[attr][clube]['moving_avgs'] = moving_avgs
                            data_for_plots[attr][clube]['line_width'] = line_width
                            data_for_plots[attr][clube]['line_color'] = line_color
                            data_for_plots[attr][clube]['show_legend'] = show_legend
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        all_values = []
                        for club_data in all_club_data[attr].values():
                            all_values.extend(list(club_data.values()))
                            
                        if all_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(all_values)
                            max_val = max(all_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                            
                    # Second pass: Calculate rankings based on moving averages and create plots
                    for i, attr in enumerate(attributes, 1):
                        # Calculate rankings for each round based on stored moving averages
                        rankings_by_round = {}
                        for round_num in all_club_data[attr]:
                            # Get all clubs' values for this round and attribute
                            round_values = all_club_data[attr][round_num]
                            # Convert to Series and rank
                            import pandas as pd
                            rankings = pd.Series(round_values).rank(ascending=False).astype(int).to_dict()
                            rankings_by_round[round_num] = rankings
                        
                        # Now create the actual traces with correct rankings
                        for clube in all_clubs:
                            if clube not in data_for_plots[attr]:
                                continue  # Skip if no data
                                
                            rounds = data_for_plots[attr][clube]['rounds']
                            moving_avgs = data_for_plots[attr][clube]['moving_avgs']
                            line_width = data_for_plots[attr][clube]['line_width']
                            line_color = data_for_plots[attr][clube]['line_color']
                            show_legend = data_for_plots[attr][clube]['show_legend']
                            
                            # Get rankings for each round
                            rankings = []
                            for r in rounds:
                                if r in rankings_by_round and clube in rankings_by_round[r]:
                                    rankings.append(int(rankings_by_round[r][clube]))
                                else:
                                    rankings.append("-")
                            
                            # Add trace with correct rankings
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=clube if clube == selected_clube else None,
                                    line=dict(width=line_width, color=line_color),
                                    customdata=rankings,  # Pass correct rankings as custom data
                                    hovertemplate=f'{clube}<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<br>Ranking: %{{customdata}}/20<extra></extra>',
                                    showlegend=show_legend if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                            
                    # Update layout for vertical arrangement - no legend
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800,
                        showlegend=False,  # Disable legend completely
                        margin=dict(l=20, r=20, t=20, b=30)
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor da Métrica", 
                            title_font=dict(color="black", size=18  ),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                fig = plot_attribute_moving_averages(dfa, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")
                st.markdown("""
                            ### CRIAÇÃO DE CHANCES - métricas
                        - **Toques na área**: Número de vezes que a equipe faz contato com a bola dentro da área do adversário.
                        - **Finalizações (pEntrada na área, %)**: Porcentagem de vezes que uma entrada na área do adversário resulta em um chute.
                        - **Finalizações (exceto pênaltis)**: Número total de finalizações da equipe, excluindo pênaltis.
                        - **Grandes oportunidades**: Número de finalizações em posições ou situações com alta probabilidade de gol.
                        - **xG (exceto pênaltis)**: Gols esperados, excluindo pênaltis. Quantifica a qualidade das chances de gol que um time tem, excluindo pênaltis.
                        - **Gols (exceto pênaltis)**: Número total de gols que a equipe marca, excluindo pênaltis.
                        - **xG (pFinalização)**: Gols esperados acumulados sem pênaltis (xG) divididos pelo número de finalizações.
                        """)
            
            #####################################################################################################################
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################

        elif st.session_state.selected_option == "2025 vs 2024":

            # Select a club
            club_selected = clube

            # Get the image URL for the selected club
            image_url = club_image_paths[club_selected]

            # Center-align and display the image
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{image_url}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )                

            # Add further instructions here
            dfa = pd.read_csv("performance_round.csv")
            dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
           
            dfb = pd.read_csv("performance_round_2024.csv")
            dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

            st.markdown("---")
            st.markdown(
                f"""
                <h3 style='text-align: center; color: black;'>
                    <br>{clube}<br>
                    Média móvel de 5 jogos
                </h3>
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span style='display: inline-flex; align-items: center;'>
                        <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                        <span style="color: blue;">{clube} - 2025</span>
                    </span>
                    <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                        <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                        <span style="color: red;">{clube} - 2024</span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("---")

            def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                """
                Plot moving averages of performance attributes for a selected club across two seasons.
                
                Parameters:
                dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                selected_clube (str): Name of the club to compare across seasons
                attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                """
                import pandas as pd
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                import numpy as np
                
                # If no attributes provided, use columns 10-14
                if attributes is None:
                    attributes = dfa.columns[11:16]
                
                # Get rounds
                max_round_a = min(dfa['rodada'].max(), 38)
                max_round_b = min(dfb['rodada'].max(), 38)
                max_round = max(max_round_a, max_round_b)
                
                # Prepare figure with subplots - vertical layout
                fig = make_subplots(
                    rows=len(attributes), 
                    cols=1,
                    subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                    shared_xaxes=True,
                    vertical_spacing=0.05
                )
                
                # Process data for both seasons
                seasons_data = {
                    '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                    '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                }
                
                # Store all values to calculate y-axis ranges
                all_values = {attr: [] for attr in attributes}
                
                # Process each season's data
                for season_name, season_info in seasons_data.items():
                    df = season_info['df']
                    color = season_info['color']
                    
                    # Filter data for the selected club only
                    club_data = df[df['clube'] == selected_clube]
                    
                    for i, attr in enumerate(attributes, 1):
                        # Initialize arrays for x and y values
                        rounds = []
                        moving_avgs = []
                        
                        # Calculate progressive means for rounds 1-4
                        for r in range(1, min(5, max_round + 1)):
                            club_rounds = club_data[club_data['rodada'] <= r]
                            if not club_rounds.empty:
                                rounds.append(r)
                                avg_value = club_rounds[attr].mean()
                                moving_avgs.append(avg_value)
                                all_values[attr].append(avg_value)
                        
                        # Calculate 5-round moving averages for round 5 onwards
                        for r in range(5, max_round + 1):
                            club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                            if len(club_rounds) > 0:
                                rounds.append(r)
                                avg_value = club_rounds[attr].mean()
                                moving_avgs.append(avg_value)
                                all_values[attr].append(avg_value)
                        
                        # Add trace for this season
                        fig.add_trace(
                            go.Scatter(
                                x=rounds,
                                y=moving_avgs,
                                mode='lines',
                                name=f"{season_name}",
                                line=dict(width=2, color=color),
                                hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                showlegend=True if i == 1 else False  # Only show in legend for first subplot
                            ),
                            row=i,
                            col=1
                        )
                
                # Find global min and max values for each attribute to set y-axis ranges with extra padding
                y_ranges = {}
                for attr in attributes:
                    attr_values = all_values[attr]
                    if attr_values:
                        # Add larger padding (20%) to min/max values to prevent data loss
                        min_val = min(attr_values)
                        max_val = max(attr_values)
                        padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                        y_ranges[attr] = [min_val - padding, max_val + padding]
                    else:
                        y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                
                # Update subplot titles to remove 'undefined' and set color to black
                for i, title in enumerate(fig['layout']['annotations']):
                    if i < len(attributes):  # Only update the actual subplot titles
                        title['text'] = attributes[i].replace("_", " ").capitalize()
                        title['font'] = dict(color="black", size=18)
                
                # Update layout for vertical arrangement
                fig.update_layout(
                    height=400 * len(attributes),
                    width=800
                )
                
                # Update axes for vertical layout
                for i in range(1, len(attributes) + 1):
                    # Only show x-axis title for the last subplot
                    if i == len(attributes):
                        fig.update_xaxes(
                            title_text="Rodada", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1
                        )
                    else:
                        fig.update_xaxes(showticklabels=True, row=i, col=1)
                        
                    # Add y-axis title to each subplot and set y-axis range
                    fig.update_yaxes(
                        title_text="Valor do Atributo", 
                        title_font=dict(color="black", size=18),
                        row=i, 
                        col=1,
                        range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                    )
                
                return fig

            # Usage:
            fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
            st.plotly_chart(fig, use_container_width=True)

            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            #INSERIR ANÁLISE POR ATRIBUTO

            atributos = ["Defesa", "Transição defensiva", "Transição ofensiva", 
                            "Ataque", "Criação de chances"]

            st.markdown("---")
            st.markdown(
                "<h3 style='text-align: center; color:black; '>Se quiser aprofundar, escolha o Atributo</h3>",
                unsafe_allow_html=True
            )
            atributo = st.selectbox("", options=atributos, index = None, placeholder = "Escolha o Atributo!")
            if atributo == ("Defesa"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
                dfb = pd.read_csv("performance_round_2024.csv")
                dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: black;'>
                        <br>{clube}<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube} - 2025</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                            <span style="color: red;">{clube} - 2024</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for a selected club across two seasons.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                    dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                    selected_clube (str): Name of the club to compare across seasons
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 16-24
                    if attributes is None:
                        attributes = dfa.columns[17:25]
                    
                    # Get rounds
                    max_round_a = min(dfa['rodada'].max(), 38)
                    max_round_b = min(dfb['rodada'].max(), 38)
                    max_round = max(max_round_a, max_round_b)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Process data for both seasons
                    seasons_data = {
                        '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                        '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                    }
                    
                    # Store all values to calculate y-axis ranges
                    all_values = {attr: [] for attr in attributes}
                    
                    # Process each season's data
                    for season_name, season_info in seasons_data.items():
                        df = season_info['df']
                        color = season_info['color']
                        
                        # Filter data for the selected club only
                        club_data = df[df['clube'] == selected_clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Add trace for this season
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=f"{season_name}",
                                    line=dict(width=2, color=color),
                                    hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                    showlegend=True if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        attr_values = all_values[attr]
                        if attr_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(attr_values)
                            max_val = max(attr_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                    
                    # Update layout for vertical arrangement
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor do Atributo", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                # Usage:
                fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### DEFESA - métricas
                        - **PPDA**: “Passes por ação defensiva”. Mede a intensidade da pressão defensiva calculando o número de passes permitidos por um time antes de tentar uma ação defensiva. Quanto menor o PPDA, maior a intensidade da pressão defensiva. A análise é limitada aos 60% iniciais do campo do oponente.
                        - **Intensidade defensiva**: Número de duelos defensivos, duelos livres, interceptações, desarmes e faltas quando a posse é do adversário, ajustado pela posse do adversário.
                        - **Duelos defensivos vencidos (%)**: Porcentagem de duelos defensivos no solo que interrompem com sucesso a progressão de um oponente ou recuperam a posse de bola.
                        - **Altura defensiva (m)**: Altura média no campo, medida em metros, das ações defensivas de um time.
                        - **Velocidade do passe do adversário**: Velocidade com que o time adversário move a bola por meio de passes. Isso pode ser influenciado pelo estilo de jogo do adversário, como ataque direto ou futebol baseado em posse de bola.
                        - **Entradas do adversário no último terço (%)**: Porcentagem de posses do time adversário que progridem com sucesso para o terço final do campo.
                        - **Entradas do adversário na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT Adversário**: Ameaça esperada baseada em ações (xT) por 100 passes bem-sucedidos do adversário originados de dentro da área defensiva da equipe. 
                        """)
                
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            if atributo == ("Transição defensiva"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
                dfb = pd.read_csv("performance_round_2024.csv")
                dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: black;'>
                        <br>{clube}<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube} - 2025</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                            <span style="color: red;">{clube} - 2024</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for a selected club across two seasons.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                    dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                    selected_clube (str): Name of the club to compare across seasons
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """

                    # If no attributes provided, use columns 16-24
                    if attributes is None:
                        attributes = dfa.columns[25:33]
                    
                    # Get rounds
                    max_round_a = min(dfa['rodada'].max(), 38)
                    max_round_b = min(dfb['rodada'].max(), 38)
                    max_round = max(max_round_a, max_round_b)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Process data for both seasons
                    seasons_data = {
                        '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                        '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                    }
                    
                    # Store all values to calculate y-axis ranges
                    all_values = {attr: [] for attr in attributes}
                    
                    # Process each season's data
                    for season_name, season_info in seasons_data.items():
                        df = season_info['df']
                        color = season_info['color']
                        
                        # Filter data for the selected club only
                        club_data = df[df['clube'] == selected_clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Add trace for this season
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=f"{season_name}",
                                    line=dict(width=2, color=color),
                                    hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                    showlegend=True if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        attr_values = all_values[attr]
                        if attr_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(attr_values)
                            max_val = max(attr_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                    
                    # Update layout for vertical arrangement
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor do Atributo", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                # Usage:
                fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### TRANSIÇÃO DEFENSIVA - métricas
                        - **Perda de posse na linha baixa**: Perdas de posse devido a passes errados, erros de domínio ou duelos ofensivos perdidos, nos 40% defensivos da equipe, ajustados pela posse.
                        - **Altura da perda de posse (m)**: Altura média no campo, medida em metros, onde ocorrem perdas de posse.
                        - **Recuperações de posse em 5s %**: Porcentagem de recuperações de bola que ocorrem em até 5 segundos após a perda da posse.
                        - **Tempo médio ação defensiva (s)**: Tempo que o time leva para executar uma ação defensiva, após perder a posse de bola.
                        - **Tempo médio para recuperação de posse (s)**: Tempo que o time leva para recuperar a posse da bola após perdê-la.
                        - **Entradas do adversário no último terço em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso no último terço em até 10 segundos após a recuperação da posse.
                        - **Entradas do adversário na área em 10s da recuperação da posse**: Número de vezes que o time adversário entra com sucesso na área em até 10 segundos após a recuperação da posse.
                        - **xG do adversário em 10s da recuperação da posse**: Gols esperados não-pênaltis (xG) acumulados dos chutes do adversário que ocorrem dentro de 10 segundos após a recuperação da posse de bola.
                        """)

            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            if atributo == ("Transição ofensiva"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
                dfb = pd.read_csv("performance_round_2024.csv")
                dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: black;'>
                        <br>{clube}<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube} - 2025</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                            <span style="color: red;">{clube} - 2024</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for a selected club across two seasons.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                    dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                    selected_clube (str): Name of the club to compare across seasons
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 31-39
                    if attributes is None:
                        attributes = dfa.columns[33:41]
                    
                    # Get rounds
                    max_round_a = min(dfa['rodada'].max(), 38)
                    max_round_b = min(dfb['rodada'].max(), 38)
                    max_round = max(max_round_a, max_round_b)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Process data for both seasons
                    seasons_data = {
                        '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                        '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                    }
                    
                    # Store all values to calculate y-axis ranges
                    all_values = {attr: [] for attr in attributes}
                    
                    # Process each season's data
                    for season_name, season_info in seasons_data.items():
                        df = season_info['df']
                        color = season_info['color']
                        
                        # Filter data for the selected club only
                        club_data = df[df['clube'] == selected_clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Add trace for this season
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=f"{season_name}",
                                    line=dict(width=2, color=color),
                                    hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                    showlegend=True if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        attr_values = all_values[attr]
                        if attr_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(attr_values)
                            max_val = max(attr_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                    
                    # Update layout for vertical arrangement
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor do Atributo", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                # Usage:
                fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### TRANSIÇÃO OFENSIVA - métricas
                        - **Recuperações de posse**: Número de vezes que um time recupera a posse da bola após perdê-la.
                        - **Altura da recuperação de posse (m)**: Altura média no campo, medida em metros, onde ocorrem as recuperações da posse.
                        - **Posse mantida em 5s**: Número de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após ganhar o controle inicialmente.
                        - **Posse mantida em 5s (%)**: Porcentagem de vezes que um time mantém a posse da bola com sucesso por pelo menos 5 segundos após retomar o controle inicialmente.
                        - **Entradas no último terço em 10s**: Número de vezes que um time move a bola com sucesso para o terço final do campo dentro de 10 segundos após recuperar a posse.
                        - **Entradas na área em 10s**: Número de vezes que uma equipe move a bola com sucesso para a área do adversário dentro de 10 segundos após recuperar a posse.
                        - **xG em 10s da recuperação da posse**: Gols esperados (não-pênaltis) acumulados (xG) de chutes feitos dentro de 10 segundos após uma equipe recuperar a posse.
                        - **xT em 10s da recuperação da posse**: Ameaça esperada acumulada (xT) gerada por ações dentro de 10 segundos após um time recuperar a posse de bola.
                        """)

            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            if atributo == ("Ataque"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
                dfb = pd.read_csv("performance_round_2024.csv")
                dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: black;'>
                        <br>{clube}<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube} - 2025</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                            <span style="color: red;">{clube} - 2024</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for a selected club across two seasons.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                    dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                    selected_clube (str): Name of the club to compare across seasons
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 39-46
                    if attributes is None:
                        attributes = dfa.columns[np.r_[41:47]]
                    
                    # Get rounds
                    max_round_a = min(dfa['rodada'].max(), 38)
                    max_round_b = min(dfb['rodada'].max(), 38)
                    max_round = max(max_round_a, max_round_b)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Process data for both seasons
                    seasons_data = {
                        '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                        '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                    }
                    
                    # Store all values to calculate y-axis ranges
                    all_values = {attr: [] for attr in attributes}
                    
                    # Process each season's data
                    for season_name, season_info in seasons_data.items():
                        df = season_info['df']
                        color = season_info['color']
                        
                        # Filter data for the selected club only
                        club_data = df[df['clube'] == selected_clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Add trace for this season
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=f"{season_name}",
                                    line=dict(width=2, color=color),
                                    hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                    showlegend=True if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        attr_values = all_values[attr]
                        if attr_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(attr_values)
                            max_val = max(attr_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                    
                    # Update layout for vertical arrangement
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor do Atributo", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                # Usage:
                fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### ATAQUE - métricas
                        - **Field tilt (%)**: Porcentagem de tempo que a bola está na metade de ataque do campo para um time específico em comparação com seu adversário.
                        - **Bola longa %**: Porcentagem de passes que são bolas longas, que são definidas como passes que percorrem uma distância significativa para chegar aos atacantes rapidamente.
                        - **Velocidade do passe**: Velocidade com que a equipe move a bola por meio de passes.
                        - **Entradas no último terço (%)**: Porcentagem de posses da equipe que progridem com sucesso para o terço final do campo.
                        - **Entradas na área (%)**: Porcentagem de posses ou passes que se movem com sucesso do terço final do campo para a área do adversário.
                        - **xT (ameaça esperada)**: Mede o quanto as ações com bola contribuem para a chance de um time marcar.
                        """)

            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            if atributo == ("Criação de chances"):

                dfa = pd.read_csv("performance_round.csv")
                dfa.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)
            
                dfb = pd.read_csv("performance_round_2024.csv")
                dfb.rename(columns={"avg_recovery_time_z": "Tempo médio para recuperação de posse (s)"}, inplace=True)

                st.markdown("---")
                st.markdown(
                    f"""
                    <h3 style='text-align: center; color: black;'>
                        <br>{clube}<br>
                        Média móvel de 5 jogos
                    </h3>
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <span style='display: inline-flex; align-items: center;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: blue; margin-right: 8px;'></span>
                            <span style="color: blue;">{clube} - 2025</span>
                        </span>
                        <span style='display: inline-flex; align-items: center; margin-left: 20px;'>
                            <span style='display: inline-block; width: 20px; height: 3px; background-color: red; margin-right: 8px;'></span>
                            <span style="color: red;">{clube} - 2024</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.write("---")

                def plot_club_seasons_comparison(dfa, dfb, selected_clube, attributes=None):
                    """
                    Plot moving averages of performance attributes for a selected club across two seasons.
                    
                    Parameters:
                    dfa (pd.DataFrame): DataFrame with club performance data for season 2025
                    dfb (pd.DataFrame): DataFrame with club performance data for season 2024
                    selected_clube (str): Name of the club to compare across seasons
                    attributes (list, optional): List of attribute column names to plot, defaults to columns 10-14
                    """
                    import pandas as pd
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    import numpy as np
                    
                    # If no attributes provided, use columns 47-54
                    if attributes is None:
                        attributes = dfa.columns[47:54]
                    
                    # Get rounds
                    max_round_a = min(dfa['rodada'].max(), 38)
                    max_round_b = min(dfb['rodada'].max(), 38)
                    max_round = max(max_round_a, max_round_b)
                    
                    # Prepare figure with subplots - vertical layout
                    fig = make_subplots(
                        rows=len(attributes), 
                        cols=1,
                        subplot_titles=[attr.replace("_", " ").capitalize() for attr in attributes],
                        shared_xaxes=True,
                        vertical_spacing=0.05
                    )
                    
                    # Process data for both seasons
                    seasons_data = {
                        '2025': {'df': dfa, 'color': 'blue', 'name': '2025'},
                        '2024': {'df': dfb, 'color': 'red', 'name': '2024'}
                    }
                    
                    # Store all values to calculate y-axis ranges
                    all_values = {attr: [] for attr in attributes}
                    
                    # Process each season's data
                    for season_name, season_info in seasons_data.items():
                        df = season_info['df']
                        color = season_info['color']
                        
                        # Filter data for the selected club only
                        club_data = df[df['clube'] == selected_clube]
                        
                        for i, attr in enumerate(attributes, 1):
                            # Initialize arrays for x and y values
                            rounds = []
                            moving_avgs = []
                            
                            # Calculate progressive means for rounds 1-4
                            for r in range(1, min(5, max_round + 1)):
                                club_rounds = club_data[club_data['rodada'] <= r]
                                if not club_rounds.empty:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Calculate 5-round moving averages for round 5 onwards
                            for r in range(5, max_round + 1):
                                club_rounds = club_data[(club_data['rodada'] > r-5) & (club_data['rodada'] <= r)]
                                if len(club_rounds) > 0:
                                    rounds.append(r)
                                    avg_value = club_rounds[attr].mean()
                                    moving_avgs.append(avg_value)
                                    all_values[attr].append(avg_value)
                            
                            # Add trace for this season
                            fig.add_trace(
                                go.Scatter(
                                    x=rounds,
                                    y=moving_avgs,
                                    mode='lines',
                                    name=f"{season_name}",
                                    line=dict(width=2, color=color),
                                    hovertemplate=f'{selected_clube} ({season_name})<br>Rodada: %{{x}}<br>{attr}: %{{y:.2f}}<extra></extra>',
                                    showlegend=True if i == 1 else False  # Only show in legend for first subplot
                                ),
                                row=i,
                                col=1
                            )
                    
                    # Find global min and max values for each attribute to set y-axis ranges with extra padding
                    y_ranges = {}
                    for attr in attributes:
                        attr_values = all_values[attr]
                        if attr_values:
                            # Add larger padding (20%) to min/max values to prevent data loss
                            min_val = min(attr_values)
                            max_val = max(attr_values)
                            padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.2
                            y_ranges[attr] = [min_val - padding, max_val + padding]
                        else:
                            y_ranges[attr] = [-1.2, 1.2]  # Default range if no data, with more padding
                    
                    # Update subplot titles to remove 'undefined' and set color to black
                    for i, title in enumerate(fig['layout']['annotations']):
                        if i < len(attributes):  # Only update the actual subplot titles
                            title['text'] = attributes[i].replace("_", " ").capitalize()
                            title['font'] = dict(color="black", size=18)
                    
                    # Update layout for vertical arrangement
                    fig.update_layout(
                        height=400 * len(attributes),
                        width=800
                    )
                    
                    # Update axes for vertical layout
                    for i in range(1, len(attributes) + 1):
                        # Only show x-axis title for the last subplot
                        if i == len(attributes):
                            fig.update_xaxes(
                                title_text="Rodada", 
                                title_font=dict(color="black", size=18),
                                row=i, 
                                col=1
                            )
                        else:
                            fig.update_xaxes(showticklabels=True, row=i, col=1)
                            
                        # Add y-axis title to each subplot and set y-axis range
                        fig.update_yaxes(
                            title_text="Valor do Atributo", 
                            title_font=dict(color="black", size=18),
                            row=i, 
                            col=1,
                            range=y_ranges[attributes[i-1]] if attributes[i-1] in y_ranges else None
                        )
                    
                    return fig

                # Usage:
                fig = plot_club_seasons_comparison(dfa, dfb, selected_clube=clube)
                st.plotly_chart(fig, use_container_width=True)

                st.write("---")

                st.markdown("""
                            ### CRIAÇÃO DE CHANCES - métricas
                        - **Toques na área**: Número de vezes que a equipe faz contato com a bola dentro da área do adversário.
                        - **Finalizações (pEntrada na área, %)**: Porcentagem de vezes que uma entrada na área do adversário resulta em um chute.
                        - **Finalizações (exceto pênaltis)**: Número total de finalizações da equipe, excluindo pênaltis.
                        - **Grandes oportunidades**: Número de finalizações em posições ou situações com alta probabilidade de gol.
                        - **xG (exceto pênaltis)**: Gols esperados, excluindo pênaltis. Quantifica a qualidade das chances de gol que um time tem, excluindo pênaltis.
                        - **Gols (exceto pênaltis)**: Número total de gols que a equipe marca, excluindo pênaltis.
                        - **xG (pFinalização)**: Gols esperados acumulados sem pênaltis (xG) divididos pelo número de finalizações.
                        """)
            
            #####################################################################################################################
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            ##################################################################################################################### 
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################
            #####################################################################################################################


        # Instructions based on selection
        if st.session_state.selected_option == "Análise de Performance":

            if clube:
                
                # Select a club
                club_selected = clube

                # Get the image URL for the selected club
                image_url = club_image_paths[club_selected]

                # Center-align and display the image
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center;">
                        <img src="{image_url}" width="150">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                #Escolha da Opção (Casa ou Fora)
                st.write("---")
                st.markdown("<h5 style='text-align: center;'>Jogando em Casa ou jogando Fora de Casa?</h5>", unsafe_allow_html=True)

                # Initialize the location option session state if it doesn't exist
                if 'location_option' not in st.session_state:
                    st.session_state.location_option = None
                    
                # Function to select location option (Casa/Fora)
                def select_location_option(option):
                    st.session_state.location_option = option

                # Define button styles for selected/unselected states
                selected_style = """
                <style>
                div[data-testid="stButton"] button.casa-fora-selected {
                    background-color: #FF4B4B !important;
                    color: white !important;
                    border-color: #FF0000 !important;
                }
                </style>
                """
                st.markdown(selected_style, unsafe_allow_html=True)

                # Create two rows with two buttons each for Casa/Fora
                col1, col2, col3 = st.columns([4, 1, 4])
                with col1:
                    # Use different button styles based on selection status
                    if st.session_state.location_option == "Casa":
                        # Create a custom HTML button when selected
                        st.markdown(
                            f"""
                            <div data-testid="stButton">
                                <button class="casa-fora-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                                    Casa
                                </button>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        st.button("Casa", type='secondary', use_container_width=True, 
                                on_click=select_location_option, args=("Casa",))
                        
                with col3:
                    # Use different button styles based on selection status
                    if st.session_state.location_option == "Fora":
                        # Create a custom HTML button when selected
                        st.markdown(
                            f"""
                            <div data-testid="stButton">
                                <button class="casa-fora-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                                    Fora
                                </button>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        st.button("Fora", type='secondary', use_container_width=True, 
                                on_click=select_location_option, args=("Fora",))
                        
                            
                #Selecting last up to five games of each club (home or away) 
                if st.session_state.location_option == "Casa":
                    # Your existing code for handling Casa selection
                    pass
                            
                    st.write("---")
                    st.markdown(f"<h3 style='text-align: center;'><b>Análise de Performance do {clube}<br>nos (até) últimos 5 jogos em Casa</b></h3>", unsafe_allow_html=True)

                    st.write("---")
                    
                    # Gráfico dos Atributos de Performance    
                    
                    #Tratamento da base de dados - PlayStyle Analysis - Inclusão da Rodada
                    df = pd.read_csv("performance_metrics.csv")
                    
                    # Numbering rounds
                    # 1. Sort the dataframe by 'date', 'game_id' and reset the index
                    df = df.sort_values(['date', 'game_id'], ascending=[True, True]).reset_index(drop=True)

                    # 2. Create the 'round' column (each round covers 20 rows)
                    df['round'] = (df.index // 20) + 1

                    # 3. Relocate the 'round' column to column position 1 (i.e., the second column)
                    cols = list(df.columns)
                    cols.remove('round')      # Remove 'round' from its current position
                    cols.insert(1, 'round')   # Insert 'round' at index 1
                    df = df[cols]
                    
                    # Initialize a new session state variable for this level                         
                    if 'analysis_type' not in st.session_state:                             
                        st.session_state.analysis_type = None                          

                    # Create a new callback function for this level                         
                    def select_analysis_type(option):                             
                        st.session_state.analysis_type = option                          

                    # Define a style for the analysis type buttons
                    analysis_type_style = """
                    <style>
                    div[data-testid="stButton"] button.analysis-type-selected {
                        background-color: #FF4B4B !important;
                        color: white !important;
                        border-color: #FF0000 !important;
                    }
                    </style>
                    """
                    st.markdown(analysis_type_style, unsafe_allow_html=True)

                    # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Casa"
                    dfa = df[df['place'] == "Casa"].groupby('team_name').tail(5)

                    # Create (últimos 5) jogos dataframe
                    jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
                    
                    # Reset index to match the original dataframe structure
                    jogos = jogos.reset_index()
                    jogos_df = jogos
                    
                    # Ensure dfa has the required columns
                    columns_to_average = dfa.columns[11:-1]

                    # Compute mean for each column for each "team_name"
                    dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()
                    

                    # Ensure dfb has the required columns
                    columns_to_normalize = dfb.columns[1:]

                    # Normalize selected columns while keeping "team_name"
                    dfc = dfb.copy()
                    dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

                    # Inverting the sign of inverted metrics
                    dfc["PPDA"] = -1*dfc["PPDA"]
                    dfc["opposition_pass_tempo"] = -1*dfc["opposition_pass_tempo"]
                    dfc["opposition_progression_percentage"] = -1*dfc["opposition_progression_percentage"]
                    dfc["opp_final_third_to_box_%"] = -1*dfc["opp_final_third_to_box_%"]
                    dfc["Opposition_xT"] = -1*dfc["Opposition_xT"]
                    dfc["high_turnovers"] = -1*dfc["high_turnovers"]
                    dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
                    dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
                    dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
                    dfc["opposition_xG_10s"] = -1*dfc["opposition_xG_10s"]
                    dfc["goals_conceded"] = -1*dfc["goals_conceded"]
                    
                    # Creating qualities columns
                    # Define the columns to average for each metric
                    defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                    "defensive_height", "opposition_pass_tempo",	
                                    "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                    "Opposition_xT"]

                    defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                    "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                    "opposition_box_entries_10s", "opposition_xG_10s"]

                    attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                    "retained_possessions_5s_%", "final_third_entries_10s",
                                                    "box_entries_10s", "xG_10s", "xT_10s"]

                    attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                    "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                    chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                            "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                        
                    # Compute the arithmetic mean for each metric and assign to the respective column
                    dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
                    dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
                    dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
                    dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
                    dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

                    # Get a list of the current columns
                    cols = list(dfc.columns)

                    # List of columns to be relocated
                    cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                    "attacking_z", "chance_creation_z"]

                    # Remove these columns from the list
                    for col in cols_to_remove:
                        cols.remove(col)

                    # Insert the columns in the desired order at index 1, adjusting the index as we go
                    for i, col in enumerate(cols_to_remove):
                        cols.insert(1 + i, col)

                    # Reorder the dataframe columns accordingly
                    dfc = dfc[cols]
                    
                    # Renaming columns
                    columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                        "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                        "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                        "defensive_intensity",
                                        "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",
                                        "Opposition_xT", "high_turnovers", "turnover_line_height",
                                        "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                        "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                        "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                        "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                        "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                        "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                        "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                        "goal_difference", "goals_conceded", "goals_scored"
                                        ]

                    columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                    "Posse adversário (%)", "Defesa", "Transição defensiva",
                                    "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                    "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                    "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                    "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                    "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                    "Entradas do adversário no último terço em 10s da recuperação da posse",
                                    "Entradas do adversário na área em 10s da recuperação da posse", 
                                    "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                    "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                    "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                    "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                    "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                    "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                    "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                    "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                    "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                        "Gols sofridos", "Gols marcados"
                                        ]

                    # Create a dictionary mapping old names to new names
                    rename_dict = dict(zip(columns_to_rename, columns_renamed))

                    # Rename columns in variable_df_z_team
                    dfc = dfc.rename(columns=rename_dict)
                    clube_data = dfc[dfc['clube'] == clube].set_index('clube')

                    # Select club attributes
                    dfc_attributes = dfc.iloc[:, np.r_[0:6]]
                    
                    # Select club metrics columns from dfc
                    dfc_metrics = dfc.iloc[:, np.r_[0, 7:30, 32:45]]

                    # Identify top 6 and bottom 6 metrics for the given clube
                    def filter_top_bottom_metrics(dfc_metrics, clube):
                        
                        # Select the row corresponding to the given club
                        clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                        
                        # Identify top 6 and bottom 6 metrics based on values (single row)
                        top_6_metrics = clube_data.iloc[0].nlargest(6).index
                        bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                        
                        # Keep only relevant columns
                        selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                        dfd = dfc_metrics[selected_columns]
                        
                        return dfd

                    # Example usage (assuming clube is defined somewhere)
                    dfd = filter_top_bottom_metrics(dfc_metrics, clube)
                    
                    #Building opponent and context data 
                    
                    ##################################################################################################################
                    ##################################################################################################################
                    
                    # Create full competition so far mean
                    dfe = df[df['place'] == "Casa"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

                    # Ensure dfa has the required columns
                    columns_to_average = dfe.columns[11:-1]

                    # Compute mean for each column for each "team_name"
                    dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

                    # Ensure dfb has the required columns
                    columns_to_normalize = dfe.columns[1:]

                    # Normalize selected columns while keeping "team_name"
                    dff = dfe.copy()
                    dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

                    # Inverting the sign of inverted metrics
                    dff["PPDA"] = -1*dff["PPDA"]
                    dff["opposition_pass_tempo"] = -1*dff["opposition_pass_tempo"]
                    dff["opposition_progression_percentage"] = -1*dff["opposition_progression_percentage"]
                    dff["opp_final_third_to_box_%"] = -1*dff["opp_final_third_to_box_%"]
                    dff["Opposition_xT"] = -1*dff["Opposition_xT"]
                    dff["high_turnovers"] = -1*dff["high_turnovers"]
                    dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
                    dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
                    dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
                    dff["opposition_xG_10s"] = -1*dff["opposition_xG_10s"]
                    dff["goals_conceded"] = -1*dff["goals_conceded"]
                    
                    # Creating qualities columns
                    # Define the columns to average for each metric
                    defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                    "defensive_height", "opposition_pass_tempo",	
                                    "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                    "Opposition_xT"]

                    defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                    "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                    "opposition_box_entries_10s", "opposition_xG_10s"]

                    attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                    "retained_possessions_5s_%", "final_third_entries_10s",
                                                    "box_entries_10s", "xG_10s", "xT_10s"]

                    attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                    "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                    chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                            "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                        
                    # Compute the arithmetic mean for each metric and assign to the respective column
                    dff["defence_z"] = dff[defence_metrics].mean(axis=1)
                    dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
                    dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
                    dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
                    dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

                    # Get a list of the current columns
                    cols = list(dff.columns)

                    # List of columns to be relocated
                    cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                    "attacking_z", "chance_creation_z"]

                    # Remove these columns from the list
                    for col in cols_to_remove:
                        cols.remove(col)

                    # Insert the columns in the desired order at index 1, adjusting the index as we go
                    for i, col in enumerate(cols_to_remove):
                        cols.insert(1 + i, col)

                    # Reorder the dataframe columns accordingly
                    dff = dff[cols]
                    
                    # Renaming columns
                    columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                        "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                        "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                        "defensive_intensity",
                                        "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",
                                        "Opposition_xT", "high_turnovers", "turnover_line_height",
                                        "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                        "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                        "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                        "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                        "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                        "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                        "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                        "goal_difference", "goals_conceded", "goals_scored"
                                        ]

                    columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                    "Posse adversário (%)", "Defesa", "Transição defensiva",
                                    "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                    "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                    "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                    "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                    "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                    "Entradas do adversário no último terço em 10s da recuperação da posse",
                                    "Entradas do adversário na área em 10s da recuperação da posse", 
                                    "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                    "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                    "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                    "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                    "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                    "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                    "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                    "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                    "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                        "Gols sofridos", "Gols marcados"
                                        ]

                    # Create a dictionary mapping old names to new names
                    rename_dict = dict(zip(columns_to_rename, columns_renamed))

                    # Rename columns in variable_df_z_team (dff has attributes)
                    dff = dff.rename(columns=rename_dict)
                    
                    # Create dfg dataframe from dff, selecting columns [1:] from dfg (dfg has metrics)
                    dfg = dff[dfd.columns[0:]]
                    
                    ##################################################################################################################### 
                    #####################################################################################################################
                    #################################################################################################################################
                    #################################################################################################################################
                    #################################################################################################################################

                    #Plotar Primeiro Gráfico - Dispersão dos atributos em eixo único:

                    # Apply CSS styling to the jogos dataframe
                    def style_jogos(df):
                        # First, let's drop the 'index' column if it exists
                        if 'index' in df.columns:
                            df = df.drop(columns=['index'])
                            
                        return df.style.set_table_styles([
                            {"selector": "th", "props": [("font-weight", "bold"), ("border-bottom", "1px solid black"), ("text-align", "center")]},
                            {"selector": "td", "props": [("border-bottom", "1px solid gray"), ("text-align", "center")]},
                            {"selector": "tbody tr th", "props": [("font-size", "1px")]},  # Set font size for index column to 1px
                            {"selector": "thead tr th:first-child", "props": [("font-size", "1px")]},  # Also set font size for index header
                            #{"selector": "table", "props": [("margin-left", "auto"), ("margin-right", "auto"), ("border-collapse", "collapse")]},
                            #{"selector": "table, th, td", "props": [("border", "none")]},  # Remove outer borders
                            {"selector": "tr", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                            {"selector": "th", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                            {"selector": "td", "props": [("border-left", "none"), ("border-right", "none")]}
                        ])

                    jogos = style_jogos(jogos)

                    # Display the styled dataframe in Streamlit using markdown
                    st.markdown(
                        '<div style="display: flex; justify-content: center;">' + jogos.to_html(border=0) + '</div>',
                        unsafe_allow_html=True
                    )

                    attribute_chart_z2 = dff
                    # The second specific data point you want to highlight
                    attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                    # Add the suffix "_completo" to the content of the "clube" column
                    attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                    
                    attribute_chart_z1 = dfc

                    # Add the single row from attribute_chart_z2 to attribute_chart_z1
                    attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                    
                    # Collecting data
                    #Collecting data to plot
                    metrics = attribute_chart_z1.iloc[:, np.r_[1:6]].reset_index(drop=True)
                    metrics_participação_1 = metrics.iloc[:, 0].tolist()
                    metrics_participação_2 = metrics.iloc[:, 1].tolist()
                    metrics_participação_3 = metrics.iloc[:, 2].tolist()
                    metrics_participação_4 = metrics.iloc[:, 3].tolist()
                    metrics_participação_5 = metrics.iloc[:, 4].tolist()
                    metrics_y = [0] * len(metrics_participação_1)

                    # The specific data point you want to highlight
                    highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                    highlight = highlight.iloc[:, np.r_[1:6]].reset_index(drop=True)
                    highlight_participação_1 = highlight.iloc[:, 0].tolist()
                    highlight_participação_2 = highlight.iloc[:, 1].tolist()
                    highlight_participação_3 = highlight.iloc[:, 2].tolist()
                    highlight_participação_4 = highlight.iloc[:, 3].tolist()
                    highlight_participação_5 = highlight.iloc[:, 4].tolist()
                    highlight_y = 0

                    # Computing the selected team specific values
                    highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                    highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                    highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                    highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                    highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)

                    highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                    highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                    highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                    highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                    highlight_participação_5_value = highlight_participação_5_value.iat[0,0]

                    # Computing the min and max value across all lists using a generator expression
                    min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                        metrics_participação_3, metrics_participação_4,
                                                        metrics_participação_5
                                                        ])
                    min_value = min_value - 0.1
                    max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                        metrics_participação_3, metrics_participação_4,
                                                        metrics_participação_5
                                                        ])
                    max_value = max_value + 0.1

                    # Create two subplots vertically aligned with separate x-axes
                    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
                    #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                    # Building the Extended Title"
                    rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                    
                    # Function to determine club's rank in metric in league
                    def get_clube_rank(clube, column_idx, dataframe):
                        # Get the actual column name from the index (using positions 1-7)
                        column_name = dataframe.columns[column_idx]
                        
                        # Rank clubs based on the specified column in descending order
                        dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                        
                        # Find the rank of the specified club
                        clube_row = dataframe[dataframe['clube'] == clube]
                        if not clube_row.empty:
                            return int(clube_row['Rank'].iloc[0])
                        else:
                            return None
                        
                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_1 = attribute_chart_z1.columns[1]
                    output_str = f"({participação_1_ranking_value}/{rows_count})"
                    full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_2 = attribute_chart_z1.columns[2]
                    output_str = f"({participação_2_ranking_value}/{rows_count})"
                    full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                    
                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_3 = attribute_chart_z1.columns[3]
                    output_str = f"({participação_3_ranking_value}/{rows_count})"
                    full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_4 = attribute_chart_z1.columns[4]
                    output_str = f"({participação_4_ranking_value}/{rows_count})"
                    full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_5 = attribute_chart_z1.columns[5]
                    output_str = f"({participação_5_ranking_value}/{rows_count})"
                    full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                    ##############################################################################################################
                    ##############################################################################################################
                    #From Claude version2

                    def calculate_ranks(values):
                        """Calculate ranks for a given metric, with highest values getting rank 1"""
                        return pd.Series(values).rank(ascending=False).astype(int).tolist()

                    def prepare_data(tabela_a, metrics_cols):
                        """Prepare the metrics data dictionary with all required data"""
                        metrics_data = {}
                        
                        for col in metrics_cols:
                            # Store the metric values
                            metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                            # Calculate and store ranks
                            metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                            # Store player names
                            metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                        
                        return metrics_data

                    def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                        """
                        Create an interactive plot showing club metrics with hover information
                        
                        Parameters:
                        tabela_a (pd.DataFrame): DataFrame containing all player data
                        club (str): clube
                        min_value (float): Minimum value for x-axis
                        max_value (float): Maximum value for x-axis
                        """
                        # List of metrics to plot
                        # Replace the hardcoded metrics_list with dynamic column retrieval
                        metrics_list = [tabela_a.columns[idx] for idx in range(1, 6)]

                        # Prepare all the data
                        metrics_data = prepare_data(tabela_a, metrics_list)
                        
                        # Calculate highlight data
                        highlight_data = {
                            f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                            for metric in metrics_list
                        }
                        
                        # Calculate highlight ranks
                        highlight_ranks = {
                            metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                            for metric in metrics_list
                        }
                        
                        # Total number of clubs
                        total_clubs = len(tabela_a)
                        
                        # Create subplots
                        fig = make_subplots(
                            rows=7, 
                            cols=1,
                            subplot_titles=[
                                f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                for metric in metrics_list
                            ],
                            vertical_spacing=0.04
                        )

                        # Update subplot titles font size and color
                        for i in fig['layout']['annotations']:
                            i['font'] = dict(size=17, color='black')

                        # Add traces for each metric
                        for idx, metric in enumerate(metrics_list, 1):
                            # Create list of colors and customize club names for legend
                            colors = []
                            custom_club_names = []
                            
                            # Track if we have any "_completo" clubs to determine if we need a legend entry
                            has_completo_clubs = False
                            
                            for name in metrics_data[f'player_names_{metric}']:
                                if '_completo' in name:
                                    colors.append('gold')
                                    has_completo_clubs = True
                                    # Strip "_completo" from name for display but add "(completo)" indicator
                                    clean_name = name.replace('_completo', '')
                                    custom_club_names.append(f"{clean_name} (completo)")
                                else:
                                    colors.append('deepskyblue')
                                    custom_club_names.append(name)
                            
                            # Add scatter plot for regular clubs
                            regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                            
                            if regular_clubs_indices:
                                fig.add_trace(
                                    go.Scatter(
                                        x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                        y=[0] * len(regular_clubs_indices),
                                        mode='markers',
                                        #name='Demais Clubes',
                                        name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                        marker=dict(
                                            color='deepskyblue',
                                            size=8
                                        ),
                                        text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                        customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            
                            # Add separate scatter plot for "_completo" clubs
                            completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                            
                            if completo_clubs_indices:
                                fig.add_trace(
                                    go.Scatter(
                                        x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                        y=[0] * len(completo_clubs_indices),
                                        mode='markers',
                                        #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                        name=f'<span style="color:gold;">{clube} (completo)</span>',
                                        marker=dict(
                                            color='gold',
                                            size=12
                                        ),
                                        text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                        customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            
                            # Prepare highlighted club name for display
                            highlight_display_name = clube
                            highlight_color = 'blue'
                            
                            if '_completo' in clube:
                                highlight_color = 'yellow'
                                highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                            
                            # Add highlighted player point
                            fig.add_trace(
                                go.Scatter(
                                    x=[highlight_data[f'highlight_{metric}']],
                                    y=[0],
                                    mode='markers',
                                    name=highlight_display_name,  # Use the formatted name
                                    marker=dict(
                                        color=highlight_color,
                                        size=12
                                    ),
                                    hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                    showlegend=True if idx == 1 else False
                                ),
                                row=idx, 
                                col=1
                            )
                        # Get the total number of metrics (subplots)
                        n_metrics = len(metrics_list)

                        # Update layout for each subplot
                        for i in range(1, n_metrics + 1):
                            if i == n_metrics:  # Only for the last subplot
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='black',
                                    zerolinewidth=1,
                                    showline=False,
                                    ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                    tickvals=[min_value/2, 0, max_value/2],
                                    tickmode='array',
                                    ticks="outside",
                                    ticklen=2,
                                    tickfont=dict(size=16),
                                    tickangle=0,
                                    side='bottom',
                                    automargin=False,
                                    row=i, 
                                    col=1
                                )
                                # Adjust layout for the last subplot
                                fig.update_layout(
                                    xaxis_tickfont_family="Arial",
                                    margin=dict(b=0)  # Reduce bottom margin
                                )
                            else:  # For all other subplots
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='grey',
                                    zerolinewidth=1,
                                    showline=False,
                                    showticklabels=False,  # Hide tick labels
                                    row=i, 
                                    col=1
                                )  # Reduces space between axis and labels

                            # Update layout for the entire figure
                            fig.update_yaxes(
                                showticklabels=False,
                                showgrid=False,
                                showline=False,
                                row=i, 
                                col=1
                            )

                        # Update layout for the entire figure
                        fig.update_layout(
                            height=600,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.12,
                                xanchor="center",
                                x=0.5,
                                font=dict(size=16)
                            ),
                            margin=dict(t=100)
                        )

                        # Add x-axis label at the bottom
                        fig.add_annotation(
                            text="Desvio-padrão",
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.02,
                            showarrow=False,
                            font=dict(size=16, color='black')
                        )

                        return fig

                    # Calculate min and max values with some padding
                    min_value_test = min([
                    min(metrics_participação_1), min(metrics_participação_2), 
                    min(metrics_participação_3), min(metrics_participação_4),
                    min(metrics_participação_5)
                    ])  # Add padding of 0.5

                    max_value_test = max([
                    max(metrics_participação_1), max(metrics_participação_2), 
                    max(metrics_participação_3), max(metrics_participação_4),
                    max(metrics_participação_5)
                    ])  # Add padding of 0.5

                    min_value = -max(abs(min_value_test), max_value_test) -0.03
                    max_value = -min_value

                    # Create the plot
                    fig = create_club_attributes_plot(
                        tabela_a=attribute_chart_z1,  # Your main dataframe
                        club=clube,  # Name of player to highlight
                        min_value= min_value,  # Minimum value for x-axis
                        max_value= max_value    # Maximum value for x-axis
                    )

                    st.plotly_chart(fig, use_container_width=True, key="unique_key_5")
                    st.write("---")

                    # Opção por plotar Destaques Positivos e Negativos
                    
                    # Check if the key exists in session state
                    if "show_destaques2" not in st.session_state:
                        st.session_state.show_destaques2 = False

                    # Your heading
                    st.markdown(f"<h4 style='text-align: center; color: black;'>Para ver os Destaques Positivos e Negativos do {clube}<br>nos últimos 5 jogos em Casa,<br>Clique abaixo!</h4>",
                                unsafe_allow_html=True)

                    # When the button is clicked, change session state
                    if st.button("Clique Aqui"):
                        st.session_state.show_destaques2 = True

                    # This content will persist after the button is clicked
                    if st.session_state.show_destaques2:

                        # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Casa"
                        dfa = df[df['place'] == "Casa"].groupby('team_name').tail(5)

                        # Create (últimos 5) jogos dataframe
                        jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
                        
                        # Reset index to match the original dataframe structure
                        jogos = jogos.reset_index()
                        jogos_df = jogos
                        
                        # Ensure dfa has the required columns
                        columns_to_average = dfa.columns[11:-1]

                        # Compute mean for each column for each "team_name"
                        dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()
                        

                        # Ensure dfb has the required columns
                        columns_to_normalize = dfb.columns[1:]

                        # Normalize selected columns while keeping "team_name"
                        dfc = dfb.copy()
                        dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

                        # Inverting the sign of inverted metrics
                        dfc["PPDA"] = -1*dfc["PPDA"]
                        dfc["opposition_pass_tempo"] = -1*dfc["opposition_pass_tempo"]
                        dfc["opposition_progression_percentage"] = -1*dfc["opposition_progression_percentage"]
                        dfc["opp_final_third_to_box_%"] = -1*dfc["opp_final_third_to_box_%"]
                        dfc["Opposition_xT"] = -1*dfc["Opposition_xT"]
                        dfc["high_turnovers"] = -1*dfc["high_turnovers"]
                        dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
                        dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
                        dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
                        dfc["opposition_xG_10s"] = -1*dfc["opposition_xG_10s"]
                        dfc["goals_conceded"] = -1*dfc["goals_conceded"]
                        
                        # Creating qualities columns
                        # Define the columns to average for each metric
                        defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                        "defensive_height", "opposition_pass_tempo",	
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                        "Opposition_xT"]

                        defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                        "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                        "opposition_box_entries_10s", "opposition_xG_10s"]

                        attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                        "retained_possessions_5s_%", "final_third_entries_10s",
                                                        "box_entries_10s", "xG_10s", "xT_10s"]

                        attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                        chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                                "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                            
                        # Compute the arithmetic mean for each metric and assign to the respective column
                        dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
                        dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
                        dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
                        dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
                        dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

                        # Get a list of the current columns
                        cols = list(dfc.columns)

                        # List of columns to be relocated
                        cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                        "attacking_z", "chance_creation_z"]

                        # Remove these columns from the list
                        for col in cols_to_remove:
                            cols.remove(col)

                        # Insert the columns in the desired order at index 1, adjusting the index as we go
                        for i, col in enumerate(cols_to_remove):
                            cols.insert(1 + i, col)

                        # Reorder the dataframe columns accordingly
                        dfc = dfc[cols]
                        
                        # Renaming columns
                        columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                            "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                            "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                            "defensive_intensity",
                                            "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                            "opposition_progression_percentage", "opp_final_third_to_box_%",
                                            "Opposition_xT", "high_turnovers", "turnover_line_height",
                                            "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                            "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                            "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                            "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                            "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                            "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                            "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                            "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                            "goal_difference", "goals_conceded", "goals_scored"
                                            ]

                        columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                        "Posse adversário (%)", "Defesa", "Transição defensiva",
                                        "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                        "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                        "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                        "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                        "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                        "Entradas do adversário no último terço em 10s da recuperação da posse",
                                        "Entradas do adversário na área em 10s da recuperação da posse", 
                                        "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                        "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                        "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                        "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                        "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                        "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                        "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                        "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                        "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                            "Gols sofridos", "Gols marcados"
                                            ]

                        # Create a dictionary mapping old names to new names
                        rename_dict = dict(zip(columns_to_rename, columns_renamed))

                        # Rename columns in variable_df_z_team
                        dfc = dfc.rename(columns=rename_dict)
                        clube_data = dfc[dfc['clube'] == clube].set_index('clube')

                        # Select club attributes
                        dfc_attributes = dfc.iloc[:, np.r_[0:6]]
                        
                        # Select club metrics columns from dfc
                        dfc_metrics = dfc.iloc[:, np.r_[0, 7:30, 32:45]]

                        # Identify top 6 and bottom 6 metrics for the given clube
                        def filter_top_bottom_metrics(dfc_metrics, clube):
                            
                            # Select the row corresponding to the given club
                            clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                            
                            # Identify top 6 and bottom 6 metrics based on values (single row)
                            top_6_metrics = clube_data.iloc[0].nlargest(6).index
                            bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                            
                            # Keep only relevant columns
                            selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                            dfd = dfc_metrics[selected_columns]
                            
                            return dfd

                        # Example usage (assuming clube is defined somewhere)
                        dfd = filter_top_bottom_metrics(dfc_metrics, clube)
                        
                        #Building opponent and context data 
                        
                        ##################################################################################################################
                        ##################################################################################################################
                        
                        # Create full competition so far mean
                        dfe = df[df['place'] == "Casa"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

                        # Ensure dfa has the required columns
                        columns_to_average = dfe.columns[11:-1]

                        # Compute mean for each column for each "team_name"
                        dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

                        # Ensure dfb has the required columns
                        columns_to_normalize = dfe.columns[1:]

                        # Normalize selected columns while keeping "team_name"
                        dff = dfe.copy()
                        dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

                        # Inverting the sign of inverted metrics
                        dff["PPDA"] = -1*dff["PPDA"]
                        dff["opposition_pass_tempo"] = -1*dff["opposition_pass_tempo"]
                        dff["opposition_progression_percentage"] = -1*dff["opposition_progression_percentage"]
                        dff["opp_final_third_to_box_%"] = -1*dff["opp_final_third_to_box_%"]
                        dff["Opposition_xT"] = -1*dff["Opposition_xT"]
                        dff["high_turnovers"] = -1*dff["high_turnovers"]
                        dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
                        dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
                        dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
                        dff["opposition_xG_10s"] = -1*dff["opposition_xG_10s"]
                        dff["goals_conceded"] = -1*dff["goals_conceded"]
                        
                        # Creating qualities columns
                        # Define the columns to average for each metric
                        defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                        "defensive_height", "opposition_pass_tempo",	
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                        "Opposition_xT"]

                        defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                        "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                        "opposition_box_entries_10s", "opposition_xG_10s"]

                        attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                        "retained_possessions_5s_%", "final_third_entries_10s",
                                                        "box_entries_10s", "xG_10s", "xT_10s"]

                        attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                        chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                                "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                            
                        # Compute the arithmetic mean for each metric and assign to the respective column
                        dff["defence_z"] = dff[defence_metrics].mean(axis=1)
                        dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
                        dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
                        dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
                        dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

                        # Get a list of the current columns
                        cols = list(dff.columns)

                        # List of columns to be relocated
                        cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                        "attacking_z", "chance_creation_z"]

                        # Remove these columns from the list
                        for col in cols_to_remove:
                            cols.remove(col)

                        # Insert the columns in the desired order at index 1, adjusting the index as we go
                        for i, col in enumerate(cols_to_remove):
                            cols.insert(1 + i, col)

                        # Reorder the dataframe columns accordingly
                        dff = dff[cols]
                        
                        # Renaming columns
                        columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                            "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                            "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                            "defensive_intensity",
                                            "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                            "opposition_progression_percentage", "opp_final_third_to_box_%",
                                            "Opposition_xT", "high_turnovers", "turnover_line_height",
                                            "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                            "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                            "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                            "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                            "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                            "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                            "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                            "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                            "goal_difference", "goals_conceded", "goals_scored"
                                            ]

                        columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                        "Posse adversário (%)", "Defesa", "Transição defensiva",
                                        "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                        "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                        "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                        "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                        "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                        "Entradas do adversário no último terço em 10s da recuperação da posse",
                                        "Entradas do adversário na área em 10s da recuperação da posse", 
                                        "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                        "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                        "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                        "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                        "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                        "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                        "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                        "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                        "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                            "Gols sofridos", "Gols marcados"
                                            ]

                        # Create a dictionary mapping old names to new names
                        rename_dict = dict(zip(columns_to_rename, columns_renamed))

                        # Rename columns in variable_df_z_team
                        dff = dff.rename(columns=rename_dict)
                        
                        # Create dfg dataframe from dff, selecting columns [1:] from dfd
                        dfg = dff[dfd.columns[0:]]
                        
                        ##################################################################################################################### 
                        #####################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################

                        #Plotar Primeiro Gráfico - Dispersão dos destaques positivos em eixo único:

                        st.write("---")

                        # Dynamically create the HTML string with the 'club' variable
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques positivos do {clube}<br>nos últimos 5 jogos em Casa</h4>",
                                    unsafe_allow_html=True
                                    )

                        attribute_chart_z2 = dfg
                        # The second specific data point you want to highlight
                        attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                        # Add the suffix "_completo" to the content of the "clube" column
                        attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                        
                        attribute_chart_z1 = dfd

                        # Add the single row from attribute_chart_z2 to attribute_chart_z1
                        attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                        
                        # Collecting data
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[1:7]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                        highlight = highlight.iloc[:, np.r_[1:7]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_y = 0

                        # Computing the selected team specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine club's rank in metric in league
                        def get_clube_rank(clube, column_idx, dataframe):
                            # Get the actual column name from the index (using positions 7-13)
                            column_name = dataframe.columns[column_idx]
                            
                            # Rank clubs based on the specified column in descending order
                            dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified club
                            clube_row = dataframe[dataframe['clube'] == clube]
                            if not clube_row.empty:
                                return int(clube_row['Rank'].iloc[0])
                            else:
                                return None
                            
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_1 = attribute_chart_z1.columns[1]
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_2 = attribute_chart_z1.columns[2]
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_3 = attribute_chart_z1.columns[3]
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_4 = attribute_chart_z1.columns[4]
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_5 = attribute_chart_z1.columns[5]
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_6_ranking_value = (get_clube_rank(clube, 6, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_6 = attribute_chart_z1.columns[6]
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                            
                            return metrics_data

                        def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                            """
                            Create an interactive plot showing club metrics with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            club (str): clube
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            # Replace the hardcoded metrics_list with dynamic column retrieval
                            metrics_list = [tabela_a.columns[idx] for idx in range(1, 7)]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of clubs
                            total_clubs = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=7, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Create list of colors and customize club names for legend
                                colors = []
                                custom_club_names = []
                                
                                # Track if we have any "_completo" clubs to determine if we need a legend entry
                                has_completo_clubs = False
                                
                                for name in metrics_data[f'player_names_{metric}']:
                                    if '_completo' in name:
                                        colors.append('gold')
                                        has_completo_clubs = True
                                        # Strip "_completo" from name for display but add "(completo)" indicator
                                        clean_name = name.replace('_completo', '')
                                        custom_club_names.append(f"{clean_name} (completo)")
                                    else:
                                        colors.append('deepskyblue')
                                        custom_club_names.append(name)
                                
                                # Add scatter plot for regular clubs
                                regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                                
                                if regular_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                            y=[0] * len(regular_clubs_indices),
                                            mode='markers',
                                            #name='Demais Clubes',
                                            name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                            marker=dict(
                                                color='deepskyblue',
                                                size=8
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                            customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Add separate scatter plot for "_completo" clubs
                                completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                                
                                if completo_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                            y=[0] * len(completo_clubs_indices),
                                            mode='markers',
                                            #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                            name=f'<span style="color:gold;">{clube} (completo)</span>',
                                            marker=dict(
                                                color='gold',
                                                size=12
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                            customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Prepare highlighted club name for display
                                highlight_display_name = clube
                                highlight_color = 'blue'
                                
                                if '_completo' in clube:
                                    highlight_color = 'yellow'
                                    highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=highlight_display_name,  # Use the formatted name
                                        marker=dict(
                                            color=highlight_color,
                                            size=12
                                        ),
                                        hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=600,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.02,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_club_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            club=clube,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True, key="unique_key_6")

                        ################################################################################################################################# 
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################

                        #Plotar Segundo Gráfico - Dispersão dos destaques negativos em eixo único:

                        # Dynamically create the HTML string with the 'club' variable
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques negativos do {clube}<br>nos últimos 5 jogos em Casa</h4>",
                                    unsafe_allow_html=True
                                    )

                        attribute_chart_z2 = dfg
                        # The second specific data point you want to highlight
                        attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                        # Add the suffix "_completo" to the content of the "clube" column
                        attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                        
                        attribute_chart_z1 = dfd

                        # Add the single row from attribute_chart_z2 to attribute_chart_z1
                        attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                        
                        # Collecting data
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[7:13]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                        highlight = highlight.iloc[:, np.r_[7:13]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_y = 0

                        # Computing the selected team specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine club's rank in metric in league
                        def get_clube_rank(clube, column_idx, dataframe):
                            # Get the actual column name from the index (using positions 7-13)
                            column_name = dataframe.columns[column_idx]
                            
                            # Rank clubs based on the specified column in descending order
                            dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified club
                            clube_row = dataframe[dataframe['clube'] == clube]
                            if not clube_row.empty:
                                return int(clube_row['Rank'].iloc[0])
                            else:
                                return None
                            
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_1_ranking_value = (get_clube_rank(clube, 7, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_1 = attribute_chart_z1.columns[7]
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_2_ranking_value = (get_clube_rank(clube, 8, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_2 = attribute_chart_z1.columns[8]
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_3_ranking_value = (get_clube_rank(clube, 9, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_3 = attribute_chart_z1.columns[9]
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_4_ranking_value = (get_clube_rank(clube, 10, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_4 = attribute_chart_z1.columns[10]
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_5_ranking_value = (get_clube_rank(clube, 11, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_5 = attribute_chart_z1.columns[11]
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_6_ranking_value = (get_clube_rank(clube, 12, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_6 = attribute_chart_z1.columns[12]
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                            
                            return metrics_data

                        def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                            """
                            Create an interactive plot showing club metrics with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            club (str): clube
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            # Replace the hardcoded metrics_list with dynamic column retrieval
                            metrics_list = [tabela_a.columns[idx] for idx in range(7, 13)]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of clubs
                            total_clubs = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=7, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Create list of colors and customize club names for legend
                                colors = []
                                custom_club_names = []
                                
                                # Track if we have any "_completo" clubs to determine if we need a legend entry
                                has_completo_clubs = False
                                
                                for name in metrics_data[f'player_names_{metric}']:
                                    if '_completo' in name:
                                        colors.append('gold')
                                        has_completo_clubs = True
                                        # Strip "_completo" from name for display but add "(completo)" indicator
                                        clean_name = name.replace('_completo', '')
                                        custom_club_names.append(f"{clean_name} (completo)")
                                    else:
                                        colors.append('deepskyblue')
                                        custom_club_names.append(name)
                                
                                # Add scatter plot for regular clubs
                                regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                                
                                if regular_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                            y=[0] * len(regular_clubs_indices),
                                            mode='markers',
                                            #name='Demais Clubes',
                                            name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                            marker=dict(
                                                color='deepskyblue',
                                                size=8
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                            customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Add separate scatter plot for "_completo" clubs
                                completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                                
                                if completo_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                            y=[0] * len(completo_clubs_indices),
                                            mode='markers',
                                            #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                            name=f'<span style="color:gold;">{clube} (completo)</span>',
                                            marker=dict(
                                                color='gold',
                                                size=12
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                            customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Prepare highlighted club name for display
                                highlight_display_name = clube
                                highlight_color = 'blue'
                                
                                if '_completo' in clube:
                                    highlight_color = 'yellow'
                                    highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=highlight_display_name,  # Use the formatted name
                                        marker=dict(
                                            color=highlight_color,
                                            size=12
                                        ),
                                        hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=600,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.02,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_club_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            club=clube,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True, key="unique_key_7")

                    ################################################################################################################################# 
                    #################################################################################################################################
                    ################################################################################################################################# 
                    #################################################################################################################################

                    #### INCLUIR BOT

                    # Create necessary files:
                    single_dfd = dfd[dfd["clube"] == clube]
                    single_dfd2 = dfc_attributes[dfc_attributes["clube"] == clube]
                    # Merge single_dfd and single_dfd2 based on "clube"
                    single_dfd = single_dfd.merge(single_dfd2, on="clube", how="left")
                    context_df = pd.read_csv("context.csv")
                    playstyle_df = pd.read_csv("play_style2.csv")
                    jogos_df = jogos_df.iloc[2]
                    
                    # Configure Google Gemini API
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

                    def generate_opponent_analysis(single_dfd, context_df, playstyle_df):
                        """
                        Generate a detailed club performance analysis based on the club's performance metrics.
                        
                        Args:
                            single_dfd (pd.DataFrame): DataFrame with club name and z-scores for better/worse metrics
                            context_df (pd.DataFrame): DataFrame with attributes and metrics definitions
                            playstyle_df (pd.DataFrame): DataFrame with play styles and their definitions
                        
                        Returns:
                            str: Generated club performance analysis in Portuguese
                        """
                        # Extract club name and metrics
                        clube = single_dfd.iloc[0, 0]
                        metricas_melhores = single_dfd.iloc[0, 1:7].to_dict()
                        metricas_piores = single_dfd.iloc[0, 7:13].to_dict()
                        attributes = single_dfd.iloc[0, 13:18].to_dict()
                        
                        # Sort metrics by z-score (abs value) to focus on most significant ones
                        metricas_melhores_sorted = {k: v for k, v in sorted(
                            metricas_melhores.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}
                        
                        metricas_piores_sorted = {k: v for k, v in sorted(
                            metricas_piores.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}
                        
                        attributes_sorted = {k: v for k, v in sorted(
                            attributes.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}
                        
                        # Create prompt for Gemini
                        prompt = (
                            f"Escreva uma análise aprofundada sobre a performance do clube {clube} baseada nos dados fornecidos, em português brasileiro. \n\n"
                            f"Escreva a análise sob a perspectiva da Comissão Técnica do clube {clube}, avaliando os pontos fortes e fracos de sua equipe. \n\n"
                            f"Análise geral sobre os atributos do clube {clube}:\n{pd.Series(attributes_sorted).to_string()}\n\n"
                            f"Pontos fortes (métricas em z-score nas quais o clube se destacou positivamente):\n{pd.Series(metricas_melhores_sorted).to_string()}\n\n"
                            f"Pontos fracos (métricas em z-score nas quais o clube se destacou negativamente):\n{pd.Series(metricas_piores_sorted).to_string()}\n\n"
                            f"Contexto Conceitual - Atributos e Métricas:\n{context_df.to_string()}\n\n"
                            "Considere o desempenho nos atributos e a relação entre as métricas destacadas e os atributos aos quais pertencem. "
                            "Inclua uma seção de pontos fortes, pontos fracos e recomendações de melhoria para o clube. "
                            "A análise deve ser bem estruturada, técnica mas compreensível e com aproximadamente 500 palavras. "
                            "Não apresente z-scores na análise final."
                        )
                        
                        # Generate the analysis using Gemini
                        model = genai.GenerativeModel("gemini-flash-latest")
                        response = model.generate_content(prompt)
                        
                        # Clean and format the response
                        analysis = response.text
                        
                        # Add title and formatting
                        formatted_analysis = f"""
                        ## {clube}
                    
                        {analysis}
                        """
                        
                        return formatted_analysis

                    def main():
                        st.write("---")

                        # Initialize session state variable
                        if "show_analise_adversario4" not in st.session_state:
                            st.session_state.show_analise_adversario4 = False

                        # Título estilizado
                        st.markdown(
                            """
                            <h3 style='text-align: center;'>Análise de Performance</h3>
                            """,
                            unsafe_allow_html=True
                        )

                        # Botão que ativa a exibição
                        if st.button("Gerar Análise de Performance", type='primary', key=106):
                            st.session_state.show_analise_adversario4 = True

                        # Conteúdo persistente após o clique
                        if st.session_state.show_analise_adversario4:

                            with st.spinner("Gerando análise de performance detalhada ..."):
                                analysis = generate_opponent_analysis(
                                    single_dfd,
                                    context_df,
                                    playstyle_df
                                )
                                
                                # Display the analysis
                                st.markdown(analysis)
                                
                                # Add download button for the analysis as PDF
                                import io
                                from fpdf import FPDF
                                
                                def create_pdf(text):
                                    text = text.replace('\u2013', '-')  # quick fix for en dash
                                    pdf = FPDF()
                                    pdf.add_page()
                                    pdf.set_auto_page_break(auto=True, margin=15)
                                    
                                    # Add title
                                    pdf.set_font("Arial", "B", 16)
                                    pdf.cell(0, 10, f"{clube}", ln=True)
                                    pdf.ln(5)
                                    
                                    # Add content
                                    pdf.set_font("Arial", "", 12)
                                    
                                    # Split text into lines and add to PDF
                                    lines = text.split('\n')
                                    for line in lines:
                                        # Check if line is a header
                                        if line.strip().startswith('#'):
                                            pdf.set_font("Arial", "B", 14)
                                            pdf.cell(0, 10, line.replace('#', '').strip(), ln=True)
                                            pdf.set_font("Arial", "", 12)
                                        else:
                                            pdf.multi_cell(0, 10, line)
                                    
                                    return pdf.output(dest="S").encode("latin-1", errors="replace")
                                
                                clube = single_dfd.iloc[0, 0]
                                pdf_data = create_pdf(analysis)
                                
                                st.download_button(
                                    label="Baixar Análise como PDF",
                                    data=pdf_data,
                                    file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.pdf",
                                    mime="application/pdf",
                                        key=204
                                )

                                # Add download button for the analysis
                                clube = single_dfd.iloc[0, 0]
                                st.download_button(
                                    label="Baixar Análise como TXT",
                                    data=analysis,
                                    file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.txt",
                                    mime="text/plain",
                                        key=205
                                )

                    if __name__ == "__main__":
                        main()

                    ################################################################################################################################# 
                    #################################################################################################################################
                    ################################################################################################################################# 
                    #################################################################################################################################

                    #### INCLUIR NOTA COM DESCRIÇÃO DAS MÉTRICAS FORTES E FRACAS
                    st.write("---")

                    st.markdown(
                        """
                        <h3 style='text-align: center;'>Quer saber as definições das Métricas? Clique abaixo!</h3>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button("Definições das Métricas", type='primary', key=107):

                        st.markdown("<p style='font-size:24px; font-weight:bold;'>Nota:</p>", unsafe_allow_html=True)
                        
                        def generate_metrics_sections(dfd, context_df):
                            # Generate positive metrics section (columns 1-7)
                            positive_metrics_names = dfd.columns[1:7]
                            
                            # Initialize positive definitions list
                            positive_metrics_definitions = []
                            
                            # For each positive metric name, find its definition in context_df
                            for metric_name in positive_metrics_names:
                                # Find the row where 'Métrica' column equals the metric name
                                matching_row = context_df[context_df['Métrica'] == metric_name]
                                
                                # If a match is found, add the definition to the list
                                if not matching_row.empty:
                                    definition = matching_row['Definição'].values[0]
                                    positive_metrics_definitions.append(definition)
                                else:
                                    # If no match is found, add an empty string as placeholder
                                    positive_metrics_definitions.append("")
                            
                            # Create the positive metrics markdown
                            positive_markdown = "#### MÉTRICAS COM DESTAQUE POSITIVO\n"
                            for name, definition in zip(positive_metrics_names, positive_metrics_definitions):
                                positive_markdown += f"- **{name}**: {definition}\n"
                            
                            # Generate negative metrics section (columns 7-13)
                            negative_metrics_names = dfd.columns[7:13]
                            
                            # Initialize negative definitions list
                            negative_metrics_definitions = []
                            
                            # For each negative metric name, find its definition in context_df
                            for metric_name in negative_metrics_names:
                                # Find the row where 'Métrica' column equals the metric name
                                matching_row = context_df[context_df['Métrica'] == metric_name]
                                
                                # If a match is found, add the definition to the list
                                if not matching_row.empty:
                                    definition = matching_row['Definição'].values[0]
                                    negative_metrics_definitions.append(definition)
                                else:
                                    # If no match is found, add an empty string as placeholder
                                    negative_metrics_definitions.append("")
                            
                            # Create the negative metrics markdown
                            negative_markdown = "#### MÉTRICAS COM DESTAQUE NEGATIVO\n"
                            for name, definition in zip(negative_metrics_names, negative_metrics_definitions):
                                negative_markdown += f"- **{name}**: {definition}\n"
                            
                            # Display both sections
                            st.markdown(positive_markdown)
                            st.markdown(negative_markdown)

                        # Example usage:
                        generate_metrics_sections(dfd, context_df)

                        ################################################################################################################################# 
                        #################################################################################################################################
                        ################################################################################################################################# 
                        #################################################################################################################################

                #Selecting last up to five games of each club (home or away) 
                elif st.session_state.location_option == "Fora":
                    # --- FORA PATH ---
                    st.write("---")
                    
                    st.markdown(f"<h3 style='text-align: center;'><b>Análise de Performance do {clube}<br> nos (até) últimos 5 jogos  Fora de Casa</b></h3>", unsafe_allow_html=True)

                    st.write("---")
                        
                    # Gráfico dos Atributos de Performance    
                    
                    #Tratamento da base de dados - PlayStyle Analysis - Inclusão da Rodada
                    df = pd.read_csv("performance_metrics.csv")
                    
                    # Numbering rounds
                    # 1. Sort the dataframe by 'date', 'game_id' and reset the index
                    df = df.sort_values(['date', 'game_id'], ascending=[True, True]).reset_index(drop=True)

                    # 2. Create the 'round' column (each round covers 20 rows)
                    df['round'] = (df.index // 20) + 1

                    # 3. Relocate the 'round' column to column position 1 (i.e., the second column)
                    cols = list(df.columns)
                    cols.remove('round')      # Remove 'round' from its current position
                    cols.insert(1, 'round')   # Insert 'round' at index 1
                    df = df[cols]
                    
                    # Initialize a new session state variable for this level                         
                    if 'analysis_type' not in st.session_state:                             
                        st.session_state.analysis_type = None                          

                    # Create a new callback function for this level                         
                    def select_analysis_type(option):                             
                        st.session_state.analysis_type = option                          

                    # Define a style for the analysis type buttons
                    analysis_type_style = """
                    <style>
                    div[data-testid="stButton"] button.analysis-type-selected {
                        background-color: #FF4B4B !important;
                        color: white !important;
                        border-color: #FF0000 !important;
                    }
                    </style>
                    """
                    st.markdown(analysis_type_style, unsafe_allow_html=True)

                    # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Fora"
                    dfa = df[df['place'] == "Fora"].groupby('team_name').tail(5)

                    # Create (últimos 5) jogos dataframe
                    jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
                    
                    # Reset index to match the original dataframe structure
                    jogos = jogos.reset_index()
                    jogos_df = jogos
                    
                    # Ensure dfa has the required columns
                    columns_to_average = dfa.columns[11:-1]

                    # Compute mean for each column for each "team_name"
                    dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()
                    dfb_fora = dfb.to_csv("dfb_fora.csv")

                    # Ensure dfb has the required columns
                    columns_to_normalize = dfb.columns[1:]

                    # Normalize selected columns while keeping "team_name"
                    dfc = dfb.copy()
                    dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

                    # Inverting the sign of inverted metrics
                    dfc["PPDA"] = -1*dfc["PPDA"]
                    dfc["opposition_pass_tempo"] = -1*dfc["opposition_pass_tempo"]
                    dfc["opposition_progression_percentage"] = -1*dfc["opposition_progression_percentage"]
                    dfc["opp_final_third_to_box_%"] = -1*dfc["opp_final_third_to_box_%"]
                    dfc["Opposition_xT"] = -1*dfc["Opposition_xT"]
                    dfc["high_turnovers"] = -1*dfc["high_turnovers"]
                    dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
                    dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
                    dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
                    dfc["opposition_xG_10s"] = -1*dfc["opposition_xG_10s"]
                    dfc["goals_conceded"] = -1*dfc["goals_conceded"]
                    
                    # Creating qualities columns
                    # Define the columns to average for each metric
                    defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                    "defensive_height", "opposition_pass_tempo",	
                                    "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                    "Opposition_xT"]

                    defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                    "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                    "opposition_box_entries_10s", "opposition_xG_10s"]

                    attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                    "retained_possessions_5s_%", "final_third_entries_10s",
                                                    "box_entries_10s", "xG_10s", "xT_10s"]

                    attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                    "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                    chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                            "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                    # Compute the arithmetic mean for each metric and assign to the respective column
                    dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
                    dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
                    dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
                    dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
                    dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

                    # Get a list of the current columns
                    cols = list(dfc.columns)

                    # List of columns to be relocated
                    cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                    "attacking_z", "chance_creation_z"]

                    # Remove these columns from the list
                    for col in cols_to_remove:
                        cols.remove(col)

                    # Insert the columns in the desired order at index 1, adjusting the index as we go
                    for i, col in enumerate(cols_to_remove):
                        cols.insert(1 + i, col)

                    # Reorder the dataframe columns accordingly
                    dfc = dfc[cols]
                    
                    # Renaming columns
                    columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                        "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                        "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                        "defensive_intensity",
                                        "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",
                                        "Opposition_xT", "high_turnovers", "turnover_line_height",
                                        "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                        "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                        "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                        "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                        "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                        "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                        "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                        "goal_difference", "goals_conceded", "goals_scored"
                                        ]

                    columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                    "Posse adversário (%)", "Defesa", "Transição defensiva",
                                    "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                    "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                    "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                    "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                    "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                    "Entradas do adversário no último terço em 10s da recuperação da posse",
                                    "Entradas do adversário na área em 10s da recuperação da posse", 
                                    "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                    "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                    "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                    "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                    "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                    "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                    "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                    "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                    "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                        "Gols sofridos", "Gols marcados"
                                        ]

                    # Create a dictionary mapping old names to new names
                    rename_dict = dict(zip(columns_to_rename, columns_renamed))

                    # Rename columns in variable_df_z_team
                    dfc = dfc.rename(columns=rename_dict)
                    clube_data = dfc[dfc['clube'] == clube].set_index('clube')

                    # Select club attributes
                    dfc_attributes = dfc.iloc[:, np.r_[0:6]]
                    
                    # Select club metrics columns from dfc
                    dfc_metrics = dfc.iloc[:, np.r_[0, 6:43]] 

                    # Identify top 6 and bottom 6 metrics for the given clube
                    def filter_top_bottom_metrics(dfc_metrics, clube):
                        
                        # Select the row corresponding to the given club
                        clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                        
                        # Identify top 6 and bottom 6 metrics based on values (single row)
                        top_6_metrics = clube_data.iloc[0].nlargest(6).index
                        bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                        
                        # Keep only relevant columns
                        selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                        dfd = dfc_metrics[selected_columns]
                        
                        return dfd

                    # Example usage (assuming clube is defined somewhere)
                    dfd = filter_top_bottom_metrics(dfc_metrics, clube)
                    
                    #Building opponent and context data 
                    
                    ##################################################################################################################
                    ##################################################################################################################
                    
                    # Create full competition so far mean
                    dfe = df[df['place'] == "Fora"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

                    # Ensure dfa has the required columns
                    columns_to_average = dfe.columns[11:-1]

                    # Compute mean for each column for each "team_name"
                    dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

                    # Ensure dfb has the required columns
                    columns_to_normalize = dfe.columns[1:]

                    # Normalize selected columns while keeping "team_name"
                    dff = dfe.copy()
                    dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

                    # Inverting the sign of inverted metrics
                    dff["PPDA"] = -1*dff["PPDA"]
                    dff["opposition_pass_tempo"] = -1*dff["opposition_pass_tempo"]
                    dff["opposition_progression_percentage"] = -1*dff["opposition_progression_percentage"]
                    dff["opp_final_third_to_box_%"] = -1*dff["opp_final_third_to_box_%"]
                    dff["Opposition_xT"] = -1*dff["Opposition_xT"]
                    dff["high_turnovers"] = -1*dff["high_turnovers"]
                    dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
                    dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
                    dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
                    dff["opposition_xG_10s"] = -1*dff["opposition_xG_10s"]
                    dff["goals_conceded"] = -1*dff["goals_conceded"]
                    
                    # Creating qualities columns
                    # Define the columns to average for each metric
                    defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                    "defensive_height", "opposition_pass_tempo",	
                                    "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                    "Opposition_xT"]

                    defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                    "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                    "opposition_box_entries_10s", "opposition_xG_10s"]

                    attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                    "retained_possessions_5s_%", "final_third_entries_10s",
                                                    "box_entries_10s", "xG_10s", "xT_10s"]

                    attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                    "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                    chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                            "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                        
                    # Compute the arithmetic mean for each metric and assign to the respective column
                    dff["defence_z"] = dff[defence_metrics].mean(axis=1)
                    dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
                    dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
                    dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
                    dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

                    # Get a list of the current columns
                    cols = list(dff.columns)

                    # List of columns to be relocated
                    cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                    "attacking_z", "chance_creation_z"]

                    # Remove these columns from the list
                    for col in cols_to_remove:
                        cols.remove(col)

                    # Insert the columns in the desired order at index 1, adjusting the index as we go
                    for i, col in enumerate(cols_to_remove):
                        cols.insert(1 + i, col)

                    # Reorder the dataframe columns accordingly
                    dff = dff[cols]
                    
                    # Renaming columns
                    columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                        "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                        "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                        "defensive_intensity",
                                        "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",
                                        "Opposition_xT", "high_turnovers", "turnover_line_height",
                                        "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                        "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                        "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                        "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                        "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                        "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                        "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                        "goal_difference", "goals_conceded", "goals_scored"
                                        ]

                    columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                    "Posse adversário (%)", "Defesa", "Transição defensiva",
                                    "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                    "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                    "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                    "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                    "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                    "Entradas do adversário no último terço em 10s da recuperação da posse",
                                    "Entradas do adversário na área em 10s da recuperação da posse", 
                                    "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                    "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                    "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                    "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                    "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                    "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                    "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                    "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                    "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                        "Gols sofridos", "Gols marcados"
                                        ]

                    # Create a dictionary mapping old names to new names
                    rename_dict = dict(zip(columns_to_rename, columns_renamed))

                    # Rename columns in variable_df_z_team (dff has attributes)
                    dff = dff.rename(columns=rename_dict)
                    
                    # Create dfg dataframe from dff, selecting columns [1:] from dfg (dfg has metrics)
                    dfg = dff[dfd.columns[0:]]
                    
                    ##################################################################################################################### 
                    #####################################################################################################################
                    #################################################################################################################################
                    #################################################################################################################################
                    #################################################################################################################################

                    #Plotar Primeiro Gráfico - Dispersão dos atributos em eixo único:

                    # Apply CSS styling to the jogos dataframe
                    def style_jogos(df):
                        # First, let's drop the 'index' column if it exists
                        if 'index' in df.columns:
                            df = df.drop(columns=['index'])
                            
                        return df.style.set_table_styles([
                            {"selector": "th", "props": [("font-weight", "bold"), ("border-bottom", "1px solid black"), ("text-align", "center")]},
                            {"selector": "td", "props": [("border-bottom", "1px solid gray"), ("text-align", "center")]},
                            {"selector": "tbody tr th", "props": [("font-size", "1px")]},  # Set font size for index column to 1px
                            {"selector": "thead tr th:first-child", "props": [("font-size", "1px")]},  # Also set font size for index header
                            #{"selector": "table", "props": [("margin-left", "auto"), ("margin-right", "auto"), ("border-collapse", "collapse")]},
                            #{"selector": "table, th, td", "props": [("border", "none")]},  # Remove outer borders
                            {"selector": "tr", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                            {"selector": "th", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                            {"selector": "td", "props": [("border-left", "none"), ("border-right", "none")]}
                        ])

                    jogos = style_jogos(jogos)

                    # Display the styled dataframe in Streamlit using markdown
                    st.markdown(
                        '<div style="display: flex; justify-content: center;">' + jogos.to_html(border=0) + '</div>',
                        unsafe_allow_html=True
                    )

                    attribute_chart_z2 = dff
                    # The second specific data point you want to highlight
                    attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                    # Add the suffix "_completo" to the content of the "clube" column
                    attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                    
                    attribute_chart_z1 = dfc

                    # Add the single row from attribute_chart_z2 to attribute_chart_z1
                    attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                    
                    # Collecting data
                    #Collecting data to plot
                    metrics = attribute_chart_z1.iloc[:, np.r_[1:6]].reset_index(drop=True)
                    metrics_participação_1 = metrics.iloc[:, 0].tolist()
                    metrics_participação_2 = metrics.iloc[:, 1].tolist()
                    metrics_participação_3 = metrics.iloc[:, 2].tolist()
                    metrics_participação_4 = metrics.iloc[:, 3].tolist()
                    metrics_participação_5 = metrics.iloc[:, 4].tolist()
                    metrics_y = [0] * len(metrics_participação_1)

                    # The specific data point you want to highlight
                    highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                    highlight = highlight.iloc[:, np.r_[1:6]].reset_index(drop=True)
                    highlight_participação_1 = highlight.iloc[:, 0].tolist()
                    highlight_participação_2 = highlight.iloc[:, 1].tolist()
                    highlight_participação_3 = highlight.iloc[:, 2].tolist()
                    highlight_participação_4 = highlight.iloc[:, 3].tolist()
                    highlight_participação_5 = highlight.iloc[:, 4].tolist()
                    highlight_y = 0

                    # Computing the selected team specific values
                    highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                    highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                    highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                    highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                    highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)

                    highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                    highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                    highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                    highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                    highlight_participação_5_value = highlight_participação_5_value.iat[0,0]

                    # Computing the min and max value across all lists using a generator expression
                    min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                        metrics_participação_3, metrics_participação_4,
                                                        metrics_participação_5
                                                        ])
                    min_value = min_value - 0.1
                    max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                        metrics_participação_3, metrics_participação_4,
                                                        metrics_participação_5
                                                        ])
                    max_value = max_value + 0.1

                    # Create two subplots vertically aligned with separate x-axes
                    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
                    #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                    # Building the Extended Title"
                    rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                    
                    # Function to determine club's rank in metric in league
                    def get_clube_rank(clube, column_idx, dataframe):
                        # Get the actual column name from the index (using positions 1-7)
                        column_name = dataframe.columns[column_idx]
                        
                        # Rank clubs based on the specified column in descending order
                        dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                        
                        # Find the rank of the specified club
                        clube_row = dataframe[dataframe['clube'] == clube]
                        if not clube_row.empty:
                            return int(clube_row['Rank'].iloc[0])
                        else:
                            return None
                        
                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_1 = attribute_chart_z1.columns[1]
                    output_str = f"({participação_1_ranking_value}/{rows_count})"
                    full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_2 = attribute_chart_z1.columns[2]
                    output_str = f"({participação_2_ranking_value}/{rows_count})"
                    full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                    
                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_3 = attribute_chart_z1.columns[3]
                    output_str = f"({participação_3_ranking_value}/{rows_count})"
                    full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_4 = attribute_chart_z1.columns[4]
                    output_str = f"({participação_4_ranking_value}/{rows_count})"
                    full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                    # Building the Extended Title"
                    # Determining club's rank in metric in league
                    participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

                    # Data to plot
                    column_name_at_index_5 = attribute_chart_z1.columns[5]
                    output_str = f"({participação_5_ranking_value}/{rows_count})"
                    full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                    ##############################################################################################################
                    ##############################################################################################################
                    #From Claude version2

                    def calculate_ranks(values):
                        """Calculate ranks for a given metric, with highest values getting rank 1"""
                        return pd.Series(values).rank(ascending=False).astype(int).tolist()

                    def prepare_data(tabela_a, metrics_cols):
                        """Prepare the metrics data dictionary with all required data"""
                        metrics_data = {}
                        
                        for col in metrics_cols:
                            # Store the metric values
                            metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                            # Calculate and store ranks
                            metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                            # Store player names
                            metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                        
                        return metrics_data

                    def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                        """
                        Create an interactive plot showing club metrics with hover information
                        
                        Parameters:
                        tabela_a (pd.DataFrame): DataFrame containing all player data
                        club (str): clube
                        min_value (float): Minimum value for x-axis
                        max_value (float): Maximum value for x-axis
                        """
                        # List of metrics to plot
                        # Replace the hardcoded metrics_list with dynamic column retrieval
                        metrics_list = [tabela_a.columns[idx] for idx in range(1, 6)]

                        # Prepare all the data
                        metrics_data = prepare_data(tabela_a, metrics_list)
                        
                        # Calculate highlight data
                        highlight_data = {
                            f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                            for metric in metrics_list
                        }
                        
                        # Calculate highlight ranks
                        highlight_ranks = {
                            metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                            for metric in metrics_list
                        }
                        
                        # Total number of clubs
                        total_clubs = len(tabela_a)
                        
                        # Create subplots
                        fig = make_subplots(
                            rows=7, 
                            cols=1,
                            subplot_titles=[
                                f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                for metric in metrics_list
                            ],
                            vertical_spacing=0.04
                        )

                        # Update subplot titles font size and color
                        for i in fig['layout']['annotations']:
                            i['font'] = dict(size=17, color='black')

                        # Add traces for each metric
                        for idx, metric in enumerate(metrics_list, 1):
                            # Create list of colors and customize club names for legend
                            colors = []
                            custom_club_names = []
                            
                            # Track if we have any "_completo" clubs to determine if we need a legend entry
                            has_completo_clubs = False
                            
                            for name in metrics_data[f'player_names_{metric}']:
                                if '_completo' in name:
                                    colors.append('gold')
                                    has_completo_clubs = True
                                    # Strip "_completo" from name for display but add "(completo)" indicator
                                    clean_name = name.replace('_completo', '')
                                    custom_club_names.append(f"{clean_name} (completo)")
                                else:
                                    colors.append('deepskyblue')
                                    custom_club_names.append(name)
                            
                            # Add scatter plot for regular clubs
                            regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                            
                            if regular_clubs_indices:
                                fig.add_trace(
                                    go.Scatter(
                                        x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                        y=[0] * len(regular_clubs_indices),
                                        mode='markers',
                                        #name='Demais Clubes',
                                        name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                        marker=dict(
                                            color='deepskyblue',
                                            size=8
                                        ),
                                        text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                        customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            
                            # Add separate scatter plot for "_completo" clubs
                            completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                            
                            if completo_clubs_indices:
                                fig.add_trace(
                                    go.Scatter(
                                        x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                        y=[0] * len(completo_clubs_indices),
                                        mode='markers',
                                        #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                        name=f'<span style="color:gold;">{clube} (completo)</span>',
                                        marker=dict(
                                            color='gold',
                                            size=12
                                        ),
                                        text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                        customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                        hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            
                            # Prepare highlighted club name for display
                            highlight_display_name = clube
                            highlight_color = 'blue'
                            
                            if '_completo' in clube:
                                highlight_color = 'yellow'
                                highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                            
                            # Add highlighted player point
                            fig.add_trace(
                                go.Scatter(
                                    x=[highlight_data[f'highlight_{metric}']],
                                    y=[0],
                                    mode='markers',
                                    name=highlight_display_name,  # Use the formatted name
                                    marker=dict(
                                        color=highlight_color,
                                        size=12
                                    ),
                                    hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                    showlegend=True if idx == 1 else False
                                ),
                                row=idx, 
                                col=1
                            )
                        # Get the total number of metrics (subplots)
                        n_metrics = len(metrics_list)

                        # Update layout for each subplot
                        for i in range(1, n_metrics + 1):
                            if i == n_metrics:  # Only for the last subplot
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='black',
                                    zerolinewidth=1,
                                    showline=False,
                                    ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                    tickvals=[min_value/2, 0, max_value/2],
                                    tickmode='array',
                                    ticks="outside",
                                    ticklen=2,
                                    tickfont=dict(size=16),
                                    tickangle=0,
                                    side='bottom',
                                    automargin=False,
                                    row=i, 
                                    col=1
                                )
                                # Adjust layout for the last subplot
                                fig.update_layout(
                                    xaxis_tickfont_family="Arial",
                                    margin=dict(b=0)  # Reduce bottom margin
                                )
                            else:  # For all other subplots
                                fig.update_xaxes(
                                    range=[min_value, max_value],
                                    showgrid=False,
                                    zeroline=True,
                                    zerolinecolor='grey',
                                    zerolinewidth=1,
                                    showline=False,
                                    showticklabels=False,  # Hide tick labels
                                    row=i, 
                                    col=1
                                )  # Reduces space between axis and labels

                            # Update layout for the entire figure
                            fig.update_yaxes(
                                showticklabels=False,
                                showgrid=False,
                                showline=False,
                                row=i, 
                                col=1
                            )

                        # Update layout for the entire figure
                        fig.update_layout(
                            height=600,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.15,
                                xanchor="center",
                                x=0.5,
                                font=dict(size=16)
                            ),
                            margin=dict(t=100)
                        )

                        # Add x-axis label at the bottom
                        fig.add_annotation(
                            text="Desvio-padrão",
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=0.02,
                            showarrow=False,
                            font=dict(size=16, color='black')
                        )

                        return fig

                    # Calculate min and max values with some padding
                    min_value_test = min([
                    min(metrics_participação_1), min(metrics_participação_2), 
                    min(metrics_participação_3), min(metrics_participação_4),
                    min(metrics_participação_5)
                    ])  # Add padding of 0.5

                    max_value_test = max([
                    max(metrics_participação_1), max(metrics_participação_2), 
                    max(metrics_participação_3), max(metrics_participação_4),
                    max(metrics_participação_5)
                    ])  # Add padding of 0.5

                    min_value = -max(abs(min_value_test), max_value_test) -0.03
                    max_value = -min_value

                    # Create the plot
                    fig = create_club_attributes_plot(
                        tabela_a=attribute_chart_z1,  # Your main dataframe
                        club=clube,  # Name of player to highlight
                        min_value= min_value,  # Minimum value for x-axis
                        max_value= max_value    # Maximum value for x-axis
                    )

                    st.plotly_chart(fig, use_container_width=True, key="unique_key_10")
                    st.write("---")

                    # Opção por plotar Destaques Positivos e Negativos
                    
                    # Check if the key exists in session state
                    if "show_destaques1" not in st.session_state:
                        st.session_state.show_destaques1 = False

                    # Your heading
                    st.markdown(f"<h4 style='text-align: center; color: black;'>Para ver os Destaques Positivos e Negativos do {clube}<br>nos últimos 5 jogos Fora de Casa,<br>Clique abaixo!</h4>",
                                unsafe_allow_html=True)

                    # When the button is clicked, change session state
                    if st.button("Clique Aqui"):
                        st.session_state.show_destaques1 = True

                    # This content will persist after the button is clicked
                    if st.session_state.show_destaques1:

                        # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Fora"
                        dfa = df[df['place'] == "Fora"].groupby('team_name').tail(5)

                        # Create (últimos 5) jogos dataframe
                        jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
                        
                        # Reset index to match the original dataframe structure
                        jogos = jogos.reset_index()
                        jogos_df = jogos
                        
                        # Ensure dfa has the required columns
                        columns_to_average = dfa.columns[11:-1]

                        # Compute mean for each column for each "team_name"
                        dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()
                        dfb_fora = dfb.to_csv("dfb_fora.csv")

                        # Ensure dfb has the required columns
                        columns_to_normalize = dfb.columns[1:]

                        # Normalize selected columns while keeping "team_name"
                        dfc = dfb.copy()
                        dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

                        # Inverting the sign of inverted metrics
                        dfc["PPDA"] = -1*dfc["PPDA"]
                        dfc["opposition_pass_tempo"] = -1*dfc["opposition_pass_tempo"]
                        dfc["opposition_progression_percentage"] = -1*dfc["opposition_progression_percentage"]
                        dfc["opp_final_third_to_box_%"] = -1*dfc["opp_final_third_to_box_%"]
                        dfc["Opposition_xT"] = -1*dfc["Opposition_xT"]
                        dfc["high_turnovers"] = -1*dfc["high_turnovers"]
                        dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
                        dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
                        dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
                        dfc["opposition_xG_10s"] = -1*dfc["opposition_xG_10s"]
                        dfc["goals_conceded"] = -1*dfc["goals_conceded"]
                        
                        # Creating qualities columns
                        # Define the columns to average for each metric
                        defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                        "defensive_height", "opposition_pass_tempo",	
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                        "Opposition_xT"]

                        defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                        "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                        "opposition_box_entries_10s", "opposition_xG_10s"]

                        attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                        "retained_possessions_5s_%", "final_third_entries_10s",
                                                        "box_entries_10s", "xG_10s", "xT_10s"]

                        attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                        chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                                "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                            
                        # Compute the arithmetic mean for each metric and assign to the respective column
                        dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
                        dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
                        dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
                        dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
                        dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

                        # Get a list of the current columns
                        cols = list(dfc.columns)

                        # List of columns to be relocated
                        cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                        "attacking_z", "chance_creation_z"]

                        # Remove these columns from the list
                        for col in cols_to_remove:
                            cols.remove(col)

                        # Insert the columns in the desired order at index 1, adjusting the index as we go
                        for i, col in enumerate(cols_to_remove):
                            cols.insert(1 + i, col)

                        # Reorder the dataframe columns accordingly
                        dfc = dfc[cols]
                        
                        # Renaming columns
                        columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                            "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                            "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                            "defensive_intensity",
                                            "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                            "opposition_progression_percentage", "opp_final_third_to_box_%",
                                            "Opposition_xT", "high_turnovers", "turnover_line_height",
                                            "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                            "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                            "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                            "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                            "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                            "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                            "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                            "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                            "goal_difference", "goals_conceded", "goals_scored"
                                            ]

                        columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                        "Posse adversário (%)", "Defesa", "Transição defensiva",
                                        "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                        "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                        "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                        "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                        "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                        "Entradas do adversário no último terço em 10s da recuperação da posse",
                                        "Entradas do adversário na área em 10s da recuperação da posse", 
                                        "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                        "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                        "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                        "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                        "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                        "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                        "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                        "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                        "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                            "Gols sofridos", "Gols marcados"
                                            ]

                        # Create a dictionary mapping old names to new names
                        rename_dict = dict(zip(columns_to_rename, columns_renamed))

                        # Rename columns in variable_df_z_team
                        dfc = dfc.rename(columns=rename_dict)
                        clube_data = dfc[dfc['clube'] == clube].set_index('clube')

                        # Select club attributes
                        dfc_attributes = dfc.iloc[:, np.r_[0:6]]
                        
                        # Select club metrics columns from dfc
                        dfc_metrics = dfc.iloc[:, np.r_[0, 6:43]]

                        # Identify top 6 and bottom 6 metrics for the given clube
                        def filter_top_bottom_metrics(dfc_metrics, clube):
                            
                            # Select the row corresponding to the given club
                            clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                            
                            # Identify top 6 and bottom 6 metrics based on values (single row)
                            top_6_metrics = clube_data.iloc[0].nlargest(6).index
                            bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                            
                            # Keep only relevant columns
                            selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                            dfd = dfc_metrics[selected_columns]
                            
                            return dfd

                        # Example usage (assuming clube is defined somewhere)
                        dfd = filter_top_bottom_metrics(dfc_metrics, clube)
                        
                        
                        ##################################################################################################################
                        ##################################################################################################################
                        
                        # Create full competition so far mean
                        dfe = df[df['place'] == "Fora"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

                        # Ensure dfa has the required columns
                        columns_to_average = dfe.columns[11:-1]

                        # Compute mean for each column for each "team_name"
                        dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

                        # Ensure dfb has the required columns
                        columns_to_normalize = dfe.columns[1:]

                        # Normalize selected columns while keeping "team_name"
                        dff = dfe.copy()
                        dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

                        # Inverting the sign of inverted metrics
                        dff["PPDA"] = -1*dff["PPDA"]
                        dff["opposition_pass_tempo"] = -1*dff["opposition_pass_tempo"]
                        dff["opposition_progression_percentage"] = -1*dff["opposition_progression_percentage"]
                        dff["opp_final_third_to_box_%"] = -1*dff["opp_final_third_to_box_%"]
                        dff["Opposition_xT"] = -1*dff["Opposition_xT"]
                        dff["high_turnovers"] = -1*dff["high_turnovers"]
                        dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
                        dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
                        dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
                        dff["opposition_xG_10s"] = -1*dff["opposition_xG_10s"]
                        dff["goals_conceded"] = -1*dff["goals_conceded"]
                        
                        # Creating qualities columns
                        # Define the columns to average for each metric
                        defence_metrics = ["PPDA", "defensive_intensity", "defensive_duels_won_%",
                                        "defensive_height", "opposition_pass_tempo",	
                                        "opposition_progression_percentage", "opp_final_third_to_box_%",	
                                        "Opposition_xT"]

                        defensive_transition_metrics = ["high_turnovers", "turnover_line_height", "recoveries_within_5s_%", 
                                                        "avg_time_to_defensive_action", "opposition_final_third_entries_10s", 
                                                        "opposition_box_entries_10s", "opposition_xG_10s"]

                        attacking_transition_metrics = ["recoveries",	"recovery_height", "retained_possessions_5s",
                                                        "retained_possessions_5s_%", "final_third_entries_10s",
                                                        "box_entries_10s", "xG_10s", "xT_10s"]

                        attacking_metrics = ["field_tilt_%",	"long_ball_%", "pass_tempo", 
                                        "final_third_entries_%", "final_third_to_box_entries_%", "xT"]

                        chance_creation_metrics = ["penalty_area_touches", "box_entries_to_shot_%", "np_shots", 
                                                "high_opportunity_shots", "np_xg", "np_goals", "xg_per_shot"]

                        # Compute the arithmetic mean for each metric and assign to the respective column
                        dff["defence_z"] = dff[defence_metrics].mean(axis=1)
                        dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
                        dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
                        dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
                        dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

                        # Get a list of the current columns
                        cols = list(dff.columns)

                        # List of columns to be relocated
                        cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                                        "attacking_z", "chance_creation_z"]

                        # Remove these columns from the list
                        for col in cols_to_remove:
                            cols.remove(col)

                        # Insert the columns in the desired order at index 1, adjusting the index as we go
                        for i, col in enumerate(cols_to_remove):
                            cols.insert(1 + i, col)

                        # Reorder the dataframe columns accordingly
                        dff = dff[cols]
                        
                        # Renaming columns
                        columns_to_rename = ["round", "game_id", "date", "fixture", "team_id", "team_name",
                                            "team_possession", "opponent_possession", "defence_z", "defensive_transition_z",
                                            "attacking_transition_z", "attacking_z", "chance_creation_z", "outcome_z", "PPDA", 
                                            "defensive_intensity",
                                            "defensive_duels_won_%", "defensive_height", "opposition_pass_tempo",
                                            "opposition_progression_percentage", "opp_final_third_to_box_%",
                                            "Opposition_xT", "high_turnovers", "turnover_line_height",
                                            "recoveries_within_5s_%", "avg_time_to_defensive_action", 
                                            "opposition_final_third_entries_10s", "opposition_box_entries_10s",
                                            "opposition_xG_10s", "recoveries", "recovery_height", "retained_possessions_5s",
                                            "retained_possessions_5s_%", "final_third_entries_10s", "box_entries_10s", 
                                            "xG_10s", "xT_10s", "possession", "opponent_possession.1", "field_tilt_%", "long_ball_%", "pass_tempo",
                                            "final_third_entries_%", "final_third_to_box_entries_%", "xT", "penalty_area_touches",
                                            "box_entries_to_shot_%", "np_shots", "high_opportunity_shots", "np_xg", "np_goals",
                                            "xg_per_shot", "ball_in_play", "expected_points", "win_probability", "total_xg",
                                            "goal_difference", "goals_conceded", "goals_scored"
                                            ]

                        columns_renamed = ["rodada", "game_id", "data", "partida", "team_id", "clube", "Posse (%)",
                                        "Posse adversário (%)", "Defesa", "Transição defensiva",
                                        "Transição ofensiva", "Ataque", "Criação de chances", "Resultado", 
                                        "PPDA", "Intensidade defensiva", "Duelos defensivos vencidos (%)",
                                        "Altura defensiva (m)", "Velocidade do passe adversário","Entradas do adversário no último terço (%)",
                                        "Entradas do adversário na área (%)", "xT adversário","Perdas de posse na linha baixa",
                                        "Altura da perda de posse (m)", "Recuperações de posse em 5s (%)", "Tempo médio ação defensiva (s)", 
                                        "Entradas do adversário no último terço em 10s da recuperação da posse",
                                        "Entradas do adversário na área em 10s da recuperação da posse", 
                                        "xG do adversário em 10s da recuperação da posse", "Recuperações de posse", 
                                        "Altura da recuperação de posse (m)", "Posse mantida em 5s", "Posse mantida em 5s (%)",
                                        "Entradas no último terço em 10s", "Entradas na área em 10s", "xG em 10s da recuperação da posse",
                                        "xT em 10s da recuperação da posse", "Posse", "Posse do adversário", "Field tilt (%)", "Bola longa (%)", 
                                        "Velocidade do passe", "Entradas no último terço (%)", "Entradas na área (%)",
                                        "xT (Ameaça esperada)", "Toques na área", "Finalizações (pEntrada na área, %)",
                                        "Finalizações (exceto pênaltis)", "Grandes oportunidades", "xG (exceto pênaltis)",
                                        "Gols (exceto pênaltis)", "xG (pFinalização)", "Bola em jogo (minutos)",
                                        "XPts (pontos esperados)", "Probabilidade de vitória (%)", "xG (Total)", "Diferença de gols",
                                            "Gols sofridos", "Gols marcados"
                                            ]

                        # Create a dictionary mapping old names to new names
                        rename_dict = dict(zip(columns_to_rename, columns_renamed))

                        # Rename columns in variable_df_z_team
                        dff = dff.rename(columns=rename_dict)
                        
                        # Create dfg dataframe from dff, selecting columns [1:] from dfd
                        dfg = dff[dfd.columns[0:]]
                        
                        ##################################################################################################################### 
                        #####################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################

                        #Plotar Primeiro Gráfico - Dispersão dos destaques positivos em eixo único:

                        st.write("---")

                        # Dynamically create the HTML string with the 'club' variable
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques positivos do {clube}<br>nos últimos 5 jogos Fora de Casa</h4>",
                                    unsafe_allow_html=True
                                    )

                        attribute_chart_z2 = dfg
                        # The second specific data point you want to highlight
                        attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                        # Add the suffix "_completo" to the content of the "clube" column
                        attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                        
                        attribute_chart_z1 = dfd

                        # Add the single row from attribute_chart_z2 to attribute_chart_z1
                        attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                        
                        # Collecting data
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[1:6]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                        highlight = highlight.iloc[:, np.r_[1:6]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_y = 0

                        # Computing the selected team specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine club's rank in metric in league
                        def get_clube_rank(clube, column_idx, dataframe):
                            # Get the actual column name from the index (using positions 1-7)
                            column_name = dataframe.columns[column_idx]
                            
                            # Rank clubs based on the specified column in descending order
                            dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified club
                            clube_row = dataframe[dataframe['clube'] == clube]
                            if not clube_row.empty:
                                return int(clube_row['Rank'].iloc[0])
                            else:
                                return None
                            
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_1 = attribute_chart_z1.columns[1]
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_2 = attribute_chart_z1.columns[2]
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_3 = attribute_chart_z1.columns[3]
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_4 = attribute_chart_z1.columns[4]
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_5 = attribute_chart_z1.columns[5]
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                            
                            return metrics_data

                        def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                            """
                            Create an interactive plot showing club metrics with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            club (str): clube
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            # Replace the hardcoded metrics_list with dynamic column retrieval
                            metrics_list = [tabela_a.columns[idx] for idx in range(1, 6)]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of clubs
                            total_clubs = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=7, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Create list of colors and customize club names for legend
                                colors = []
                                custom_club_names = []
                                
                                # Track if we have any "_completo" clubs to determine if we need a legend entry
                                has_completo_clubs = False
                                
                                for name in metrics_data[f'player_names_{metric}']:
                                    if '_completo' in name:
                                        colors.append('gold')
                                        has_completo_clubs = True
                                        # Strip "_completo" from name for display but add "(completo)" indicator
                                        clean_name = name.replace('_completo', '')
                                        custom_club_names.append(f"{clean_name} (completo)")
                                    else:
                                        colors.append('deepskyblue')
                                        custom_club_names.append(name)
                                
                                # Add scatter plot for regular clubs
                                regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                                
                                if regular_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                            y=[0] * len(regular_clubs_indices),
                                            mode='markers',
                                            #name='Demais Clubes',
                                            name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                            marker=dict(
                                                color='deepskyblue',
                                                size=8
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                            customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Add separate scatter plot for "_completo" clubs
                                completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                                
                                if completo_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                            y=[0] * len(completo_clubs_indices),
                                            mode='markers',
                                            #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                            name=f'<span style="color:gold;">{clube} (completo)</span>',
                                            marker=dict(
                                                color='gold',
                                                size=12
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                            customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Prepare highlighted club name for display
                                highlight_display_name = clube
                                highlight_color = 'blue'
                                
                                if '_completo' in clube:
                                    highlight_color = 'yellow'
                                    highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=highlight_display_name,  # Use the formatted name
                                        marker=dict(
                                            color=highlight_color,
                                            size=12
                                        ),
                                        hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=600,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.15,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=0.02,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_club_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            club=clube,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True, key="unique_key_11")
                        st.write("---")

                        ################################################################################################################################# 
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################
                        #################################################################################################################################

                        #Plotar Segundo Gráfico - Dispersão dos destaques negativos em eixo único:

                        # Dynamically create the HTML string with the 'club' variable
                        # Use the dynamically created HTML string in st.markdown
                        st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques negativos do {clube}<br>nos últimos 5 jogos Fora de Casa</h4>",
                                    unsafe_allow_html=True
                                    )

                        attribute_chart_z2 = dfg
                        # The second specific data point you want to highlight
                        attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
                        # Add the suffix "_completo" to the content of the "clube" column
                        attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
                        
                        attribute_chart_z1 = dfd

                        # Add the single row from attribute_chart_z2 to attribute_chart_z1
                        attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
                        
                        # Collecting data
                        #Collecting data to plot
                        metrics = attribute_chart_z1.iloc[:, np.r_[7:13]].reset_index(drop=True)
                        metrics_participação_1 = metrics.iloc[:, 0].tolist()
                        metrics_participação_2 = metrics.iloc[:, 1].tolist()
                        metrics_participação_3 = metrics.iloc[:, 2].tolist()
                        metrics_participação_4 = metrics.iloc[:, 3].tolist()
                        metrics_participação_5 = metrics.iloc[:, 4].tolist()
                        metrics_participação_6 = metrics.iloc[:, 5].tolist()
                        metrics_y = [0] * len(metrics_participação_1)

                        # The specific data point you want to highlight
                        highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
                        highlight = highlight.iloc[:, np.r_[7:13]].reset_index(drop=True)
                        highlight_participação_1 = highlight.iloc[:, 0].tolist()
                        highlight_participação_2 = highlight.iloc[:, 1].tolist()
                        highlight_participação_3 = highlight.iloc[:, 2].tolist()
                        highlight_participação_4 = highlight.iloc[:, 3].tolist()
                        highlight_participação_5 = highlight.iloc[:, 4].tolist()
                        highlight_participação_6 = highlight.iloc[:, 5].tolist()
                        highlight_y = 0

                        # Computing the selected team specific values
                        highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
                        highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
                        highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
                        highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
                        highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
                        highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

                        highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
                        highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
                        highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
                        highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
                        highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
                        highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

                        # Computing the min and max value across all lists using a generator expression
                        min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        min_value = min_value - 0.1
                        max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                            metrics_participação_3, metrics_participação_4,
                                                            metrics_participação_5, metrics_participação_6
                                                            ])
                        max_value = max_value + 0.1

                        # Create two subplots vertically aligned with separate x-axes
                        fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
                        #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

                        # Building the Extended Title"
                        rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
                        
                        # Function to determine club's rank in metric in league
                        def get_clube_rank(clube, column_idx, dataframe):
                            # Get the actual column name from the index (using positions 7-13)
                            column_name = dataframe.columns[column_idx]
                            
                            # Rank clubs based on the specified column in descending order
                            dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                            
                            # Find the rank of the specified club
                            clube_row = dataframe[dataframe['clube'] == clube]
                            if not clube_row.empty:
                                return int(clube_row['Rank'].iloc[0])
                            else:
                                return None
                            
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_1_ranking_value = (get_clube_rank(clube, 7, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_1 = attribute_chart_z1.columns[7]
                        output_str = f"({participação_1_ranking_value}/{rows_count})"
                        full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_2_ranking_value = (get_clube_rank(clube, 8, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_2 = attribute_chart_z1.columns[8]
                        output_str = f"({participação_2_ranking_value}/{rows_count})"
                        full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
                        
                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_3_ranking_value = (get_clube_rank(clube, 9, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_3 = attribute_chart_z1.columns[9]
                        output_str = f"({participação_3_ranking_value}/{rows_count})"
                        full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_4_ranking_value = (get_clube_rank(clube, 10, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_4 = attribute_chart_z1.columns[10]
                        output_str = f"({participação_4_ranking_value}/{rows_count})"
                        full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_5_ranking_value = (get_clube_rank(clube, 11, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_5 = attribute_chart_z1.columns[11]
                        output_str = f"({participação_5_ranking_value}/{rows_count})"
                        full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

                        # Building the Extended Title"
                        # Determining club's rank in metric in league
                        participação_6_ranking_value = (get_clube_rank(clube, 12, attribute_chart_z1))

                        # Data to plot
                        column_name_at_index_6 = attribute_chart_z1.columns[12]
                        output_str = f"({participação_6_ranking_value}/{rows_count})"
                        full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

                        ##############################################################################################################
                        ##############################################################################################################
                        #From Claude version2

                        def calculate_ranks(values):
                            """Calculate ranks for a given metric, with highest values getting rank 1"""
                            return pd.Series(values).rank(ascending=False).astype(int).tolist()

                        def prepare_data(tabela_a, metrics_cols):
                            """Prepare the metrics data dictionary with all required data"""
                            metrics_data = {}
                            
                            for col in metrics_cols:
                                # Store the metric values
                                metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                                # Calculate and store ranks
                                metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                                # Store player names
                                metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                            
                            return metrics_data

                        def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                            """
                            Create an interactive plot showing club metrics with hover information
                            
                            Parameters:
                            tabela_a (pd.DataFrame): DataFrame containing all player data
                            club (str): clube
                            min_value (float): Minimum value for x-axis
                            max_value (float): Maximum value for x-axis
                            """
                            # List of metrics to plot
                            # Replace the hardcoded metrics_list with dynamic column retrieval
                            metrics_list = [tabela_a.columns[idx] for idx in range(7, 13)]

                            # Prepare all the data
                            metrics_data = prepare_data(tabela_a, metrics_list)
                            
                            # Calculate highlight data
                            highlight_data = {
                                f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                                for metric in metrics_list
                            }
                            
                            # Calculate highlight ranks
                            highlight_ranks = {
                                metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                                for metric in metrics_list
                            }
                            
                            # Total number of clubs
                            total_clubs = len(tabela_a)
                            
                            # Create subplots
                            fig = make_subplots(
                                rows=7, 
                                cols=1,
                                subplot_titles=[
                                    f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                                    for metric in metrics_list
                                ],
                                vertical_spacing=0.04
                            )

                            # Update subplot titles font size and color
                            for i in fig['layout']['annotations']:
                                i['font'] = dict(size=17, color='black')

                            # Add traces for each metric
                            for idx, metric in enumerate(metrics_list, 1):
                                # Create list of colors and customize club names for legend
                                colors = []
                                custom_club_names = []
                                
                                # Track if we have any "_completo" clubs to determine if we need a legend entry
                                has_completo_clubs = False
                                
                                for name in metrics_data[f'player_names_{metric}']:
                                    if '_completo' in name:
                                        colors.append('gold')
                                        has_completo_clubs = True
                                        # Strip "_completo" from name for display but add "(completo)" indicator
                                        clean_name = name.replace('_completo', '')
                                        custom_club_names.append(f"{clean_name} (completo)")
                                    else:
                                        colors.append('deepskyblue')
                                        custom_club_names.append(name)
                                
                                # Add scatter plot for regular clubs
                                regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                                
                                if regular_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                            y=[0] * len(regular_clubs_indices),
                                            mode='markers',
                                            #name='Demais Clubes',
                                            name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                            marker=dict(
                                                color='deepskyblue',
                                                size=8
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                            customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Add separate scatter plot for "_completo" clubs
                                completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                                
                                if completo_clubs_indices:
                                    fig.add_trace(
                                        go.Scatter(
                                            x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                            y=[0] * len(completo_clubs_indices),
                                            mode='markers',
                                            #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                            name=f'<span style="color:gold;">{clube} (completo)</span>',
                                            marker=dict(
                                                color='gold',
                                                size=12
                                            ),
                                            text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                            customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                            hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                            showlegend=True if idx == 1 else False
                                        ),
                                        row=idx, 
                                        col=1
                                    )
                                
                                # Prepare highlighted club name for display
                                highlight_display_name = clube
                                highlight_color = 'blue'
                                
                                if '_completo' in clube:
                                    highlight_color = 'yellow'
                                    highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                                
                                # Add highlighted player point
                                fig.add_trace(
                                    go.Scatter(
                                        x=[highlight_data[f'highlight_{metric}']],
                                        y=[0],
                                        mode='markers',
                                        name=highlight_display_name,  # Use the formatted name
                                        marker=dict(
                                            color=highlight_color,
                                            size=12
                                        ),
                                        hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                                        showlegend=True if idx == 1 else False
                                    ),
                                    row=idx, 
                                    col=1
                                )
                            # Get the total number of metrics (subplots)
                            n_metrics = len(metrics_list)

                            # Update layout for each subplot
                            for i in range(1, n_metrics + 1):
                                if i == n_metrics:  # Only for the last subplot
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='black',
                                        zerolinewidth=1,
                                        showline=False,
                                        ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                                        tickvals=[min_value/2, 0, max_value/2],
                                        tickmode='array',
                                        ticks="outside",
                                        ticklen=2,
                                        tickfont=dict(size=16),
                                        tickangle=0,
                                        side='bottom',
                                        automargin=False,
                                        row=i, 
                                        col=1
                                    )
                                    # Adjust layout for the last subplot
                                    fig.update_layout(
                                        xaxis_tickfont_family="Arial",
                                        margin=dict(b=0)  # Reduce bottom margin
                                    )
                                else:  # For all other subplots
                                    fig.update_xaxes(
                                        range=[min_value, max_value],
                                        showgrid=False,
                                        zeroline=True,
                                        zerolinecolor='grey',
                                        zerolinewidth=1,
                                        showline=False,
                                        showticklabels=False,  # Hide tick labels
                                        row=i, 
                                        col=1
                                    )  # Reduces space between axis and labels

                                # Update layout for the entire figure
                                fig.update_yaxes(
                                    showticklabels=False,
                                    showgrid=False,
                                    showline=False,
                                    row=i, 
                                    col=1
                                )

                            # Update layout for the entire figure
                            fig.update_layout(
                                height=600,
                                showlegend=True,
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.17,
                                    xanchor="center",
                                    x=0.5,
                                    font=dict(size=16)
                                ),
                                margin=dict(t=100)
                            )

                            # Add x-axis label at the bottom
                            fig.add_annotation(
                                text="Desvio-padrão",
                                xref="paper",
                                yref="paper",
                                x=0.5,
                                y=-0.02,
                                showarrow=False,
                                font=dict(size=16, color='black')
                            )

                            return fig

                        # Calculate min and max values with some padding
                        min_value_test = min([
                        min(metrics_participação_1), min(metrics_participação_2), 
                        min(metrics_participação_3), min(metrics_participação_4),
                        min(metrics_participação_5), min(metrics_participação_6)
                        ])  # Add padding of 0.5

                        max_value_test = max([
                        max(metrics_participação_1), max(metrics_participação_2), 
                        max(metrics_participação_3), max(metrics_participação_4),
                        max(metrics_participação_5), max(metrics_participação_6)
                        ])  # Add padding of 0.5

                        min_value = -max(abs(min_value_test), max_value_test) -0.03
                        max_value = -min_value

                        # Create the plot
                        fig = create_club_attributes_plot(
                            tabela_a=attribute_chart_z1,  # Your main dataframe
                            club=clube,  # Name of player to highlight
                            min_value= min_value,  # Minimum value for x-axis
                            max_value= max_value    # Maximum value for x-axis
                        )

                        st.plotly_chart(fig, use_container_width=True, key="unique_key_12")

                    ################################################################################################################################# 
                    #################################################################################################################################
                    ################################################################################################################################# 
                    #################################################################################################################################

                    #### INCLUIR BOT

                    st.write("---")
                    st.markdown(
                        """
                        <h3 style='text-align: center;'>Análise de Performance</h3>
                        """,
                        unsafe_allow_html=True
                    )

                    # Create necessary files:
                    single_dfd = dfd[dfd["clube"] == clube]
                    single_dfd2 = dfc_attributes[dfc_attributes["clube"] == clube]
                    # Merge single_dfd and single_dfd2 based on "clube"
                    single_dfd = single_dfd.merge(single_dfd2, on="clube", how="left")
                    context_df = pd.read_csv("context.csv")
                    playstyle_df = pd.read_csv("play_style2.csv")
                    jogos_df = jogos_df.iloc[2]
                    
                    # Configure Google Gemini API
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

                    def generate_opponent_analysis(single_dfd, context_df, playstyle_df):
                        """
                        Generate a detailed club performance analysis based on the club's performance metrics.
                        
                        Args:
                            single_dfd (pd.DataFrame): DataFrame with club name and z-scores for better/worse metrics
                            context_df (pd.DataFrame): DataFrame with attributes and metrics definitions
                            playstyle_df (pd.DataFrame): DataFrame with play styles and their definitions
                        
                        Returns:
                            str: Generated club performance analysis in Portuguese
                        """
                        # Extract club name and metrics
                        clube = single_dfd.iloc[0, 0]
                        metricas_melhores = single_dfd.iloc[0, 1:7].to_dict()
                        metricas_piores = single_dfd.iloc[0, 7:13].to_dict()
                        attributes = single_dfd.iloc[0, 13:18].to_dict()
                        
                        # Sort metrics by z-score (abs value) to focus on most significant ones
                        metricas_melhores_sorted = {k: v for k, v in sorted(
                            metricas_melhores.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}
                        
                        metricas_piores_sorted = {k: v for k, v in sorted(
                            metricas_piores.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}
                        
                        attributes_sorted = {k: v for k, v in sorted(
                            attributes.items(), 
                            key=lambda item: abs(item[1]), 
                            reverse=True
                        )}

                        # Create prompt for Gemini
                        prompt = (
                            f"Escreva uma análise aprofundada sobre a performance do clube {clube} baseada nos dados fornecidos, em português brasileiro. \n\n"
                            f"Escreva a análise sob a perspectiva da Comissão Técnica do clube {clube}, avaliando os pontos fortes e fracos de sua equipe. \n\n"
                            f"Análise geral sobre os atributos do clube {clube}:\n{pd.Series(attributes_sorted).to_string()}\n\n"
                            f"Pontos fortes (métricas em z-score nas quais o clube se destacou positivamente):\n{pd.Series(metricas_melhores_sorted).to_string()}\n\n"
                            f"Pontos fracos (métricas em z-score nas quais o clube se destacou negativamente):\n{pd.Series(metricas_piores_sorted).to_string()}\n\n"
                            f"Contexto Conceitual - Atributos e Métricas:\n{context_df.to_string()}\n\n"
                            "Considere o desempenho nos atributos e a relação entre as métricas destacadas e os atributos aos quais pertencem. "
                            "Inclua uma seção de pontos fortes, pontos fracos e recomendações de melhoria para o clube. "
                            "A análise deve ser bem estruturada, técnica mas compreensível e com aproximadamente 500 palavras. "
                            "Não apresente z-scores na análise final."
                        )
                        
                        # Generate the analysis using Gemini
                        model = genai.GenerativeModel("gemini-flash-latest")
                        response = model.generate_content(prompt)
                        
                        # Clean and format the response
                        analysis = response.text
                        
                        # Add title and formatting
                        formatted_analysis = f"""
                        ## {clube}
                    
                        {analysis}
                        """
                        
                        return formatted_analysis

                    def main():
                        st.write("---")
                        # Initialize session state variable
                        if "show_analise_adversario2" not in st.session_state:
                            st.session_state.show_analise_adversario2 = False

                        # Título estilizado
                        #st.markdown("<p style='font-size:35px; font-weight:bold; text-align:center;'>Análise de Adversário</p>", unsafe_allow_html=True)

                        # Botão que ativa a exibição
                        if st.button("Gerar Análise de Performance", type='primary', key=110):
                            st.session_state.show_analise_adversario2 = True

                        # Conteúdo persistente após o clique
                        if st.session_state.show_analise_adversario2:
                            with st.spinner("Gerando análise de performance detalhada ..."):
                                analysis = generate_opponent_analysis(
                                    single_dfd,
                                    context_df,
                                    playstyle_df
                                )
                                
                                # Display the analysis
                                st.markdown(analysis)
                                
                                # Add download button for the analysis as PDF
                                import io
                                from fpdf import FPDF
                                
                                def create_pdf(text):
                                    text = text.replace('\u2013', '-')  # quick fix for en dash
                                    pdf = FPDF()
                                    pdf.add_page()
                                    pdf.set_auto_page_break(auto=True, margin=15)
                                    
                                    # Add title
                                    pdf.set_font("Arial", "B", 16)
                                    pdf.cell(0, 10, f"{clube}", ln=True)
                                    pdf.ln(5)
                                    
                                    # Add content
                                    pdf.set_font("Arial", "", 12)
                                    
                                    # Split text into lines and add to PDF
                                    lines = text.split('\n')
                                    for line in lines:
                                        # Check if line is a header
                                        if line.strip().startswith('#'):
                                            pdf.set_font("Arial", "B", 14)
                                            pdf.cell(0, 10, line.replace('#', '').strip(), ln=True)
                                            pdf.set_font("Arial", "", 12)
                                        else:
                                            pdf.multi_cell(0, 10, line)
                                    
                                    return pdf.output(dest="S").encode("latin-1", errors="replace")
                                
                                clube = single_dfd.iloc[0, 0]
                                pdf_data = create_pdf(analysis)
                                
                                st.download_button(
                                    label="Baixar Análise como PDF",
                                    data=pdf_data,
                                    file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.pdf",
                                    mime="application/pdf",
                                        key=208
                                )

                                # Add download button for the analysis
                                clube = single_dfd.iloc[0, 0]
                                st.download_button(
                                    label="Baixar Análise como TXT",
                                    data=analysis,
                                    file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.txt",
                                    mime="text/plain",
                                        key=209
                                )

                    if __name__ == "__main__":
                        main()

                    ################################################################################################################################# 
                    #################################################################################################################################
                    ################################################################################################################################# 
                    #################################################################################################################################

                    #### INCLUIR NOTA COM DESCRIÇÃO DAS MÉTRICAS FORTES E FRACAS
                    st.write("---")
                    st.markdown(
                        """
                        <h3 style='text-align: center;'>Quer saber as definições das Métricas? Clique abaixo!</h3>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button("Definições das Métricas", key=111):

                        st.markdown("<p style='font-size:24px; font-weight:bold;'>Nota:</p>", unsafe_allow_html=True)
                        
                        def generate_metrics_sections(dfd, context_df):
                            # Generate positive metrics section (columns 1-7)
                            positive_metrics_names = dfd.columns[1:7]
                            
                            # Initialize positive definitions list
                            positive_metrics_definitions = []
                            
                            # For each positive metric name, find its definition in context_df
                            for metric_name in positive_metrics_names:
                                # Find the row where 'Métrica' column equals the metric name
                                matching_row = context_df[context_df['Métrica'] == metric_name]
                                
                                # If a match is found, add the definition to the list
                                if not matching_row.empty:
                                    definition = matching_row['Definição'].values[0]
                                    positive_metrics_definitions.append(definition)
                                else:
                                    # If no match is found, add an empty string as placeholder
                                    positive_metrics_definitions.append("")
                            
                            # Create the positive metrics markdown
                            positive_markdown = "#### MÉTRICAS COM DESTAQUE POSITIVO\n"
                            for name, definition in zip(positive_metrics_names, positive_metrics_definitions):
                                positive_markdown += f"- **{name}**: {definition}\n"
                            
                            # Generate negative metrics section (columns 7-13)
                            negative_metrics_names = dfd.columns[7:13]
                            
                            # Initialize negative definitions list
                            negative_metrics_definitions = []
                            
                            # For each negative metric name, find its definition in context_df
                            for metric_name in negative_metrics_names:
                                # Find the row where 'Métrica' column equals the metric name
                                matching_row = context_df[context_df['Métrica'] == metric_name]
                                
                                # If a match is found, add the definition to the list
                                if not matching_row.empty:
                                    definition = matching_row['Definição'].values[0]
                                    negative_metrics_definitions.append(definition)
                                else:
                                    # If no match is found, add an empty string as placeholder
                                    negative_metrics_definitions.append("")
                            
                            # Create the negative metrics markdown
                            negative_markdown = "#### MÉTRICAS COM DESTAQUE NEGATIVO\n"
                            for name, definition in zip(negative_metrics_names, negative_metrics_definitions):
                                negative_markdown += f"- **{name}**: {definition}\n"
                            
                            # Display both sections
                            st.markdown(positive_markdown)
                            st.markdown(negative_markdown)

                        # Example usage:
                        generate_metrics_sections(dfd, context_df)

                ################################################################################################################################# 
                #################################################################################################################################
                ################################################################################################################################# 
                #################################################################################################################################

# Step 2: Clube Analysis
elif st.session_state.step == "opponent_analysis":

    # Custom CSS for better formatting
    st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stAlert {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #ff4b4b;
        }
        .info-box {
            background-color: #e6f3ff;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #4B8BF5;
            margin-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        .katex {
            font-size: 1.1em;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <h4>Análise do adversário: </h4>
    <p>Analisa o Estilo de Jogo do adversário escolhido, com base nos (até) últimos 5 jogos disputados em casa ou fora.</p>
    <p>Ao escolher o local do jogo, leve em conta que a referência é o ADVERSÁRIO. 
    Por exemplo, suponha que o Vasco vai enfrentar o Cruzeiro em BH. A escolha do local deve ser "Casa", já que o adversário (Cruzeiro) estará jogando em casa.</p>
    </div>
    """, unsafe_allow_html=True)

    #Escolha do Adversário    
    st.markdown("<h5 style='text-align: center;'><br>Digite o nome do Adversário!</h5>", unsafe_allow_html=True)

    clubes = ['Vasco da Gama', 'Atletico MG', 'Bahia', 
              'Botafogo RJ', 'Ceara', 'Corinthians', 'Cruzeiro', 
              'Flamengo', 'Fluminense', 'Fortaleza', 'Gremio', 
              'Internacional', 'Juventude', 'Mirassol', 'Palmeiras', 
              'Red Bull Bragantino', 'Santos', 'Sao Paulo', 'Sport', 'Vitoria'
             ]

    clubes2 = ['Atletico MG', 'Bahia', 
              'Botafogo RJ', 'Ceara', 'Corinthians', 'Cruzeiro', 
              'Flamengo', 'Fluminense', 'Fortaleza', 'Gremio', 
              'Internacional', 'Juventude', 'Mirassol', 'Palmeiras', 
              'Red Bull Bragantino', 'Santos', 'Sao Paulo', 'Sport', 'Vitoria'
             ]

    clube = st.selectbox("", options=clubes2)
    
    if clube:
        
        #Escolha da Opção (Casa ou Fora)
        st.write("---")
        st.markdown("<h5 style='text-align: center;'>Jogando em Casa ou jogando Fora de Casa?</h5>", unsafe_allow_html=True)

        # Initialize a second session state variable if it doesn't exist
        if 'analysis_option' not in st.session_state:
            st.session_state.analysis_option = None
            
        if 'analysis_type' not in st.session_state:
            st.session_state.analysis_type = None
            
        # Function to select analysis option
        def select_analysis_option(option):
            st.session_state.analysis_option = option

        # Function to select analysis type
        def select_analysis_type(option):
            st.session_state.analysis_type = option

        # Define button styles for selected/unselected states
        selected_style = """
        <style>
        div[data-testid="stButton"] button.casa-fora-selected {
            background-color: #FF4B4B !important;
            color: white !important;
            border-color: #FF0000 !important;
        }
        </style>
        """
        st.markdown(selected_style, unsafe_allow_html=True)

        # Create two rows with two buttons each for Casa/Fora
        col1, col2, col3 = st.columns([4, 1, 4])
        with col1:
            # Use different button styles based on selection status
            if st.session_state.selected_option == "Casa":
                # Create a custom HTML button when selected
                st.markdown(
                    f"""
                    <div data-testid="stButton">
                        <button class="casa-fora-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                            Casa
                        </button>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.button("Casa", type='secondary', use_container_width=True, 
                        on_click=select_option, args=("Casa",))
                
        with col3:
            # Use different button styles based on selection status
            if st.session_state.selected_option == "Fora":
                # Create a custom HTML button when selected
                st.markdown(
                    f"""
                    <div data-testid="stButton">
                        <button class="casa-fora-selected" style="width:100%; padding:0.5rem; font-weight:400;">
                            Fora
                        </button>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.button("Fora", type='secondary', use_container_width=True, 
                        on_click=select_option, args=("Fora",))
                
                    
        #Selecting last up to five games of each club (home or away) 
        if st.session_state.selected_option == "Casa":
            # Your existing code for handling Casa selection
            pass
                    
            st.write("---")
                
            # Custom CSS for better formatting
            st.markdown("""
            <style>
                .main {
                    padding: 2rem;
                }
                .stAlert {
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid #ff4b4b;
                }
                .info-box {
                    background-color: #e6f3ff;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid #4B8BF5;
                    margin-bottom: 1rem;
                }
                h1, h2, h3 {
                    color: #1E3A8A;
                }
                .katex {
                    font-size: 1.1em;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-box">
            <p><h4>Análise do Estilo de Jogo do Clube:</h4></p>
            <p>Esta ferramenta gera automaticamente uma análise do estilo de jogo do clube, utilizando dados 
            estatísticos de desempenho relacionados às diferentes fases do jogo: Defesa, Transição Defensiva, 
            Transição Ofensiva, Ataque e Criação de Chances. A análise identifica os pontos fortes e fracos da 
            equipe nas últimas cinco partidas disputadas fora de casa. O usuário pode visualizar a análise 
            diretamente na interface e baixá-la em formato PDF ou TXT para uso posterior.
            </div>
            """, unsafe_allow_html=True)

            st.write("---")
            
            st.markdown(f"<h3 style='text-align: center;'><b>Análise de Estilo de Jogo do Adversário jogando em Casa</b></h3>", unsafe_allow_html=True)

            st.write("---")
            
            # Select a club
            club_selected = clube

            # Get the image URL for the selected club
            image_url = club_image_paths[club_selected]

            # Center-align and display the image
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{image_url}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )                
                    

        ################################################################################################################################# 
        #################################################################################################################################
        #################################################################################################################################
        #################################################################################################################################
        #################################################################################################################################

            # Gráfico dos Destaques de Estilo    
            
            #Tratamento da base de dados - PlayStyle Analysis - Inclusão da Rodada
            df = pd.read_csv("play_style_metrics.csv")
            dfa = df.sort_values(by="date", ascending=False)

            # Initialize a new session state variable for this level                         
            if 'analysis_type' not in st.session_state:                             
                st.session_state.analysis_type = None                          

            # Create a new callback function for this level                         
            def select_analysis_type(option):                             
                st.session_state.analysis_type = option                          

            # Define a style for the analysis type buttons
            analysis_type_style = """
            <style>
            div[data-testid="stButton"] button.analysis-type-selected {
                background-color: #FF4B4B !important;
                color: white !important;
                border-color: #FF0000 !important;
            }
            </style>
            """
            st.markdown(analysis_type_style, unsafe_allow_html=True)


            # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Casa"
            dfa = df[df['place'] == "Casa"].groupby('team_name').tail(5)

            # Create (últimos 5) jogos dataframe
            jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
            
            # Reset index to match the original dataframe structure
            jogos = jogos.reset_index()
            jogos_df = jogos
            
            # Ensure dfa has the required columns
            columns_to_average = dfa.columns[11:]

            # Compute mean for each column for each "team_name"
            dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()

            # Ensure dfb has the required columns
            columns_to_normalize = dfb.columns[1:]

            # Normalize selected columns while keeping "team_name"
            dfc = dfb.copy()
            dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

            # Inverting the sign of inverted metrics
            dfc["PPDA"] = -1*dfc["PPDA"]
            dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
            dfc["transition_vulnerability_index"] = -1*dfc["transition_vulnerability_index"]
            dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
            dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
            dfc["time_to_progression_seconds"] = -1*dfc["time_to_progression_seconds"]

            
            # Creating qualities columns
            # Define the columns to average for each metric
            defence_metrics = ["defensive_height", "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct",
                            "defensive_intensity"]

            defensive_transition_metrics = ["avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                            "transition_vulnerability_index", "opposition_final_third_entries_10s",
                                            "opposition_box_entries_10s"]	

            attacking_transition_metrics = ["time_to_progression_seconds", "first_pass_forward_pct",
                                            "final_third_entries_10s_pct", "box_entries_10s_pct",
                                            "retained_possessions_5s_pct"]	

            attacking_metrics = ["long_ball_%", "buildup_%", "progressive_passes_%", 
                                "crosses_per_final_third_entry", "dribbles_per_final_third_entry", 
                                "box_entries_from_crosses", "box_entries_from_carries"]

            chance_creation_metrics = ["sustained_attacks", "direct_attack", 
                                    "shots_per_final_third_pass", "shots_outside_box"]
                
            # Compute the arithmetic mean for each metric and assign to the respective column
            dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
            dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
            dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
            dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
            dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

            # Get a list of the current columns
            cols = list(dfc.columns)

            # List of columns to be relocated
            cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                            "attacking_z", "chance_creation_z"]

            # Remove these columns from the list
            for col in cols_to_remove:
                cols.remove(col)

            # Insert the columns in the desired order at index 1, adjusting the index as we go
            for i, col in enumerate(cols_to_remove):
                cols.insert(1 + i, col)

            # Reorder the dataframe columns accordingly
            dfc = dfc[cols]
            
            # Renaming columns
            # Renaming columns
            columns_to_rename = ["round", "date", "fixture", "team_name",
                                "team_possession", "opponent_possession", "defence", "defensive_transition",
                                "attacking_transition", "attacking", "chance_creation", "defensive_height", 
                                "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct","defensive_intensity",	
                                "avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                "transition_vulnerability_index", "opposition_final_third_entries_10s", 
                                "opposition_box_entries_10s", "time_to_progression_seconds", "first_pass_forward_pct", 
                                "final_third_entries_10s_pct", "box_entries_10s_pct", "retained_possessions_5s_pct", 
                                "long_ball_%", "buildup_%", "progressive_passes_%", "crosses_per_final_third_entry", 
                                "dribbles_per_final_third_entry", "box_entries_from_crosses", "box_entries_from_carries", 
                                "sustained_attacks", "direct_attack", "shots_per_final_third_pass", "shots_outside_box"
                                ]

            columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                            "Posse adversário (%)", "Defesa", "Transição defensiva",
                            "Transição ofensiva", "Ataque", "Criação de chances", 
                            "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                            "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                            "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                            "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                            "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                            "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                            "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                            "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                                ]

            # Create a dictionary mapping old names to new names
            rename_dict = dict(zip(columns_to_rename, columns_renamed))

            # Rename columns in variable_df_z_team
            dfc = dfc.rename(columns=rename_dict)
            clube_data = dfc[dfc['clube'] == clube].set_index('clube')
            
            # Select club attributes
            dfc_attributes = dfc.iloc[:, np.r_[0:6]]
            
            # Select club metrics columns from dfc
            dfc_metrics = dfc.iloc[:, np.r_[0, 6:32]]

            # Identify top 6 and bottom 6 metrics for the given clube
            def filter_top_bottom_metrics(dfc_metrics, clube):
                
                # Select the row corresponding to the given club
                clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                
                # Identify top 6 and bottom 6 metrics based on values (single row)
                top_6_metrics = clube_data.iloc[0].nlargest(6).index
                bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                
                # Keep only relevant columns
                selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                dfd = dfc_metrics[selected_columns]
                
                return dfd

            # Identify top 8 and bottom 8 metrics for the given clube
            def filter_8top_bottom_metrics(dfc_metrics, clube):
                
                # Select the row corresponding to the given club
                clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                
                # Identify top 8 and bottom 8 metrics based on values (single row)
                top_8_metrics = clube_data.iloc[0].nlargest(8).index
                bottom_8_metrics = clube_data.iloc[0].nsmallest(8).index
                
                # Keep only relevant columns
                selected_columns2 = ['clube'] + list(top_8_metrics) + list(bottom_8_metrics)
                dfd8 = dfc_metrics[selected_columns2]
                
                
                return dfd8

            # Example usage (assuming clube is defined somewhere)
            dfd = filter_top_bottom_metrics(dfc_metrics, clube)
            dfd8 = filter_8top_bottom_metrics(dfc_metrics, clube)
            
            #Building opponent and context data
            
            ##################################################################################################################
            ##################################################################################################################
            
            # Create full competition so far mean
            dfe = df[df['place'] == "Casa"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

            # Ensure dfa has the required columns
            columns_to_average = dfe.columns[11:]

            # Compute mean for each column for each "team_name"
            dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

            # Ensure dfb has the required columns
            columns_to_normalize = dfe.columns[1:]

            # Normalize selected columns while keeping "team_name"
            dff = dfe.copy()
            dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

            # Inverting the sign of inverted metrics
            dff["PPDA"] = -1*dff["PPDA"]
            dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
            dff["transition_vulnerability_index"] = -1*dff["transition_vulnerability_index"]
            dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
            dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
            dff["time_to_progression_seconds"] = -1*dff["time_to_progression_seconds"]
            
            # Creating qualities columns
            # Define the columns to average for each metric
            defence_metrics = ["defensive_height", "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct",
                            "defensive_intensity"]

            defensive_transition_metrics = ["avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                            "transition_vulnerability_index", "opposition_final_third_entries_10s",
                                            "opposition_box_entries_10s"]	

            attacking_transition_metrics = ["time_to_progression_seconds", "first_pass_forward_pct",
                                            "final_third_entries_10s_pct", "box_entries_10s_pct",
                                            "retained_possessions_5s_pct"]	

            attacking_metrics = ["long_ball_%", "buildup_%", "progressive_passes_%", 
                                "crosses_per_final_third_entry", "dribbles_per_final_third_entry", 
                                "box_entries_from_crosses", "box_entries_from_carries"]

            chance_creation_metrics = ["sustained_attacks", "direct_attack", 
                                    "shots_per_final_third_pass", "shots_outside_box"]
                
            # Compute the arithmetic mean for each metric and assign to the respective column
            dff["defence_z"] = dff[defence_metrics].mean(axis=1)
            dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
            dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
            dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
            dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

            # Get a list of the current columns
            cols = list(dff.columns)

            # List of columns to be relocated
            cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                            "attacking_z", "chance_creation_z"]

            # Remove these columns from the list
            for col in cols_to_remove:
                cols.remove(col)

            # Insert the columns in the desired order at index 1, adjusting the index as we go
            for i, col in enumerate(cols_to_remove):
                cols.insert(1 + i, col)

            # Reorder the dataframe columns accordingly
            dff = dff[cols]
            
            # Renaming columns
            columns_to_rename = ["round", "date", "fixture", "team_name",
                                "team_possession", "opponent_possession", "defence", "defensive_transition",
                                "attacking_transition", "attacking", "chance_creation", "defensive_height", 
                                "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct","defensive_intensity",	
                                "avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                "transition_vulnerability_index", "opposition_final_third_entries_10s", 
                                "opposition_box_entries_10s", "time_to_progression_seconds", "first_pass_forward_pct", 
                                "final_third_entries_10s_pct", "box_entries_10s_pct", "retained_possessions_5s_pct", 
                                "long_ball_%", "buildup_%", "progressive_passes_%", "crosses_per_final_third_entry", 
                                "dribbles_per_final_third_entry", "box_entries_from_crosses", "box_entries_from_carries", 
                                "sustained_attacks", "direct_attack", "shots_per_final_third_pass", "shots_outside_box"
                                ]

            columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                            "Posse adversário (%)", "Defesa", "Transição defensiva",
                            "Transição ofensiva", "Ataque", "Criação de chances", 
                            "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                            "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                            "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                            "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                            "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                            "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                            "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                            "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                                ]

            # Create a dictionary mapping old names to new names
            rename_dict = dict(zip(columns_to_rename, columns_renamed))

            # Rename columns in variable_df_z_team (dff has attributes)
            dff = dff.rename(columns=rename_dict)
            
            # Create dfg dataframe from dff, selecting columns [1:] from dfg (dfg has metrics)
            dfg = dff[dfd.columns[0:]]
            
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################

            #Plotar Primeiro Gráfico - Dispersão dos destaques positivos em eixo único:

            # Dynamically create the HTML string with the 'club' variable
            # Use the dynamically created HTML string in st.markdown

            # Apply CSS styling to the jogos dataframe
            def style_jogos(df):
                # First, let's drop the 'index' column if it exists
                if 'index' in df.columns:
                    df = df.drop(columns=['index'])
                    
                return df.style.set_table_styles([
                    {"selector": "th", "props": [("font-weight", "bold"), ("border-bottom", "1px solid black"), ("text-align", "center")]},
                    {"selector": "td", "props": [("border-bottom", "1px solid gray"), ("text-align", "center")]},
                    {"selector": "tbody tr th", "props": [("font-size", "1px")]},  # Set font size for index column to 1px
                    {"selector": "thead tr th:first-child", "props": [("font-size", "1px")]},  # Also set font size for index header
                    #{"selector": "table", "props": [("margin-left", "auto"), ("margin-right", "auto"), ("border-collapse", "collapse")]},
                    #{"selector": "table, th, td", "props": [("border", "none")]},  # Remove outer borders
                    {"selector": "tr", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                    {"selector": "th", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                    {"selector": "td", "props": [("border-left", "none"), ("border-right", "none")]}
                ])

            jogos = style_jogos(jogos)

            # Display the styled dataframe in Streamlit using markdown
            st.markdown(
                '<div style="display: flex; justify-content: center;">' + jogos.to_html(border=0) + '</div>',
                unsafe_allow_html=True
            )
            #st.write("---")

            #st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques positivos do {clube}<br>nos últimos 5 jogos em {st.session_state.selected_option}</h4>",
            #            unsafe_allow_html=True
            #            )

            attribute_chart_z2 = dfg
            # The second specific data point you want to highlight
            attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
            # Add the suffix "_completo" to the content of the "clube" column
            attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
            
            attribute_chart_z1 = dfd

            # Add the single row from attribute_chart_z2 to attribute_chart_z1
            attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
            
            # Collecting data
            #Collecting data to plot
            metrics = attribute_chart_z1.iloc[:, np.r_[1:7]].reset_index(drop=True)
            metrics_participação_1 = metrics.iloc[:, 0].tolist()
            metrics_participação_2 = metrics.iloc[:, 1].tolist()
            metrics_participação_3 = metrics.iloc[:, 2].tolist()
            metrics_participação_4 = metrics.iloc[:, 3].tolist()
            metrics_participação_5 = metrics.iloc[:, 4].tolist()
            metrics_participação_6 = metrics.iloc[:, 5].tolist()
            metrics_y = [0] * len(metrics_participação_1)

            # The specific data point you want to highlight
            highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
            highlight = highlight.iloc[:, np.r_[1:7]].reset_index(drop=True)
            highlight_participação_1 = highlight.iloc[:, 0].tolist()
            highlight_participação_2 = highlight.iloc[:, 1].tolist()
            highlight_participação_3 = highlight.iloc[:, 2].tolist()
            highlight_participação_4 = highlight.iloc[:, 3].tolist()
            highlight_participação_5 = highlight.iloc[:, 4].tolist()
            highlight_participação_6 = highlight.iloc[:, 5].tolist()
            highlight_y = 0

            # Computing the selected team specific values
            highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
            highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
            highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
            highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
            highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
            highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

            highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
            highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
            highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
            highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
            highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
            highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

            # Computing the min and max value across all lists using a generator expression
            min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            min_value = min_value - 0.1
            max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            max_value = max_value + 0.1

            # Create two subplots vertically aligned with separate x-axes
            fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
            #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

            # Building the Extended Title"
            rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
            
            # Function to determine club's rank in metric in league
            def get_clube_rank(clube, column_idx, dataframe):
                # Get the actual column name from the index (using positions 1-7)
                column_name = dataframe.columns[column_idx]
                
                # Rank clubs based on the specified column in descending order
                dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                
                # Find the rank of the specified club
                clube_row = dataframe[dataframe['clube'] == clube]
                if not clube_row.empty:
                    return int(clube_row['Rank'].iloc[0])
                else:
                    return None
                
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

            # Data to plot
            column_name_at_index_1 = attribute_chart_z1.columns[1]
            output_str = f"({participação_1_ranking_value}/{rows_count})"
            full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

            # Data to plot
            column_name_at_index_2 = attribute_chart_z1.columns[2]
            output_str = f"({participação_2_ranking_value}/{rows_count})"
            full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
            
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

            # Data to plot
            column_name_at_index_3 = attribute_chart_z1.columns[3]
            output_str = f"({participação_3_ranking_value}/{rows_count})"
            full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

            # Data to plot
            column_name_at_index_4 = attribute_chart_z1.columns[4]
            output_str = f"({participação_4_ranking_value}/{rows_count})"
            full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

            # Data to plot
            column_name_at_index_5 = attribute_chart_z1.columns[5]
            output_str = f"({participação_5_ranking_value}/{rows_count})"
            full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_6_ranking_value = (get_clube_rank(clube, 6, attribute_chart_z1))

            # Data to plot
            column_name_at_index_6 = attribute_chart_z1.columns[6]
            output_str = f"({participação_6_ranking_value}/{rows_count})"
            full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

            ##############################################################################################################
            ##############################################################################################################
            #From Claude version2

            def calculate_ranks(values):
                """Calculate ranks for a given metric, with highest values getting rank 1"""
                return pd.Series(values).rank(ascending=False).astype(int).tolist()

            def prepare_data(tabela_a, metrics_cols):
                """Prepare the metrics data dictionary with all required data"""
                metrics_data = {}
                
                for col in metrics_cols:
                    # Store the metric values
                    metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                    # Calculate and store ranks
                    metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                    # Store player names
                    metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                
                return metrics_data

            def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                """
                Create an interactive plot showing club metrics with hover information
                
                Parameters:
                tabela_a (pd.DataFrame): DataFrame containing all player data
                club (str): clube
                min_value (float): Minimum value for x-axis
                max_value (float): Maximum value for x-axis
                """
                # List of metrics to plot
                # Replace the hardcoded metrics_list with dynamic column retrieval
                metrics_list = [tabela_a.columns[idx] for idx in range(1, 7)]

                # Prepare all the data
                metrics_data = prepare_data(tabela_a, metrics_list)
                
                # Calculate highlight data
                highlight_data = {
                    f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                    for metric in metrics_list
                }
                
                # Calculate highlight ranks
                highlight_ranks = {
                    metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                    for metric in metrics_list
                }
                
                # Total number of clubs
                total_clubs = len(tabela_a)
                
                # Create subplots
                fig = make_subplots(
                    rows=7, 
                    cols=1,
                    subplot_titles=[
                        f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                        for metric in metrics_list
                    ],
                    vertical_spacing=0.04
                )

                # Update subplot titles font size and color
                for i in fig['layout']['annotations']:
                    i['font'] = dict(size=17, color='black')

                # Add traces for each metric
                for idx, metric in enumerate(metrics_list, 1):
                    # Create list of colors and customize club names for legend
                    colors = []
                    custom_club_names = []
                    
                    # Track if we have any "_completo" clubs to determine if we need a legend entry
                    has_completo_clubs = False
                    
                    for name in metrics_data[f'player_names_{metric}']:
                        if '_completo' in name:
                            colors.append('gold')
                            has_completo_clubs = True
                            # Strip "_completo" from name for display but add "(completo)" indicator
                            clean_name = name.replace('_completo', '')
                            custom_club_names.append(f"{clean_name} (completo)")
                        else:
                            colors.append('deepskyblue')
                            custom_club_names.append(name)
                    
                    # Add scatter plot for regular clubs
                    regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                    
                    if regular_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                y=[0] * len(regular_clubs_indices),
                                mode='markers',
                                #name='Demais Clubes',
                                name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                marker=dict(
                                    color='deepskyblue',
                                    size=8
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Add separate scatter plot for "_completo" clubs
                    completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                    
                    if completo_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                y=[0] * len(completo_clubs_indices),
                                mode='markers',
                                #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                name=f'<span style="color:gold;">{clube} (completo)</span>',
                                marker=dict(
                                    color='gold',
                                    size=12
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Prepare highlighted club name for display
                    highlight_display_name = clube
                    highlight_color = 'blue'
                    
                    if '_completo' in clube:
                        highlight_color = 'yellow'
                        highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                    
                    # Add highlighted player point
                    fig.add_trace(
                        go.Scatter(
                            x=[highlight_data[f'highlight_{metric}']],
                            y=[0],
                            mode='markers',
                            name=highlight_display_name,  # Use the formatted name
                            marker=dict(
                                color=highlight_color,
                                size=12
                            ),
                            hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )
                # Get the total number of metrics (subplots)
                n_metrics = len(metrics_list)

                # Update layout for each subplot
                for i in range(1, n_metrics + 1):
                    if i == n_metrics:  # Only for the last subplot
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='black',
                            zerolinewidth=1,
                            showline=False,
                            ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                            tickvals=[min_value/2, 0, max_value/2],
                            tickmode='array',
                            ticks="outside",
                            ticklen=2,
                            tickfont=dict(size=16),
                            tickangle=0,
                            side='bottom',
                            automargin=False,
                            row=i, 
                            col=1
                        )
                        # Adjust layout for the last subplot
                        fig.update_layout(
                            xaxis_tickfont_family="Arial",
                            margin=dict(b=0)  # Reduce bottom margin
                        )
                    else:  # For all other subplots
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='grey',
                            zerolinewidth=1,
                            showline=False,
                            showticklabels=False,  # Hide tick labels
                            row=i, 
                            col=1
                        )  # Reduces space between axis and labels

                    # Update layout for the entire figure
                    fig.update_yaxes(
                        showticklabels=False,
                        showgrid=False,
                        showline=False,
                        row=i, 
                        col=1
                    )

                # Update layout for the entire figure
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=16)
                    ),
                    margin=dict(t=100)
                )

                # Add x-axis label at the bottom
                fig.add_annotation(
                    text="Desvio-padrão",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.06,
                    showarrow=False,
                    font=dict(size=16, color='black')
                )

                return fig

            # Calculate min and max values with some padding
            min_value_test = min([
            min(metrics_participação_1), min(metrics_participação_2), 
            min(metrics_participação_3), min(metrics_participação_4),
            min(metrics_participação_5), min(metrics_participação_6)
            ])  # Add padding of 0.5

            max_value_test = max([
            max(metrics_participação_1), max(metrics_participação_2), 
            max(metrics_participação_3), max(metrics_participação_4),
            max(metrics_participação_5), max(metrics_participação_6)
            ])  # Add padding of 0.5

            min_value = -max(abs(min_value_test), max_value_test) -0.03
            max_value = -min_value

            # Create the plot
            fig = create_club_attributes_plot(
                tabela_a=attribute_chart_z1,  # Your main dataframe
                club=clube,  # Name of player to highlight
                min_value= min_value,  # Minimum value for x-axis
                max_value= max_value    # Maximum value for x-axis
            )

            #st.plotly_chart(fig, use_container_width=True, key="unique_key_8")
            #st.write("---")

    ################################################################################################################################# 
    #################################################################################################################################
    #################################################################################################################################
    #################################################################################################################################
    #################################################################################################################################

            #Plotar Segundo Gráfico - Dispersão dos destaques negativos em eixo único:

            # Dynamically create the HTML string with the 'club' variable
            # Use the dynamically created HTML string in st.markdown
            #st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques negativos do {clube}<br>nos últimos 5 jogos em {st.session_state.selected_option}</h4>",
            #            unsafe_allow_html=True
            #            )

            attribute_chart_z2 = dfg
            # The second specific data point you want to highlight
            attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
            # Add the suffix "_completo" to the content of the "clube" column
            attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
            
            attribute_chart_z1 = dfd

            # Add the single row from attribute_chart_z2 to attribute_chart_z1
            attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
            
            # Collecting data
            #Collecting data to plot
            metrics = attribute_chart_z1.iloc[:, np.r_[7:13]].reset_index(drop=True)
            metrics_participação_1 = metrics.iloc[:, 0].tolist()
            metrics_participação_2 = metrics.iloc[:, 1].tolist()
            metrics_participação_3 = metrics.iloc[:, 2].tolist()
            metrics_participação_4 = metrics.iloc[:, 3].tolist()
            metrics_participação_5 = metrics.iloc[:, 4].tolist()
            metrics_participação_6 = metrics.iloc[:, 5].tolist()
            metrics_y = [0] * len(metrics_participação_1)

            # The specific data point you want to highlight
            highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
            highlight = highlight.iloc[:, np.r_[7:13]].reset_index(drop=True)
            highlight_participação_1 = highlight.iloc[:, 0].tolist()
            highlight_participação_2 = highlight.iloc[:, 1].tolist()
            highlight_participação_3 = highlight.iloc[:, 2].tolist()
            highlight_participação_4 = highlight.iloc[:, 3].tolist()
            highlight_participação_5 = highlight.iloc[:, 4].tolist()
            highlight_participação_6 = highlight.iloc[:, 5].tolist()
            highlight_y = 0

            # Computing the selected team specific values
            highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
            highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
            highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
            highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
            highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
            highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

            highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
            highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
            highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
            highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
            highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
            highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

            # Computing the min and max value across all lists using a generator expression
            min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            min_value = min_value - 0.1
            max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            max_value = max_value + 0.1

            # Create two subplots vertically aligned with separate x-axes
            fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
            #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

            # Building the Extended Title"
            rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
            
            # Function to determine club's rank in metric in league
            def get_clube_rank(clube, column_idx, dataframe):
                # Get the actual column name from the index (using positions 7-13)
                column_name = dataframe.columns[column_idx]
                
                # Rank clubs based on the specified column in descending order
                dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                
                # Find the rank of the specified club
                clube_row = dataframe[dataframe['clube'] == clube]
                if not clube_row.empty:
                    return int(clube_row['Rank'].iloc[0])
                else:
                    return None
                
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_1_ranking_value = (get_clube_rank(clube, 7, attribute_chart_z1))

            # Data to plot
            column_name_at_index_1 = attribute_chart_z1.columns[7]
            output_str = f"({participação_1_ranking_value}/{rows_count})"
            full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_2_ranking_value = (get_clube_rank(clube, 8, attribute_chart_z1))

            # Data to plot
            column_name_at_index_2 = attribute_chart_z1.columns[8]
            output_str = f"({participação_2_ranking_value}/{rows_count})"
            full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
            
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_3_ranking_value = (get_clube_rank(clube, 9, attribute_chart_z1))

            # Data to plot
            column_name_at_index_3 = attribute_chart_z1.columns[9]
            output_str = f"({participação_3_ranking_value}/{rows_count})"
            full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_4_ranking_value = (get_clube_rank(clube, 10, attribute_chart_z1))

            # Data to plot
            column_name_at_index_4 = attribute_chart_z1.columns[10]
            output_str = f"({participação_4_ranking_value}/{rows_count})"
            full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_5_ranking_value = (get_clube_rank(clube, 11, attribute_chart_z1))

            # Data to plot
            column_name_at_index_5 = attribute_chart_z1.columns[11]
            output_str = f"({participação_5_ranking_value}/{rows_count})"
            full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_6_ranking_value = (get_clube_rank(clube, 12, attribute_chart_z1))

            # Data to plot
            column_name_at_index_6 = attribute_chart_z1.columns[12]
            output_str = f"({participação_6_ranking_value}/{rows_count})"
            full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

            ##############################################################################################################
            ##############################################################################################################
            #From Claude version2

            def calculate_ranks(values):
                """Calculate ranks for a given metric, with highest values getting rank 1"""
                return pd.Series(values).rank(ascending=False).astype(int).tolist()

            def prepare_data(tabela_a, metrics_cols):
                """Prepare the metrics data dictionary with all required data"""
                metrics_data = {}
                
                for col in metrics_cols:
                    # Store the metric values
                    metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                    # Calculate and store ranks
                    metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                    # Store player names
                    metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                
                return metrics_data

            def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                """
                Create an interactive plot showing club metrics with hover information
                
                Parameters:
                tabela_a (pd.DataFrame): DataFrame containing all player data
                club (str): clube
                min_value (float): Minimum value for x-axis
                max_value (float): Maximum value for x-axis
                """
                # List of metrics to plot
                # Replace the hardcoded metrics_list with dynamic column retrieval
                metrics_list = [tabela_a.columns[idx] for idx in range(7, 13)]

                # Prepare all the data
                metrics_data = prepare_data(tabela_a, metrics_list)
                
                # Calculate highlight data
                highlight_data = {
                    f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                    for metric in metrics_list
                }
                
                # Calculate highlight ranks
                highlight_ranks = {
                    metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                    for metric in metrics_list
                }
                
                # Total number of clubs
                total_clubs = len(tabela_a)
                
                # Create subplots
                fig = make_subplots(
                    rows=7, 
                    cols=1,
                    subplot_titles=[
                        f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                        for metric in metrics_list
                    ],
                    vertical_spacing=0.04
                )

                # Update subplot titles font size and color
                for i in fig['layout']['annotations']:
                    i['font'] = dict(size=17, color='black')

                # Add traces for each metric
                for idx, metric in enumerate(metrics_list, 1):
                    # Create list of colors and customize club names for legend
                    colors = []
                    custom_club_names = []
                    
                    # Track if we have any "_completo" clubs to determine if we need a legend entry
                    has_completo_clubs = False
                    
                    for name in metrics_data[f'player_names_{metric}']:
                        if '_completo' in name:
                            colors.append('gold')
                            has_completo_clubs = True
                            # Strip "_completo" from name for display but add "(completo)" indicator
                            clean_name = name.replace('_completo', '')
                            custom_club_names.append(f"{clean_name} (completo)")
                        else:
                            colors.append('deepskyblue')
                            custom_club_names.append(name)
                    
                    # Add scatter plot for regular clubs
                    regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                    
                    if regular_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                y=[0] * len(regular_clubs_indices),
                                mode='markers',
                                #name='Demais Clubes',
                                name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                marker=dict(
                                    color='deepskyblue',
                                    size=8
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Add separate scatter plot for "_completo" clubs
                    completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                    
                    if completo_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                y=[0] * len(completo_clubs_indices),
                                mode='markers',
                                #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                name=f'<span style="color:gold;">{clube} (completo)</span>',
                                marker=dict(
                                    color='gold',
                                    size=12
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Prepare highlighted club name for display
                    highlight_display_name = clube
                    highlight_color = 'blue'
                    
                    if '_completo' in clube:
                        highlight_color = 'yellow'
                        highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                    
                    # Add highlighted player point
                    fig.add_trace(
                        go.Scatter(
                            x=[highlight_data[f'highlight_{metric}']],
                            y=[0],
                            mode='markers',
                            name=highlight_display_name,  # Use the formatted name
                            marker=dict(
                                color=highlight_color,
                                size=12
                            ),
                            hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )
                # Get the total number of metrics (subplots)
                n_metrics = len(metrics_list)

                # Update layout for each subplot
                for i in range(1, n_metrics + 1):
                    if i == n_metrics:  # Only for the last subplot
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='black',
                            zerolinewidth=1,
                            showline=False,
                            ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                            tickvals=[min_value/2, 0, max_value/2],
                            tickmode='array',
                            ticks="outside",
                            ticklen=2,
                            tickfont=dict(size=16),
                            tickangle=0,
                            side='bottom',
                            automargin=False,
                            row=i, 
                            col=1
                        )
                        # Adjust layout for the last subplot
                        fig.update_layout(
                            xaxis_tickfont_family="Arial",
                            margin=dict(b=0)  # Reduce bottom margin
                        )
                    else:  # For all other subplots
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='grey',
                            zerolinewidth=1,
                            showline=False,
                            showticklabels=False,  # Hide tick labels
                            row=i, 
                            col=1
                        )  # Reduces space between axis and labels

                    # Update layout for the entire figure
                    fig.update_yaxes(
                        showticklabels=False,
                        showgrid=False,
                        showline=False,
                        row=i, 
                        col=1
                    )

                # Update layout for the entire figure
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=16)
                    ),
                    margin=dict(t=100)
                )

                # Add x-axis label at the bottom
                fig.add_annotation(
                    text="Desvio-padrão",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.06,
                    showarrow=False,
                    font=dict(size=16, color='black')
                )

                return fig

            # Calculate min and max values with some padding
            min_value_test = min([
            min(metrics_participação_1), min(metrics_participação_2), 
            min(metrics_participação_3), min(metrics_participação_4),
            min(metrics_participação_5), min(metrics_participação_6)
            ])  # Add padding of 0.5

            max_value_test = max([
            max(metrics_participação_1), max(metrics_participação_2), 
            max(metrics_participação_3), max(metrics_participação_4),
            max(metrics_participação_5), max(metrics_participação_6)
            ])  # Add padding of 0.5

            min_value = -max(abs(min_value_test), max_value_test) -0.03
            max_value = -min_value

            # Create the plot
            fig = create_club_attributes_plot(
                tabela_a=attribute_chart_z1,  # Your main dataframe
                club=clube,  # Name of player to highlight
                min_value= min_value,  # Minimum value for x-axis
                max_value= max_value    # Maximum value for x-axis
            )

            #st.plotly_chart(fig, use_container_width=True, key="unique_key_9")

        #################################################################################################################################
        #################################################################################################################################

            #### INCLUIR BOT

            st.write("---")
            st.markdown(
                """
                <h3 style='text-align: center;'>Análise de Estilo de Jogo</h3>
                """,
                unsafe_allow_html=True
            )

            # Create necessary files:
            single_dfd = dfd8[dfd8["clube"] == clube]
            single_dfd2 = dfc_attributes[dfc_attributes["clube"] == clube]
            # Merge single_dfd and single_dfd2 based on "clube"
            single_dfd = single_dfd.merge(single_dfd2, on="clube", how="left")
            context_df = pd.read_csv("context_style.csv")
            playstyle_df = pd.read_csv("play_style2.csv")
            jogos_df = jogos_df.iloc[2]

            
            # Configure Google Gemini API
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

            def generate_opponent_analysis(single_dfd, context_df, playstyle_df, jogos_df):
                """
                Generate a detailed play style analysis based on the club's play style metrics.
                
                Args:
                    single_dfd (pd.DataFrame): DataFrame with club name and z-scores for better/worse play style metrics
                    context_df (pd.DataFrame): DataFrame with play style attributes and metrics definitions
                    playstyle_df (pd.DataFrame): DataFrame with play styles and their definitions
                    jogos_df (pd.DataFrame): DataFrame with the fixtures of the last 5 club matches                            
                
                Returns:
                    str: Generated play style analysis in Portuguese
                """
                # Extract club name and metrics
                clube = single_dfd.iloc[0, 0]
                metricas_melhores = single_dfd.iloc[0, 1:9].to_dict()
                metricas_piores = single_dfd.iloc[0, 9:17].to_dict()
                attributes = single_dfd.iloc[0, 17:22].to_dict()
                jogos_df = jogos_df.to_dict()
                
                # Sort metrics by z-score (abs value) to focus on most significant ones
                metricas_melhores_sorted = {k: v for k, v in sorted(
                    metricas_melhores.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                metricas_piores_sorted = {k: v for k, v in sorted(
                    metricas_piores.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                attributes_sorted = {k: v for k, v in sorted(
                    attributes.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                # Create prompt for Gemini
                prompt = (
                    f"Escreva uma análise aprofundada do estilo de jogo do clube {clube} baseada nos dados fornecidos, em português brasileiro. \n\n"
                    f"Escreva a análise sob a perspectiva de um adversário que irá enfrentar o clube {clube} na próxima partida e quer entender sua estratégia de jogo. \n\n"
                    f"Pontos fortes (métricas em z-score que destacam as opções de jogo mais utilizadas pelo clube):\n{pd.Series(metricas_melhores_sorted).to_string()}\n\n"
                    f"Pontos fracos (métricas em z-score que destacam as opções de jogo menos utilizadas pelo clube):\n{pd.Series(metricas_piores_sorted).to_string()}\n\n"
                    f"jogos (resultados das últimas 5 partidas disputadas pelo clube):\n{pd.Series(jogos_df).to_string()}\n\n"
                    f"Contexto Conceitual - Atributos e Métricas:\n{context_df.to_string()}\n\n"
                    f"Estilos de Jogo:\n{playstyle_df.to_string()}\n\n"
                    "Considere o os resultados dos jogos, o desempenho nas métricas e a relação entre a definição das métricas destacadas e dos atributos aos quais pertencem para identificar o estilo de jogo do clube. "
                    "Se a identificação for clara, descreva o possível estilo de jogo da equipe com base nas definições fornecidas para atributos e métricas. "
                    "A análise deve ser bem estruturada, técnica mas compreensível e com aproximadamente 500 palavras. "
                    "Não apresente z-scores na análise final."
                )
                
                # Generate the analysis using Gemini
                model = genai.GenerativeModel("gemini-flash-latest")
                response = model.generate_content(prompt)
                
                # Clean and format the response
                analysis = response.text
                
                # Add title and formatting
                formatted_analysis = f"""
                ## {clube}
            
                {analysis}
                """
                
                return formatted_analysis

            def main():

                # Initialize session state variable
                if "show_analise_adversario4" not in st.session_state:
                    st.session_state.show_analise_adversario4 = False

                # Título estilizado
                #st.markdown("<p style='font-size:35px; font-weight:bold; text-align:center;'>Análise de Adversário</p>", unsafe_allow_html=True)

                # Botão que ativa a exibição
                if st.button("Gerar Análise de Estilo de Jogo", type='primary', key=113):
                    st.session_state.show_analise_adversario4 = True

                # Conteúdo persistente após o clique
                if st.session_state.show_analise_adversario4:

                    with st.spinner("Gerando análise detalhada do adversário..."):
                        analysis = generate_opponent_analysis(
                            single_dfd,
                            context_df,
                            playstyle_df,
                            jogos_df
                        )
                        
                        # Display the analysis
                        st.markdown(analysis)
                        
                        # Add download button for the analysis as PDF
                        import io
                        from fpdf import FPDF
                        
                        def create_pdf(text):
                            text = text.replace('\u2013', '-')  # quick fix for en dash
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            # Add title
                            pdf.set_font("Arial", "B", 16)
                            pdf.cell(0, 10, f"{clube}", ln=True)
                            pdf.ln(5)
                            
                            # Add content
                            pdf.set_font("Arial", "", 12)
                            
                            # Split text into lines and add to PDF
                            lines = text.split('\n')
                            for line in lines:
                                # Check if line is a header
                                if line.strip().startswith('#'):
                                    pdf.set_font("Arial", "B", 14)
                                    pdf.cell(0, 10, line.replace('#', '').strip(), ln=True)
                                    pdf.set_font("Arial", "", 12)
                                else:
                                    pdf.multi_cell(0, 10, line)
                            
                            return pdf.output(dest="S").encode("latin-1", errors="replace")
                        
                        clube = single_dfd.iloc[0, 0]
                        pdf_data = create_pdf(analysis)
                        
                        st.download_button(
                            label="Baixar Análise como PDF",
                            data=pdf_data,
                            file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.pdf",
                            mime="application/pdf",
                            key=202
                        )

                        # Add download button for the analysis
                        clube = single_dfd.iloc[0, 0]
                        st.download_button(
                            label="Baixar Análise como TXT",
                            data=analysis,
                            file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.txt",
                            mime="text/plain",
                            key=203
                        )

            if __name__ == "__main__":
                main()

            #################################################################################################################################
            ################################################################################################################################# 
            #################################################################################################################################

                ################################################################################################################################# 
                #################################################################################################################################
                ################################################################################################################################# 
                #################################################################################################################################


            def calculate_club_similarity(dfc_metrics, clube):
                """
                Calculate the similarity index between a reference club and all other clubs
                based on five attributes, with each attribute worth 0-20 points.
                """
                # Get the index of the reference club
                if clube not in dfc_metrics.iloc[:, 0].values:
                    st.error(f"Reference club '{clube}' not found in the dataset")
                    return None
                
                ref_idx = dfc_metrics.index[dfc_metrics.iloc[:, 0] == clube][0]
                # Define attribute column ranges
                attribute_ranges = {
                    "Defesa": range(1, 5),
                    "Transição defensiva": range(5, 10),
                    "Transição ofensiva": range(10, 15),
                    "Ataque": range(15, 22),
                    "Criação de chances": range(22, 26)
                }
                
                # Dictionary to store results
                similarity_results = {}
                
                # Calculate similarity for each club
                for idx, row in dfc_metrics.iterrows():
                    club_name = row.iloc[0]
                    
                    if club_name == clube:
                        continue
                    
                    # Calculate similarity for each attribute
                    attribute_similarities = {}
                    
                    for attr_name, col_range in attribute_ranges.items():
                        # Extract reference club and current club attribute values
                        ref_attr = dfc_metrics.iloc[ref_idx, col_range].values.reshape(1, -1)
                        club_attr = dfc_metrics.iloc[idx, col_range].values.reshape(1, -1)
                        
                        # Calculate cosine similarity
                        cos_sim = cosine_similarity(ref_attr, club_attr)[0][0]
                        
                        # Convert to 0-20 scale
                        # Cosine similarity ranges from -1 to 1, so we rescale from 0 to 20
                        # where -1 -> 0, 0 -> 10, 1 -> 20
                        attr_similarity = 10 * (cos_sim + 1)
                        
                        attribute_similarities[attr_name] = attr_similarity
                    
                    # Calculate total similarity
                    total_similarity = sum(attribute_similarities.values())
                    
                    # Store results
                    similarity_results[club_name] = {
                        'Total': total_similarity,
                        **attribute_similarities
                    }
                
                # Convert to DataFrame for easier handling
                similarity_df = pd.DataFrame.from_dict(similarity_results, orient='index')
                similarity_df = similarity_df.sort_values('Total', ascending=False)
                
                return similarity_df

            def plot_similarity_index(similarity_df, clube):
                """
                Create a horizontal bar chart with attribute breakdown showing individual
                attribute values (out of 20) in the hover template
                """
                if similarity_df is None or similarity_df.empty:
                    return None
                    
                # Create a figure with custom layout
                fig = go.Figure()
                
                # Define attribute colors matching the example image
                colors = {
                    'Defesa': '#D3D3D3',  # Light Gray
                    'Transição defensiva': '#4682B4',  # Blue
                    'Transição ofensiva': '#FFD700',  # Yellow/Gold
                    'Ataque': '#006400',  # Dark Green
                    'Criação de chances': '#FF4500'  # Red/Orange
                }
                
                # Attributes in the desired order (based on the example image legend)
                attributes = ['Ataque', 'Defesa', 'Transição ofensiva', 'Transição defensiva', 'Criação de chances']
                
                # Get clubs in descending order of total similarity
                clubs = similarity_df.index.tolist()
                
                # Calculate positions for stacked bars
                positions = {attr: [] for attr in attributes}
                cumulative = np.zeros(len(clubs))
                
                for attr in attributes:
                    positions[attr] = cumulative.copy()
                    cumulative += similarity_df[attr].values
                
                # Add each attribute as a stacked bar
                for i, attr in enumerate(attributes):
                    fig.add_trace(go.Bar(
                        y=clubs,
                        x=similarity_df[attr],
                        name=attr,
                        orientation='h',
                        marker=dict(color=colors[attr]),
                        base=positions[attr],
                        customdata=similarity_df[attr],  # Store the actual attribute value
                        hovertemplate=f"{attr}: %{{customdata:.1f}}/20<extra></extra>"  # Use customdata instead of x
                    ))

                # Customize layout
                fig.update_layout(
                    # Center the title
                    title=dict(
                        text=f"Similaridade de Estilo de Jogo entre o {clube}<br> e os demais clubes nas últimas 5 partidas disputadas",
                        x=0.5,
                        xanchor='center',
                        font=dict(size=18)
                    ),
                    xaxis=dict(
                        title='',
                        range=[0, 100],
                        tickvals=[0, 20, 40, 60, 80, 100],
                        tickfont=dict(size=14, 
                                        color='black'),
                        showgrid=True,
                        gridcolor='lightgray'
                    ),
                    yaxis=dict(
                        title='',
                        autorange="reversed",  # Ensure highest similarity at top
                        tickfont=dict(
                            size=14,
                            color='black'
                        )
                    ),
                    barmode='stack',
                    # Adjust legend position and properties
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,  # Lower position to make room for x-axis labels
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12),
                        bgcolor='rgba(255,255,255,0.8)'
                    ),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='black'),
                    height=650,  # Increased height to accommodate the legend
                    width=900,
                    hovermode="y unified",
                    margin=dict(l=150, r=50, t=80, b=100)  # Increased bottom margin for x-axis labels
                )
                
                # Ensure the y-axis labels are black and larger
                fig.update_yaxes(
                    tickfont=dict(
                        size=14,
                        color='black'
                    )
                )
                
                return fig

            def display_similarity_analysis(dfc_metrics):
                """
                Display the club similarity analysis section in a Streamlit app
                with the provided dfc_metrics DataFrame
                """
                st.markdown(
                    """
                    <h3 style='text-align: center;'>Índice de Similaridade de Estilo de Jogo</h3>
                    """,
                    unsafe_allow_html=True
                )

                # Custom CSS for better formatting
                st.markdown("""
                <style>
                    .main {
                        padding: 2rem;
                    }
                    .stAlert {
                        background-color: #f8f9fa;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        border-left: 5px solid #ff4b4b;
                    }
                    .info-box {
                        background-color: #e6f3ff;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        border-left: 5px solid #4B8BF5;
                        margin-bottom: 1rem;
                    }
                    h1, h2, h3 {
                        color: #1E3A8A;
                    }
                    .katex {
                        font-size: 1.1em;
                    }
                </style>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="info-box">
                <p><h4>Índice de Similaridade de Estilo de Jogo:</h4></p>
                <p>Quantifica as semelhanças táticas entre clubes de futebol nas diferentes fases do jogo, como defesa, 
                transições defensivas, transições ofensivas, ataque e criação de chances. Cada aspecto recebe uma nota de 0 a 20, 
                somando um total máximo de 100 pontos. Quanto maior a pontuação, mais parecido é o estilo de jogo entre os times comparados. 
                Considera os últimos jogos disputados, em casa ou fora.
                </div>
                """, unsafe_allow_html=True)

                
                # Club selection via dropdown
                
                # Add a button to trigger the analysis
                if st.button("Calcule o Índice", type='primary', key=100):
                    # Run analysis
                    with st.spinner("Calculating similarity indices..."):
                        similarity_df = calculate_club_similarity(dfc_metrics, clube)
                    
                    if similarity_df is not None:
                        # Create and display the plot
                        fig = plot_similarity_index(similarity_df, clube)
                        if fig is not None:
                            st.plotly_chart(fig, use_container_width=True)

            st.write("---")
            display_similarity_analysis(dfc_metrics)


        ################################################################################################################################# 
        #################################################################################################################################
        ################################################################################################################################# 
        #################################################################################################################################



            #################################################################################################################################
            #################################################################################################################################
            #################################################################################################################################

            #### INCLUIR NOTA COM DESCRIÇÃO DAS MÉTRICAS FORTES E FRACAS
            st.write("---")
            st.markdown(
                """
                <h3 style='text-align: center;'>Quer saber as definições das Métricas? Clique abaixo!</h3>
                """,
                unsafe_allow_html=True
            )

            if st.button("Definições das Métricas", key=109):

                st.markdown("<p style='font-size:24px; font-weight:bold;'>Nota:</p>", unsafe_allow_html=True)
                
                def generate_metrics_sections(dfd, context_df):
                    # Generate positive metrics section (columns 1-7)
                    positive_metrics_names = dfd.columns[1:7]
                    
                    # Initialize positive definitions list
                    positive_metrics_definitions = []
                    
                    # For each positive metric name, find its definition in context_df
                    for metric_name in positive_metrics_names:
                        # Find the row where 'Métrica' column equals the metric name
                        matching_row = context_df[context_df['Métrica'] == metric_name]
                        
                        # If a match is found, add the definition to the list
                        if not matching_row.empty:
                            definition = matching_row['Definição'].values[0]
                            positive_metrics_definitions.append(definition)
                        else:
                            # If no match is found, add an empty string as placeholder
                            positive_metrics_definitions.append("")
                    
                    # Create the positive metrics markdown
                    positive_markdown = "#### MÉTRICAS COM DESTAQUE POSITIVO\n"
                    for name, definition in zip(positive_metrics_names, positive_metrics_definitions):
                        positive_markdown += f"- **{name}**: {definition}\n"
                    
                    # Generate negative metrics section (columns 7-13)
                    negative_metrics_names = dfd.columns[7:13]
                    
                    # Initialize negative definitions list
                    negative_metrics_definitions = []
                    
                    # For each negative metric name, find its definition in context_df
                    for metric_name in negative_metrics_names:
                        # Find the row where 'Métrica' column equals the metric name
                        matching_row = context_df[context_df['Métrica'] == metric_name]
                        
                        # If a match is found, add the definition to the list
                        if not matching_row.empty:
                            definition = matching_row['Definição'].values[0]
                            negative_metrics_definitions.append(definition)
                        else:
                            # If no match is found, add an empty string as placeholder
                            negative_metrics_definitions.append("")
                    
                    # Create the negative metrics markdown
                    negative_markdown = "#### MÉTRICAS COM DESTAQUE NEGATIVO\n"
                    for name, definition in zip(negative_metrics_names, negative_metrics_definitions):
                        negative_markdown += f"- **{name}**: {definition}\n"
                    
                    # Display both sections
                    st.markdown(positive_markdown)
                    st.markdown(negative_markdown)

                # Example usage:
                generate_metrics_sections(dfd, context_df)


                #################################################################################################################################
                ################################################################################################################################# 
                #################################################################################################################################
                #################################################################################################################################
                #################################################################################################################################
                #################################################################################################################################

        #Selecting last up to five games of each club (home or away) 
        elif st.session_state.selected_option == "Fora":
            # --- FORA PATH ---
            st.write("---")
            
            # Custom CSS for better formatting
            st.markdown("""
            <style>
                .main {
                    padding: 2rem;
                }
                .stAlert {
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid #ff4b4b;
                }
                .info-box {
                    background-color: #e6f3ff;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid #4B8BF5;
                    margin-bottom: 1rem;
                }
                h1, h2, h3 {
                    color: #1E3A8A;
                }
                .katex {
                    font-size: 1.1em;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-box">
            <p><h4>Análise do Estilo de Jogo do Clube:</h4></p>
            <p>Esta ferramenta gera automaticamente uma análise do estilo de jogo do clube, utilizando dados 
            estatísticos de desempenho relacionados às diferentes fases do jogo: Defesa, Transição Defensiva, 
            Transição Ofensiva, Ataque e Criação de Chances. A análise identifica os pontos fortes e fracos da 
            equipe nas últimas cinco partidas disputadas fora de casa. O usuário pode visualizar a análise 
            diretamente na interface e baixá-la em formato PDF ou TXT para uso posterior.
            </div>
            """, unsafe_allow_html=True)


            #Tratamento da base de dados - PlayStyle Analysis - Inclusão da Rodada
            df = pd.read_csv("play_style_metrics.csv")
            dfa = df.sort_values(by="date", ascending=False)
            
            # Initialize a new session state variable for this level                         
            if 'analysis_type' not in st.session_state:                             
                st.session_state.analysis_type = None                          

            # Create a new callback function for this level                         
            def select_analysis_type(option):                             
                st.session_state.analysis_type = option                          

            # Define a style for the analysis type buttons
            analysis_type_style = """
            <style>
            div[data-testid="stButton"] button.analysis-type-selected {
                background-color: #FF4B4B !important;
                color: white !important;
                border-color: #FF0000 !important;
            }
            </style>
            """
            st.markdown(analysis_type_style, unsafe_allow_html=True)

            # Filter df to get the first 5 "game_id" for each "team_name" where "place" == "Fora"
            dfa = df[df['place'] == "Fora"].groupby('team_name').tail(5)

            # Create (últimos 5) jogos dataframe
            jogos = dfa.loc[dfa["team_name"] == clube, ["date", "fixture"]].rename(columns={"fixture": "Últimos 5 Jogos", "date": "Data"}).sort_values(by="Data", ascending=False)
            
            # Reset index to match the original dataframe structure
            jogos = jogos.reset_index()
            jogos_df = jogos
            
            # Ensure dfa has the required columns
            columns_to_average = dfa.columns[11:]

            # Compute mean for each column for each "team_name"
            dfb = dfa.groupby('team_name')[columns_to_average].mean().reset_index()
            #dfb_fora = dfb.to_csv("dfb_fora.csv")

            # Ensure dfb has the required columns
            columns_to_normalize = dfb.columns[1:]

            # Normalize selected columns while keeping "team_name"
            dfc = dfb.copy()
            dfc[columns_to_normalize] = dfb[columns_to_normalize].apply(zscore)

            # Inverting the sign of inverted metrics
            dfc["PPDA"] = -1*dfc["PPDA"]
            dfc["avg_time_to_defensive_action"] = -1*dfc["avg_time_to_defensive_action"]
            dfc["transition_vulnerability_index"] = -1*dfc["transition_vulnerability_index"]
            dfc["opposition_final_third_entries_10s"] = -1*dfc["opposition_final_third_entries_10s"]
            dfc["opposition_box_entries_10s"] = -1*dfc["opposition_box_entries_10s"]
            dfc["time_to_progression_seconds"] = -1*dfc["time_to_progression_seconds"]
            
            # Creating qualities columns
            defence_metrics = ["defensive_height", "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct",
                            "defensive_intensity"]

            defensive_transition_metrics = ["avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                            "transition_vulnerability_index", "opposition_final_third_entries_10s",
                                            "opposition_box_entries_10s"]	

            attacking_transition_metrics = ["time_to_progression_seconds", "first_pass_forward_pct",
                                            "final_third_entries_10s_pct", "box_entries_10s_pct",
                                            "retained_possessions_5s_pct"]	

            attacking_metrics = ["long_ball_%", "buildup_%", "progressive_passes_%", 
                                "crosses_per_final_third_entry", "dribbles_per_final_third_entry", 
                                "box_entries_from_crosses", "box_entries_from_carries"]

            chance_creation_metrics = ["sustained_attacks", "direct_attack", 
                                    "shots_per_final_third_pass", "shots_outside_box"]
                
            # Compute the arithmetic mean for each metric and assign to the respective column
            dfc["defence_z"] = dfc[defence_metrics].mean(axis=1)
            dfc["defensive_transition_z"] = dfc[defensive_transition_metrics].mean(axis=1)
            dfc["attacking_transition_z"] = dfc[attacking_transition_metrics].mean(axis=1)
            dfc["attacking_z"] = dfc[attacking_metrics].mean(axis=1)
            dfc["chance_creation_z"] = dfc[chance_creation_metrics].mean(axis=1)

            # Get a list of the current columns
            cols = list(dfc.columns)

            # List of columns to be relocated
            cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                            "attacking_z", "chance_creation_z"]

            # Remove these columns from the list
            for col in cols_to_remove:
                cols.remove(col)

            # Insert the columns in the desired order at index 1, adjusting the index as we go
            for i, col in enumerate(cols_to_remove):
                cols.insert(1 + i, col)

            # Reorder the dataframe columns accordingly
            dfc = dfc[cols]
            
            # Renaming columns
            # Renaming columns
            columns_to_rename = ["round", "date", "fixture", "team_name",
                                "team_possession", "opponent_possession", "defence", "defensive_transition",
                                "attacking_transition", "attacking", "chance_creation", "defensive_height", 
                                "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct","defensive_intensity",	
                                "avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                "transition_vulnerability_index", "opposition_final_third_entries_10s", 
                                "opposition_box_entries_10s", "time_to_progression_seconds", "first_pass_forward_pct", 
                                "final_third_entries_10s_pct", "box_entries_10s_pct", "retained_possessions_5s_pct", 
                                "long_ball_%", "buildup_%", "progressive_passes_%", "crosses_per_final_third_entry", 
                                "dribbles_per_final_third_entry", "box_entries_from_crosses", "box_entries_from_carries", 
                                "sustained_attacks", "direct_attack", "shots_per_final_third_pass", "shots_outside_box"
                                ]

            columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                            "Posse adversário (%)", "Defesa", "Transição defensiva",
                            "Transição ofensiva", "Ataque", "Criação de chances", 
                            "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                            "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                            "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                            "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                            "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                            "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                            "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                            "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                                ]

            # Create a dictionary mapping old names to new names
            rename_dict = dict(zip(columns_to_rename, columns_renamed))

            # Rename columns in variable_df_z_team
            dfc = dfc.rename(columns=rename_dict)
            clube_data = dfc[dfc['clube'] == clube].set_index('clube')

            # Select club attributes
            dfc_attributes = dfc.iloc[:, np.r_[0:6]]
            
            # Select club metrics columns from dfc
            dfc_metrics = dfc.iloc[:, np.r_[0, 6:32]]

            # Identify top 6 and bottom 6 metrics for the given clube
            def filter_top_bottom_metrics(dfc_metrics, clube):
                
                # Select the row corresponding to the given club
                clube_data = dfc_metrics[dfc_metrics['clube'] == clube].set_index('clube')
                
                # Identify top 6 and bottom 6 metrics based on values (single row)
                top_6_metrics = clube_data.iloc[0].nlargest(6).index
                bottom_6_metrics = clube_data.iloc[0].nsmallest(6).index
                
                # Keep only relevant columns
                selected_columns = ['clube'] + list(top_6_metrics) + list(bottom_6_metrics)
                dfd = dfc_metrics[selected_columns]
                
                return dfd

            # Example usage (assuming clube is defined somewhere)
            dfd = filter_top_bottom_metrics(dfc_metrics, clube)
            
            
            ##################################################################################################################
            ##################################################################################################################
            
            # Create full competition so far mean
            dfe = df[df['place'] == "Fora"].groupby('team_name', as_index=False).apply(lambda x: x.reset_index(drop=True))

            # Ensure dfa has the required columns
            columns_to_average = dfe.columns[11:]

            # Compute mean for each column for each "team_name"
            dfe = dfe.groupby('team_name')[columns_to_average].mean().reset_index()

            # Ensure dfb has the required columns
            columns_to_normalize = dfe.columns[1:]

            # Normalize selected columns while keeping "team_name"
            dff = dfe.copy()
            dff[columns_to_normalize] = dff[columns_to_normalize].apply(zscore)

            dff["PPDA"] = -1*dff["PPDA"]
            dff["avg_time_to_defensive_action"] = -1*dff["avg_time_to_defensive_action"]
            dff["transition_vulnerability_index"] = -1*dff["transition_vulnerability_index"]
            dff["opposition_final_third_entries_10s"] = -1*dff["opposition_final_third_entries_10s"]
            dff["opposition_box_entries_10s"] = -1*dff["opposition_box_entries_10s"]
            dff["time_to_progression_seconds"] = -1*dff["time_to_progression_seconds"]
            
            # Creating qualities columns
            defence_metrics = ["defensive_height", "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct",
                            "defensive_intensity"]

            defensive_transition_metrics = ["avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                            "transition_vulnerability_index", "opposition_final_third_entries_10s",
                                            "opposition_box_entries_10s"]	

            attacking_transition_metrics = ["time_to_progression_seconds", "first_pass_forward_pct",
                                            "final_third_entries_10s_pct", "box_entries_10s_pct",
                                            "retained_possessions_5s_pct"]	

            attacking_metrics = ["long_ball_%", "buildup_%", "progressive_passes_%", 
                                "crosses_per_final_third_entry", "dribbles_per_final_third_entry", 
                                "box_entries_from_crosses", "box_entries_from_carries"]

            chance_creation_metrics = ["sustained_attacks", "direct_attack", 
                                    "shots_per_final_third_pass", "shots_outside_box"]
                
            # Compute the arithmetic mean for each metric and assign to the respective column
            dff["defence_z"] = dff[defence_metrics].mean(axis=1)
            dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
            dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
            dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
            dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)
                
            # Compute the arithmetic mean for each metric and assign to the respective column
            dff["defence_z"] = dff[defence_metrics].mean(axis=1)
            dff["defensive_transition_z"] = dff[defensive_transition_metrics].mean(axis=1)
            dff["attacking_transition_z"] = dff[attacking_transition_metrics].mean(axis=1)
            dff["attacking_z"] = dff[attacking_metrics].mean(axis=1)
            dff["chance_creation_z"] = dff[chance_creation_metrics].mean(axis=1)

            # Get a list of the current columns
            cols = list(dff.columns)

            # List of columns to be relocated
            cols_to_remove = ["defence_z", "defensive_transition_z", "attacking_transition_z", 
                            "attacking_z", "chance_creation_z"]

            # Remove these columns from the list
            for col in cols_to_remove:
                cols.remove(col)

            # Insert the columns in the desired order at index 1, adjusting the index as we go
            for i, col in enumerate(cols_to_remove):
                cols.insert(1 + i, col)

            # Reorder the dataframe columns accordingly
            dff = dff[cols]
            
            # Renaming columns
            columns_to_rename = ["round", "date", "fixture", "team_name",
                                "team_possession", "opponent_possession", "defence", "defensive_transition",
                                "attacking_transition", "attacking", "chance_creation", "defensive_height", 
                                "high_recoveries_pct", "PPDA", "fouls_in_attacking_half_pct","defensive_intensity",	
                                "avg_time_to_defensive_action", "counter_press_Success_Rate_%",
                                "transition_vulnerability_index", "opposition_final_third_entries_10s", 
                                "opposition_box_entries_10s", "time_to_progression_seconds", "first_pass_forward_pct", 
                                "final_third_entries_10s_pct", "box_entries_10s_pct", "retained_possessions_5s_pct", 
                                "long_ball_%", "buildup_%", "progressive_passes_%", "crosses_per_final_third_entry", 
                                "dribbles_per_final_third_entry", "box_entries_from_crosses", "box_entries_from_carries", 
                                "sustained_attacks", "direct_attack", "shots_per_final_third_pass", "shots_outside_box"
                                ]

            columns_renamed = ["rodada", "data", "partida", "clube", "Posse (%)",
                            "Posse adversário (%)", "Defesa", "Transição defensiva",
                            "Transição ofensiva", "Ataque", "Criação de chances", 
                            "Altura defensiva (m)", "Recuperações de posse no último terço (%)", "PPDA", "Faltas no campo de ataque (%)",
                            "Intensidade defensiva", "Tempo médio ação defensiva (s)", "Sucesso da pressão pós perda (5s) (%)",
                            "Índice de Vulnerabilidade na Transição", "Entradas do adversário no último terço em 10s",
                            "Entradas do adversário na área em 10s", "Tempo para progressão (s)", "Primeiro passe à frente (%)",
                            "Entradas no último terço em 10s", "Entradas na área em 10s", "Posse mantida em 5s (%)",
                            "Bola longa (%)", "Buildup do goleiro (%)", "Passes progressivos do terço médio (%)", "Entradas no último terço por Cruzamentos (%)",
                            "Entradas no último terço por Dribles (%)", "Entradas na área por Cruzamentos (%)", "Entradas na área por Conduções (%)",
                            "Finalizações em ataque sustentado (%)", "Finalizações em ataque direto (%)", "Finalizações por passe no último terço (%)", "Finalizações de fora da área (%)"
                                ]

            # Create a dictionary mapping old names to new names
            rename_dict = dict(zip(columns_to_rename, columns_renamed))

            # Rename columns in variable_df_z_team (dff has attributes)
            dff = dff.rename(columns=rename_dict)
            
            # Create dfg dataframe from dff, selecting columns [1:] from dfg (dfg has metrics)
            dfg = dff[dfd.columns[0:]]
            
            ##################################################################################################################### 
            #####################################################################################################################
            #################################################################################################################################

            #Plotar Primeiro Gráfico - Dispersão dos destaques positivos em eixo único:

            # Dynamically create the HTML string with the 'club' variable
            # Use the dynamically created HTML string in st.markdown
            st.write("---")
            
            st.markdown(f"<h3 style='text-align: center;'><b>Análise de Estilo de Jogo do Adversário jogando Fora de Casa</b></h3>", unsafe_allow_html=True)

            st.write("---")
            
            # Select a club
            club_selected = clube

            # Get the image URL for the selected club
            image_url = club_image_paths[club_selected]

            # Center-align and display the image
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{image_url}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )                

            # Apply CSS styling to the jogos dataframe
            def style_jogos(df):
                # First, let's drop the 'index' column if it exists
                if 'index' in df.columns:
                    df = df.drop(columns=['index'])
                    
                return df.style.set_table_styles([
                    {"selector": "th", "props": [("font-weight", "bold"), ("border-bottom", "1px solid black"), ("text-align", "center")]},
                    {"selector": "td", "props": [("border-bottom", "1px solid gray"), ("text-align", "center")]},
                    {"selector": "tbody tr th", "props": [("font-size", "1px")]},  # Set font size for index column to 1px
                    {"selector": "thead tr th:first-child", "props": [("font-size", "1px")]},  # Also set font size for index header
                    #{"selector": "table", "props": [("margin-left", "auto"), ("margin-right", "auto"), ("border-collapse", "collapse")]},
                    #{"selector": "table, th, td", "props": [("border", "none")]},  # Remove outer borders
                    {"selector": "tr", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                    {"selector": "th", "props": [("border-top", "none"), ("border-left", "none"), ("border-right", "none")]},
                    {"selector": "td", "props": [("border-left", "none"), ("border-right", "none")]}
                ])

            jogos = style_jogos(jogos)

            # Display the styled dataframe in Streamlit using markdown
            st.markdown(
                '<div style="display: flex; justify-content: center;">' + jogos.to_html(border=0) + '</div>',
                unsafe_allow_html=True
            )
            st.write("---")



            #st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques positivos do {clube}<br>nos últimos 5 jogos {st.session_state.selected_option} de Casa</h4>",
            #            unsafe_allow_html=True
            #            )

            attribute_chart_z2 = dfg
            # The second specific data point you want to highlight
            attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
            # Add the suffix "_completo" to the content of the "clube" column
            attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
            
            attribute_chart_z1 = dfd

            # Add the single row from attribute_chart_z2 to attribute_chart_z1
            attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
            
            # Collecting data
            #Collecting data to plot
            metrics = attribute_chart_z1.iloc[:, np.r_[1:7]].reset_index(drop=True)
            metrics_participação_1 = metrics.iloc[:, 0].tolist()
            metrics_participação_2 = metrics.iloc[:, 1].tolist()
            metrics_participação_3 = metrics.iloc[:, 2].tolist()
            metrics_participação_4 = metrics.iloc[:, 3].tolist()
            metrics_participação_5 = metrics.iloc[:, 4].tolist()
            metrics_participação_6 = metrics.iloc[:, 5].tolist()
            metrics_y = [0] * len(metrics_participação_1)

            # The specific data point you want to highlight
            highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
            highlight = highlight.iloc[:, np.r_[1:7]].reset_index(drop=True)
            highlight_participação_1 = highlight.iloc[:, 0].tolist()
            highlight_participação_2 = highlight.iloc[:, 1].tolist()
            highlight_participação_3 = highlight.iloc[:, 2].tolist()
            highlight_participação_4 = highlight.iloc[:, 3].tolist()
            highlight_participação_5 = highlight.iloc[:, 4].tolist()
            highlight_participação_6 = highlight.iloc[:, 5].tolist()
            highlight_y = 0

            # Computing the selected team specific values
            highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
            highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
            highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
            highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
            highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
            highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

            highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
            highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
            highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
            highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
            highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
            highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

            # Computing the min and max value across all lists using a generator expression
            min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            min_value = min_value - 0.1
            max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            max_value = max_value + 0.1

            # Create two subplots vertically aligned with separate x-axes
            fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
            #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

            # Building the Extended Title"
            rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
            
            # Function to determine club's rank in metric in league
            def get_clube_rank(clube, column_idx, dataframe):
                # Get the actual column name from the index (using positions 1-7)
                column_name = dataframe.columns[column_idx]
                
                # Rank clubs based on the specified column in descending order
                dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                
                # Find the rank of the specified club
                clube_row = dataframe[dataframe['clube'] == clube]
                if not clube_row.empty:
                    return int(clube_row['Rank'].iloc[0])
                else:
                    return None
                
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_1_ranking_value = (get_clube_rank(clube, 1, attribute_chart_z1))

            # Data to plot
            column_name_at_index_1 = attribute_chart_z1.columns[1]
            output_str = f"({participação_1_ranking_value}/{rows_count})"
            full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_2_ranking_value = (get_clube_rank(clube, 2, attribute_chart_z1))

            # Data to plot
            column_name_at_index_2 = attribute_chart_z1.columns[2]
            output_str = f"({participação_2_ranking_value}/{rows_count})"
            full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
            
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_3_ranking_value = (get_clube_rank(clube, 3, attribute_chart_z1))

            # Data to plot
            column_name_at_index_3 = attribute_chart_z1.columns[3]
            output_str = f"({participação_3_ranking_value}/{rows_count})"
            full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_4_ranking_value = (get_clube_rank(clube, 4, attribute_chart_z1))

            # Data to plot
            column_name_at_index_4 = attribute_chart_z1.columns[4]
            output_str = f"({participação_4_ranking_value}/{rows_count})"
            full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_5_ranking_value = (get_clube_rank(clube, 5, attribute_chart_z1))

            # Data to plot
            column_name_at_index_5 = attribute_chart_z1.columns[5]
            output_str = f"({participação_5_ranking_value}/{rows_count})"
            full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_6_ranking_value = (get_clube_rank(clube, 6, attribute_chart_z1))

            # Data to plot
            column_name_at_index_6 = attribute_chart_z1.columns[6]
            output_str = f"({participação_6_ranking_value}/{rows_count})"
            full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

            ##############################################################################################################
            ##############################################################################################################
            #From Claude version2

            def calculate_ranks(values):
                """Calculate ranks for a given metric, with highest values getting rank 1"""
                return pd.Series(values).rank(ascending=False).astype(int).tolist()

            def prepare_data(tabela_a, metrics_cols):
                """Prepare the metrics data dictionary with all required data"""
                metrics_data = {}
                
                for col in metrics_cols:
                    # Store the metric values
                    metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                    # Calculate and store ranks
                    metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                    # Store player names
                    metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                
                return metrics_data

            def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                """
                Create an interactive plot showing club metrics with hover information
                
                Parameters:
                tabela_a (pd.DataFrame): DataFrame containing all player data
                club (str): clube
                min_value (float): Minimum value for x-axis
                max_value (float): Maximum value for x-axis
                """
                # List of metrics to plot
                # Replace the hardcoded metrics_list with dynamic column retrieval
                metrics_list = [tabela_a.columns[idx] for idx in range(1, 7)]

                # Prepare all the data
                metrics_data = prepare_data(tabela_a, metrics_list)
                
                # Calculate highlight data
                highlight_data = {
                    f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                    for metric in metrics_list
                }
                
                # Calculate highlight ranks
                highlight_ranks = {
                    metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                    for metric in metrics_list
                }
                
                # Total number of clubs
                total_clubs = len(tabela_a)
                
                # Create subplots
                fig = make_subplots(
                    rows=7, 
                    cols=1,
                    subplot_titles=[
                        f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                        for metric in metrics_list
                    ],
                    vertical_spacing=0.04
                )

                # Update subplot titles font size and color
                for i in fig['layout']['annotations']:
                    i['font'] = dict(size=17, color='black')

                # Add traces for each metric
                for idx, metric in enumerate(metrics_list, 1):
                    # Create list of colors and customize club names for legend
                    colors = []
                    custom_club_names = []
                    
                    # Track if we have any "_completo" clubs to determine if we need a legend entry
                    has_completo_clubs = False
                    
                    for name in metrics_data[f'player_names_{metric}']:
                        if '_completo' in name:
                            colors.append('gold')
                            has_completo_clubs = True
                            # Strip "_completo" from name for display but add "(completo)" indicator
                            clean_name = name.replace('_completo', '')
                            custom_club_names.append(f"{clean_name} (completo)")
                        else:
                            colors.append('deepskyblue')
                            custom_club_names.append(name)
                    
                    # Add scatter plot for regular clubs
                    regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                    
                    if regular_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                y=[0] * len(regular_clubs_indices),
                                mode='markers',
                                #name='Demais Clubes',
                                name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                marker=dict(
                                    color='deepskyblue',
                                    size=8
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Add separate scatter plot for "_completo" clubs
                    completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                    
                    if completo_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                y=[0] * len(completo_clubs_indices),
                                mode='markers',
                                #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                name=f'<span style="color:gold;">{clube} (completo)</span>',
                                marker=dict(
                                    color='gold',
                                    size=12
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Prepare highlighted club name for display
                    highlight_display_name = clube
                    highlight_color = 'blue'
                    
                    if '_completo' in clube:
                        highlight_color = 'yellow'
                        highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                    
                    # Add highlighted player point
                    fig.add_trace(
                        go.Scatter(
                            x=[highlight_data[f'highlight_{metric}']],
                            y=[0],
                            mode='markers',
                            name=highlight_display_name,  # Use the formatted name
                            marker=dict(
                                color=highlight_color,
                                size=12
                            ),
                            hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )
                # Get the total number of metrics (subplots)
                n_metrics = len(metrics_list)

                # Update layout for each subplot
                for i in range(1, n_metrics + 1):
                    if i == n_metrics:  # Only for the last subplot
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='black',
                            zerolinewidth=1,
                            showline=False,
                            ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                            tickvals=[min_value/2, 0, max_value/2],
                            tickmode='array',
                            ticks="outside",
                            ticklen=2,
                            tickfont=dict(size=16),
                            tickangle=0,
                            side='bottom',
                            automargin=False,
                            row=i, 
                            col=1
                        )
                        # Adjust layout for the last subplot
                        fig.update_layout(
                            xaxis_tickfont_family="Arial",
                            margin=dict(b=0)  # Reduce bottom margin
                        )
                    else:  # For all other subplots
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='grey',
                            zerolinewidth=1,
                            showline=False,
                            showticklabels=False,  # Hide tick labels
                            row=i, 
                            col=1
                        )  # Reduces space between axis and labels

                    # Update layout for the entire figure
                    fig.update_yaxes(
                        showticklabels=False,
                        showgrid=False,
                        showline=False,
                        row=i, 
                        col=1
                    )

                # Update layout for the entire figure
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=16)
                    ),
                    margin=dict(t=100)
                )

                # Add x-axis label at the bottom
                fig.add_annotation(
                    text="Desvio-padrão",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.06,
                    showarrow=False,
                    font=dict(size=16, color='black')
                )

                return fig

            # Calculate min and max values with some padding
            min_value_test = min([
            min(metrics_participação_1), min(metrics_participação_2), 
            min(metrics_participação_3), min(metrics_participação_4),
            min(metrics_participação_5), min(metrics_participação_6)
            ])  # Add padding of 0.5

            max_value_test = max([
            max(metrics_participação_1), max(metrics_participação_2), 
            max(metrics_participação_3), max(metrics_participação_4),
            max(metrics_participação_5), max(metrics_participação_6)
            ])  # Add padding of 0.5

            min_value = -max(abs(min_value_test), max_value_test) -0.03
            max_value = -min_value

            # Create the plot
            fig = create_club_attributes_plot(
                tabela_a=attribute_chart_z1,  # Your main dataframe
                club=clube,  # Name of player to highlight
                min_value= min_value,  # Minimum value for x-axis
                max_value= max_value    # Maximum value for x-axis
            )

            #st.plotly_chart(fig, use_container_width=True, key="unique_key_13")
            #st.write("---")

    ################################################################################################################################# 
    #################################################################################################################################
    #################################################################################################################################
    #################################################################################################################################
    #################################################################################################################################

            #Plotar Segundo Gráfico - Dispersão dos destaques negativos em eixo único:

            # Dynamically create the HTML string with the 'club' variable
            # Use the dynamically created HTML string in st.markdown
            #st.markdown(f"<h4 style='text-align: center; color: black;'>Destaques negativos do {clube}<br>nos últimos 5 jogos {st.session_state.selected_option} de Casa</h4>",
            #            unsafe_allow_html=True
            #            )

            attribute_chart_z2 = dfg
            # The second specific data point you want to highlight
            attribute_chart_z2 = attribute_chart_z2[(attribute_chart_z2['clube']==clube)]
            # Add the suffix "_completo" to the content of the "clube" column
            attribute_chart_z2['clube'] = attribute_chart_z2['clube'] + "_completo"
            
            attribute_chart_z1 = dfd

            # Add the single row from attribute_chart_z2 to attribute_chart_z1
            attribute_chart_z1 = pd.concat([attribute_chart_z1, attribute_chart_z2], ignore_index=True)
            
            # Collecting data
            #Collecting data to plot
            metrics = attribute_chart_z1.iloc[:, np.r_[7:13]].reset_index(drop=True)
            metrics_participação_1 = metrics.iloc[:, 0].tolist()
            metrics_participação_2 = metrics.iloc[:, 1].tolist()
            metrics_participação_3 = metrics.iloc[:, 2].tolist()
            metrics_participação_4 = metrics.iloc[:, 3].tolist()
            metrics_participação_5 = metrics.iloc[:, 4].tolist()
            metrics_participação_6 = metrics.iloc[:, 5].tolist()
            metrics_y = [0] * len(metrics_participação_1)

            # The specific data point you want to highlight
            highlight = attribute_chart_z1[(attribute_chart_z1['clube']==clube)]
            highlight = highlight.iloc[:, np.r_[7:13]].reset_index(drop=True)
            highlight_participação_1 = highlight.iloc[:, 0].tolist()
            highlight_participação_2 = highlight.iloc[:, 1].tolist()
            highlight_participação_3 = highlight.iloc[:, 2].tolist()
            highlight_participação_4 = highlight.iloc[:, 3].tolist()
            highlight_participação_5 = highlight.iloc[:, 4].tolist()
            highlight_participação_6 = highlight.iloc[:, 5].tolist()
            highlight_y = 0

            # Computing the selected team specific values
            highlight_participação_1_value = pd.DataFrame(highlight_participação_1).reset_index(drop=True)
            highlight_participação_2_value = pd.DataFrame(highlight_participação_2).reset_index(drop=True)
            highlight_participação_3_value = pd.DataFrame(highlight_participação_3).reset_index(drop=True)
            highlight_participação_4_value = pd.DataFrame(highlight_participação_4).reset_index(drop=True)
            highlight_participação_5_value = pd.DataFrame(highlight_participação_5).reset_index(drop=True)
            highlight_participação_6_value = pd.DataFrame(highlight_participação_6).reset_index(drop=True)

            highlight_participação_1_value = highlight_participação_1_value.iat[0,0]
            highlight_participação_2_value = highlight_participação_2_value.iat[0,0]
            highlight_participação_3_value = highlight_participação_3_value.iat[0,0]
            highlight_participação_4_value = highlight_participação_4_value.iat[0,0]
            highlight_participação_5_value = highlight_participação_5_value.iat[0,0]
            highlight_participação_6_value = highlight_participação_6_value.iat[0,0]

            # Computing the min and max value across all lists using a generator expression
            min_value = min(min(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            min_value = min_value - 0.1
            max_value = max(max(lst) for lst in [metrics_participação_1, metrics_participação_2, 
                                                metrics_participação_3, metrics_participação_4,
                                                metrics_participação_5, metrics_participação_6
                                                ])
            max_value = max_value + 0.1

            # Create two subplots vertically aligned with separate x-axes
            fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1)
            #ax.set_xlim(min_value, max_value)  # Set the same x-axis scale for each plot

            # Building the Extended Title"
            rows_count = attribute_chart_z1[(attribute_chart_z1['clube'] == clube)].shape[0]
            
            # Function to determine club's rank in metric in league
            def get_clube_rank(clube, column_idx, dataframe):
                # Get the actual column name from the index (using positions 7-13)
                column_name = dataframe.columns[column_idx]
                
                # Rank clubs based on the specified column in descending order
                dataframe['Rank'] = dataframe[column_name].rank(ascending=False, method='min')
                
                # Find the rank of the specified club
                clube_row = dataframe[dataframe['clube'] == clube]
                if not clube_row.empty:
                    return int(clube_row['Rank'].iloc[0])
                else:
                    return None
                
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_1_ranking_value = (get_clube_rank(clube, 7, attribute_chart_z1))

            # Data to plot
            column_name_at_index_1 = attribute_chart_z1.columns[7]
            output_str = f"({participação_1_ranking_value}/{rows_count})"
            full_title_participação_1 = f"{column_name_at_index_1} {output_str} {highlight_participação_1_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_2_ranking_value = (get_clube_rank(clube, 8, attribute_chart_z1))

            # Data to plot
            column_name_at_index_2 = attribute_chart_z1.columns[8]
            output_str = f"({participação_2_ranking_value}/{rows_count})"
            full_title_participação_2 = f"{column_name_at_index_2} {output_str} {highlight_participação_2_value}"
            
            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_3_ranking_value = (get_clube_rank(clube, 9, attribute_chart_z1))

            # Data to plot
            column_name_at_index_3 = attribute_chart_z1.columns[9]
            output_str = f"({participação_3_ranking_value}/{rows_count})"
            full_title_participação_3 = f"{column_name_at_index_3} {output_str} {highlight_participação_3_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_4_ranking_value = (get_clube_rank(clube, 10, attribute_chart_z1))

            # Data to plot
            column_name_at_index_4 = attribute_chart_z1.columns[10]
            output_str = f"({participação_4_ranking_value}/{rows_count})"
            full_title_participação_4 = f"{column_name_at_index_4} {output_str} {highlight_participação_4_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_5_ranking_value = (get_clube_rank(clube, 11, attribute_chart_z1))

            # Data to plot
            column_name_at_index_5 = attribute_chart_z1.columns[11]
            output_str = f"({participação_5_ranking_value}/{rows_count})"
            full_title_participação_5 = f"{column_name_at_index_5} {output_str} {highlight_participação_5_value}"

            # Building the Extended Title"
            # Determining club's rank in metric in league
            participação_6_ranking_value = (get_clube_rank(clube, 12, attribute_chart_z1))

            # Data to plot
            column_name_at_index_6 = attribute_chart_z1.columns[12]
            output_str = f"({participação_6_ranking_value}/{rows_count})"
            full_title_participação_6 = f"{column_name_at_index_6} {output_str} {highlight_participação_6_value}"

            ##############################################################################################################
            ##############################################################################################################
            #From Claude version2

            def calculate_ranks(values):
                """Calculate ranks for a given metric, with highest values getting rank 1"""
                return pd.Series(values).rank(ascending=False).astype(int).tolist()

            def prepare_data(tabela_a, metrics_cols):
                """Prepare the metrics data dictionary with all required data"""
                metrics_data = {}
                
                for col in metrics_cols:
                    # Store the metric values
                    metrics_data[f'metrics_{col}'] = tabela_a[col].tolist()
                    # Calculate and store ranks
                    metrics_data[f'ranks_{col}'] = calculate_ranks(tabela_a[col])
                    # Store player names
                    metrics_data[f'player_names_{col}'] = tabela_a['clube'].tolist()
                
                return metrics_data

            def create_club_attributes_plot(tabela_a, club, min_value, max_value):
                """
                Create an interactive plot showing club metrics with hover information
                
                Parameters:
                tabela_a (pd.DataFrame): DataFrame containing all player data
                club (str): clube
                min_value (float): Minimum value for x-axis
                max_value (float): Maximum value for x-axis
                """
                # List of metrics to plot
                # Replace the hardcoded metrics_list with dynamic column retrieval
                metrics_list = [tabela_a.columns[idx] for idx in range(7, 13)]

                # Prepare all the data
                metrics_data = prepare_data(tabela_a, metrics_list)
                
                # Calculate highlight data
                highlight_data = {
                    f'highlight_{metric}': tabela_a[tabela_a['clube'] == clube][metric].iloc[0]
                    for metric in metrics_list
                }
                
                # Calculate highlight ranks
                highlight_ranks = {
                    metric: int(pd.Series(tabela_a[metric]).rank(ascending=False)[tabela_a['clube'] == clube].iloc[0])
                    for metric in metrics_list
                }
                
                # Total number of clubs
                total_clubs = len(tabela_a)
                
                # Create subplots
                fig = make_subplots(
                    rows=7, 
                    cols=1,
                    subplot_titles=[
                        f"{metric.capitalize()} ({highlight_ranks[metric]}/{total_clubs}) {highlight_data[f'highlight_{metric}']:.2f}"
                        for metric in metrics_list
                    ],
                    vertical_spacing=0.04
                )

                # Update subplot titles font size and color
                for i in fig['layout']['annotations']:
                    i['font'] = dict(size=17, color='black')

                # Add traces for each metric
                for idx, metric in enumerate(metrics_list, 1):
                    # Create list of colors and customize club names for legend
                    colors = []
                    custom_club_names = []
                    
                    # Track if we have any "_completo" clubs to determine if we need a legend entry
                    has_completo_clubs = False
                    
                    for name in metrics_data[f'player_names_{metric}']:
                        if '_completo' in name:
                            colors.append('gold')
                            has_completo_clubs = True
                            # Strip "_completo" from name for display but add "(completo)" indicator
                            clean_name = name.replace('_completo', '')
                            custom_club_names.append(f"{clean_name} (completo)")
                        else:
                            colors.append('deepskyblue')
                            custom_club_names.append(name)
                    
                    # Add scatter plot for regular clubs
                    regular_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' not in name]
                    
                    if regular_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in regular_clubs_indices],
                                y=[0] * len(regular_clubs_indices),
                                mode='markers',
                                #name='Demais Clubes',
                                name=f'<span style="color:deepskyblue;">Demais Clubes</span>',
                                marker=dict(
                                    color='deepskyblue',
                                    size=8
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in regular_clubs_indices],
                                customdata=[custom_club_names[i] for i in regular_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Add separate scatter plot for "_completo" clubs
                    completo_clubs_indices = [i for i, name in enumerate(metrics_data[f'player_names_{metric}']) if '_completo' in name]
                    
                    if completo_clubs_indices:
                        fig.add_trace(
                            go.Scatter(
                                x=[metrics_data[f'metrics_{metric}'][i] for i in completo_clubs_indices],
                                y=[0] * len(completo_clubs_indices),
                                mode='markers',
                                #name= f'{clube} (completo)',  # Dedicated legend entry for completo clubs
                                name=f'<span style="color:gold;">{clube} (completo)</span>',
                                marker=dict(
                                    color='gold',
                                    size=12
                                ),
                                text=[f"{metrics_data[f'ranks_{metric}'][i]}/{total_clubs}" for i in completo_clubs_indices],
                                customdata=[custom_club_names[i] for i in completo_clubs_indices],
                                hovertemplate='%{customdata}<br>Rank: %{text}<br>Value: %{x:.2f}<extra></extra>',
                                showlegend=True if idx == 1 else False
                            ),
                            row=idx, 
                            col=1
                        )
                    
                    # Prepare highlighted club name for display
                    highlight_display_name = clube
                    highlight_color = 'blue'
                    
                    if '_completo' in clube:
                        highlight_color = 'yellow'
                        highlight_display_name = clube.replace('_completo', '') + ' (completo)'
                    
                    # Add highlighted player point
                    fig.add_trace(
                        go.Scatter(
                            x=[highlight_data[f'highlight_{metric}']],
                            y=[0],
                            mode='markers',
                            name=highlight_display_name,  # Use the formatted name
                            marker=dict(
                                color=highlight_color,
                                size=12
                            ),
                            hovertemplate=f'{highlight_display_name}<br>Rank: {highlight_ranks[metric]}/{total_clubs}<br>Value: %{{x:.2f}}<extra></extra>',
                            showlegend=True if idx == 1 else False
                        ),
                        row=idx, 
                        col=1
                    )
                # Get the total number of metrics (subplots)
                n_metrics = len(metrics_list)

                # Update layout for each subplot
                for i in range(1, n_metrics + 1):
                    if i == n_metrics:  # Only for the last subplot
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='black',
                            zerolinewidth=1,
                            showline=False,
                            ticktext=["PIOR", "MÉDIA (0)", "MELHOR"],
                            tickvals=[min_value/2, 0, max_value/2],
                            tickmode='array',
                            ticks="outside",
                            ticklen=2,
                            tickfont=dict(size=16),
                            tickangle=0,
                            side='bottom',
                            automargin=False,
                            row=i, 
                            col=1
                        )
                        # Adjust layout for the last subplot
                        fig.update_layout(
                            xaxis_tickfont_family="Arial",
                            margin=dict(b=0)  # Reduce bottom margin
                        )
                    else:  # For all other subplots
                        fig.update_xaxes(
                            range=[min_value, max_value],
                            showgrid=False,
                            zeroline=True,
                            zerolinecolor='grey',
                            zerolinewidth=1,
                            showline=False,
                            showticklabels=False,  # Hide tick labels
                            row=i, 
                            col=1
                        )  # Reduces space between axis and labels

                    # Update layout for the entire figure
                    fig.update_yaxes(
                        showticklabels=False,
                        showgrid=False,
                        showline=False,
                        row=i, 
                        col=1
                    )

                # Update layout for the entire figure
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=16)
                    ),
                    margin=dict(t=100)
                )

                # Add x-axis label at the bottom
                fig.add_annotation(
                    text="Desvio-padrão",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.06,
                    showarrow=False,
                    font=dict(size=16, color='black')
                )

                return fig

            # Calculate min and max values with some padding
            min_value_test = min([
            min(metrics_participação_1), min(metrics_participação_2), 
            min(metrics_participação_3), min(metrics_participação_4),
            min(metrics_participação_5), min(metrics_participação_6)
            ])  # Add padding of 0.5

            max_value_test = max([
            max(metrics_participação_1), max(metrics_participação_2), 
            max(metrics_participação_3), max(metrics_participação_4),
            max(metrics_participação_5), max(metrics_participação_6)
            ])  # Add padding of 0.5

            min_value = -max(abs(min_value_test), max_value_test) -0.03
            max_value = -min_value

            # Create the plot
            fig = create_club_attributes_plot(
                tabela_a=attribute_chart_z1,  # Your main dataframe
                club=clube,  # Name of player to highlight
                min_value= min_value,  # Minimum value for x-axis
                max_value= max_value    # Maximum value for x-axis
            )

            #st.plotly_chart(fig, use_container_width=True, key="unique_key_14")

        #################################################################################################################################
        #################################################################################################################################
        #################################################################################################################################
        #################################################################################################################################

#### INCLUIR BOT

            st.markdown(
                """
                <h3 style='text-align: center;'>Análise de Estilo de Jogo</h3>
                """,
                unsafe_allow_html=True
            )

            # Create necessary files:
            single_dfd = dfd[dfd["clube"] == clube]
            single_dfd2 = dfc_attributes[dfc_attributes["clube"] == clube]
            # Merge single_dfd and single_dfd2 based on "clube"
            single_dfd = single_dfd.merge(single_dfd2, on="clube", how="left")
            context_df = pd.read_csv("context_style.csv")
            playstyle_df = pd.read_csv("play_style2.csv")
            jogos_df = jogos_df.iloc[2]


            
            # Configure Google Gemini API
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

            def generate_opponent_analysis(single_dfd, context_df, playstyle_df):
                """
                Generate a detailed opponent analysis based on the club's performance metrics.
                
                Args:
                    single_dfd (pd.DataFrame): DataFrame with club name and z-scores for better/worse metrics
                    context_df (pd.DataFrame): DataFrame with attributes and metrics definitions
                    playstyle_df (pd.DataFrame): DataFrame with play styles and their definitions
                
                Returns:
                    str: Generated opponent analysis in Portuguese
                """
                # Extract club name and metrics
                clube = single_dfd.iloc[0, 0]
                metricas_melhores = single_dfd.iloc[0, 1:7].to_dict()
                metricas_piores = single_dfd.iloc[0, 7:13].to_dict()
                attributes = single_dfd.iloc[0, 13:18].to_dict()
                
                # Sort metrics by z-score (abs value) to focus on most significant ones
                metricas_melhores_sorted = {k: v for k, v in sorted(
                    metricas_melhores.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                metricas_piores_sorted = {k: v for k, v in sorted(
                    metricas_piores.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                attributes_sorted = {k: v for k, v in sorted(
                    attributes.items(), 
                    key=lambda item: abs(item[1]), 
                    reverse=True
                )}
                
                # Create prompt for Gemini
                prompt = (
                    f"Escreva uma análise aprofundada do estilo de jogo do clube {clube} baseada nos dados fornecidos, em português brasileiro. \n\n"
                    f"Escreva a análise sob a perspectiva de um adversário que irá enfrentar o clube {clube} na próxima partida e quer entender sua estratégia de jogo. \n\n"
                    f"Pontos fortes (métricas em z-score que destacam as opções de jogo mais utilizadas pelo clube):\n{pd.Series(metricas_melhores_sorted).to_string()}\n\n"
                    f"Pontos fracos (métricas em z-score que destacam as opções de jogo menos utilizadas pelo clube):\n{pd.Series(metricas_piores_sorted).to_string()}\n\n"
                    f"jogos (resultados das últimas 5 partidas disputadas pelo clube):\n{pd.Series(jogos_df).to_string()}\n\n"
                    f"Contexto Conceitual - Atributos e Métricas:\n{context_df.to_string()}\n\n"
                    f"Estilos de Jogo:\n{playstyle_df.to_string()}\n\n"
                    "Considere o os resultados dos jogos, o desempenho nas métricas e a relação entre a definição das métricas destacadas e dos atributos aos quais pertencem para identificar o estilo de jogo do clube. "
                    "Se a identificação for clara, descreva o possível estilo de jogo da equipe com base nas definições fornecidas para atributos e métricas. "
                    "A análise deve ser bem estruturada, técnica mas compreensível e com aproximadamente 500 palavras. "
                    "Não apresente z-scores na análise final."
                )
                
                # Generate the analysis using Gemini
                model = genai.GenerativeModel("gemini-flash-latest")
                response = model.generate_content(prompt)
                
                # Clean and format the response
                analysis = response.text
                
                # Add title and formatting
                formatted_analysis = f"""
                ## {clube}
            
                {analysis}
                """
                
                return formatted_analysis

            def main():
                st.write("---")
                # Initialize session state variable
                if "show_analise_adversario3" not in st.session_state:
                    st.session_state.show_analise_adversario3 = False

                # Título estilizado
                #st.markdown("<p style='font-size:35px; font-weight:bold; text-align:center;'>Análise de Adversário</p>", unsafe_allow_html=True)

                # Botão que ativa a exibição
                if st.button("Gerar Análise do Adversário", type='primary', key=112):
                    st.session_state.show_analise_adversario3 = True

                # Conteúdo persistente após o clique
                if st.session_state.show_analise_adversario3:
                    with st.spinner("Gerando análise detalhada do adversário..."):
                        analysis = generate_opponent_analysis(
                            single_dfd,
                            context_df,
                            playstyle_df
                        )
                        
                        # Display the analysis
                        st.markdown(analysis)
                        
                        # Add download button for the analysis as PDF
                        import io
                        from fpdf import FPDF
                        
                        def create_pdf(text):
                            text = text.replace('\u2013', '-')  # quick fix for en dash
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            # Add title
                            pdf.set_font("Arial", "B", 16)
                            pdf.cell(0, 10, f"{clube}", ln=True)
                            pdf.ln(5)
                            
                            # Add content
                            pdf.set_font("Arial", "", 12)
                            
                            # Split text into lines and add to PDF
                            lines = text.split('\n')
                            for line in lines:
                                # Check if line is a header
                                if line.strip().startswith('#'):
                                    pdf.set_font("Arial", "B", 14)
                                    pdf.cell(0, 10, line.replace('#', '').strip(), ln=True)
                                    pdf.set_font("Arial", "", 12)
                                else:
                                    pdf.multi_cell(0, 10, line)
                            
                            return pdf.output(dest="S").encode("latin-1", errors="replace")
                        
                        clube = single_dfd.iloc[0, 0]
                        pdf_data = create_pdf(analysis)
                        
                        st.download_button(
                            label="Baixar Análise como PDF",
                            data=pdf_data,
                            file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.pdf",
                            mime="application/pdf",
                                key=210
                        )

                        # Add download button for the analysis
                        clube = single_dfd.iloc[0, 0]
                        st.download_button(
                            label="Baixar Análise como TXT",
                            data=analysis,
                            file_name=f"analise_{re.sub('[^a-zA-Z0-9]', '_', clube)}.txt",
                            mime="text/plain",
                                key=211
                        )

            if __name__ == "__main__":
                main()

            ##################################################################################################################
            ##################################################################################################################
            ##################################################################################################################
            ##################################################################################################################

            def calculate_club_similarity(dfc_metrics, clube):
                """
                Calculate the similarity index between a reference club and all other clubs
                based on five attributes, with each attribute worth 0-20 points.
                """
                # Get the index of the reference club
                if clube not in dfc_metrics.iloc[:, 0].values:
                    st.error(f"Reference club '{clube}' not found in the dataset")
                    return None
                
                ref_idx = dfc_metrics.index[dfc_metrics.iloc[:, 0] == clube][0]
                
                # Define attribute column ranges
                attribute_ranges = {
                    "Defesa": range(1, 5),
                    "Transição defensiva": range(5, 10),
                    "Transição ofensiva": range(10, 15),
                    "Ataque": range(15, 22),
                    "Criação de chances": range(22, 26)
                }
                
                # Dictionary to store results
                similarity_results = {}
                
                # Calculate similarity for each club
                for idx, row in dfc_metrics.iterrows():
                    club_name = row.iloc[0]
                    
                    if club_name == clube:
                        continue
                    
                    # Calculate similarity for each attribute
                    attribute_similarities = {}
                    
                    for attr_name, col_range in attribute_ranges.items():
                        # Extract reference club and current club attribute values
                        ref_attr = dfc_metrics.iloc[ref_idx, col_range].values.reshape(1, -1)
                        club_attr = dfc_metrics.iloc[idx, col_range].values.reshape(1, -1)
                        
                        # Calculate cosine similarity
                        cos_sim = cosine_similarity(ref_attr, club_attr)[0][0]
                        
                        # Convert to 0-20 scale
                        # Cosine similarity ranges from -1 to 1, so we rescale from 0 to 20
                        # where -1 -> 0, 0 -> 10, 1 -> 20
                        attr_similarity = 10 * (cos_sim + 1)
                        
                        attribute_similarities[attr_name] = attr_similarity
                    
                    # Calculate total similarity
                    total_similarity = sum(attribute_similarities.values())
                    
                    # Store results
                    similarity_results[club_name] = {
                        'Total': total_similarity,
                        **attribute_similarities
                    }
                
                # Convert to DataFrame for easier handling
                similarity_df = pd.DataFrame.from_dict(similarity_results, orient='index')
                similarity_df = similarity_df.sort_values('Total', ascending=False)
                
                return similarity_df

            def plot_similarity_index(similarity_df, clube):
                """
                Create a horizontal bar chart with attribute breakdown showing individual
                attribute values (out of 20) in the hover template
                """
                if similarity_df is None or similarity_df.empty:
                    return None
                    
                # Create a figure with custom layout
                fig = go.Figure()
                
                # Define attribute colors matching the example image
                colors = {
                    'Defesa': '#D3D3D3',  # Light Gray
                    'Transição defensiva': '#4682B4',  # Blue
                    'Transição ofensiva': '#FFD700',  # Yellow/Gold
                    'Ataque': '#006400',  # Dark Green
                    'Criação de chances': '#FF4500'  # Red/Orange
                }
                
                # Attributes in the desired order (based on the example image legend)
                attributes = ['Ataque', 'Defesa', 'Transição ofensiva', 'Transição defensiva', 'Criação de chances']
                
                # Get clubs in descending order of total similarity
                clubs = similarity_df.index.tolist()
                
                # Calculate positions for stacked bars
                positions = {attr: [] for attr in attributes}
                cumulative = np.zeros(len(clubs))
                
                for attr in attributes:
                    positions[attr] = cumulative.copy()
                    cumulative += similarity_df[attr].values
                
                # Add each attribute as a stacked bar
                for i, attr in enumerate(attributes):
                    fig.add_trace(go.Bar(
                        y=clubs,
                        x=similarity_df[attr],
                        name=attr,
                        orientation='h',
                        marker=dict(color=colors[attr]),
                        base=positions[attr],
                        customdata=similarity_df[attr],  # Store the actual attribute value
                        hovertemplate=f"{attr}: %{{customdata:.1f}}/20<extra></extra>"  # Use customdata instead of x
                    ))

                # Customize layout
                fig.update_layout(
                    # Center the title
                    title=dict(
                        text=f"Similaridade de Estilo de Jogo entre o {clube}<br> e os demais clubes nas últimas 5 partidas disputadas",
                        x=0.5,
                        xanchor='center',
                        font=dict(size=18)
                    ),
                    xaxis=dict(
                        title='',
                        range=[0, 100],
                        tickvals=[0, 20, 40, 60, 80, 100],
                        tickfont=dict(size=14, 
                                        color='black'),
                        showgrid=True,
                        gridcolor='lightgray'
                    ),
                    yaxis=dict(
                        title='',
                        autorange="reversed",  # Ensure highest similarity at top
                        tickfont=dict(
                            size=14,
                            color='black'
                        )
                    ),
                    barmode='stack',
                    # Adjust legend position and properties
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,  # Lower position to make room for x-axis labels
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12),
                        bgcolor='rgba(255,255,255,0.8)'
                    ),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='black'),
                    height=650,  # Increased height to accommodate the legend
                    width=900,
                    hovermode="y unified",
                    margin=dict(l=150, r=50, t=80, b=100)  # Increased bottom margin for x-axis labels
                )
                
                # Ensure the y-axis labels are black and larger
                fig.update_yaxes(
                    tickfont=dict(
                        size=14,
                        color='black'
                    )
                )
                
                return fig

            def display_similarity_analysis(dfc_metrics):
                """
                Display the club similarity analysis section in a Streamlit app
                with the provided dfc_metrics DataFrame
                """
                st.markdown(
                    """
                    <h3 style='text-align: center;'>Índice de Similaridade de Estilo de Jogo</h3>
                    """,
                    unsafe_allow_html=True
                )

                # Custom CSS for better formatting
                st.markdown("""
                <style>
                    .main {
                        padding: 2rem;
                    }
                    .stAlert {
                        background-color: #f8f9fa;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        border-left: 5px solid #ff4b4b;
                    }
                    .info-box {
                        background-color: #e6f3ff;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        border-left: 5px solid #4B8BF5;
                        margin-bottom: 1rem;
                    }
                    h1, h2, h3 {
                        color: #1E3A8A;
                    }
                    .katex {
                        font-size: 1.1em;
                    }
                </style>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class="info-box">
                <p><h4>Índice de Similaridade de Estilo de Jogo:</h4></p>
                <p>Quantifica as semelhanças táticas entre clubes de futebol nas diferentes fases do jogo, como defesa, 
                transições defensivas, transições ofensivas, ataque e criação de chances. Cada aspecto recebe uma nota de 0 a 20, 
                somando um total máximo de 100 pontos. Quanto maior a pontuação, mais parecido é o estilo de jogo entre os times comparados.
                Considera os últimos jogos disputados, em casa ou fora.
                </div>
                """, unsafe_allow_html=True)
                
                # Club selection via dropdown
                
                # Add a button to trigger the analysis
                if st.button("Calcule o Índice!", type='primary', key=103):
                    # Run analysis
                    with st.spinner("Calculating similarity indices..."):
                        similarity_df = calculate_club_similarity(dfc_metrics, clube)
                    
                    if similarity_df is not None:
                        # Create and display the plot
                        fig = plot_similarity_index(similarity_df, clube)
                        if fig is not None:
                            st.plotly_chart(fig, use_container_width=True)

            st.write("---")
            display_similarity_analysis(dfc_metrics)

        ################################################################################################################################# 
        #################################################################################################################################
        ################################################################################################################################# 
        #################################################################################################################################

# Rodapé estilizado
st.markdown("---", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.9em;">
        Desempenho dos clubes da Série A 2025 | Análise de Adversário<br>
        2025 - @JAmerico1898
    </div>
    """,
    unsafe_allow_html=True
)
