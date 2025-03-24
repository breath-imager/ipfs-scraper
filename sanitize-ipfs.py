import re

def sanitize_ipfs_urls(input_file):
    """
    Read IPFS URLs from a text file and remove everything but the hash starting with 'bafy'
    Args:
        input_file (str): Path to the input text file containing IPFS URLs (one per line)
    """
    sanitized_urls = []
    
    # Read URLs from input file
    with open(input_file, 'r') as f:
        urls = f.readlines()
    
    for url in urls:
        url = url.strip()  # Remove whitespace/newlines
        # Extract the hash from the URL
        hash = re.search(r'ipfs://([^/]+)', url)
        if hash:
            sanitized_urls.append(hash.group(1))
            
    with open('sanitized_ipfs_hashes.txt', 'w') as f:
        for hash in sanitized_urls:
            f.write(f"{hash}\n")

sanitize_ipfs_urls('ipfs_list.txt')