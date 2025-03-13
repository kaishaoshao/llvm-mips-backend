import lit.formats

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
(r'%filecheck', '~/llvm-project/build/bin/FileCheck'),
]

config.substitutions.extend(substitutions)
