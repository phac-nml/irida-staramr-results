# IRIDA StarAMR Results

IRIDA StarAMR Results program enables StarAMR analysis results that were run through IRIDA to be downloaded into a spreadsheet using the command line. 

## Running from source code

1. __Clone the repository:__
   ```
   > git clone https://github.com/phac-nml/irida-staramr-results.git
   ```

2. __Install and build the Project__
   ```
   > cd irida-staramr-results
   > make
   > source .virtualenv/bin/activate
   ```
  

3. __Configuration for IRIDA REST API:__
   - You will need to create a client in IRIDA. Refer to [IRIDA client configuration](https://irida.corefacility.ca/documentation/user/administrator/#managing-system-clients) guide for more details.
   - You will need to create your own configuration file in YAML. Refer to [example-config.yml](example-config.yml) for more information on how to format the file.
    
        #### Config Fields:
    
        - `base-url`: The server URL to download results from. If you navigate to your instance of IRIDA in your web browser, the URL (after you’ve logged in) will often look like: https://irida.corefacility.ca/irida/. The URL you should enter into the Server URL field is that URL, with api/ at the end. So in the case of https://irida.corefacility.ca/irida/, you should enter the URL https://irida.corefacility.ca/irida/api/
        - `client-id`: The id from the IRIDA client you created
        - `client-secret`: The id from the IRIDA client you created


4. __Execute the program:__
    ```
    > irida-staramr-results -u <IRIDA_USERNAME> -pw <IRIDA_PASSWORD> -c <CONFIG_FILE_PATH> -p <PROJECT> -o <OUTPUT_FILE_NAME>.xlsx
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
