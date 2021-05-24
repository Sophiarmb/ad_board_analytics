#!/bin/bash

# This script will find every file with a `*.py` extention recursively
# starting in the current working directory.  It then executes PyLint
# in turn on each file.

python_file_list=(`find $directory -type f -name \*.py`)
for python_file in "${python_file_list[@]}"
do
    :
    echo ${python_file}
    pylint ${python_file}
done



