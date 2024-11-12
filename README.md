# Kong Konnect to 42Crunch OpenAPI Specification Extraction and Import

This repository contains scripts to automate the extraction of OpenAPI specifications from a Kong API gateway and import them into the 42Crunch platform for API security and governance.

## Purpose

The purpose of these scripts is to streamline the migration of OpenAPI definitions from Kong to 42Crunch. They automate the retrieval of OpenAPI definition objects from Kong, organize and store them locally, and then import these definitions into 42Crunch. This process aids in maintaining an up-to-date and secure collection of API specifications, enabling security analysis and compliance within 42Crunch.

## Dependencies

The following dependencies are required to run the scripts:
1.	Python (version 3.6 or higher)
2.	API Tokens:
*	A valid API token for Kong with read permissions to access OpenAPI definition objects.
*	A valid API token for 42Crunch with write permissions to import API definitions.
3.	Python Packages:
*	requests: Used for making HTTP requests to Kong and 42Crunch APIs.
*	Install the required packages by running:

'pip install requests'

## Scripts Overview

The extraction and import process is divided into three scripts:
1.	Script 1: Retrieve All OpenAPI Definitions in a Flat File
This script retrieves all OpenAPI definition objects from Kong and stores them in a single flat file (all_openapi_definitions.json). It provides an overview of all definitions, making it easy to view and verify which APIs are available in Kong.
2.	Script 2: Retrieve OpenAPI Definitions Individually and Store Locally
This script iterates through each OpenAPI definition object in Kong, retrieves them individually, and saves each one as a separate file in a designated local directory (openapi_definitions). This structure organizes each API’s definition into its own file for easier management and individual access.
3.	Script 3: Import OpenAPI Definitions into 42Crunch
This script reads the locally stored OpenAPI definition files from openapi_definitions and imports each one into the 42Crunch platform. This script leverages the 42Crunch API to add each API definition, enabling 42Crunch’s security analysis and governance features on these imported APIs.

## Usage Instructions

### Prerequisites

Ensure that you have the required API tokens for both Kong and 42Crunch, and that these tokens have the necessary privileges for the API operations performed by each script.

### Running the Scripts

	1.	Run Script 1 to retrieve all OpenAPI definitions and store them in a flat file:

`python retrieve_all_definitions.py`

This will create all_openapi_definitions.json containing the list of all OpenAPI definition objects from Kong.

	2.	Run Script 2 to retrieve each OpenAPI definition individually and store it locally:

`python retrieve_individual_definitions.py`

This will create a directory named openapi_definitions and save each OpenAPI definition file as a separate .json file within it.

	3.	Run Script 3 to import the locally stored OpenAPI definitions into 42Crunch:

`python import_to_42crunch.py`

Each file in openapi_definitions will be imported into 42Crunch as an API definition.

## Additional Notes

	•	Error Handling: Each script includes basic error handling for network errors and authorization issues. Ensure your API tokens are valid and correctly set in the script or environment before running.
	•	Rate Limits: Both Kong and 42Crunch may have API rate limits. Avoid running the scripts too frequently to prevent hitting these limits.

## Example Directory Structure

After running all scripts, your directory structure should look like this:

<img width="435" alt="image" src="https://github.com/user-attachments/assets/e4a8f859-962a-46f7-8b92-526bc3a588c5">

## Troubleshooting

	•	Authentication Issues: If you encounter authentication errors, check that your API tokens have the necessary privileges and are correctly configured.
	•	Connection Errors: Network or server issues may cause connection errors. Verify your internet connection and the availability of Kong and 42Crunch endpoints.

## License

This project is licensed under the MIT License.
