import pandas as pd
import streamlit as st
import warnings
import altair as alt

try:
    # Load the dataset into a DataFrame
    data = pd.read_csv("vehicles_us.csv")


    # Remove Warnings
    warnings.filterwarnings('ignore')

    # Replace NaN values in the 'price' column with the median of the column
    median_price = data['price'].median()
    data['price'].fillna(median_price, inplace=True)

    # Replace NaN values in the 'model_year' column with the median of the column
    median_model_year = data['model_year'].median()
    data['model_year'].fillna(median_model_year, inplace=True)

    # Replace missing values in 'cylinders' with the median
    median_cylinders = data['cylinders'].median()
    data['cylinders'].fillna(median_cylinders, inplace=True)

    # Replace missing values in 'odometer' with the median
    median_odometer = data['odometer'].median()
    data['odometer'].fillna(median_odometer, inplace=True)

    # Replace missing values in 'is_4wd' with the mode
    mode_4wd = data['is_4wd'].mode()[0]
    data['is_4wd'].fillna(mode_4wd, inplace=True)

    # Replace missing values in 'paint_color' with the mode
    mode_paint_color = data['paint_color'].mode()[0]
    data['paint_color'].fillna(mode_paint_color, inplace=True)

    # List of car manufacturers
    Manufacturers = [
        'Acura', 'BMW', 'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge',
        'Ford', 'GMC', 'Honda', 'Hyundai', 'Jeep', 'Kia', 'Mercedes-Benz',
        'Nissan', 'Ram', 'Subaru', 'Toyota', 'Volkswagen'
    ]

    # Function to extract manufacturer name from model
    def extract_manufacturer(model):
        for manufacturer in Manufacturers:
            if manufacturer.lower() in model.lower():
                return manufacturer
        return None

    # Create a new column "Manufacturer" and extract manufacturer names
    data['Manufacturer'] = data['model'].apply(extract_manufacturer)

    # Remove manufacturer names from "model" column
    data['model'] = data['model'].apply(lambda x: ' '.join(word for word in x.split() if word.lower() not in Manufacturers))

    # Group by Manufacturer and Vehicle Type, and count the number of vehicles for each combination
    Manufacturers_type_counts = data.groupby(['Manufacturer', 'type']).size().unstack(fill_value=0)

    # List of words to remove from the "model" column
    words_to_remove = ['bmw', 'honda', 'kia', 'gmc', 'jeep', 'chevrolet', 'toyota', 'subaru',
                       'nissan', 'ford', 'hyundai', 'cadillac', 'buick', 'ram', 'dodge',
                       'acura', 'chrysler', 'volkswagen', 'mercedes-benz']

    # Remove specified words from the "model" column
    data['model'] = data['model'].apply(lambda x: ' '.join(word for word in x.split() if word.lower() not in words_to_remove))

    # Identify unique manufacturers present in the data
    unique_models = data['model'].str.lower().unique()
    unique_manufacturers = set()
    for model in unique_models:
        for manufacturer in Manufacturers:
            if manufacturer.lower() in model:
                unique_manufacturers.add(manufacturer)

    # Update manufacturer list
    Manufacturers += list(unique_manufacturers)

    # Remove duplicates and sort the list
    Manufacturers = sorted(list(set(Manufacturers)))

    # Group by Manufacturer and Vehicle Type, and count the number of vehicles for each combination
    manufacturers_type_counts = data.groupby(['Manufacturer', 'type']).size().unstack(fill_value=0)

    # Streamlit Header
    st.title("Exploratory Data Analysis")

    # Checkbox to include manufacturers with less than 1000 ads
    include_less_than_1000 = st.checkbox("Include manufacturers with less than 1000 ads")

    # Filter data based on checkbox selection
    if not include_less_than_1000:
        # Count number of ads per manufacturer
        manufacturer_counts = data['Manufacturer'].value_counts()
        # Filter out manufacturers with less than 1000 ads
        included_manufacturers = manufacturer_counts[manufacturer_counts >= 1000].index
        data_filtered = data[data['Manufacturer'].isin(included_manufacturers)]
    else:
        data_filtered = data

    # Display the filtered data table
    st.subheader("Data Viewer")
    st.dataframe(data_filtered)

    # Select a manufacturer
    selected_manufacturer = st.selectbox("Select a manufacturer", Manufacturers)

    # Filter data based on selected manufacturer
    manufacturer_data = manufacturers_type_counts.loc[selected_manufacturer]

    # Reset index for Altair plot
    manufacturer_data = manufacturer_data.reset_index()

    # Altair bar chart
    chart = alt.Chart(manufacturer_data).mark_bar().encode(
        x='type',
        y=alt.Y(selected_manufacturer + ':Q', title='Count'),  # Use selected manufacturer as field name
        tooltip=['type', selected_manufacturer]  # Include manufacturer name in tooltip
    ).properties(
        title=f"Vehicle Types by Manufacturer: {selected_manufacturer}",
        width=600,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

    # Streamlit Header
    st.title("Histogram of Condition vs Model Year")

    # Create a chart using Altair
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('model_year:O', title='Model Year'),
        y=alt.Y('count()', title='Frequency'),
        color='condition:N',
        tooltip=['model_year', 'condition', 'count()']
    ).properties(
        width=600,
        height=400,
        title="Histogram of Condition vs Model Year"
    )

    # Show the chart
    st.altair_chart(chart, use_container_width=True)


    # Streamlit Header
    st.title("Price Distribution Comparison Between Manufacturers")

    # Create select boxes for choosing manufacturers
    manufacturer1 = st.selectbox("Select Manufacturer 1", sorted(data['Manufacturer'].unique()))
    manufacturer2 = st.selectbox("Select Manufacturer 2", sorted(data['Manufacturer'].unique()))

    # Filter the data for the selected manufacturers
    filtered_data = data[(data['Manufacturer'] == manufacturer1) | (data['Manufacturer'] == manufacturer2)]

    # Group the filtered data by Manufacturer and calculate the mean price
    grouped_data = filtered_data.groupby('Manufacturer')['price'].mean().reset_index()

    # Create a checkbox for normalization
    normalize = st.checkbox("Normalize Histogram")

    if normalize:
        # Calculate the total price
        total_price = grouped_data['price'].sum()

        # Calculate the percentage of the total price for each manufacturer
        grouped_data['percentage'] = grouped_data['price'] / total_price * 100
        y_title = 'Percentage'
    else:
        y_title = 'Price'

    # Create a bar chart using Altair
    chart = alt.Chart(grouped_data).mark_bar().encode(
        y='Manufacturer:N',
        x=alt.X('percentage:Q' if normalize else 'price:Q', title=y_title),
        color=alt.Color('Manufacturer:N', scale=alt.Scale(scheme='category10'), legend=None),
        tooltip=['Manufacturer', 'percentage' if normalize else 'price']
    ).properties(
        width=600,
        height=400,
        title=f"Price Distribution Comparison Between {manufacturer1} and {manufacturer2}"
    )

    # Show the chart
    st.altair_chart(chart, use_container_width=True)

except FileNotFoundError:
    st.error("File not found. Please make sure the file path is correct.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")