# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """
    Choose the fruits you want in your custom Smoothie!
  """
)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

name_on_order = st.text_input("Name on Smoothie")
st.write(f"The name on your order will be: {name_on_order}")

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
submit_button = st.button("Submit Order")

if ingredient_list and submit_button:
    ingredients_string = " ".join(ingredient_list)

    for fruit in ingredient_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit, ["SEARCH_ON"]]
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.subheader(f"{fruit} Nutrition Information")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    my_insert_stmt = f"""
                        INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS, NAME_ON_ORDER)
                        VALUES('{ingredients_string}', '{name_on_order}')
                    """

    session.sql(my_insert_stmt).collect()
    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
