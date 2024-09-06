from census import Census
from us import states
import requests
import logging
import os
import pandas as pd
from pprint import pprint
import openpyxl

api_key = os.getenv('API_KEY')


def get_zip_code_list(raw_data_path: str) -> list:
    """Returns a list of only the zip codes from the data.txt file. 

    Args:
        raw_data_path (_type_): string path to .txt file. 

    Returns:
        list: comma separated integer, 5 digit zip codes. 
    """
    zip_code_list = []
    data = transform_raw_zip_data(raw_data_path)
    for i in data:
        zip_code_list.append(int(i[0]))
    return zip_code_list

def get_table_profile_ids(table_name_path:str) -> list:
    table_profile_id_list = []
    data = transform_raw_table_names(table_name_path)
    for i in data:
        table_profile_id_list.append(str(i[0]))
    return table_profile_id_list

def get_table_id_common_paths(table_name_path:str) -> list:
    table_id_common_name_list = []
    data = transform_raw_table_names(table_name_path)
    for i in data:
        table_id_common_name_list.append(str(i[1]))
    return table_id_common_name_list

def export_zip_dataframe(state_abrv:str, table_profile_id_list_path:str, raw_data_path:str, year=2022) -> None:
    """Exports an excel file by collecting all of the data from the downstream functions. 

    Args:
        zip_code_list (list): comma separated list of zip codes. 
        state_abrv (str): two letter state abbreviation
        table_profile_id_list (list): comma separated list of the census data tables you want collected. 
        raw_data_path (str): path to a txt file of line separated values in the style: 60119,IL,KANE,ELBURN,6,0. These are obtained from https://www.freemaptools.com/find-zip-codes-inside-radius.htm
        year (int, optional): _description_. Defaults to 2022.

    Return:
        None
    """
   
    zip_code_list = get_zip_code_list(raw_data_path)
    table_profile_id_list = get_table_profile_ids(table_profile_id_list_path)

   
    main_df = dict.fromkeys(table_profile_id_list,{})
    main_df.update(get_location_column(zip_code_list, raw_data_path))
    for table_id in table_profile_id_list:
        main_df.update(get_all_column_data(state_abrv, table_id, raw_data_path, 2022))

    zip_data = pd.DataFrame(main_df)
    column_params = dict(transform_raw_table_names(table_profile_id_list_path))
    zip_data.rename(columns=column_params, inplace=True)
    file_name = 'export_test.xlsx'
    zip_data.to_excel(file_name)

def get_all_column_data(state_abrv:str, table_profile_id:str, raw_data_path:str, year=2022) -> dict:
    """returns a single dict with a single key of the table_profile_id. 

    Args:
        zip_code_list (int): list of 5 digit zip codes
        state_abrv (str): 2-letter state abbreviation
        table_profile_id (str): single census table profile id (ex. 'S1901_C01_012E')
        year (int, optional): 4 digit year, defaults to 2022.

    Returns:
        dict: Returns a dictionary with the key as table_profile_id. The value of that key is another \
                dictionary with multiple k/v pairs following (zip_code:value)
    """

    zip_code_list = get_zip_code_list(raw_data_path)

    id_dict = {table_profile_id:{}}
    for zip in zip_code_list:
        value = get_zip_data_point(zip, table_profile_id, state_abrv, 2022)
        id_dict[table_profile_id][zip] = value
    return id_dict

def get_zip_data_point(zip_code: int, table_profile_id: str, state_abrv, year=2022) -> str:
    """Retrieves a single table value, if available, calls the get_api_response function.

    Args:
        zip_code (int): 5 digit zip code
        table_profile_id (str): single census table profile id (ex. 'S1901_C01_012E')
        state_abrv (str): 2-letter state abbreviation
        year (int, optional): 4 digit year, defaults to 2022.

    Returns:
        int or str: Dependent on the table requested. Typically an int. get_api_response function returns the value. 
    """

    # Get Detailed Tables

    if table_profile_id[0] == 'B':
        fips_arg = 'states.' + state_abrv + '.fips'
        try:
            temp_dict = {zip_code:None}
            c = Census(api_key)
            data_list = c.acs5.state_zipcode(table_profile_id,  # This is the variable for median household income
                                        fips_arg, # State FIPS code (CA is an example)
                                        zip_code,        # Zip Code
                                        year=year)      # Year
                # Get the (first and only) dictionary from the list and then get the value from the key. 
            table_value = data_list[0][table_profile_id]
            return table_value

        except Exception as e:
            logging.info(f"An error ocurred with getting the data in B. Exception: {e}")
            return None

    # Get Subject Tables
    elif table_profile_id[0] == 'S':
            try:
                url = f"https://api.census.gov/data/{year}/acs/acs5/subject?get={table_profile_id}&for=zip%20code%20tabulation%20area:{zip_code}&key={api_key}"
                return get_api_response(zip_code, table_profile_id, url)  
            except Exception as e:
                logging.info(f"An error occurred with calling the API: {e}")
                return None

    # Get Data Profiles        
    elif table_profile_id[0] == 'D':
        try:
            url = f"https://api.census.gov/data/{year}/acs/acs5/profile?get=group{table_profile_id}&for=zip%20code%20tabulation%20area:{zip_code}&key={api_key}"
            return get_api_response(zip_code, table_profile_id, url)  
        except Exception as e:
            logging.info(f"An error occurred with calling the API: {e}")
            return None
        
    # Get Comparison Profiles        
    elif table_profile_id[0] == 'C':
        try:
            url = f"https://api.census.gov/data/{year}/acs/acs5/cprofile?get=group{table_profile_id}&for=zip%20code%20tabulation%20area:{zip_code}&key={api_key}"
            return get_api_response(zip_code, table_profile_id, url)            
        except Exception as e:
            logging.info(f"An error occurred with calling the API: {e}")
            return None
        
    else:
        logging.info(f"Table ID does not start with B, S, D, or C")
        return None


