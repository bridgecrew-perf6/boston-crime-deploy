import streamlit as st
import numpy as np 
import pandas as pd 
import plotly.graph_objects as go
import plotly.express as px
import datashader as ds
import datashader.transfer_functions as tf
from colorcet import fire

px.defaults.color_discrete_sequence = px.colors.qualitative.Antique

@st.cache(persist=True)
def read_dataset():
    data = pd.read_csv('https://github.com/korentomas/boston-crime-data/raw/main/bostoncrime.zip', compression='zip', low_memory=False, encoding='latin')
    data.loc[data.OFFENSE_CODE_GROUP.isnull(),'OFFENSE_CODE_GROUP'] = 'Other'
    return data

@st.cache(persist=True)
def density_map(data):
    dataf = data.query('Lat < 44').query('Lat > 36').query('Long < -69').query('Long > -74')
    cvs = ds.Canvas(plot_width=350, plot_height=350)
    agg = cvs.points(dataf, x='Long', y='Lat')

    # agg is an xarray object, see http://xarray.pydata.org/en/stable/ for more details
    coords_lat, coords_lon = agg.coords['Lat'].values, agg.coords['Long'].values
    # Corners of the image, which need to be passed to mapbox
    coordinates = [[coords_lon[0], coords_lat[0]],
                [coords_lon[-1], coords_lat[0]],
                [coords_lon[-1], coords_lat[-1]],
                [coords_lon[0], coords_lat[-1]]]

    img = tf.shade(agg, cmap=fire)[::-1].to_pil()

    # Trick to create rapidly a figure with mapbox axes
    fig = px.scatter_mapbox(dataf[:1], lat='Lat', lon='Long', zoom=10.5, opacity=0, height=400)
    # Add the datashader image as a mapbox layer image
    fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0},title_y=1,
                    mapbox_layers = [
                    {
                        "sourcetype": "image",
                        "source": img,
                        "coordinates": coordinates
                    }]
    )
    return fig

# Viz methods
# TreeMap
@st.cache(persist=True)
def treemap(categories,title,path,values):
    fig = px.treemap(categories, path=path, values=values, height=700,
                 title=title, color_discrete_sequence = px.colors.sequential.RdBu)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, title_y=1)
    fig.data[0].textinfo = 'label+text+value'
    return fig

