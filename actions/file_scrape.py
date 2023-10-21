import os
import re

def scrape_uploaded_files(uploaded_files_dir, regex_patterns):
    # Initialize an empty dictionary to store scrape results
    scrape_results = {}
    
    # Loop through each file in the uploaded files directory
    for filename in os.listdir(uploaded_files_dir):
        filepath = os.path.join(uploaded_files_dir, filename)
        scrape_results[filename] = []
        
        # Open the file and apply regex patterns
        with open(filepath, 'r') as file:
            file_content = file.read()
            for pattern in regex_patterns:
                matches = re.findall(pattern, file_content)
                if matches:
                    scrape_results[filename].extend(matches)
                    
    return scrape_results

# Example Usage
# Assuming the uploaded files are stored in a directory called 'uploaded_files'
# regex_patterns = [r'\\b(?:[a-zA-Z]\\w{2,})\\b', r'\\d{2,}']
# scrape_results = scrape_uploaded_files('uploaded_files', regex_patterns)
# print(scrape_results)
