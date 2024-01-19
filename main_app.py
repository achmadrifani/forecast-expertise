import streamlit as st
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
import folium
from folium.features import DivIcon
from datetime import datetime, timedelta

wx_icon_dict = {"cerah":"https://www.bmkg.go.id/asset/img/weather_icon/ID/cerah-am.png",
                "cerah berawan":"https://www.bmkg.go.id/asset/img/weather_icon/ID/cerah%20berawan-am.png",
                2:"https://www.bmkg.go.id/asset/img/weather_icon/ID/cerah%20berawan-am.png",
                "berawan":"https://www.bmkg.go.id/asset/img/weather_icon/ID/berawan-am.png",
                "berawan tebal":"https://www.bmkg.go.id/asset/img/weather_icon/ID/berawan tebal-am.png",
                10:"https://www.bmkg.go.id/asset/img/weather_icon/ID/asap-am.png",
                45:"https://www.bmkg.go.id/asset/img/weather_icon/ID/kabut-am.png",
                "hujan ringan":"https://www.bmkg.go.id/asset/img/weather_icon/ID/hujan%20ringan-am.png",
                "hujan sedang":"https://www.bmkg.go.id/asset/img/weather_icon/ID/hujan%20sedang-am.png",
                "hujan lebat":"https://www.bmkg.go.id/asset/img/weather_icon/ID/hujan%20lebat-am.png",
                "hujan petir":"https://www.bmkg.go.id/asset/img/weather_icon/ID/hujan%20petir-am.png",
                97:"https://www.bmkg.go.id/asset/img/weather_icon/ID/hujan%20petir-am.png"}

st.set_page_config(layout="wide")

def get_leadtime(df, leadtime):
    return df.loc[df['LEADTIME'] == leadtime]

def nextf():
    if st.session_state["slider"] < leadtimes[-1]:
        st.session_state.slider += (leadtimes[1] - leadtimes[0])
    else:
        pass
    return


def prevf():
    if st.session_state["slider"] > leadtimes[0]:
        st.session_state.slider -= (leadtimes[1] - leadtimes[0])
    else:
        pass
    return


def save_data(df,lead,new_data):
    df.loc[df['LEADTIME'] == lead] = new_data
    return df


def change_data(df):
    st.session_state[f'df_lead_{lead}'] = df

with st.sidebar:
    st.markdown('''# Panduan Penggunaan''')
    st.markdown('''1. Edit forecast dengan cara mengubah data di kolom "WX".
  
2. Kondisi Cuaca yang Tersedia:  
cerah, cerah berawan, berawan, berawan tebal, hujan ringan, hujan sedang, hujan lebat, hujan petir.
  
3. Setelah selesai mengedit klik tombol 'Save Edit'.

4. Lanjutkan mengedit dengan klik tombol 'Next' untuk mengedit data selanjutnya.''')
    st.divider()
    st.markdown('''_Created by: Achmad Rifani @ 2023_''')

st.title("Forecast Data Editor")
df = pd.read_csv("data/20240116.csv")
df['DATETIME'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], format='%d/%m/%Y %I:%M %p')
datetimes = df['DATETIME'].unique()
df['LEADTIME'] = (df['DATETIME'] - df['DATETIME'].iloc[0]).dt.total_seconds() / 3600
leadtimes = df['LEADTIME'].unique().astype(int)
loc = pd.read_csv("data/berau_loc.csv")

if 'df_edit' not in st.session_state:
    st.session_state.df_edit = df

if 'lead_button' not in st.session_state:
    st.session_state.lead_button = 0

# plot point in map with using st folium from loc dataframe
col1, col2 = st.columns(2)

column_config = {"COMPANY CODE": None,
                 "BISNIS AREA": None,
                 "LONGITUDE": None,
                 "LATITUDE": None,
                 "WXICON": st.column_config.ImageColumn("ICON", width=60)}

with col1:
    # bcols = st.columns(9,gap='small')
    # count = 0
    # for lead in df['LEADTIME'].unique():
    #     with bcols[count]:
    #         if st.button(f'+{int(lead)}'):
    #             st.session_state.lead_button = lead
    #
    #         count += 1
    #         if count >= 8:
    #             count = 0

    lead = st.select_slider('Select a leadtime', options=leadtimes, key="slider",
                            format_func=lambda x: f"{datetimes[0] + timedelta(hours=int(x)):%d/%m %H:%M WITA}")
    df_lead = get_leadtime(df, lead)
    df_lead["WXICON"] = df_lead["WX"].map(wx_icon_dict)
    button_container = st.container()



    st.write(f"### Valid time: {datetimes[int(st.session_state.slider/3)]} WITA")

    if f'df_lead_{lead}' not in st.session_state:
        st.session_state[f'df_lead_{lead}'] = df_lead

    new_data = st.data_editor(st.session_state[f'df_lead_{lead}'], use_container_width=True, column_config=column_config,
                              column_order=("COMPANY CODE", "AFD", "LONGITUDE", "LATITUDE", "WX", "WXICON"))

    button_column = button_container.columns([0.2, 0.2, 0.6], gap="small")
    with button_column[0]:
        prev_button = st.button("Previous", on_click=prevf, key="sub_one")
    with button_column[1]:
        next_button = st.button("Next", on_click=nextf, key="add_one")
    with button_column[2]:
        save_button = st.button("Save Edit", key="save", type="primary")

    if save_button:
        st.session_state[f'df_lead_{lead}'] = new_data
        st.session_state.df_edit = save_data(df,lead,new_data)
        df_edit = save_data(df,lead,new_data)
        st.success("Data saved!")

with col2:
    m = folium.Map(location=[2.157303929418144, 117.46093554221964], zoom_start=10, max_zoom=12, min_zoom=10)
    markers = folium.FeatureGroup(name="Markers")
    for index, row in new_data.iterrows():
        tr_icon = folium.CustomIcon(icon_image=f"{wx_icon_dict[row['WX']]}", icon_size=(30, 30))
        div_icon = DivIcon(icon_size=(150, 36), icon_anchor=(0,0), html=f"<div style='font-size: 8pt; color: red; font-weight: bold; text-align: left;'>{row['AFD']}</div>")
        folium.Marker([row['LATITUDE'], row['LONGITUDE']], tooltip=row['BISNIS AREA'], icon=tr_icon).add_to(markers)
        folium.Marker([row['LATITUDE']-0.01, row['LONGITUDE']], icon=div_icon).add_to(markers)
    data = st_folium(m, use_container_width=True, feature_group_to_add=markers)

st.divider()
button2_container= st.container()
st.write("## Preview Data")
# final_data = st.dataframe(st.session_state.df_edit)
df_final = pd.DataFrame(st.session_state.df_edit)
df_final = df_final.iloc[:,:-2]
st.dataframe(df_final)

down_csv = button2_container.download_button("Download Data", data=df_final.to_csv(), mime="text/csv", type="primary")
# #download the file
# if down_csv:
#     df_final.to_csv("data/20240116.csv", index=False)
#     st.success("Data downloaded!")




