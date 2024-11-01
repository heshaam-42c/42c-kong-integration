# based on 42c-discovery
import time
import requests
import json
import ruamel.yaml
import unicodedata
import re
import csv
import base64
import getpass
import os
import sys

API_ENDPOINT = "https://demolabs.42crunch.cloud/api/v1"
summaryReport = []
summaryReportFile = "summaryReport.csv"
topCriticalFile = "topCritical.csv"
topHighFile = "topHigh.csv"

top_issues_critical = {}
top_issues_high = {}
descriptions = {}

def upload_file(collection_name, fileName):
  collectionUUID = retrieveCollectionUUID(collection_name, token)
  if collectionUUID == "":
    print("error: collection not found")
    sys.exit()
  if "yaml" in fileName or "yml" in fileName:
      return submitYAMLFile(fileName, collectionUUID)
  elif "json" in fileName:
      return submitJSONFile(fileName, collectionUUID)
  else:
      print("error: unsupported file type")
      sys.exit()
  
def retrieveCollectionUUID (collection_name, token):
  url = API_ENDPOINT + "/collections"

  headers = {"accept": "application/json",
           "X-API-KEY": token}
  r = requests.get(url, headers=headers)

  if r.status_code != 200:
    print ("Can't list collections")
    print(f"failed with status code {r.status_code}") 
    sys.exit()

  target_collection_id = ""
  for c in r.json()['list']:
      if c['desc']['name'] == collection_name:
          target_collection_id = c['desc']['id']
          break
  
  return target_collection_id

def stripNonAlphaNum(text):
    encodedText = unicodedata.normalize('NFKD', text)
    return re.sub('[^A-Za-z0-9\\-_]+', '', encodedText)

def submitJSONFile(file_name, target_collection_id):
  try:
    with open(file_name, 'r', encoding='utf-8') as json_file:
      print (f"Loading file: {file_name}")
      try:
        data = json.load(json_file)
      except:
        # JSON is invalid - Skipping
        print("Error while parsing JSON file") 
        sys.exit()
      else:   
        api_name_raw = data['info']['title'] + '_' + data['info']['version']
        api_name = stripNonAlphaNum(api_name_raw)
        print(f"Submitting API: {api_name}")
        contents = open (file_name, 'r').read()
        return import_file (contents, api_name, file_name, target_collection_id)
  except:
    print("unexpected error")
    sys.exit()

def submitYAMLFile(file_name, target_collection_id):
  try:
      with open(file_name, 'r') as yaml_file:
        print (f"Loading file: {file_name}")
        try:
          data = ruamel.yaml.load(yaml_file, Loader=ruamel.yaml.Loader)
        except:
          print("Error while parsing YAML file")
          sys.exit()
        else:
          # Converting YAML to JSON
          print ("Converting to JSON...")
          with open (file_name, 'r') as fpi:
            yaml_contents = ruamel.yaml.load(fpi, Loader=ruamel.yaml.Loader)
            api_name_raw = yaml_contents['info']['title'] + '_' + yaml_contents['info']['version']
            api_name = stripNonAlphaNum(api_name_raw)
            print(f"Submitting API: {api_name}")
            json_contents = json.dumps(yaml_contents, indent=2)
            return import_file (json_contents, api_name, file_name, target_collection_id)
  except:
    print("unexpected error")
    sys.exit()


def import_file (contents, api_name, file_name, target_collection_id):
  print ("Connecting to", API_ENDPOINT)
  multipart_form_data = {
    'specfile': (file_name, contents , 'application/json'),
    'name': ('', api_name),
    'cid':  ('', target_collection_id)
  }

  # ---- submit the OpenAPI contract to 42Crunch -----------
  url = f"{API_ENDPOINT}/apis"
  headers = {"accept": "application/json",
                    "X-API-KEY": token}

  response = requests.post(url,
              files=multipart_form_data, headers=headers)

  if response:
    api_id = response.json()["desc"]["id"]        
    print (f"Successfully submitted API: {file_name} with 42c ID is {api_id} ")
    return api_id
  else:
    print(f" Import failed with status code {response.status_code}") 
    sys.exit()

def writeOnFile(name, id):
  if not os.path.exists(config_filename):
    data = {'audit' : {'mapping' : {name : id}}}
    filee = open(config_filename, "w")
    ruamel.yaml.dump(data, filee, Dumper=ruamel.yaml.RoundTripDumper)
    filee.close()
  else:
    with open(config_filename, 'r') as yaml_file:
      try:
          data = ruamel.yaml.load(yaml_file, Loader=ruamel.yaml.Loader)
      except:
         print("error")
      else:
          data["audit"]["mapping"][name] = id

    filee = open(config_filename, "w")
    ruamel.yaml.dump(data, filee, Dumper=ruamel.yaml.RoundTripDumper)
    filee.close()
    
