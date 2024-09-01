from logging import FileHandler
from typing import Annotated
from fastapi import FastAPI
import os
from fastapi import FastAPI, File, UploadFile, Path
from sqlalchemy import delete,select
from csv_dealer import HandleCsv
from db import CsvRequestStatus, get_db_session, CsvRequest
from uuid_extensions import uuid7
from datetime import datetime
from file_handle import FileHandler
from background import process_csv


app = FastAPI()


@app.get("/")
def read_root():
    dir_list = os.listdir("../")
    return {"result": dir_list}


@app.post("/process")
def process_file(csv_file: UploadFile):
    global file_path
    try:
        csv_content = csv_file.file.read()
        valid_file = HandleCsv.read_and_validate_csv(csv_content)

        if valid_file == True:

            csv_request_guid = str(uuid7())

            # store the file in storage
            file_save_result = FileHandler.save_file(
                str(csv_request_guid), csv_content)

            if file_save_result == False:
                return {"result": "failure", "message": "Error saving file. Contact system admin."}

            # store file in db
            csv_request = CsvRequest(
                request_guid=csv_request_guid,
                filename=csv_file.filename,
                status=CsvRequestStatus.UPLOADED.name,
                created_on=datetime.now()
            )
            with get_db_session() as session:
                session.add(csv_request)
                session.commit()
                print(f"Added File: {csv_request}")
                process_csv.delay(csv_request_guid, csv_request.id)
                return {"result": "success", "file": csv_request}
        else:
            return {"result": "failure", "message": "Invalid CSV file"}

    except Exception as e:
        print(f"Error in processing csv: {e}")
        return {"result": "error", "message": str(e)}


@app.post("/get_file_size")
def update_item(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/check-csv")
def check_csv(file: Annotated[bytes, File()]):
    try:
        print(f"file received type :  {type(file)}")
        result = HandleCsv.read_and_validate_csv(file)
        return {"result": result}
    except Exception as e:
        print(e)
        return {"result": "File Failed Check"}


@app.get("/reset_csv")
def delete_all_csv():
    try:
        with get_db_session() as session:
            session = get_db_session()
            session.execute(delete(CsvRequest))
            session.commit()
        return {"success": "Successfully deleted all files"}
    except Exception as e:
        return {"failure": e}


@app.get("/check_status/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
):
    with get_db_session() as session:
        csv_request = session.execute(
            select(CsvRequest).where(CsvRequest.id == item_id)
        ).scalar_one_or_none()
        
        if csv_request is None:
            return {"error": "CSV request not found"}
        
        is_completed = csv_request.status == CsvRequestStatus.COMPLETED.name
        
    return {"item_id": item_id, "is_completed": is_completed}

