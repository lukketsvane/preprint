import os
import re

def search_files(directory, query):
    """
    Searches for the query in all files within the specified directory.
    
    Args:
    - directory (str): Path to the directory where the files are stored.
    - query (str): Search query.
    
    Returns:
    - list of str: List of matching lines from the files.
    """
    matching_lines = []

    # Iterate through every file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Check if it's a file
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                
                # Search for the query in each line of the file
                for line in lines:
                    if re.search(query, line, re.IGNORECASE):
                        matching_lines.append(line.strip())

    return matching_lines