def get_report(api_id, api_name):

    url = f"{API_ENDPOINT}/apis/{api_id}/assessmentreport"

    headers = {"accept": "application/json",
            "X-API-KEY": token}

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise NameError(f"GET /assessmentreport {r.status_code}")

    report = r.json()
  
    # ---- Process the report -------------------------

    # This retrieves and decodes the list of issues
    details = json.loads(base64.decodebytes(report["data"].encode("utf-8")))

    #print("========== details ===========")
    #print(details)
    #print("========== end of details ===========")

    # If global-security issue is present, the API does not have global authentication
    # If operation-security issue is present, the API does not have authentication for one of the operations
    if "security" not in details:
        hasGlobalSecurity = "InvalidSchema"
        hasOperationSecurity = "InvalidSchema"
    else:
        hasGlobalSecurity = "True"
        hasOperationSecurity = "True"
        for iss in details["security"]["issues"]:
            if iss == "global-security" or iss == "v3-global-security":
                hasGlobalSecurity = "False"
            if iss == "operation-security" or iss == "v3-global-security":
                hasOperationSecurity = "False"
            #print(iss)
            criticality = details["security"]["issues"][iss]['criticality']
            if criticality == 5:
                top_issues_critical[iss] = top_issues_critical.get(iss, 0) + len(details["security"]["issues"][iss]["issues"])
                descriptions[iss] = details["security"]["issues"][iss]['description']
            if criticality == 4:
                top_issues_high[iss] = top_issues_high.get(iss, 0) + len(details["security"]["issues"][iss]["issues"])
                descriptions[iss] = details["security"]["issues"][iss]['description']

    if "data" in details:
        for iss in details["data"]["issues"]:
            criticality = details["data"]["issues"][iss]['criticality']
            if criticality == 5:
                top_issues_critical[iss] = top_issues_critical.get(iss, 0) + len(details["data"]["issues"][iss]["issues"])
                descriptions[iss] = details["data"]["issues"][iss]['description']
            if criticality == 4:
                top_issues_high[iss] = top_issues_high.get(iss, 0) + len(details["data"]["issues"][iss]["issues"])
                descriptions[iss] = details["data"]["issues"][iss]['description']

    report_url = f"https://us.42crunch.cloud/apis/{api_id}/security-audit-report"

    item = {'name': api_name, 'grade': int(
        round(float(report["attr"]["data"]["grade"]))),
        'valid': report["attr"]["data"]["isValid"],
        'issues_total': report["attr"]["data"]["numErrors"],
        'issues_critical': report["attr"]["data"]["numCriticals"],
        'issues_high': report["attr"]["data"]["numHighs"],
        'issues_medium': report["attr"]["data"]["numMediums"],
        'issues_low': report["attr"]["data"]["numLows"],
        'hasGlobalSecurity': hasGlobalSecurity,
        'hasOperationSecurity': hasOperationSecurity,
        'report_url': report_url}

    print("Report retrieved and processed")
    #print(item)

    # Add the new entry to the summary report
    summaryReport.append(item)

    # ---- Save issue stats -----------------------------------

    #print("========== top_issues_critical ===========")
    #print(top_issues_critical)
    #print(top_issues_high)
    #print("========== end of top_issues_critical ===========")


    # ---- Save the summary report to CSV file -------------------------

    with open(summaryReportFile, 'w', newline='') as csvfile:
        fieldnames = ['name', 'grade',
                      'valid',
                      'issues_total',
                      'issues_critical',
                      'issues_high',
                      'issues_medium',
                      'issues_low',
                      'hasGlobalSecurity',
                      'hasOperationSecurity',
                      'report_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in summaryReport:
            writer.writerow(row)

    # ---- Save the top critical & high issues to file -------------------------

    with open(topCriticalFile, 'w', newline='') as csvfile:
        fieldnames = ['issue_id', 'description', 'count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for issue in top_issues_critical:
            row = {'issue_id': issue,
                  'description': descriptions[issue],
                  'count': top_issues_critical[issue]
                  }
            writer.writerow(row)

    with open(topHighFile, 'w', newline='') as csvfile:
        fieldnames = ['issue_id', 'description', 'count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for issue in top_issues_high:
            row = {'issue_id': issue,
                  'description': descriptions[issue],
                  'count': top_issues_high[issue]
                  }
            writer.writerow(row)


### MAIN PART
config_filename = './42c-conf.yaml'

# file_name = input("Target api name ? ")
file_name = "/Users/heshaamattar/github/heshaam-42c/42c-kong-integration/OAS/pixi.json"

# target_collection_name =  input("Target collection name ? ")
target_collection_name = "GitHubActions heshaam-42c/Pixi--main"

# token = getpass.getpass('42C API Token: ')
token = "api_de157c54-394f-454b-b85d-3637a8c47005"

api_id = upload_file(target_collection_name, file_name)

writeOnFile(file_name, api_id)

time.sleep(3)

get_report(api_id, file_name)