import yaml
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Union

class AnnotationProcessor:
    """
    Process multiple YAML annotation files and combine them into a single JSON output.
    """
    
    @staticmethod
    def process_yaml_files(yaml_dir: Union[str, Path], output_file: Union[str, Path, None] = None) -> Dict[str, Any]:
        """
        Process all YAML files in a directory and combine them into a single structure.
        
        Args:
            yaml_dir: Directory containing YAML annotation files
            output_file: Optional path to save the JSON output file
            
        Returns:
            Combined data structure from all YAML files
        
        Raises:
            FileNotFoundError: If the directory doesn't exist
            ValueError: If no YAML files found in the directory
        """
        yaml_dir = Path(yaml_dir)
        
        if not yaml_dir.exists() or not yaml_dir.is_dir():
            raise FileNotFoundError(f"Directory not found: {yaml_dir}")
        
        yaml_files = list(yaml_dir.glob("*.yaml")) + list(yaml_dir.glob("*.yml"))
        
        if len(yaml_files) == 0:
            raise ValueError(f"No YAML files found in directory: {yaml_dir}")
        
        all_problems = []
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as file:
                    data = yaml.safe_load(file)
                    if data:  
                        all_problems.append(data[0])
                        print(f"\tProcessed: {yaml_file.name}")
            except Exception as e:
                print(f"Error processing {yaml_file.name}: {e}", file=sys.stderr)
        
        if not all_problems:
            raise ValueError("No valid data found in any YAML files")
        
        final_data = {"problems": all_problems}
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w') as file:
                json.dump(final_data, file, indent=2)
            print(f"Combined all YAML files into a JSON output saved at: {output_path}")
        
        return final_data

def main():
    """Command-line entry point"""
    parser = argparse.ArgumentParser(description="Process YAML annotation files into a single JSON structure")
    parser.add_argument("yaml_dir", help="Directory containing YAML annotation files")
    parser.add_argument("--output", "-o", default="problems.json", 
                        help="Output JSON file path (default: problems.json)")
    
    args = parser.parse_args()
    
    try:
        AnnotationProcessor.process_yaml_files(args.yaml_dir, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()