def get_api_response(zip_code, table_profile_id, url) -> str:
    """Returns the response from the API as a single int or str value. 

    Args:
        zip_code (_type_): 5 digit int
        table_profile_id (_type_): string
        url (_type_): string
         (_type_):  dict

    Returns:
        int/str: value
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[1][0]

    elif response.status_code == 204:
        logging.info(f"Success, but no data: {response.status_code}, {response.text}")
        print(f'Likely no data for zip code: {zip_code} and table {table_profile_id}: {response.status_code}')
        return 'no_data'
    else:
        logging.info(f"Error code: {response.status_code}, {response.text}")
        return 'error'


def transform_raw_table_names(table_txt_list_path:str) -> list:
    """ returns a list of tuples with the census_table_id and its common name. 

    Args:
        table_list_path (str): _description_

    Returns:
        _type_: _description_
    """
    with open(table_txt_list_path, 'r') as file:
        raw_data_list = file.read()

    rows = raw_data_list.strip().split('\n')
    result = []
    for row in rows:
        columns = row.split(',')
        census_table_id = columns[0]
        census_table_common_name = columns[1]
        
        # Step 6: Append the extracted values as a tuple
        result.append((census_table_id, census_table_common_name))
    return result


def transform_raw_zip_data(data_list_path:str) -> list:
    """Returns a list of tuples in the form: (zip code, city name, state, county)

    Args:
        data_list_path (str): Path to a txt file containing the combined export from: https://www.freemaptools.com/find-zip-codes-inside-user-defined-area.htm

    Returns: list of tuples: (zip, city, state, county)
    """


    with open(data_list_path, 'r') as file:
        raw_data_list = file.read()

    # Step 1: Split the data by new lines to get each row
    rows = raw_data_list.strip().split('\n')

    # Step 2: Create a list to store the result
    result = []

    # Step 3: Process each row
    for row in rows:
        # Step 4: Split the row by commas to extract values
        columns = row.split(',')
        
        # Step 5: Extract zip code, city name, state, and county
        zip_code = int(columns[0])
        state = columns[1]
        county = columns[2]
        city_name = columns[3]
        
        # Step 6: Append the extracted values as a tuple
        result.append((zip_code, city_name, state, county))
    return result



def setup_logger(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as needed."""
    # Source: https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings 

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(fmt=' %(name)s :: %(levelname)-8s :: %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_city_state_county(zip_code, raw_data_path) -> str:
    """Returns a city, state-county values as a string

    Args:
        zip_code (_type_): int
        raw_data_path (_type_): string

    Returns:
        Returns a city, state-county values as a string
    """
    
    for location in transform_raw_zip_data(raw_data_path):
        for i in location:
            if i == zip_code:
                value = (location[1] + ', ' + location[2] + ' - ' + location[3])
    return value


def get_location_column(zip_code_list, raw_data_path) -> dict:
    """Returns a dict with a value == dict of key value pairs of zip codes and their city, state - county 

    Args:
        zip_code_list (_type_): list of zip codes
        raw_data_path (_type_): path to the raw data containing the zip codes and their assocaited city, state - county values. 

    Returns:
        dict: 'Location' is the key, with value == dict of key value pairs of zip codes and their city, state - county. 
    """
    zip_code_list = get_zip_code_list(raw_data_path)
    
    location_dict = {'Location': {}}

    for zip in zip_code_list:
        zip_location = get_city_state_county(zip, raw_data_path)
        temp_dict = {zip: zip_location}
        location_dict['Location'].update(temp_dict)

    return location_dict





export_zip_dataframe('IL', 'table_profile_id_list.txt', 'zip_code_data.txt', 2022)