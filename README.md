# Run Dashboard Air Quality Dataset
## Set Up Environment
python -m venv venv

venv\Scripts\activate

pip install os numpy pandas geopandas matplotlib seaborn statistics streamlit babel shapely openpyxl

pip freeze > requirements.txt
## Run streamlit app
streamlit run dashboard-proyek-cad2.py
