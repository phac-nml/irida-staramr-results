# IRIDA StarAMR Results

IRIDA StarAMR Results program enables StarAMR analysis results that were run through IRIDA to be batch downloaded into a collection of spreadsheets using the command line. 

# How to use:

- Assuming you have already installed the program, you can use `irida-staramr-results` command.

   ### Examples
   ```
   $ irida-staramr-results --help
   ```
   ```
   $ irida-staramr-results -u admin -pw password1 -c /path/to/conf.yml -p 1 -o out -fd 2021-01-02 -td 2021-04-31
   ```
- There a few arguments it accepts:

   ## Arguments

   #### Required:

   | Name | Shortcut | Type | Example | Description |
   |------|----------|------|---------|-------------|
   |`--project`|`-p`| `int` | 1 |Project(s) to scan for StarAMR results.|
   |`--config`|`-c`| `string` | /path/to/conf.yml |Path to a configuration file. [See configuration details here.](#Configuration-for-IRIDA-REST-API)|

   #### Optional:

   | Name | Shortcut | Type | Example | Description |
   |------|----------|------|---------|-------------|
   |`--help`|`-h`|N/A|N/A|Show help message.|
   |`--version`|`-v`|N/A|N/A|The current version of irida-staramr-results.|
   |`--split_results`|`-sr`|N/A|N/A|Export each analysis results into separate output files resulting to one `.xlsx` file per analysis.|
   |`--username`|`-u`| `string` | admin |This is your IRIDA account username.|
   |`--password`|`-pw`| `string` | password1 |This is your IRIDA account password.|
   |`--output`|`-o`| `string` | out |The name of the output excel file.|
   |`--from_date`|`-fd`|`string`|2021-01-03|Download only results of the analysis that were created **from** this date.*|
   |`--to_date`|`-td`|`string`|2021-04-01|Download only results of the analysis that were created **to** this date.*|

   __Notes:__ 
   - \* Dates are formatted as `YYYY-mm-dd` (eg. 2021-04-08) and include hours from 00:00:00 to 23:59:59 of the inputted date.

# Setup
### Python
   IRIDA StarAMR Results requires **Python version 3.8 or later**. Check the Python version you are using with:
   ```
   $ python --version
   ```

### Configuration for IRIDA REST API

- You will need to have a client instance in IRIDA.
  - Only IRIDA administrators can create client instances. Users should contact their IRIDA admin for client credentials.
  - Refer to [IRIDA client configuration](https://irida.corefacility.ca/documentation/user/administrator/#managing-system-clients) guide for more details.
- You will need to create your own configuration file in YAML. Here is an [example](./example-config.yml).

  #### Fields:

  - `base-url`: The server URL to download results from. If you navigate to your instance of IRIDA in your web browser, the URL (after you’ve logged in) will often look like: https://irida.corefacility.ca/irida/. The URL you should enter into the Server URL field is that URL, with api/ at the end. So in the case of https://irida.corefacility.ca/irida/, you should enter the URL https://irida.corefacility.ca/irida/api/
  - `client-id`: The id from the IRIDA client you created
  - `client-secret`: The id from the IRIDA client you created


# Installing from source code
The following instructions describe how to install and execute IRIDA StarAMR Results from repository.

1. __Clone the repository:__
   ```
   $ git clone https://github.com/phac-nml/irida-staramr-results.git
   ```

2. __Install and build the project__
   ```
   $ cd irida-staramr-results
   $ make
   $ source .virtualenv/bin/activate
   ```

3. __Execute the program:__ See [argument chart](#Arguments) above for what these arguments means. 
    ```
    $ irida-staramr-results -u <IRIDA_USERNAME> -pw <IRIDA_PASSWORD> -c <CONFIG_FILE_PATH> -p <PROJECT> -o <OUTPUT_FILE_NAME> -fd <FROM_DATE> -td <TO_DATE>
    ```


# Running Tests
### Unit test
1. Running the unit tests can be done with the command:
    ```
    $ make unittests
    ```


## Legal

Copyright Government of Canada 2021

Written by: National Microbiology Laboratory, Public Health Agency of Canada

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


## Contact

**Gary van Domselaar**: gary.vandomselaar@phac-aspc.gc.ca
