import requests
import time
from tqdm import tqdm
#
# This file collects data for the example portfolio using the input csv from 
# ../data/api_csv_input.csv and the user api key stored at ../api_key.txt, which 
# is gitignored to ensure API key privacy.
#
steps = [
    "Uploading csv",
    "Processing upload",
    "Requesting export",
    "Exporting",
    "Downloading",
]

# Set desired scenarios and return intervals
SCENARIO = "ssp370"
RETURN = [10, 50, 100, 200, 500]

# Set API urls, headers, and API key
BASE_URL = "https://apis.climate-x.com/main"
UPLOAD_URL = f"{BASE_URL}/external-upload-csv/"
EXPORT_URL = f"{BASE_URL}/export-csv/"
with open("../api_key.txt", "r") as f:
    API_KEY = f.read().strip()
HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json"
}

with tqdm(total=len(steps)) as pbar:
    # Upload csv with asset locations
    with open("../data/api_csv_input.csv", "rb") as f:
        response = requests.post(UPLOAD_URL, headers=HEADERS, files={"file": f})

    if response.status_code == 200:
        data = response.json()
        project_id = data["project_id"]
        job_id = data["job_id"]
    else:
        raise ValueError(f"Upload failed: {response.status_code} - {response.text}")
    pbar.set_description("Uploading CSV")
    pbar.update(1)

    # Wait for upload to process, then continue
    while True:
        status_response = requests.get(
            f"{BASE_URL}/import-assets/{job_id}", headers=HEADERS
        )
        status = status_response.json()
        if status["status"] == "COMPLETED":
            break
        elif status["status"] == "FAILED":
            raise Exception("Upload Failed!")
        time.sleep(5)
    pbar.update(1)

    # Start export csv request
    export_response = requests.post(
        EXPORT_URL,
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "project_id": project_id,
            "defended": False,
            "scenario": SCENARIO,
            "one_in_x": RETURN,
        },
    )

    if export_response.status_code == 200:
        export = export_response.json()
        export_job_id = export["export_job_id"]
    else:
        raise ValueError(
            f"Export failed: {export_response.status_code} - {export_response.text}"
        )
    pbar.update(1)

    # Wait for job to process, then continue
    while True:
        download_response = requests.get(
            f"{BASE_URL}/export-csv/{export_job_id}", headers=HEADERS
        )
        download = download_response.json()
        if download["status"] == "COMPLETED":
            break
        elif download["status"] == "FAILED":
            raise Exception("Download Failed!")
        time.sleep(5)
    pbar.update(1)

    # Download the export data csv, save to relative data directory
    pbar.set_description("Downloading file")
    download_url = download["url"]
    file_response = requests.get(download_url)

    return_str = (
        "_".join(str(r) for r in RETURN) if isinstance(RETURN, list) else str(RETURN)
    )
    output_filename = f"../data/api_csv_output_{SCENARIO}_{return_str}.csv"

    if file_response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(file_response.content)
        print(f"Saved to {output_filename}")
    else:
        raise ValueError(
            f"Download failed: {file_response.status_code} - {file_response.text}"
        )
    pbar.set_description("Done!")
    pbar.update(1)
