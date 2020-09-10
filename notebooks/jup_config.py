'''
patch for convenience of importing source code to notebooks.
Should be executed at the start of the notebook
In the future notebooks should be integrated with an appropriate package manner
'''
import os

with open('code_path.txt', 'r') as f:
    path = f.read()
    os.chdir(path)
