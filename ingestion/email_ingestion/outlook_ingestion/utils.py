import os
import uuid
from datetime import datetime

def generate_custom_uuid_with_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    timestamp_str = dt.strftime('%Y%m%dT%H%M%S')
    random_uuid = uuid.uuid4().hex
    custom_uuid = f"{timestamp_str}-{random_uuid}"
    
    return custom_uuid

def sanitize_file_name(file_name, max_length=100):

    if len(file_name) > max_length:
        base, ext = os.path.splitext(file_name)
        file_name = base[:max_length-len(ext)] + ext
    return file_name