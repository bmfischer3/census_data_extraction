
#  Census Data Extraction and Comparison Tool

## Table of Contents
- [Census Data Extraction and Comparison Tool](#census-data-extraction-and-comparison-tool)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Business Problem](#business-problem)
  - [Data Sources](#data-sources)
  - [Methods](#methods)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Quick Glance at Results](#quick-glance-at-results)
  - [Limitations](#limitations)
  - [Other Resources](#other-resources)
  - [Revision History](#revision-history)
    - [How to Update](#how-to-update)

## Overview
This project allows users to provide a list of ZIP codes and a list of desired census data tables. It retrieves the data from the census API and compiles the requested information for easy comparison across ZIP codes, exporting the results to a spreadsheet.

## Business Problem
Businesses and analysts often need to compare demographic or economic data across different regions. Manually retrieving this data from the U.S. Census Bureau for multiple ZIP codes can be time-consuming. This tool automates that process, enabling quicker, more efficient analysis of multiple regions.

## Data Sources
The U.S. Census Bureau API is used as the primary data source to retrieve requested census data tables.

## Methods
- User provides a list of ZIP codes and desired census data tables.
- The program calls the Census Bureau API for each ZIP code and table.
- The resulting data is processed and output into a spreadsheet for easy comparison.
- With the exception of "Detailed Tables," all tables are accessed through building a call URL. Examples of those URLs can be found here:
  - https://www.census.gov/data/developers/data-sets/acs-5year.html


## Tech Stack
- **Programming Language**: Python
- **Libraries/Frameworks**:
  - `requests` for API calls
  - `pandas` for data manipulation
  - `openpyxl` for Excel file generation
- **Data Storage**: Output as .xlsx file

## Installation
1. **Clone the repository:**
```bash
   git clone https://github.com/bmfischer3/census_data_extraction.git
   cd repo
```

2. **Create and activate a virtual environment:**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use \`venv\Scripts\activate\`
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
   export API_KEY=your_api_key_here
```

## Usage
1. **Step 1**: Provide the list of ZIP codes and census data tables in the two .txt files named "table_profile_id_list.txt" and "zip_code_data.txt."

   - You can retrieve a list of tables by clicking the "HTML" link for each table variable in the below link:
     - https://www.census.gov/data/developers/data-sets/acs-5year.html
     - The table names should start with a B, S, D, or C and look something like: `B24122_486E`.

```bash
# table_profile_id_list.txt should look like the below:

# You will need to provide the second value and name it whatever you want.


S1901_C01_001E,total_households 
S1901_C01_012E,median_household_income 
S1901_C01_013E,mean_household_income
B25012_003E,owned_homes_with_children_under18
B25012_009E,owned_homes_with_NO_children_under18 
B25012_001E,total_households2

# zip_code_data.txt should look like the below:

{zip_code}, {STATE}, {City}, {County}, {time_zone}
# Timezone may be ommitted, as it is not used. 

# Use this resource: https://www.freemaptools.com/find-zip-codes-inside-user-defined-area.htm

# The above resource will provide the zip codes in the below format.

60554,IL,KANE,SUGAR GROVE,6,0
60512,IL,KENDALL,BRISTOL,6,0
60124,IL,KANE,ELGIN,6,0
60147,IL,KANE,LAFOX,6,0
60183,IL,KANE,WASCO,6,0
60175,IL,KANE,SAINT CHARLES,6,0
60136,IL,KANE,GILBERTS,6,0
60506,IL,KANE,AURORA,6,0
60538,IL,KENDALL,MONTGOMERY,6,0
60542,IL,KANE,NORTH AURORA,6,0
60134,IL,KANE,GENEVA,6,0
60510,IL,KANE,BATAVIA,6,0
60539,IL,KANE,MOOSEHEART,6,0
60543,IL,KENDALL,OSWEGO,6,0
60507,IL,KANE,AURORA,6,0
60568,IL,KANE,AURORA,6,0

```


2. **Step 2**: Invoke the `export_zip_dataframe` function by providing the state abbreviation, path to the table_profile_id_list.txt, path to the zip_code_data.txt list, and year if differing from 2022. 

3. **Step 3**: An excel file will be exported to the current directory. 

## Quick Glance at Results
- In this example, I gathered zip codes from all regions circled in the below image. Essentially all of Chicago. 

![chicago,illinois](2024-09-06-13-42-55.png)

A snippet of the resulting data is below:

![](2024-09-06-13-43-39.png)


  
## Limitations
- **Limited to Zip Code**: Data can only be retrieved by zip code at this time. 
- **Data Accuracy**: Some data isn't available and for those values a 0 or -6666666 may appear. Additionally, discrepancies in how the data is collected may affect results. Diving into those methodologies is beyond the scope of this project. 


## Other Resources
- [U.S. Census Bureau API Documentation](https://www.census.gov/data/developers/data-sets.html)


## Revision History

| Date       | Version | Author       | Description                                           |
|------------|---------|--------------|-------------------------------------------------------|
| 2024-09-06 | 1.0.0   | B. Fischer   | Initial creation of the repository and documentation. |
| YYYY-MM-DD | X.X.X   | Your Name    | Description of the changes made.                      |

### How to Update
1. Add a new row to the table above for each update.
2. Increment the version number following semantic versioning (e.g., 1.0.1 for small changes, 1.1.0 for a new feature, 2.0.0 for a major update).
3. Include the date, author, and description of the changes.


