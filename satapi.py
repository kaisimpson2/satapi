import requests
import os


USERNAME = "hsksimp2@liverpool.ac.uk"
PASSWORD = "*********"

# CDSE API endpoint
BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
PRODUCT_TYPE = "SR_2_WAT___"      
START_DATE = "2018-01-01T00:00:00Z"
END_DATE   = "2024-01-05T23:59:59Z"

AREA_WKT = (
    "POLYGON((-10 59, 7 50, 6.5 59, 2 53.0, -10 55))"
)

DOWNLOAD_DIR = "./s3_altimetry_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


query = (
    f"{BASE_URL}?"
    f"$filter=contains(Name,'S3A_SR_2_WAT') "
    f"and ContentDate/Start ge {START_DATE} "
    f"and ContentDate/End le {END_DATE} "
)

print("Querying CDSE API...")
print(query)

response = requests.get(query, auth=(USERNAME, PASSWORD))

if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit()

data = response.json()
products = data.get("value", [])

print(f"Found {len(products)} products.\n")


for prod in products:
    prod_id = prod["Id"]
    prod_name = prod["Name"]

    print(f"Downloading: {prod_name}")

    # Download URL
    download_url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({prod_id})/$value"

    out_path = os.path.join(DOWNLOAD_DIR, f"{prod_name}.zip")

    with requests.get(download_url, auth=(USERNAME, PASSWORD), stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"Saved → {out_path}\n")

print("Finished downloading all products.")

