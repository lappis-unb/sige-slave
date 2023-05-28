#!/bin/bash

log_directory="logs" 

echo "Clean *.log -> $log_directory"
find "$log_directory" -name "*.log" -type f -exec truncate -s 0 {} \;

echo "Cleaning completed!"
