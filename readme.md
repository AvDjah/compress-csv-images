# Image Compressor Project API

## Tech Used:
    1. fastapi : To write the endpoints.
    2. sqlalchemy : To handle db write and read.
    3. celery : To create and run background tasks
    4. alembic : To create and maintain migrations (didn't use much)
    5. rabbitmq : backend store to be used along alembic.

- This project provides an API for processing CSV files related to image compression tasks. 
- Currently, the api takes in files using a POST /process and then processes it in the background.
- Currently the image compression algo is left empty. It is emulated as a long operation using `time.sleep()` of 3s to 7s time.
- Below are the available endpoints and their descriptions.

## Endpoints


| Endpoint                | Description                                                                 | Request Parameters                                                                 | Response                                                                                       |
|-------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **POST /process**       | Processes an uploaded CSV file, validates it, stores it, and initiates background processing. | - `csv_file` (UploadFile): The CSV file to be processed.                          | - `200 OK`: A JSON object indicating success and a unique request ID for querying.                   |
|                         |                                                                             |                                                                                   | - `400 Bad Request`: A JSON object indicating failure and the reason for the failure.          |
| **GET /reset_csv**      | Deletes all CSV file records from the database.                             | None                                                                              | - `200 OK`: A JSON object indicating success.                                                  |
|                         |                                                                             |                                                                                   | - `500 Internal Server Error`: A JSON object indicating failure and the reason for the failure.|
| **GET /check_status/{item_id}** | Checks the status of a CSV request by its ID.                              | - `item_id` (int): The ID of the CSV request to check.                            | - `200 OK`: A JSON object containing the item ID and its completion status.                    |
|                         |                                                                             |                                                                                   | - `404 Not Found`: A JSON object indicating that the CSV request was not found.                |



## Directory Structure

Below is the directory structure of the Image Compressor Project along with a brief description of each file:
image-compressor-project/
- __init__.py: Package initializer
- celeryconfig.py: Configuration for Celery tasks
- csv_dealer.py: Handles CSV reading and validation
- db.py: Database models and responsible for providing session connection to db.
- file_handle.py: Responsible for reading and saving file from/to file system.
- main.py: Main entry point for the FastAPI application. Contains all the endpoints.
- readme.md: Project documentation
- background.py: Contains the main async image processing tasks responsible for processing the csv's and images in the background.


## How to Run the Program

To run the Image Compressor Project, follow the steps below:

1. **Start the FastAPI server:**

   - For development:
     ```sh
     fastapi dev main.py
     ```

   - For production:
     ```sh
     fastapi run main.py
     ```

2. **Start the Celery worker:**
   ```sh
   celery -A background worker --loglevel=INFO
   ```

3. **Query the API requests:**

   - You can use tools like `curl`, `Postman`, or any other API client to interact with the endpoints.

   - Example using `curl` to process a CSV file:
     ```sh
     curl -X POST "http://127.0.0.1:8000/process" -F "csv_file=@path_to_your_file.csv"
     ```

   - Example using `curl` to check the status of a CSV request:
     ```sh
     curl -X GET "http://127.0.0.1:8000/check_status/{item_id}"
     ```

   - Example using `curl` to reset all CSV records:
     ```sh
     curl -X GET "http://127.0.0.1:8000/reset_csv"
     ```

Make sure to replace `path_to_your_file.csv` with the actual path to your CSV file and `{item_id}` with the actual ID of the CSV request you want to check.


