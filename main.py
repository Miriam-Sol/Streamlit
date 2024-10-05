import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from utils import *

# Configuración de la página
st.set_page_config(page_title="Reviews de Hoteles Milan", layout="wide")

# Título y descripción
st.title("Milan hotels")
st.markdown(
    """
    ### An app that shows opinions on hotels in Milan
    """
)

# Cargar datos
path = 'data/hotel_reviews.csv'
df = load_data(path, 100000)

# Calculate average score for each hotel
hotel_stats = df.groupby('hotel_name')\
    .agg(average_score=('reviewer_score', 'mean'), number_reviews=('reviewer_score', 'count'))


# Add a title to the sidebar for filters
st.sidebar.header("Filters")

# User input for score filter and minimum num of reviews
min_reviews = st.sidebar.slider('Select minimum number of reviews', 0, 1000, 0)
score_threshold = st.sidebar.slider('Select minimum average score', 0.0, 10.0, 3.0)

filtered_hotels = hotel_stats[(hotel_stats['average_score'] > score_threshold) &
    (hotel_stats['number_reviews'] >= min_reviews)]\
    .sort_values('average_score', ascending=False)\
    .reset_index()

display_df = filtered_hotels.rename(columns={
    'hotel_name': 'Hotel Name',
    'average_score': 'Average Score',
    'number_reviews': 'Number of Reviews'
})

# Display results
st.write('Hotels with average score higher than', score_threshold)
st.dataframe(display_df, width=700, height=200)

### Add the Map Visualization ###
# If filtered hotels exist, show them on the map
if not filtered_hotels.empty:
    # Add latitude and longitude from the original df (if exists)
    filtered_hotels_with_location = pd.merge(filtered_hotels, df[['hotel_name', 'lat', 'lng', 'hotel_address']].drop_duplicates(subset=['hotel_name']), on='hotel_name', how='inner')

    st.write('Map of Hotels')

    # Create a PyDeck layer to display points
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_hotels_with_location,
        get_position='[lng, lat]',  # Longitude, Latitude from dataset
        get_color='[200, 30, 0, 160]',  # Red color for the points
        get_radius=100,  # Size of points on the map
        pickable=True,  # Allow user to click on points
    )

    # Set the initial view of the map to Milan
    milan_latitude = 45.4642  # Latitude for Milan
    milan_longitude = 9.1900  # Longitude for Milan

    view_state = pdk.ViewState(
        latitude=milan_latitude,
        longitude=milan_longitude,
        zoom=12,  # Adjust zoom level to focus on Milan
        pitch=45  # Tilt the map for better perspective
    )

    tooltip = {
        "text" : "Hotel Name: {hotel_name}"
                "\nAddress: {hotel_address}"
    }
    # Add the map to the Streamlit app
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',  # Use Mapbox styling
        initial_view_state=view_state,
        layers=[layer],
        tooltip= tooltip,
    ))

    st.write('---')


selected_hotel = st.selectbox('Select a hotel to see reviews:', filtered_hotels['hotel_name'])

##### Reviews for chosen hotel
# Show the average score of the selected hotel
if selected_hotel:
    # Display reviews for the selected hotel
    hotel_reviews = df[df['hotel_name'] == selected_hotel]

    if not hotel_reviews.empty:
        #### Allow user to filter reviews by score
        min_score, max_score = st.slider('Select review score range:', 0, 10, (0, 10))

        #### Nationality Filter ####
        # Get unique nationalities from the dataset
        nationalities = hotel_reviews['reviewer_nationality'].unique()

        selected_nationalities = st.multiselect(
            'Filter by reviewer nationality:',
            options=nationalities,
            default=[],  # Default: nothing selected
            help="Select one or more nationalities"  # Tooltip to guide users
        )

        if len(selected_nationalities) == 0:
            selected_nationalities = nationalities

        # Date range selection
        date_range = st.date_input("Select review date range:",
                                           [pd.to_datetime('2017-06-01'), pd.to_datetime('2017-12-31')])
        start_date, end_date = date_range

        # Filter reviews based on the selected score range
        hotel_reviews['Date'] = pd.to_datetime(hotel_reviews['review_date']).dt.date
        hotel_reviews = hotel_reviews[
            (hotel_reviews['reviewer_score'] >= min_score) &
            (hotel_reviews['reviewer_score'] <= max_score) &
            (hotel_reviews['reviewer_nationality'].isin(selected_nationalities)) &
            (hotel_reviews['Date'] >= start_date) & (hotel_reviews['Date'] <= end_date)
        ].sort_values('Date', ascending=False)


        st.write('Reviews:')
        for index, row in hotel_reviews.iterrows():

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Date:** {row['review_date']}")

            with col2:
                st.write(f"**Reviewer Score:** {row['reviewer_score']}")

            with col3:
                st.write(f"**Reviewer Nationality:** {row['reviewer_nationality']}")

            # st.write(f"**Date:** {row['review_date']}")
            # st.write(f"**Reviewer Score:** {row['reviewer_score']}")
            st.write(f"**Positive Review:** {row['positive_review']}")
            st.write(f"**Negative Review:** {row['negative_review']}")
            st.write('---')  # Separator for readability
    else:
        st.write('No reviews available for this hotel.')