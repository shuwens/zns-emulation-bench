import boto3
import json

access_key = "YE39S1BMH6IXCMYOIJ89"
secret_key = "eZ6Xvo8zO4lYETGeOU5xOV05oQc0g5AazhJw5byZ"

conn = boto3.client(
    "s3",
    "us-east-1",
    endpoint_url="http://12.12.12.2:80",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)

bucket = "public"

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:PutObject", "s3:GetObject"],
            "Resource": ["arn:aws:s3:::{0}/*".format(bucket)],
        }
    ],
}

bucket_policy = json.dumps(bucket_policy)
conn.put_bucket_policy(Bucket=bucket, Policy=bucket_policy)
