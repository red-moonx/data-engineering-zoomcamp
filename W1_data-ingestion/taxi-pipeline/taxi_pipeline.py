import dlt
import requests

@dlt.resource(name="taxi_trips", write_disposition="replace")
def taxi_trips_resource():
    url = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
    page = 1
    while True:
        params = {"page": page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"Page {page} - Records: {len(data)}")
        
        if not data:
            break
            
        yield data
        page += 1

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="taxi_pipeline",
        destination="duckdb",
        dataset_name="taxi_data",
    )
    load_info = pipeline.run(taxi_trips_resource())
    print(load_info)
