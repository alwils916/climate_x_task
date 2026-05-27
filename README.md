## Setup
This project uses a venv with the required packages specified in `requirements.txt` and Python 3.12.1.

1. Create and activate venv
```
python -m venv cx_venv
source cx_venv/bin/activate
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Clean and prep provided xlsx for input to API as csv
```
cd scripts
python create_input_csv.py
```
4. Query API for climate data
```
python collect_climate_data.py
```