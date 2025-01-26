# Google Maps Places Search App

A Streamlit application that searches for businesses using the Google Maps Places API. The app allows users to search for businesses based on keywords and location, displaying results on an interactive map and in a detailed list format.

## Features

- Search businesses by keyword and location
- Interactive map display using Plotly
- Detailed business information including:
  - Business name
  - Address
  - Phone number
  - Operating hours
- Data export options in CSV and JSON formats
- Local caching of search results to minimize API calls
- Configurable search radius

## Prerequisites

- Python 3.7+
- Pipenv
- Google Maps API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

3. Create a `.env` file in the project root directory and add your Google Maps API key:
```
API_MAPS=your_google_maps_api_key_here
```

## Required Dependencies

- streamlit
- plotly
- googlemaps
- pandas
- python-dotenv

## Usage

1. Activate the virtual environment:
```bash
pipenv shell
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Access the application in your web browser at `http://localhost:8501`

## How to Use

1. Enter a search keyword (e.g., "gas stations")
2. Specify a location (e.g., "Campo Grande, MS")
3. Adjust the search radius using the slider (1000m - 20000m)
4. Click "Buscar" (Search) to initiate the search
5. View results on the interactive map and in the detailed list
6. Export results in CSV or JSON format if needed

## Data Caching

The application implements a local caching system to store search results and business details:
- Search results are saved as JSON files in the format `empresas_[keyword]_[location].json`
- Business details are saved as JSON files in the format `detalhes_empresas_[keyword]_[location].json`


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The application is configured to use OpenStreetMap as the base map layer
- API calls are optimized to prevent excessive usage through local caching
- The interface is currently in Portuguese, but can be easily modified for other languages
