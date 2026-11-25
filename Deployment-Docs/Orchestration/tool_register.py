TOOLS = {
    "churn_risk": {
        "version": "v2",
        "endpoint": "/api/v2/churn/predict",
        "enabled": True,
    },
    "demand_forecast": {
        "version": "v1",
        "endpoint": "/api/v1/forecast/predict",
        "enabled": True,
    },

    "business_recommendation": {
        "version": "v1",
        "endpoint": "/api/v1/recommendation/predict",
        "enabled": True,
    },
}

def get_tool(tool_name: str):
    return TOOLS.get(tool_name)