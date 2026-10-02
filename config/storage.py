import boto3, io, json

def connect_to_r2_using_boto3(r2_client_credentials):
    return boto3.client(**r2_client_credentials)

def create_r2_bucket(s3, bucket: str='video-game-statistics'):
    existing_buckets = [b['Name'] for b in s3.list_buckets().get('Buckets', [])]

    if bucket not in existing_buckets:
        s3.create_bucket(Bucket=bucket)
        print(f"✅ Success! Bucket '{bucket}' created.")

def get_r2_object_metadata(s3, bucket='video-game-statistics'):
    return s3.list_objects_v2(Bucket=bucket).get('Contents', [])

def serialize_json_data(data):
    return io.BytesIO(json.dumps(data, separators=(',', ':')).encode('utf-8'))

def upload_object_to_r2_bucket(s3, bucket, filename, body, content_type):
    s3.put_object(Bucket=bucket, Key=filename, Body=body, ContentType=content_type)

def connect_to_r2_using_httpfs(conn, r2_secret_credentials):
    conn.execute(f"""
        INSTALL httpfs;
        LOAD httpfs;

        CREATE OR REPLACE SECRET secret ({r2_secret_credentials});
    """)