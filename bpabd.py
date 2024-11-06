import aiohttp
import asyncio
import time
from urllib.parse import urlparse, urlunparse
import argparse

# Load the wordlist from a file
def load_wordlist(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

# Generate URLs by inserting words from the wordlist into different positions
def generate_urls(base_url, wordlist):
    parsed_url = urlparse(base_url)
    base_path_parts = parsed_url.path.strip('/').split('/')
    
    urls = []
    for word in wordlist:
        for i in range(len(base_path_parts) + 1):
            new_path_parts = base_path_parts[:i] + [word] + base_path_parts[i:]
            new_path = '/' + '/'.join(new_path_parts)
            new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, new_path, '', '', ''))
            urls.append(new_url)
    
    return urls

# Fuzz the generated URLs asynchronously
async def fuzz_url(session, original_response, url, original_length):
    try:
        start_time = time.time()
        async with session.get(url) as response:
            response_text = await response.text()
            response_length = len(response_text)
            response_time = time.time() - start_time
            
            # Skip 404 status codes
            if response.status == 404:
                return None
            
            return {
                'url': url,
                'status_code': response.status,
                'length_diff': response_length - original_length,
                'time_diff': response_time
            }
    except Exception as e:
        print(f"Error with URL {url}: {e}")
    return None

async def fuzz_urls(original_url, urls, status_codes):
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        async with session.get(original_url) as original_response:
            original_text = await original_response.text()
            original_length = len(original_text)
            
            tasks = [fuzz_url(session, original_response, url, original_length) for url in urls]
            results = await asyncio.gather(*tasks)

    # Filter results based on status codes if specified
    return [result for result in results if result and (result['status_code'] in status_codes)]

# Main function to run the fuzzing tool
def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='URL Fuzzing Tool')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('-u', '--url', required=True, help='Target URL to fuzz')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-mc', '--status-codes', type=str, default='200', help='Comma-separated list of status codes to include in results')

    # Parse the arguments
    args = parser.parse_args()

    # Load the wordlist and target URL
    wordlist = load_wordlist(args.wordlist)
    target_url = args.url
    
    # Generate URLs and fuzz them
    urls_to_fuzz = generate_urls(target_url, wordlist)
    
    # Parse status codes from the input
    status_codes = set(map(int, args.status_codes.split(',')))
    
    results = asyncio.run(fuzz_urls(target_url, urls_to_fuzz, status_codes))
    
    # Prepare output lines
    output_lines = []
    for result in results:
        output_lines.append(f"URL: {result['url']}")
        output_lines.append(f"Status Code: {result['status_code']}")
        output_lines.append(f"Length Difference: {result['length_diff']}")
        output_lines.append('--------------------')

    # Print results to the console
    print("\n".join(output_lines))

    # Output results to a file if specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write("\n".join(output_lines))

if __name__ == "__main__":
    main()
