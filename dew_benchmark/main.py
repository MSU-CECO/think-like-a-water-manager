import json
import sys
from pathlib import Path

from envs import DEFAULT_CONFIG, PROBLEMS_FPATH_INPUT

from data import ALL_EQUATIONS, ALL_TERMS

from utils.neo4j_manager import Neo4jManager
from utils.dataset_generator import DatasetGenerator
from utils.problem_loader import ProblemLoader
from utils.annotation_processor import AnnotationProcessor



def load_config(config_path):
    """Load configuration from a JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Config file '{config_path}' is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def is_yaml_folder(path):
    """Check if path is a folder containing YAML files"""
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return False
        
    # Check for YAML files in the directory
    yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
    return len(yaml_files) > 0


def process_input_problems(problems_path):
    """
    Process input problems which can be either a JSON file or a folder with YAML files.
    if it is the latter case, it creates an intermediary JSON output file saved at PROBLEMS_FPATH_INPUT.
    
    Args:
        problems_path: Path to JSON file or folder with YAML files
        
    Returns:
        List of problem templates
    """
    path = Path(problems_path)
    
    # Check if input is a folder containing YAML files
    if is_yaml_folder(path):
        print(f"Processing YAML files from folder: {path}")
        try:
            # Process YAML files into a single structure
            data = AnnotationProcessor.process_yaml_files(path, output_file=PROBLEMS_FPATH_INPUT)
            return ProblemLoader.load_from_json(data)
        except Exception as e:
            print(f"Error processing YAML files: {e}")
            sys.exit(1)
    
    # Otherwise treat as a JSON file
    elif path.exists() and path.is_file():
        print(f"Loading problem templates from JSON file: {path}")
        return ProblemLoader.load_from_json(path)
    
    else:
        print(f"Error: Input path '{problems_path}' is neither a valid JSON file nor a folder with YAML files.")
        sys.exit(1)


def make_json_serializable(data):
    """Recursively convert non-serializable objects in the dataset to strings."""
    if isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(v) for v in data]
    elif isinstance(data, (int, float, str)) or data is None:
        return data
    else:
        # Convert non-serializable objects (e.g., SymPy Mul) to strings
        return str(data)


def main():
    # Parse command line arguments for config file
    import argparse
    parser = argparse.ArgumentParser(description="Generate math problem dataset")
    parser.add_argument("--config", required=True, help="Path to configuration file (JSON)")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    problems_path = config.get("problems_path")
    if not problems_path:
        print("Error: 'problems_path' not specified in config file.")
        sys.exit(1)
        
    output_file = config.get("output_file", DEFAULT_CONFIG["output_file"])
    variations = config.get("variations", DEFAULT_CONFIG["variations"])
    
    # Neo4j connection settings
    neo4j_uri = config.get("neo4j_uri", DEFAULT_CONFIG["neo4j_uri"])
    neo4j_user = config.get("neo4j_user", DEFAULT_CONFIG["neo4j_user"])
    neo4j_password = config.get("neo4j_password", DEFAULT_CONFIG["neo4j_password"])
    
    if not neo4j_password:
        print("Warning: No Neo4j password provided in config. Using empty password.")
    
    # Initialize Neo4j manager
    neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
    
    
    # Build knowledge graph
    neo4j_manager.build_knowledge_graph(ALL_EQUATIONS, ALL_TERMS)
    
    # Load problem templates from JSON file or YAML directory
    templates = process_input_problems(problems_path)

    
    # Generate dataset
    dataset_generator = DatasetGenerator(neo4j_manager, ALL_EQUATIONS)
    dataset = dataset_generator.generate_dataset(templates, num_variations_per_template=variations)
    
    dataset = make_json_serializable(dataset)

    # Save dataset
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    # Clean up
    neo4j_manager.close()
    
    print(f"Created {len(dataset)} problem variations from {len(templates)} templates")
    print(f"Dataset saved to {output_file}")

if __name__ == "__main__":
    main()