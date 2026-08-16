import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


st.title('Telangana PDS Analytics')
# Create Navigation Plane
r=st.sidebar.radio('Navigation',['Filter Data','Pattern Analysis','Geospatial Map','Performance'])

# read Data in Streamlit Application
feature_df=pd.read_csv(r'C:\Users\Pushpalata\Documents\GUVI DataScience\telangana govt data\cluster_data.csv')
main_df=pd.read_csv(r"C:\Users\Pushpalata\Documents\GUVI DataScience\telangana govt data\main_data.csv")

if r == 'Filter Data':
    # Show Entire Data
    if 'show_content' not in st.session_state:
        st.session_state.show_content = False
    if st.button('show Data'):
        st.session_state.show_content = not st.session_state.show_content
    if st.session_state.show_content:
        st.dataframe(main_df)

    # Filter the record in three layer (Dist wise, Office wise, shop wise)
    st.write('** Dist wise filter record**')
    s=st.selectbox('distCode',main_df['distCode'].unique())
    if s in feature_df['distCode'].unique():
        filtered_df=main_df[main_df['distCode'] == s]
        st.dataframe(filtered_df)
        st.write('Total no of officeCode in dist',filtered_df['officeCode'].nunique())
        office=st.selectbox('officeCode',filtered_df['officeCode'].unique())
        if office in filtered_df['officeCode'].unique():
            refiltered_df=filtered_df[filtered_df['officeCode'] == office]
            st.dataframe(refiltered_df)
            st.write('Total no of shops under an office',refiltered_df['shopNo'].nunique())
            shopNo=st.selectbox('shopNo',refiltered_df['shopNo'].unique())
            if shopNo in filtered_df['shopNo'].unique():
                st.dataframe(refiltered_df[refiltered_df['shopNo'] == shopNo])
# All kind of Analysis with Supportes Map
if r == 'Pattern Analysis':
    r1=st.sidebar.radio(' ',['distribution of commodities','Dist wise Distribution','relationship b/w entitlement and execution','ration card status'],)
    if r1 == 'distribution of commodities':
        commodities=['riceAfsc', 'riceFsc', 'riceAap','wheat', 'sugar', 'rgdal', 'kerosene', 'totalAmount', 'salt','otherShopTransCnt']
        x_value=st.selectbox('commodities',commodities)
        fig = px.histogram(main_df, x=x_value, title=f"Histogram of {x_value}")
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig,use_container_width=True)
    if r1 == 'Dist wise Distribution':
        commodities=['riceAfsc', 'riceFsc', 'riceAap','wheat', 'sugar', 'rgdal', 'kerosene', 'totalAmount', 'salt','otherShopTransCnt']
        x_value=st.selectbox('commodities',commodities)
        fig=px.bar(main_df,x='distName',y=x_value,title=f'Dist wise Distribution of {x_value}')
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig,use_container_width=True)
    if r1 == 'relationship b/w entitlement and execution':
        st.write(' relationship between totalRcs (Entitlement) and noOfTrans (Actual Execution)')
        fig1,ax = plt.subplots()
        ax.set_xlabel('noOfRcs')
        ax.set_ylabel('noOfTrans')
        ax.scatter(main_df['noOfRcs'],main_df['noOfTrans'])
        st.pyplot(fig1)
    if r1 == 'ration card status':
        x_val=st.selectbox('RCS',['rcNfsaAay', 'rcNfsaPhh', 'totalRcNfsa','rcStateAay',  'rcStatePhh','rcStateAap', 'totalRcState','totalRcs'])
        y_val=st.selectbox('unit',['unitsNfsaAay','unitsNfsaPhh','totalUnitsNfsa','unitsStateAay','unitsStatePhh', 'unitsStateAap','totalUnitsState','totalUnits'])
        df=main_df.groupby(by='distName')[[y_val,x_val]].sum()
        st.subheader('Ration Card Status')
        st.bar_chart(df)
        st.write(df)
            
# Visualization of clusters of shops on Map       
if r == 'Geospatial Map':
    st.header('MAP')
    df=feature_df[['distCode','shopNo','longitude','latitude','Cluster']]
    selected_cluster = st.selectbox("Highlight Cluster", sorted(df["Cluster"].unique()))
    df["opacity"] = df["Cluster"].apply(lambda x: 1.0 if x == selected_cluster else 0.15)
    fig1 = px.scatter_mapbox(
            df,
            lat='latitude',              
            lon='longitude',             
            color='Cluster',                 
            hover_name='shopNo', 
            zoom=7, 
            opacity=df["opacity"],
            center={"lat": df['latitude'].mean(), "lon":df['longitude'].mean()},         
            mapbox_style="carto-positron",
            )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Dist wise cluster of shops on map
    selected_dist=st.selectbox("Highlight Dist", df["distCode"].unique())
    df_dist = df[df["distCode"] == selected_dist ] 
    filtered_df=df_dist[df_dist["Cluster"] == selected_cluster]              
    fig = px.scatter_mapbox(
        filtered_df,
        lat='latitude',              
        lon='longitude',                              
        hover_name='shopNo', 
        zoom=7, 
        center={"lat": df['latitude'].mean(), "lon":df['longitude'].mean()},         
        mapbox_style="carto-positron",
        )
    st.plotly_chart(fig, use_container_width=True)
   # Outlier shop information
    outlier_index=[]
    for i in ['longitude','latitude']:
        Q1=df[i].quantile(0.25)
        Q3=df[i].quantile(0.75)
        IQR=Q3 - Q1
        LW=Q1-1.5*IQR
        UW=Q3+1.5*IQR
        outlier_index.extend(df[df[i]<LW].index)
    ind=set(outlier_index)
    st.write('Outlier Shop:',len(ind))
    st.write(df.loc[list(ind)])
    
    
# Performance Analysis  
if r == 'Performance':
    main_df['util_ratio']=main_df['noOfTrans']/main_df['totalRcs']
    st.write('Dist wise distribution ratio: Transactions/Total Ration Cards')
    st.write(main_df.groupby(by='distName')['util_ratio'].sum())

    st.write('shopNo and see its performance compared to its cluster average.')
    df=feature_df[['shopNo','Cluster','noOfTrans','totalRcs']]
    df['util_ratio']=df['noOfTrans']/df['totalRcs']
    s=st.selectbox('shopNo',df['shopNo'].unique())
    st.dataframe(df[df['shopNo'] == s][['util_ratio','Cluster']])
    st.write(df.groupby(by='Cluster')['util_ratio'].mean())
