import lit.formats
from dotenv import load_dotenv
import os

env_filepath = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
print("env_filepath: ", env_filepath)
res = load_dotenv(dotenv_path=env_filepath)
if not res:
    print("Error loading .env file")    
    sys.exit(1)
FILECHECK_PATH = os.environ.get("FILECHECK_PATH")

config.name = 'SnippetParser'
config.test_format = lit.formats.ShTest(True)

config.suffixes = ['.cpp', '.h']
config.test_source_root = os.path.dirname(__file__)
# config.test_exec_root = 
# go to ../build for test_exec_root
build_dir = os.path.join(config.test_source_root, '..', '..', 'build')
config.test_exec_root = build_dir

substitutions = [
('%parser',
    'python3 ' + os.path.join(config.test_source_root, '..', 'main.py')
),
(r'%filecheck', FILECHECK_PATH),
]

config.substitutions.extend(substitutions)
