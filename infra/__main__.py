"""A Google Cloud Python Pulumi program"""

import pulumi
import pathlib
from pulumi_gcp import storage

env = pulumi.get_stack()

bucket = storage.Bucket(
    'hanuri',
    location="US",
    website={"main_page_suffix": "index.html"},
    uniform_bucket_level_access=True
)

cache_control = "no-cache" if env == "staging" else "max-age=3600"

build_dir = pathlib.Path(__file__).parent.parent / "dist"
for path in build_dir.iterdir():
    if path.is_file() and path.name not in (".DS_Store"):
        bucket_object = storage.BucketObject(
            path.name,
            bucket=bucket.name,
            name=path.name,
            source=pulumi.FileAsset(path),
            cache_control=cache_control,
        )

bucket_iam_binding = storage.BucketIAMBinding(
    "hanuri-public-access",
    bucket=bucket.name,
    role="roles/storage.objectViewer",
    members=["allUsers"],
)

pulumi.export("bucket_name", bucket.url)
pulumi.export("url", pulumi.Output.concat("http://storage.googleapis.com/", bucket.id, "/", "index.html"))

