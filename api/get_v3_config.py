import json
from streamlit_javascript import st_javascript
from common_handling import response

def execute():
    features = st_javascript("""await localStorage.getItem("features");""")
    tables = st_javascript("""await localStorage.getItem("tables");""")

    data = {
        "features": json.loads(features) if features != 0 else [],
        "tables": json.loads(tables) if tables != 0 else []
    }

    return response.execute("SUCCESS", 
                            "Config key fetched successfully",
                            data)