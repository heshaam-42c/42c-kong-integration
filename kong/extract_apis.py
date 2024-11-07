import http.client
import json

def list_api_products ():
    conn = http.client.HTTPSConnection("us.api.konghq.com")

    headers = {
        'accept': "application/json",
        'Authorization': "Bearer " + KONG_ACCESS_TOKEN
        }

    conn.request("GET", "/v2/api-products?page%5Bsize%5D=10&page%5Bnumber%5D=1&sort=name%20desc", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse JSON data
    json_data = json.loads(data.decode("utf-8"))
    for item in json_data["data"]:
        print(item["name"] + " - " + item["id"])
        list_api_product_versions(item["id"])
    return json_data

def list_api_product_versions (api_product_id):
    conn = http.client.HTTPSConnection("us.api.konghq.com")

    headers = {
        'accept': "application/json",
        'Authorization': "Bearer " + KONG_ACCESS_TOKEN
        }

    conn.request("GET", f"/v2/api-products/{api_product_id}/product-versions?page%5Bsize%5D=10&page%5Bnumber%5D=1&filter%5Bpublish_status%5D=unpublished&sort=name%20desc", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse JSON data
    json_data = json.loads(data.decode("utf-8"))
    for item in json_data["data"]:
        print("  " + item["name"] + " - " + item["id"])
        fetch_api_product_version_specs(api_product_id, item["id"])

    return json_data

def fetch_api_product_version_specs (api_product_id, api_product_version_id):
    conn = http.client.HTTPSConnection("us.api.konghq.com")

    headers = {
        'accept': "application/json",
        'Authorization': "Bearer " + KONG_ACCESS_TOKEN
        }

    conn.request("GET", f"/v2/api-products/{api_product_id}/product-versions/{api_product_version_id}/specifications", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse JSON data
    json_data = json.loads(data.decode("utf-8"))
    for item in json_data["data"]:
        print("    " + item["name"] + " - " + item["id"])
    
    return json_data

# main
KONG_ACCESS_TOKEN = "xxxx"

list_api_products()