import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

##########################################################################################
# source:
#Bundesamt für Landestopografie swisstopo,
#icon-library.com/icon/cow-icon-png-16.html,
#onlinewebfonts.com/icon/317590,
#https://www.iconfinder.com/icons/3586814/animals_face_goat_icon

##########################################################################################
############ Helper Functions ############################################################

# Function to load and display a map in Streamlit using html from folium
def display_map(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        map_html = f.read()
    st.components.v1.html(map_html, height=500)

# Function to extract top 5 breeds
def extract_top_5(df):
    breed_counts = {}
    for breeds in df['top_5_breeds']:
        breed_list = breeds.split(',')
        for breed in breed_list:
            breed = breed.strip()
            if ' ' in breed:
                breed_parts = breed.rsplit(' ', 1)
                if len(breed_parts) == 2:
                    name, count = breed_parts
                    count = int(count)
                    if name != 'Andere':
                        if name in breed_counts:
                            breed_counts[name] += count
                        else:
                            breed_counts[name] = count
    breed_df = pd.DataFrame(list(breed_counts.items()), columns=['Breed', 'Count'])
    breed_df = breed_df.sort_values(by='Count', ascending=False).head(5)
    return breed_df

# Function to create custom tabs with custom css
def custom_tabs(labels):
    css = '''
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 2.5rem;
            color: black;
        }
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)
    return st.tabs(labels)

##########################################################################################
# Set the page configuration
st.set_page_config(
    page_title="Nutztierverteilung",
    page_icon="✅",
    layout="wide",
)

##########################################################################################
########## Set the background image ######################################################
# Set the background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://source.unsplash.com/ein-feld-mit-grunem-gras-und-bergen-im-hintergrund-xRGRXYo5Axg");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}
</style>
"""
st.markdown(background_image, unsafe_allow_html=True)
input_style = """
<style>
input[type="text"] {
    background-color: transparent;
    color: #a19eae;
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}
</style>
"""
st.markdown(input_style, unsafe_allow_html=True)

##########################################################################################
# sidebar navagation
def language_navigation():
    language = st.sidebar.radio('Sprache auswählen:', ['DE - Deutsch', 'FR - Français'])
    if language == 'DE - Deutsch':
        german_section()
    elif language == 'FR - Français':
        french_section()

###########################################
### german section ###################
#########################################
def german_section():
    st.sidebar.markdown('**Landwirte und Viehzüchter**\n- Entscheidungen über den Ausbau oder die Reduktion ihrer Bestände treffen.\n- Zuchtpräferenzen planen und optimieren.')
    st.sidebar.markdown('**Politische Entscheidungsträger**\n- Entwickeln Förderprogramme für weniger entwickelte Regionen. \n - Verhindern Engpässe durch gezielte Verteilung der Schlachthofstandorte. \n- Geben Hinweise auf Zuchtpräferenzen und unterstützen die Förderung der genetischen Vielfalt und Gesundheit der Viehbestände.')
    st.sidebar.markdown('**Kontakt:** ADLS22, ZHAW, Wädenswil, Schweiz')
    st.sidebar.markdown('**Datenquellen:** identitas AG')
    st.sidebar.markdown('**Stichdatum:** 30.04.2024')
    
    # Load the cleaned data
    df_cattle = pd.read_csv('cattle-cleaned-canton.csv')
    df_goats = pd.read_csv('goats-cleaned-canton.csv')
    df_sheep = pd.read_csv('sheep-cleaned-canton.csv')

    # Extract the top 5 breeds
    top_5_cattle = extract_top_5(df_cattle)
    top_5_goats = extract_top_5(df_goats)
    top_5_sheep = extract_top_5(df_sheep)

    # Title of the dashboard
    st.title('Schweizer Viehbestand')

    # prepare the data
    df_cattle['Type'] = 'Rinder'
    df_goats['Type'] = 'Ziegen'
    df_sheep['Type'] = 'Schafe'
    df_cattle = df_cattle[['canton', 'count', 'count_per_100_inhabitants', 'count_per_surface_km2', 'Type']]
    df_goats = df_goats[['canton', 'count', 'count_per_100_inhabitants', 'count_per_surface_km2','Type']]
    df_sheep = df_sheep[['canton', 'count','count_per_100_inhabitants', 'count_per_surface_km2', 'Type']]
    df_combined = pd.concat([df_cattle, df_goats, df_sheep])
    df_grouped_count = df_combined.groupby(['canton', 'Type'])['count'].sum().reset_index()
    df_grouped_100_inh = df_combined.groupby(['canton', 'Type'])['count_per_100_inhabitants'].mean().reset_index()
    df_grouped_surface = df_combined.groupby(['canton', 'Type'])['count_per_surface_km2'].mean().reset_index()
    df_grouped_count = df_grouped_count.sort_values(by='canton', ascending=True)
    df_grouped_100_inh = df_grouped_100_inh.sort_values(by='canton', ascending=True)
    df_grouped_surface = df_grouped_surface.sort_values(by='canton', ascending=True)

    # Create the plots for the distribution of animals
    col01, col02, col03 = st.columns(3)
    with col01:
        fig1 = px.bar(df_grouped_count, x='canton', y='count', color='Type', 
                        title='Viehbestand in Kantonen', 
                        labels={'count': 'Anzahl absolut', 'canton': 'Kanton'}, 
                        barmode='stack',
                        color_discrete_map={'Rinder': '#6c757d', 'Schafe': '#8ecae6', 'Ziegen': 'green'},
                        hover_data={'count': True, 'Type': True, 'canton': False})
        fig1.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig1, use_container_width=True, height=400)
    with col02:
        fig2 = px.bar(df_grouped_100_inh, x='canton', y='count_per_100_inhabitants', color='Type', 
                        title='Viehbestand pro 100 Einwohnerin in Kantonen', 
                        labels={'count_per_100_inhabitants': 'Anzahl pro 100 Einwohner', 'canton': 'Kanton'}, 
                        barmode='stack',
                        color_discrete_map={'Rinder': '#6c757d', 'Schafe': '#8ecae6', 'Ziegen': 'green'},
                        hover_data={'count_per_100_inhabitants': True, 'Type': True, 'canton': False})
        fig2.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig2, use_container_width=True, height=400)
    with col03:
        fig3 = px.bar(df_grouped_surface, x='canton', y='count_per_surface_km2', color='Type', 
                        title='Viehbestand pro km² in Kantonen', 
                        labels={'count_per_surface_km2': 'Anzahl pro km²', 'canton': 'Kanton'}, 
                        barmode='stack',
                        color_discrete_map={'Rinder': '#6c757d', 'Schafe': '#8ecae6', 'Ziegen': 'green'},
                        hover_data={'count_per_surface_km2': True, 'Type': True, 'canton': False})
        fig3.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig3, use_container_width=True, height=700)

    # selction of the animal type
    st.markdown('<span style="color:black; font-size:1.2rem;">Geografische Darstellung der Dichte von lebenden, registrierten Tieren pro Kanton: Anzahl absolut, Anzahl pro Landfläche in km² ohne Gewässer, Anzahl pro 100 Einwohner sowie die fünf beliebtesten Rassen und Namen. Bewegen Sie die «Maus» über die Karte, um die Ergebnisse anzuzeigen.</span>',
                unsafe_allow_html=True)
    style = """
    <style>
        .stSelectbox > div {font-size: 20px;}
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    animal_type = st.selectbox("Wählen Sie das Tier:", {
        "Rinder": "Cattle",
        "Ziegen": "Goats",
        "Schafe": "Sheep"
    })


    # Sort the dataframes by count, count_per_100_inhabitants, and count_per_surface_km2
    top_10_inhabitants = df_cattle.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface = df_cattle.nlargest(10, 'count_per_surface_km2')

    top_10_inhabitants_goats = df_goats.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface_goats = df_goats.nlargest(10, 'count_per_surface_km2')

    top_10_inhabitants_sheep = df_sheep.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface_sheep = df_sheep.nlargest(10, 'count_per_surface_km2')

    def categorize(count, thresholds):
        for i, threshold in enumerate(thresholds):
            if count < threshold:
                return f"{thresholds[i-1]} - {threshold}"
        return f"{thresholds[-1]}+"

    if animal_type == "Rinder":
        df = df_cattle
        thresholds = [0, 25000, 50000, 100000, 200000]
        #colors lightest to darkest for cattle
        # ['#f2f2f2', '#cccccc','#9999a1', '#66666e', '#000000']
        colors = ['#66666e', '#9999a1','#000000', '#cccccc', '#f2f2f2'] # order bug fix
    elif animal_type == "Ziegen":
        df = df_goats
        thresholds = [0, 1000, 3000, 5000, 10000, 20000]
        # lightest to darkest  for goats:
        # '#E9F3F5', '#caf0f8', '#90e0ef', '#00b4d8', '#0077b6', '#184e77']
        colors = ['#0077b6', '#00b4d8', '#184e77', '#caf0f8', '#90e0ef', '#E9F3F5'] # order bug fix
    else:
        df = df_sheep
        thresholds = [0, 5000, 15000, 30000, 50000, 70000]
        # lightest to darkest for sheep
        # ['#ccff33', '#9ef01a', '#38b000', '#007200', '#004b23', '#00331a']
        colors = ['#38b000', '#007200', '#00331a', '#9ef01a', '#004b23', '#ccff33'] # order bug fix


    df['category'] = df['count'].apply(lambda x: categorize(x, thresholds))
    df_pie = df.groupby('category').agg({'count': 'sum'}).reset_index()
    df_pie['category'] = pd.Categorical(df_pie['category'], 
                                        categories=[f"{thresholds[i]} - {thresholds[i+1]}" for i in range(len(thresholds)-1)] + [f"{thresholds[-1]}+"], 
                                        ordered=True)
    df_pie = df_pie.sort_values('category')

    fig_pie = px.pie(df_pie, 
                    names='category', 
                    values='count',
                    title=f'Anteil der {animal_type} nach Anzahl absolut pro Kanton',
                    color_discrete_sequence=colors)
    fig_pie.update_traces(textposition='inside', texttemplate='%{label}<br>%{percent:.1%}')
    fig_pie.update_layout(title={
        'text': f'Anteil der {animal_type} nach Anzahl absolut pro Kanton',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        showlegend=False, width=440, height=500)

    col1, col2 = st.columns([2, 1])

    if animal_type == "Rinder":
        with col1:
            display_map("swiss_canton_map_cattle_de.html")   
    elif animal_type == "Ziegen":
        with col1:
            display_map("swiss_canton_map_goats_de.html")       
    else:
        with col1:
            display_map("swiss_canton_map_sheep_de.html")

    with col2:
        st.plotly_chart(fig_pie)

    col11, col22, col33 = st.columns([1, 1, 1])
    with col11:
        metric = "Anzahl pro Landfläche in km²"
        if animal_type == "Rinder":
            data = top_10_surface
            bar_color = 'gray'
        elif animal_type == "Ziegen":
            data = top_10_surface_goats
            bar_color = '#219ebc'
        else:
            data = top_10_surface_sheep
            bar_color = 'green'
        fig_surface = px.bar(data, x='count_per_surface_km2', y='canton', orientation='h', title=f'Top 10 {metric} von {animal_type} per Kanton',
                labels={'count_per_surface_km2': f'{metric}', 'canton': 'Kanton'}, text='count_per_surface_km2')
        fig_surface.update_traces(marker_color=bar_color, textfont_color='white')
        fig_surface.update_layout(
            xaxis_title=f'{metric}',
            yaxis_title='Kanton',
            yaxis_categoryorder='total ascending',
            xaxis=dict(showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)', width=440, height=500
        )
        st.plotly_chart(fig_surface)
    with col22:
        metric = "Anzahl pro 100 Einwohner"
        if animal_type == "Rinder":
            data = top_10_inhabitants
            bar_color = 'gray'
        elif animal_type == "Ziegen":
            data = top_10_inhabitants_goats
            bar_color = '#219ebc'
        else:
            data = top_10_inhabitants_sheep
            bar_color = 'green'
        fig_inhabitants = px.bar(data, x='count_per_100_inhabitants', y='canton', orientation='h', title=f'Top 10 {metric} von {animal_type} per Kanton',
                labels={'count_per_100_inhabitants': f'{metric}', 'canton': 'Kanton'}, text='count_per_100_inhabitants')
        fig_inhabitants.update_traces(marker_color=bar_color, textfont_color='white')
        fig_inhabitants.update_layout(
            xaxis_title=f'{metric}',
            yaxis_title='Kanton',
            yaxis_categoryorder='total ascending',
            xaxis=dict(showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)', width=440, height=500
        )
        st.plotly_chart(fig_inhabitants)
    with col33:
        if animal_type == "Rinder":
            fig_breed = px.bar(top_5_cattle, x='Count', y='Breed', orientation='h', title='Top 5 Rassen der Rinder')
            bar_color = 'gray'
        elif animal_type == "Ziegen":
            fig_breed = px.bar(top_5_goats, x='Count', y='Breed', orientation='h', title='Top 5 Rassen der Ziegen')
            bar_color = '#219ebc'
        else:
            fig_breed = px.bar(top_5_sheep, x='Count', y='Breed', orientation='h', title='Top 5 Rassen der Schafe')
            bar_color = 'green'
        fig_breed.update_traces(marker_color=bar_color)
        fig_breed.update_layout(xaxis_title='Anzahl absolut', yaxis_title='Rasse', showlegend=False, 
                                yaxis_categoryorder='total ascending', 
                                plot_bgcolor='rgba(0,0,0,0)', width=440, height=500)
        if animal_type == "Rinder":
            image_path = "https://source.unsplash.com/eine-braun-weisse-kuh-steht-auf-einem-uppigen-grunen-feld-aAi6d0PPX-Y"
        elif animal_type == "Ziegen":
            image_path = "https://source.unsplash.com/braune-und-weisse-hirsche-die-tagsuber-auf-grauem-betonboden-stehen-kls0AxWhUOw"
        else:
            image_path = "https://source.unsplash.com/ein-schaf-steht-auf-einem-feldfeld-neben-einem-zaun-HnOxnKntU3E"
        fig_breed.add_layout_image(
            dict(
                source=image_path,
                xref="paper", yref="paper",
                x=0.6, y=0.52,
                sizex=0.5, sizey=0.5, opacity=1, layer="below", xanchor="left", yanchor="top"
            )
        )
        st.plotly_chart(fig_breed)

    sheep_df = pd.read_csv("sheep-map-commune.csv",delimiter=";", skiprows=1)
    goats_df = pd.read_csv("goats-map-commune.csv", delimiter=";", skiprows=1)
    cattle_df = pd.read_csv("cattle-map-commune.csv", delimiter=";", skiprows=1)

    sheep_df.columns = ['Gemeinde', 'Anzahl Schafe', 'Anzahl Schafe pro 100 Einwohner', 'Anzahl Schafe pro km²', '10 beliebteste Rassen', '10 beliebteste Namen']
    goats_df.columns = ['Gemeinde',  'Anzahl Ziegen', 'Anzahl Ziegen pro 100 Einwohner', 'Anzahl Ziegen pro km²', '10 beliebteste Rassen', '10 beliebteste Namen']
    cattle_df.columns = ['Gemeinde',  'Anzahl Rinder', 'Anzahl Rinder pro 100 Einwohner', 'Anzahl Rinder pro km²', '10 beliebteste Rassen', '10 beliebteste Namen']

    col111, col222 = st.columns([1, 1])

    if animal_type == "Rinder":
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Geografische Darstellung der Dichte von lebenden, registrierten Tieren pro Gemeinde.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_cattle_de.html")   
    elif animal_type == "Ziegen":
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Geografische Darstellung der Dichte von lebenden, registrierten Tieren pro Gemeinde.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_goats_de.html")       
    else:
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Geografische Darstellung der Dichte von lebenden, registrierten Tieren pro Gemeinde.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_sheep_de.html")

    with col222:
        if animal_type == "Rinder":
            df = cattle_df
        elif animal_type == "Ziegen":
            df = goats_df             
        else:
            df = sheep_df

        st.markdown('<span style="color:black; font-size:1.2rem;">Tabellarische Darstellung der Daten nach Gemeinden. Mit der Suche 🔍 können Sie die Daten nach Gemeinden filtern.</span>', unsafe_allow_html=True)
        st.dataframe(df, height=500)

    df_slaughterhouses = pd.read_csv("slaughterhouse_with_coordinates.csv")

    col1111, col2222 = st.columns([1, 1])

    with col1111:
        st.markdown('<span style="color:black; font-size:1.2rem;">Geografische Darstellung von Schlachthöfe</span>', unsafe_allow_html=True)
        if animal_type == "Rinder":            
            display_map("slaughterhouses_map_cattle_de.html")
        elif animal_type == "Ziegen":
            display_map("slaughterhouses_map_goats_de.html")
        else:
            display_map("slaughterhouses_map_sheep_de.html")

    with col2222:
        st.markdown('<span style="color:black; font-size:1.2rem;">Detaillierte Auflistung der Schlachthöfe.</span>', unsafe_allow_html=True)
        st.dataframe(df_slaughterhouses, height=500)


### end german section ####################


##########################################################################
#### French Section#######################################################
##########################################################################

def french_section():
    st.sidebar.markdown('**Agriculteurs et éleveurs**\n- Décider de l’agrandissement ou de la réduction de leurs troupeaux.\n- Planifier et optimiser les préférences d’élevage.')
    st.sidebar.markdown('**Décideurs politiques**\n- Développer des programmes de soutien pour les régions moins développées ou éviter les surcapacités dans certaines régions.\n- Donner des indications sur les préférences d’élevage et soutenir la promotion de la diversité génétique et de la santé des troupeaux.\n- Planifier stratégiquement les investissements dans les infrastructures dans les régions à forte densité de bétail.')
    st.sidebar.markdown('**Contact :** ADLS22, ZHAW, Wädenswil, Suisse')
    st.sidebar.markdown('**Sources des données :** identitas AG')
    st.sidebar.markdown('**Date de référence :** 30.04.2024')

    df_cattle = pd.read_csv('cattle-cleaned-canton.csv')
    df_goats = pd.read_csv('goats-cleaned-canton.csv')
    df_sheep = pd.read_csv('sheep-cleaned-canton.csv')

    top_5_cattle = extract_top_5(df_cattle)
    top_5_goats = extract_top_5(df_goats)
    top_5_sheep = extract_top_5(df_sheep)

    st.title('Cheptel Suisse')
    df_cattle['Type'] = 'Bovins'
    df_goats['Type'] = 'Caprins'
    df_sheep['Type'] = 'Ovins'
    df_cattle = df_cattle[['canton', 'count', 'count_per_100_inhabitants', 'count_per_surface_km2', 'Type']]
    df_goats = df_goats[['canton', 'count', 'count_per_100_inhabitants', 'count_per_surface_km2','Type']]
    df_sheep = df_sheep[['canton', 'count','count_per_100_inhabitants', 'count_per_surface_km2', 'Type']]
    df_combined = pd.concat([df_cattle, df_goats, df_sheep])
    df_grouped_count = df_combined.groupby(['canton', 'Type'])['count'].sum().reset_index()
    df_grouped_100_inh = df_combined.groupby(['canton', 'Type'])['count_per_100_inhabitants'].mean().reset_index()
    df_grouped_surface = df_combined.groupby(['canton', 'Type'])['count_per_surface_km2'].mean().reset_index()
    df_grouped_count = df_grouped_count.sort_values(by='canton', ascending=True)
    df_grouped_100_inh = df_grouped_100_inh.sort_values(by='canton', ascending=True)
    df_grouped_surface = df_grouped_surface.sort_values(by='canton', ascending=True)

    col01, col02, col03 = st.columns(3)
    with col01:
        fig1 = px.bar(df_grouped_count, x='canton', y='count', color='Type', 
                        title='Cheptel par canton', 
                        labels={'count': 'Nombre absolu', 'canton': 'Canton'}, 
                        barmode='stack',
                        color_discrete_map={'Bovins': '#6c757d', 'Ovins': '#8ecae6', 'Caprins': 'green'},
                        hover_data={'count': True, 'Type': True, 'canton': False})
        fig1.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig1, use_container_width=True, height=400)
    with col02:
        fig2 = px.bar(df_grouped_100_inh, x='canton', y='count_per_100_inhabitants', color='Type', 
                        title='Cheptel pour 100 habitants par canton', 
                        labels={'count_per_100_inhabitants': 'Nombre pour 100 habitants', 'canton': 'Canton'}, 
                        barmode='stack',
                        color_discrete_map={'Bovins': '#6c757d', 'Ovins': '#8ecae6', 'Caprins': 'green'},
                        hover_data={'count_per_100_inhabitants': True, 'Type': True, 'canton': False})
        fig2.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig2, use_container_width=True, height=400)
    with col03:
        fig3 = px.bar(df_grouped_surface, x='canton', y='count_per_surface_km2', color='Type', 
                        title='Cheptel par km² par canton', 
                        labels={'count_per_surface_km2': 'Nombre par km²', 'canton': 'Canton'}, 
                        barmode='stack',
                        color_discrete_map={'Bovins': '#6c757d', 'Ovins': '#8ecae6', 'Caprins': 'green'},
                        hover_data={'count_per_surface_km2': True, 'Type': True, 'canton': False})
        fig3.update_xaxes(tickfont=dict(size=8))
        st.plotly_chart(fig3, use_container_width=True, height=700)

    st.markdown('<span style="color:black; font-size:1.2rem;">Représentation géographique de la densité des animaux vivants enregistrés par canton : nombre absolu, nombre par surface terrestre en km² sans cours d’eau, nombre pour 100 habitants ainsi que les cinq races et noms les plus populaires. Déplacez la souris sur la carte pour afficher les résultats.</span>',
                unsafe_allow_html=True)
    style = """
    <style>
        .stSelectbox > div {font-size: 20px;}
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    animal_type = st.selectbox("Sélectionnez l'animal:", {
        "Bovins": "Cattle",
        "Caprins": "Goats",
        "Ovins": "Sheep"
    })

    top_10_inhabitants = df_cattle.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface = df_cattle.nlargest(10, 'count_per_surface_km2')

   
    top_10_inhabitants_goats = df_goats.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface_goats = df_goats.nlargest(10, 'count_per_surface_km2')

    top_10_inhabitants_sheep = df_sheep.nlargest(10, 'count_per_100_inhabitants')
    top_10_surface_sheep = df_sheep.nlargest(10, 'count_per_surface_km2')

    def categorize(count, thresholds):
        for i, threshold in enumerate(thresholds):
            if count < threshold:
                return f"{thresholds[i-1]} - {threshold}"
        return f"{thresholds[-1]}+"

    if animal_type == "Bovins":
        df = df_cattle
        thresholds = [0, 25000, 50000, 100000, 200000]
        #colors lightest to darkest = ['#f2f2f2', '#cccccc','#9999a1', '#66666e', '#000000']
        colors = ['#66666e', '#9999a1','#000000', '#cccccc', '#f2f2f2'] # order bug fix
    elif animal_type == "Caprins":
        df = df_goats
        thresholds = [0, 1000, 3000, 5000, 10000, 20000]
        # from lightest to darkest = ['#E9F3F5', '#caf0f8', '#90e0ef', '#00b4d8', '#0077b6', '#184e77']
        colors = ['#0077b6', '#00b4d8', '#184e77', '#caf0f8', '#90e0ef', '#E9F3F5'] # order bug fix
    else:
        df = df_sheep
        thresholds = [0, 5000, 15000, 30000, 50000, 70000]
        #colors = ['#ccff33', '#9ef01a', '#38b000', '#007200', '#004b23', '#00331a']$
        colors = ['#38b000', '#007200', '#00331a', '#9ef01a', '#004b23', '#ccff33'] # order bug fix

    df['category'] = df['count'].apply(lambda x: categorize(x, thresholds))
    df_pie = df.groupby('category').agg({'count': 'sum'}).reset_index()
    df_pie['category'] = pd.Categorical(df_pie['category'], 
                                        categories=[f"{thresholds[i]} - {thresholds[i+1]}" for i in range(len(thresholds)-1)] + [f"{thresholds[-1]}+"], 
                                        ordered=True)
    df_pie = df_pie.sort_values('category')

    fig_pie = px.pie(df_pie, 
                    names='category', 
                    values='count',
                    title=f'Part des {animal_type} par nombre absolu par canton',
                    color_discrete_sequence=colors)
    fig_pie.update_traces(textposition='inside', texttemplate='%{label}<br>%{percent:.1%}')
    fig_pie.update_layout(title={
        'text': f'Part des {animal_type} par nombre absolu par canton',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        showlegend=False, width=440, height=500)

    col1, col2 = st.columns([2, 1])

    if animal_type == "Bovins":
        with col1:
            display_map("swiss_canton_map_cattle_fr.html")   
    elif animal_type == "Caprins":
        with col1:
            display_map("swiss_canton_map_goats_fr.html")       
    else:
        with col1:
            display_map("swiss_canton_map_sheep_fr.html")

    with col2:
        st.plotly_chart(fig_pie)

    col11, col22, col33 = st.columns([1, 1, 1])
    with col11:
        metric = "Nombre par surface en km²"
        if animal_type == "Bovins":
            data = top_10_surface
            bar_color = 'gray'
        elif animal_type == "Caprins":
            data = top_10_surface_goats
            bar_color = '#219ebc'
        else:
            data = top_10_surface_sheep
            bar_color = 'green'
        fig_surface = px.bar(data, x='count_per_surface_km2', y='canton', orientation='h', title=f'Top 10 {metric} de {animal_type} par canton',
                labels={'count_per_surface_km2': f'{metric}', 'canton': 'Canton'}, text='count_per_surface_km2')
        fig_surface.update_traces(marker_color=bar_color, textfont_color='white')
        fig_surface.update_layout(
            xaxis_title=f'{metric}',
            yaxis_title='Canton',
            yaxis_categoryorder='total ascending',
            xaxis=dict(showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)', width=440, height=500
        )
        st.plotly_chart(fig_surface)
    with col22:
        metric = "Nombre pour 100 habitants"
        if animal_type == "Bovins":
            data = top_10_inhabitants
            bar_color = 'gray'
        elif animal_type == "Caprins":
            data = top_10_inhabitants_goats
            bar_color = '#219ebc'
        else:
            data = top_10_inhabitants_sheep
            bar_color = 'green'
        fig_inhabitants = px.bar(data, x='count_per_100_inhabitants', y='canton', orientation='h', title=f'Top 10 {metric} de {animal_type} par canton',
                labels={'count_per_100_inhabitants': f'{metric}', 'canton': 'Canton'}, text='count_per_100_inhabitants')
        fig_inhabitants.update_traces(marker_color=bar_color, textfont_color='white')
        fig_inhabitants.update_layout(
            xaxis_title=f'{metric}',
            yaxis_title='Canton',
            yaxis_categoryorder='total ascending',
            xaxis=dict(showgrid=False, showticklabels=False, showline=False),
            yaxis=dict(showgrid=False),
            plot_bgcolor='rgba(0,0,0,0)', width=440, height=500
        )
        st.plotly_chart(fig_inhabitants)
    with col33:
        if animal_type == "Bovins":
            fig_breed = px.bar(top_5_cattle, x='Count', y='Breed', orientation='h', title='Top 5 races de Bovins')
            bar_color = 'gray'
        elif animal_type == "Caprins":
            fig_breed = px.bar(top_5_goats, x='Count', y='Breed', orientation='h', title='Top 5 races de Caprins')
            bar_color = '#219ebc'
        else:
            fig_breed = px.bar(top_5_sheep, x='Count', y='Breed', orientation='h', title='Top 5 races de Ovins')
            bar_color = 'green'
        fig_breed.update_traces(marker_color=bar_color)
        fig_breed.update_layout(xaxis_title='Nombre absolu', yaxis_title='Race', showlegend=False, 
                                yaxis_categoryorder='total ascending', 
                                plot_bgcolor='rgba(0,0,0,0)', width=440, height=500)
        if animal_type == "Bovins":
            image_path = "https://source.unsplash.com/eine-braun-weisse-kuh-steht-auf-einem-uppigen-grunen-feld-aAi6d0PPX-Y"
        elif animal_type == "Caprins":
            image_path = "https://source.unsplash.com/braune-und-weisse-hirsche-die-tagsuber-auf-grauem-betonboden-stehen-kls0AxWhUOw"
        else:
            image_path = "https://source.unsplash.com/ein-schaf-steht-auf-einem-feldfeld-neben-einem-zaun-HnOxnKntU3E"
        fig_breed.add_layout_image(
            dict(
                source=image_path,
                xref="paper", yref="paper",
                x=0.6, y=0.52,
                sizex=0.5, sizey=0.5, opacity=1, layer="below", xanchor="left", yanchor="top"
            )
        )
        st.plotly_chart(fig_breed)

    sheep_df = pd.read_csv("sheep-map-commune.csv",delimiter=";", skiprows=1)
    goats_df = pd.read_csv("goats-map-commune.csv", delimiter=";", skiprows=1)
    cattle_df = pd.read_csv("cattle-map-commune.csv", delimiter=";", skiprows=1)

    sheep_df.columns = ['Commune', 'Nombre de Ovins', 'Nombre de Ovins pour 100 habitants', 'Nombre de Ovins par km²', '10 races les plus populaires', '10 noms les plus populaires']
    goats_df.columns = ['Commune',  'Nombre de Caprins', 'Nombre de Caprins pour 100 habitants', 'Nombre de Caprins par km²', '10 races les plus populaires', '10 noms les plus populaires']
    cattle_df.columns = ['Commune',  'Nombre de Bovins', 'Nombre de Bovins pour 100 habitants', 'Nombre de Bovins par km²', '10 races les plus populaires', '10 noms les plus populaires']

    col111, col222 = st.columns([1, 1])

    if animal_type == "Bovins":
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Représentation géographique de la densité des animaux vivants enregistrés par commune.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_cattle_fr.html")   
    elif animal_type == "Caprins":
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Représentation géographique de la densité des animaux vivants enregistrés par commune.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_goats_fr.html")       
    else:
        with col111:
            st.markdown('<span style="color:black; font-size:1.2rem;">Représentation géographique de la densité des animaux vivants enregistrés par commune.</span>', unsafe_allow_html=True)
            display_map("swiss_communes_map_sheep_fr.html")

    with col222:
        if animal_type == "Bovins":
            df = cattle_df
        elif animal_type == "Caprins":
            df = goats_df             
        else:
            df = sheep_df

        st.markdown('<span style="color:black; font-size:1.2rem;">Représentation tabulaire des données par commune. Utilisez la recherche 🔍 pour filtrer les données par commune.</span>', unsafe_allow_html=True)
        st.dataframe(df, height=500)

    df_slaughterhouses = pd.read_csv("slaughterhouse_with_coordinates.csv")

    col1111, col2222 = st.columns([1, 1])

    with col1111:
        st.markdown('<span style="color:black; font-size:1.2rem;">Représentation géographique des abattoirs</span>', unsafe_allow_html=True)
        if animal_type == "Bovins":            
            display_map("slaughterhouses_map_cattle_fr.html")
        elif animal_type == "Caprins":
            display_map("slaughterhouses_map_goats_fr.html")
        else:
            display_map("slaughterhouses_map_sheep_fr.html")

    with col2222:
        st.markdown('<span style="color:black; font-size:1.2rem;">Liste détaillée des abattoirs</span>', unsafe_allow_html=True)
        st.dataframe(df_slaughterhouses, height=500)

def main():
    language_navigation()

if __name__ == "__main__":
    main()

# End of the Streamlit app

