import requests
import json
import os

def get_ipfs_data(ipfs_hash):
    url = f"https://ipfs.io/ipfs/{ipfs_hash}"
    global response  # Make response accessible to save_data_to_file
    response = requests.get(url)
    
    # Check if response was successful
    response.raise_for_status()
    
    # Check content type from headers
    content_type = response.headers.get('content-type', '')
    
    if 'application/json' in content_type:
        return response.json()
    elif 'image' in content_type:
        return response.content
    else:
        # Return raw text if not JSON or image
        return response.text

def save_data_to_file(data, ipfs_hash):
    # Create refractpass directory if it doesn't exist
    os.makedirs('refractpass', exist_ok=True)
    
    # Create a filename using the IPFS hash in the refractpass folder
    if isinstance(data, (dict, list)):
        # If data is JSON-serializable, save as .json
        filename = os.path.join('refractpass', f"{ipfs_hash}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    else:
        # For binary content (like images), save in binary mode
        filename = os.path.join('refractpass', f"{ipfs_hash}.png")
        with open(filename, 'wb') as f:
            f.write(response.content)
    return filename

def get_ipfs_hashes_from_folder(folder_url):
    """
    Fetches JSON metadata files from an IPFS folder and extracts image URLs.
    Returns a list of unique IPFS hashes for the images.
    """
    ipfs_hashes = set()
    
    try:
        # Fetch the directory listing from IPFS
        response = requests.get(folder_url)
        response.raise_for_status()
        
        # Parse the HTML content to find JSON file links
        content = response.text
        words = content.split()
        json_hashes = [word.split('/ipfs/')[-1].split('"')[0] for word in words 
                      if word.__contains__('filename') and word.__contains__('/ipfs/')]
        
        # Process each JSON file to extract image URLs
        for json_hash in json_hashes:
            try:
                metadata = get_ipfs_data(json_hash)
                print(metadata)
                
                if isinstance(metadata, dict) and 'image' in metadata:
                    # Check if name exists and contains a number > 1168
                    if 'name' in metadata:
                        try:
                            # Extract number from name (assuming format like "Name #1234")
                            name_num = int(''.join(filter(str.isdigit, metadata['name'])))
                            if name_num <= 1168:
                                continue  # Skip this entry if number is <= 1168
                        except ValueError:
                            print(f"Could not parse number from name: {metadata['name']}")
                            continue
                            
                    # Extract IPFS hash from the image URL
                    image_url = metadata['image']
                    print(image_url)
                    if 'ipfs' in image_url:
                        # Extract hash from ipfs:// or https://ipfs.io/ipfs/ format
                        image_hash = image_url.split('ipfs/')[-1].strip('/')
                        ipfs_hashes.add(image_hash)
                        print(f"Found image hash: {image_hash}")
            except Exception as e:
                print(f"Error processing metadata file {json_hash}: {e}")
                
    except Exception as e:
        print(f"Error fetching IPFS folder content: {e}")
    
    return list(ipfs_hashes)

def process_ipfs_hashes():
    try:
        with open('sanitized_ipfs_hashes.txt', 'r') as f:
            ipfs_hashes = f.read().splitlines()
            for ipfs_hash in ipfs_hashes:
                print(f"Processing {ipfs_hash}")
                result = get_ipfs_data(ipfs_hash)
                filename = save_data_to_file(result, ipfs_hash)
                print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error processing IPFS hashes: {e}")


""" ipfs_list = get_ipfs_hashes_from_folder("https://ipfs.io/ipfs/bafybeigyjkungku7rmber2tqkojsnromv723lbxieias5c737mxjymzj3e/")
with open('ipfs_list.txt', 'w') as f:
    for ipfs_hash in ipfs_list:
        f.write(f"{ipfs_hash}\n") """
process_ipfs_hashes()