# Histogram
@st.cache(persist=True)
def histogram(data,path,color,title,xaxis,yaxis):
    fig = px.histogram(data, x=path,color=color)
    fig.update_layout(
        title_text=title,
        xaxis_title_text=xaxis, 
        yaxis_title_text=yaxis, 
        title_y=1,
        bargap=0.2, 
        bargroupgap=0.1,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig
    

# Bar
@st.cache(persist=True)
def bar(categories,x,y,color,title,xlab,ylab):
    fig = px.bar(categories, x=x, y=y,
             color=color,
             height=400)
    fig.update_layout(
    title_text=title, 
    xaxis_title_text=xlab, 
    yaxis_title_text=ylab,
    title_y=1,
    bargap=0.2, 
    bargroupgap=0.1,
    margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig

def year_crimes_analysis(data, years, display_all=False, display_major=False, display_major_month=False, display_major_dayweek=False, display_crime_month=False, display_crime_eachday=False, display_crime_hour=False):
    if display_all==True or display_major==True:
        number_crimes_year = data['OFFENSE_CODE_GROUP'].value_counts()
        categories_year = pd.DataFrame(data=number_crimes_year.index, columns=["OFFENSE_CODE_GROUP"])
        categories_year['values'] = number_crimes_year.values

        fig = treemap(categories_year,'Major Crimes in Boston in ' + ', '.join(str(x) for x in years),['OFFENSE_CODE_GROUP'],categories_year['values'])
        st.plotly_chart(fig, use_container_width=True)

        histogram(data,"OFFENSE_CODE_GROUP","OFFENSE_CODE_GROUP",'Major Crimes in Boston in ' + ', '.join(str(x) for x in years),'Crime','Count')

        fig = px.bar(categories_year, x=categories_year['OFFENSE_CODE_GROUP'][0:10], y=categories_year['values'][0:10],
                    color=categories_year['OFFENSE_CODE_GROUP'][0:10], height=400)

        fig.update_layout(
            title_text='Top 10 Major Crimes in Boston in ' + ', '.join(str(x) for x in years), # title of plot
            title_y=1,
            xaxis_title_text='Crime', # xaxis label
            yaxis_title_text='Count', # yaxis label
            bargap=0.2, 
            bargroupgap=0.1,
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        st.plotly_chart(fig, use_container_width=True)

    if display_all==True or display_major_month==True:
        Number_crimes_month_year = data['MONTH'].value_counts()
        months_year = pd.DataFrame(data=Number_crimes_month_year.index, columns=["MONTH"])
        months_year['values'] = Number_crimes_month_year.values

        fig = go.Figure(go.Bar(
                y=months_year['values'],
                x=months_year['MONTH'],
            marker=dict(
                color='green',

            ),
                orientation='v'))

        fig.update_layout(
            title_text='Major Crimes in Boston per month in ' + ', '.join(str(x) for x in years), # title of plot
            title_y=1,
            xaxis_title_text='Month', # xaxis label
            yaxis_title_text='Count ', # yaxis label
            bargap=0.2, 
            bargroupgap=0.1,
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        st.plotly_chart(fig, use_container_width=True)

    if display_all==True or display_major_dayweek==True:
        Number_crimes_days_year = data['DAY_OF_WEEK'].value_counts()
        days_year= pd.DataFrame(data=Number_crimes_days_year.index, columns=["DAY_OF_WEEK"])
        days_year['values'] = Number_crimes_days_year.values

        histogram(data,"DAY_OF_WEEK","DAY_OF_WEEK",'Crime count on each day in ' + ', '.join(str(x) for x in years),'Day','Crimes Count')


        fig = go.Figure(data=[go.Pie(labels=days_year['DAY_OF_WEEK'], values=days_year['values'])])
        fig.update_layout(
            title_text='Crime count on each day in ' + ', '.join(str(x) for x in years),
            title_y=1, # title of plot
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        st.plotly_chart(fig, use_container_width=True)

    if display_all==True or display_crime_month==True:
        fig = histogram(data,"OFFENSE_CODE_GROUP","MONTH",'Crime count per Category on each Month in ' + ', '.join(str(x) for x in years),'Category','Crimes Count on each Month')
        st.plotly_chart(fig, use_container_width=True)

    if display_all==True or display_crime_eachday==True:
        fig = histogram(data,"MONTH","DAY_OF_WEEK",'Crime count per Month on each Day in ' + ', '.join(str(x) for x in years),'Month','Crimes Count on each Day')
        st.plotly_chart(fig, use_container_width=True)

    if display_all==True or display_crime_hour==True:
        fig = histogram(data,"DAY_OF_WEEK","HOUR",'Crime count per Day on each Hour in ' + ', '.join(str(x) for x in years),'Day','Crimes Count on each Hour')
        st.plotly_chart(fig, use_container_width=True)



data = read_dataset()

container = st.container()

container.title('Crimes in Boston Analysis 🚓')
container.markdown('**developed by: :milky_way: [Tomás Pablo Korenblit](https://www.linkedin.com/in/tomas-pablo-korenblit/)**', unsafe_allow_html=True)
container.markdown("Crime incident reports are provided by Boston Police Department (BPD) to document the initial details surrounding an incident to which BPD officers respond. <br> [Google CoLab](https://colab.research.google.com/drive/1fU-8ZvgQyIuoQcn7A-MI7nyftRz1SoX0?usp=sharing) <br> Dataset source: [Analyze Boston](https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system)", unsafe_allow_html =True)

container.plotly_chart(density_map(data), use_container_width=True)

# Arranca la parte ejecutable
def run():
    with st.form(key='Nuevo gasto'):
        years = st.multiselect('Choose year for which to analyze the crime data', ['All', 2015, 2016, 2017, 2018, 2019, 2020, 2021],[2020, 2021])
        graphs = st.multiselect('Choose visualizations for the crime data', ['All', 'Major Crimes', 'Major Crimes per Month', 'Crime count per day', 'Crime count per Category on each Month', 'Crime count per Month on each Day', 'Crime count per Day on each Hour'], ['Major Crimes'])
        
        submit_button_type = st.form_submit_button(label='Submit')

        if submit_button_type:            
            if 'All' in years:
                years = [2015, 2016, 2017, 2018, 2019, 2020, 2021]

            year_mask = np.in1d(data['YEAR'], years)
            data_year = data.loc[year_mask,:].reset_index(drop=True)

            display_all = 'All' in graphs
            display_major = 'Major Crimes' in graphs
            display_major_month = 'Major Crimes per Month' in graphs
            display_major_dayweek = 'Crime count per day' in graphs
            display_crime_month = 'Crime count per Category on each Month' in graphs
            display_crime_eachday = 'Crime count per Month on each Day' in graphs
            display_crime_hour = 'Crime count per Day on each Hour' in graphs
            year_crimes_analysis(data_year, years, display_all, display_major, display_major_month, display_major_dayweek, display_crime_month, display_crime_eachday, display_crime_hour)



if __name__ == '__main__':
    run()