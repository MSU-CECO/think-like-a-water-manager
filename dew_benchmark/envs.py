import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ANNOTATION_DIR = os.path.join(BASE_DIR, "annotations")
ANNOTATION_YAML_DIR = os.path.join(ANNOTATION_DIR, "inputs_yaml")
ANNOTATION_CYAML_DIR = os.path.join(ANNOTATION_DIR, "copyrighted_yaml")
ANNOTATION_JSON_DIR = os.path.join(ANNOTATION_DIR, "outputs_json")
ANNOTATION_DEFINITIONS_DIR = os.path.join(ANNOTATION_DIR, "definitions_yaml")

DATA_DIR = os.path.join(BASE_DIR, "data")



PROBLEMS_BASENAME_INPUT  = "problems_definition.json"
DS_FINAL_BASENAME_OUTPUT = "dewpoint-math-ds.json"

PROBLEMS_FPATH_INPUT  = os.path.join(ANNOTATION_JSON_DIR, PROBLEMS_BASENAME_INPUT)
DS_FINAL_FPATH_OUTPUT = os.path.join(ANNOTATION_JSON_DIR, DS_FINAL_BASENAME_OUTPUT)


DEFAULT_CONFIG = {
    "output_file": DS_FINAL_FPATH_OUTPUT,
    "variations": 1,
    "neo4j_uri": "neo4j://localhost:7687",
    "neo4j_user": "neo4j",
    "neo4j_password": ""
}

DEFAULT_PROBLEM_DIFFICULTY_LEVEL = "medium"
DEFAULT_NUM_DECIMALS_TO_ROUND_TO = 2
DEFAULT_NUM_PROBLEMS_PER_TEMPLATE = 5

