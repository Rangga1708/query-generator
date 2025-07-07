import json
from streamlit_javascript import st_javascript
from common_handling import response

def execute():
    features = {"name": "tes", "id": "tes"}
    st_javascript(f"""await localStorage.setItem("features", JSON.stringify({features}));""")

    features = st_javascript(f"""await localStorage.getItem("features");""")
    tables = st_javascript(f"""await localStorage.getItem("tables");""")

    if features != 0:
        print(type(features))
        print(features)
        print(json.loads(features))

    data = {
        "features": features if features != 0 else [],
        "tables": tables if tables != 0 else []
    }

    return response.execute("SUCCESS", 
                            "Config key fetched successfully",
                            data)