import streamlit as st
from BASIRIS import BASDatabase
import os

### Streamlit page
bas_database = BASDatabase()
st.title("BASLABS Climate Action")

company_name = st.text_input("Company Name")
company_description = st.text_area("Company Description")

sectors = [
    "Apparel",
    "Biotech",
    "health care & pharma",
    "Chemicals",
    "Fodd, beverage & agriculture",
    "Fossil Fuels",
    "Hospitality",
    "Infrastructure",
    "Manufacturing",
    "Power Generation",
    "Retail",
    "Services",
    "Transportation services",
    "NA",
]
company_sector = st.selectbox("Company Sector", sectors)


# chat_input = st.text_input("Ask me anything about climate action...")
@st.cache_data()
def get_results(query):
    return bas_database.search_UN(query)


if st.button("Submit"):
    st.write(
        f"""
    Company Name: {company_name}
    Company Description: {company_description}
    Company Sector: {company_sector}
    """
    )

    results = get_results(company_description)
    results
