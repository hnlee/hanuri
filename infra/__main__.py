"""A Google Cloud Python Pulumi program"""

import pulumi
import pathlib
from pulumi_gcp import storage, compute

env = pulumi.get_stack()

bucket = storage.Bucket(
    'hanuri',
    location="US",
    website={"main_page_suffix": "index.html"},
    uniform_bucket_level_access=True
)
cache_control = "no-cache"

def upload_file(path: pathlib.Path, prefix: str | None = None) -> None:
    if path.is_file() and path.name not in (".DS_Store"):
        name = path.name if prefix is None else f"{prefix}/{path.name}"
        storage.BucketObject(
            name,
            bucket=bucket.name,
            name=name,
            source=pulumi.FileAsset(path),
            cache_control=cache_control,
        )


build_dir = pathlib.Path(__file__).parent.parent / "dist"
for path in build_dir.iterdir():
    upload_file(path)
    if path.is_dir():
        for subpath in path.iterdir():
            upload_file(subpath, prefix=path.name)


bucket_iam_binding = storage.BucketIAMBinding(
    "hanuri-public-access",
    bucket=bucket.name,
    role="roles/storage.objectViewer",
    members=["allUsers"],
)


if env == "prod":
    backend_bucket = compute.BackendBucket(
        "backend-bucket", bucket_name=bucket.name, enable_cdn=True
    )
    ip = compute.GlobalAddress("ip")
    url_map = compute.URLMap("url-map", default_service=backend_bucket.id)
    ssl = compute.ManagedSslCertificate("default", name="hanuri", managed={"domains": ["hanurikoreanschool.org", "www.hanurikoreanschool.org"]})
    https_proxy = compute.TargetHttpsProxy("https-proxy", url_map=url_map.id, ssl_certificates=[ssl.id])
    https_forwarding_rule = compute.GlobalForwardingRule(
        "https-forwarding-rule",
        ip_address=ip.address,
        ip_protocol="TCP",
        port_range="443",
        target=https_proxy.id,
        load_balancing_scheme="EXTERNAL_MANAGED"
    )
    redirect_url_map = compute.URLMap("redirect-map", default_url_redirect={"https_redirect": True, "strip_query": False})
    http_proxy = compute.TargetHttpProxy("http-proxy", url_map=redirect_url_map.id)
    http_forwarding_rule = compute.GlobalForwardingRule("http-forwarding-rule", ip_address=ip.address, ip_protocol="TCP", port_range="80", target=http_proxy.id, load_balancing_scheme="EXTERNAL_MANAGED")


pulumi.export("bucket_name", bucket.url)
pulumi.export("url", pulumi.Output.concat("http://storage.googleapis.com/", bucket.id, "/", "index.html"))


