from celery import Celery
import time
import csv
import random
import time
from sqlalchemy import and_, select, update
from sqlalchemy.orm import joinedload
from file_handle import FileHandler
import requests
from PIL import Image
import os
from io import BytesIO
from uuid_extensions import uuid7
from db import CsvRequest, CsvRequestStatus, ImageItem, ImageItemStatus, get_db_session

app = Celery('tasks')
app.config_from_object('celeryconfig')
app.conf.update(CELERY_BEAT_SCHEDULE={})

@app.task
def add(x, y):
    return x + y


@app.task
def process_image(image_name : str, image_guid : str):
    def download_and_save_image(image_url, save_dir="./files/images"):
        try:
            # Fetch the image
            response = requests.get(image_url)
            response.raise_for_status()

            # Check if it's a valid image
            try:
                img = Image.open(BytesIO(response.content))
                img.verify()
            except Exception:
                print(f"Invalid image: {image_url}")
                return False

            # Load the image using PIL
            try:
                img = Image.open(BytesIO(response.content))
                img.verify()
            except Exception:
                with get_db_session() as session:
                    session.execute(update(ImageItem).where(ImageItem.image_guid == image_guid).values(status=ImageItemStatus.INVALID.name))
                    session.commit()
                return False

            # Generate a filename from the URL
            filename = os.path.join(save_dir, f"{image_guid}.jpeg")

            # Save the compressed image using PIL
            img.save(filename, 'JPEG', optimize = True,quality = 95)

            print(f"Image saved: {filename}")
                
            # imitating image saving logic using sleep            
            sleep_time = random.uniform(3, 7)
            time.sleep(sleep_time)
             
            # Create the directory if it doesn't exist
            os.makedirs(save_dir, exist_ok=True)

            # Generate a filename from the URL
            filename = os.path.join(save_dir, os.path.basename(f"{image_guid}.jpeg"))

            # Save the image
            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f"Image saved: {filename}")
            with get_db_session() as session:
                session.execute(update(ImageItem).where(ImageItem.image_guid == image_guid).values(status=ImageItemStatus.PROCESSED.name))
                session.commit()
            
            # call the job to check if all jobs completed 
            update_csv_status(image_guid)
            
            return True
        except requests.RequestException as e:
            print(f"Error downloading image {image_url}: {str(e)}")
            with get_db_session() as session:
                session.execute(update(ImageItem).where(ImageItem.image_guid == image_guid).values(status=ImageItemStatus.FAILED.name))
            return False
    return download_and_save_image(image_name)



@app.task
def process_csv(csv_name,csv_request_id):
    try:
        csv_content = FileHandler.read_file(csv_name)
        if csv_content is None:
            return f"Error: Unable to read {csv_name}"

        from io import BytesIO, TextIOWrapper

        csv_buffer = BytesIO(csv_content)
        text_stream = TextIOWrapper(csv_buffer, encoding='utf-8')
        csv_reader = csv.reader(text_stream)
        next(csv_reader, None)
        image_guid = str(uuid7())
        # Process each row
        for row in csv_reader:
            if len(row) >= 3:
                print(f"Value in third column: {row[2]}")
                image_item = ImageItem(
                    image_guid = image_guid,
                    image_name = "",
                    status = ImageItemStatus.PENDING.name,
                    input_url = str(row[2]),
                    output_url = "",
                    csv_request_id = csv_request_id
                )
               
                with get_db_session() as session:
                    session.add(image_item)
                    session.commit()
                    
                process_image.delay(row[2],image_guid)
            else:
                print(f"Row does not have a third column: {row}")
        
        return f"processing {csv_name}" 
    except Exception as e:
        return f"failed processing {csv_name}"


@app.task
def update_csv_status(image_guid):
    try:
        with get_db_session() as session:
            image_item = session.execute(
                select(ImageItem).options(joinedload(ImageItem.csv_request)).where(ImageItem.image_guid == image_guid)
            ).scalar_one()
            if image_item is None:
                print(f"Image item not found while updating csv : {image_guid}")
                return False
            
            # check if any image with status pending is remaining for the current associated csv_request
            pending_images = session.execute(
                select(ImageItem).where(
                    and_(
                        ImageItem.csv_request_id == image_item.csv_request_id,
                        ImageItem.status == ImageItemStatus.PENDING.name
                    )
                )
            ).scalars().all()
            
            if not pending_images:
                # No pending images left, update the CSV request status
                session.execute(
                    update(CsvRequest)
                    .where(CsvRequest.id == image_item.csv_request_id)
                    .values(status=CsvRequestStatus.COMPLETED.name)
                )
                session.commit()
                print(f"CSV request {image_item.csv_request_id} completed")
            else:
                print(f"CSV request {image_item.csv_request_id} still has {len(pending_images)} pending images")
        
        return True
        # Now you can access image_item.csv_request
        # ... rest of your code ...

    except Exception as e:
        print(f"Error updating csv status: {str(e)}")
        return False
    
    


if __name__ == '__main__':
    app.start()