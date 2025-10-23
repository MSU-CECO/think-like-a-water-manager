#!/usr/bin/env python3
"""
Small script to upload a JSON file to a Hugging Face repository.
"""

import os
from huggingface_hub import HfApi, login

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN")  
REPO_ID = "msu-ceco/dew-logiq"  
REPO_TYPE = "dataset"  

# File paths - map local files to repo paths with splits
FILES_TO_UPLOAD = [
    {
        "local_path": "./annotations/outputs_json/dew-logiq.json",
        "repo_path": "data/test.json",  
    },
    # {
    #     "local_path": "",
    #     "repo_path": "",
    # },
    # {
    #     "local_path": "",
    #     "repo_path": "",
    # },
]

def upload_json_to_hf():
    """Upload JSON files to a Hugging Face repository with splits."""
    
    # Authenticate
    if HF_TOKEN:
        login(token=HF_TOKEN)
    else:
        # This will prompt for token or use cached credentials
        login()
    
    # Initialize API
    api = HfApi()
    
    try:
        # Create the repository if it doesn't exist
        api.create_repo(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            exist_ok=True,  
            private=False  
        )
        
        # Upload each file
        for file_info in FILES_TO_UPLOAD:
            local_path = file_info["local_path"]
            repo_path = file_info["repo_path"]
            
            if not os.path.exists(local_path):
                print(f"Skipping {local_path} (file not found)")
                continue
            
            print(f"Uploading {local_path} -> {repo_path}...")
            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=repo_path,
                repo_id=REPO_ID,
                repo_type=REPO_TYPE,
                commit_message=f"Upload {repo_path}"
            )
            print(f"Uploaded {repo_path}")
        
        print(f"\nAll files uploaded to https://huggingface.co/datasets/{REPO_ID}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    upload_json_to_hf()