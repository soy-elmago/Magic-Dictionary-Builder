#!/usr/bin/env python3
"""
Dictionary Builder for Bug Bounty & Pentesting
Generates custom wordlists from GAU and URLFinder results
"""

import subprocess
import argparse
import sys
from urllib.parse import urlparse
import os
from pathlib import Path

class DictionaryBuilder:
    def __init__(self, timeout=None):
        # Extensions to filter out (not include in dictionary)
        self.filtered_extensions = {
            'js', 'gif', 'jpg', 'jpeg', 'png', 'css', 'ttf', 'woff', 'woff2', 
            'svg', 'pdf', 'ico', 'webp', 'mp4', 'mp3', 'avi', 'mov', 'zip', 
            'rar', 'tar', 'gz', 'bz2', 'exe', 'dmg', 'iso', 'doc', 'docx', 
            'xls', 'xlsx', 'ppt', 'pptx', 'eot', 'swf'
        }
        self.timeout = timeout
        
    def run_gau(self, domain):
        """Execute GAU with subdomains"""
        print(f"[+] Running GAU for {domain}...")
        print(f"[*] This may take several minutes for large domains...")
        print(f"[*] Press Ctrl+C to interrupt if needed")
        try:
            cmd = ['gau', '--subs', domain]
            print(f"[*] Executing: {' '.join(cmd)}")
            
            # Use timeout if specified, otherwise no timeout
            kwargs = {'capture_output': True, 'text': True}
            if self.timeout:
                kwargs['timeout'] = self.timeout
                print(f"[*] Timeout set to {self.timeout} seconds")
            else:
                print(f"[*] No timeout - will wait for completion")
            
            result = subprocess.run(cmd, **kwargs)
            
            if result.returncode == 0:
                urls = [url.strip() for url in result.stdout.strip().split('\n') if url.strip()]
                print(f"[+] GAU completed! Found {len(urls)} URLs")
                return urls
            else:
                print(f"[-] GAU returned code {result.returncode}")
                if result.stderr:
                    print(f"[-] GAU stderr: {result.stderr}")
                return []
        except subprocess.TimeoutExpired:
            print(f"[-] GAU timeout after {self.timeout} seconds")
            return []
        except KeyboardInterrupt:
            print("\n[-] GAU interrupted by user")
            return []
        except FileNotFoundError:
            print("[-] GAU not found. Install with: go install github.com/lc/gau/v2/cmd/gau@latest")
            return []
        except Exception as e:
            print(f"[-] Unexpected error running GAU: {e}")
            return []
    
    def run_urlfinder(self, domain):
        """Execute URLFinder from Project Discovery"""
        print(f"[+] Running URLFinder for {domain}...")
        print(f"[*] This may take several minutes for large domains...")
        print(f"[*] Press Ctrl+C to interrupt if needed")
        try:
            # URLFinder command with domain and silent mode
            cmd = ['urlfinder', '-d', domain, '-silent']
            print(f"[*] Executing: {' '.join(cmd)}")
            
            # Use timeout if specified, otherwise no timeout
            kwargs = {'capture_output': True, 'text': True}
            if self.timeout:
                kwargs['timeout'] = self.timeout
                print(f"[*] Timeout set to {self.timeout} seconds")
            else:
                print(f"[*] No timeout - will wait for completion")
            
            result = subprocess.run(cmd, **kwargs)
            
            if result.returncode == 0:
                urls = [url.strip() for url in result.stdout.strip().split('\n') if url.strip()]
                print(f"[+] URLFinder completed! Found {len(urls)} URLs")
                return urls
            else:
                print(f"[-] URLFinder returned code {result.returncode}")
                if result.stderr:
                    print(f"[-] URLFinder stderr: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print(f"[-] URLFinder timeout after {self.timeout} seconds")
            return []
        except KeyboardInterrupt:
            print("\n[-] URLFinder interrupted by user")
            return []
        except FileNotFoundError:
            print("[-] URLFinder not found. Install with: go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest")
            return []
        except Exception as e:
            print(f"[-] Unexpected error running URLFinder: {e}")
            return []
    
    def extract_paths(self, urls):
        """Extract directories and files from URLs"""
        paths = set()
        
        for url in urls:
            if not url or not url.startswith(('http://', 'https://')):
                continue
                
            try:
                parsed = urlparse(url)
                path = parsed.path
                
                if not path or path == '/':
                    continue
                
                # Split path into parts
                path_parts = [part for part in path.split('/') if part]
                
                for part in path_parts:
                    if not part:
                        continue
                    
                    # If it's a file, check extension
                    if '.' in part:
                        extension = part.split('.')[-1].lower()
                        if extension not in self.filtered_extensions:
                            paths.add(part)
                    else:
                        # It's a directory
                        paths.add(part)
                
                # Also add partial paths (parent directories)
                current_path = ""
                for part in path_parts[:-1]:  # Exclude last part if it's a file
                    if part:
                        paths.add(part)
                        
            except Exception as e:
                print(f"[-] Error parsing URL {url}: {e}")
                continue
        
        return paths
    
    def save_dictionary(self, words, output_file):
        """Save the dictionary sorted and unique"""
        try:
            unique_words = sorted(set(words))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in unique_words:
                    f.write(f"{word}\n")
            
            print(f"[+] Dictionary saved to {output_file}")
            print(f"[+] Total unique words: {len(unique_words)}")
            
            return True
        except Exception as e:
            print(f"[-] Error saving file: {e}")
            return False
    
    def build_dictionary(self, domain, output_file, skip_gau=False, skip_urlfinder=False):
        """Main process to build the dictionary"""
        print(f"[+] Starting dictionary building for {domain}")
        print(f"[*] This may take several minutes for large domains...")
        
        if self.timeout:
            print(f"[*] Timeout set to {self.timeout} seconds per tool")
        else:
            print(f"[*] No timeout - tools will run until completion")
        
        gau_urls = []
        urlfinder_urls = []
        
        # Run tools
        if not skip_gau:
            print(f"\n[*] Step 1: Running GAU...")
            gau_urls = self.run_gau(domain)
        else:
            print(f"\n[*] Step 1: Skipping GAU")
        
        if not skip_urlfinder:
            step_num = 2 if not skip_gau else 1
            print(f"\n[*] Step {step_num}: Running URLFinder...")
            urlfinder_urls = self.run_urlfinder(domain)
        else:
            print(f"\n[*] Step 2: Skipping URLFinder")
        
        final_step = 3 if not skip_gau and not skip_urlfinder else 2
        print(f"\n[*] Step {final_step}: Processing results...")
        
        # Show individual results
        print(f"[*] GAU results: {len(gau_urls)} URLs")
        print(f"[*] URLFinder results: {len(urlfinder_urls)} URLs")
        
        # Combine results
        all_urls = list(set(gau_urls + urlfinder_urls))
        print(f"[+] Total unique URLs found: {len(all_urls)}")
        
        if not all_urls:
            print("[-] No URLs found.")
            print("[*] Possible causes:")
            print("    - Domain might be new or have limited web presence")
            print("    - Network connectivity issues")
            print("    - Tools not properly installed")
            print("    - Domain doesn't exist in archive sources")
            print("    - Try increasing timeout with -t flag")
            return False
        
        # Show sample URLs for debugging
        if all_urls and len(all_urls) > 0:
            print(f"[*] Sample URLs found:")
            for i, url in enumerate(all_urls[:5]):
                print(f"    {url}")
            if len(all_urls) > 5:
                print(f"    ... and {len(all_urls) - 5} more")
        
        # Extract paths
        paths = self.extract_paths(all_urls)
        print(f"[+] Paths extracted: {len(paths)}")
        
        if not paths:
            print("[-] No valid paths extracted from URLs")
            return False
        
        # Show sample paths
        sample_paths = sorted(list(paths))[:10]
        print(f"[*] Sample paths: {', '.join(sample_paths[:5])}")
        if len(sample_paths) > 5:
            print(f"    ... and {len(paths) - 5} more")
        
        # Save dictionary
        return self.save_dictionary(paths, output_file)

def main():
    parser = argparse.ArgumentParser(
        description="Custom dictionary generator for Bug Bounty and Pentesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 dictionary_builder.py -i example.com -o wordlist.txt
  python3 dictionary_builder.py --input target.com --output custom_dict.txt
  python3 dictionary_builder.py -i deere.com -o deere.txt -t 1800
  python3 dictionary_builder.py -i target.com -o gau_only.txt --no-urlfinder
  python3 dictionary_builder.py -i target.com -o url_only.txt --no-gau
  python3 dictionary_builder.py --test-tools

Requirements:
  - gau: go install github.com/lc/gau/v2/cmd/gau@latest
  - urlfinder: go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
        """
    )
    
    parser.add_argument('-i', '--input', 
                       help='Target domain (e.g., example.com)')
    parser.add_argument('-o', '--output', 
                       help='Output file for the dictionary')
    parser.add_argument('--test-tools', action='store_true',
                       help='Test if GAU and URLFinder are properly installed')
    parser.add_argument('-t', '--timeout', type=int,
                       help='Timeout in seconds for each tool (default: no timeout)')
    parser.add_argument('--no-gau', action='store_true',
                       help='Skip GAU and only use URLFinder')
    parser.add_argument('--no-urlfinder', action='store_true',
                       help='Skip URLFinder and only use GAU')
    
    args = parser.parse_args()
    
    # Test tools if requested
    if args.test_tools:
        test_tools()
        return
    
    # Validate required arguments
    if not args.input or not args.output:
        parser.error("Both -i/--input and -o/--output are required (unless using --test-tools)")
    
    # Validate domain
    domain = args.input.strip()
    if not domain:
        print("[-] Invalid domain")
        sys.exit(1)
    
    # Create instance and build dictionary
    builder = DictionaryBuilder(timeout=args.timeout)
    
    # Override tool selection if specified
    if args.no_gau and args.no_urlfinder:
        parser.error("Cannot skip both GAU and URLFinder")
    
    success = builder.build_dictionary(domain, args.output, 
                                     skip_gau=args.no_gau, 
                                     skip_urlfinder=args.no_urlfinder)
    
    if success:
        print(f"\n[+] Dictionary created successfully!")
        sys.exit(0)
    else:
        print(f"\n[-] Error creating dictionary")
        sys.exit(1)

def test_tools():
    """Test if required tools are installed and working"""
    print("[+] Testing required tools...")
    
    tools = [
        ('gau', ['gau', '--help']),
        ('urlfinder', ['urlfinder', '-h'])
    ]
    
    all_working = True
    
    for tool_name, cmd in tools:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"[+] {tool_name}: OK")
            else:
                print(f"[-] {tool_name}: Error (return code {result.returncode})")
                all_working = False
        except FileNotFoundError:
            print(f"[-] {tool_name}: Not found")
            all_working = False
        except subprocess.TimeoutExpired:
            print(f"[-] {tool_name}: Timeout")
            all_working = False
        except Exception as e:
            print(f"[-] {tool_name}: Error - {e}")
            all_working = False
    
    if all_working:
        print("\n[+] All tools are working correctly!")
    else:
        print("\n[-] Some tools need to be installed or fixed")
        print("\nInstallation commands:")
        print("go install github.com/lc/gau/v2/cmd/gau@latest")
        print("go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest")

if __name__ == "__main__":
    main()
