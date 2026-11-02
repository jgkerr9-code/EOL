import datetime
import requests
import pandas as pd

# List of products to pull from the live endoflife.date API
PRODUCT_MAPPING = {
    "Ubuntu": "ubuntu",
    "RHEL": "rhel",
    "Alpine Linux": "alpine",
    "Linux Kernel": "linux",
    "macOS": "macos"
}

def fetch_live_lifecycle_data():
    all_cycles = []
    today = datetime.date.today()
    one_year_hence = today + datetime.timedelta(days=365)
    headers = {"Accept": "application/json"}

    for dashboard_name, api_slug in PRODUCT_MAPPING.items():
        url = f"https://endoflife.date{api_slug}.json"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                continue
            cycles_data = response.json()

            for item in cycles_data:
                cycle_name = item.get("cycle")
                release_date_str = item.get("releaseDate")
                eol_date_str = item.get("eol")

                eol_date = None
                if isinstance(eol_date_str, str):
                    try:
                        eol_date = datetime.datetime.strptime(eol_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        pass

                status = "Supported (no EOL date)"
                if eol_date:
                    if eol_date <= today:
                        status = "Unsupported (EOL passed)"
                    elif today < eol_date <= one_year_hence:
                        status = "Ending within 12 months"
                    else:
                        status = "Supported"
                elif eol_date_str is False:
                    status = "Unsupported (no EOL date)"

                all_cycles.append({
                    "Product": dashboard_name,
                    "Cycle": cycle_name,
                    "Released": release_date_str,
                    "End of life": eol_date_str if eol_date else "-",
                    "Status": status
                })
        except Exception as e:
            print(f"Error updating {dashboard_name}: {e}")
    return pd.DataFrame(all_cycles)

# Pull data and save it directly over your old Excel file layout
df_live = fetch_live_lifecycle_data()
df_live.to_excel("all_versions.xlsx", index=False)
print("Spreadsheet successfully overwritten with real-time data!")

