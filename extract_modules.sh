#!/bin/bash

# This script extracts dkms_modules from base_package.yml using shyaml
# and outputs them in a format that can be interpreted as a shell array.

if [ $# -lt 1 ]; then
    echo "Usage: $0 <yaml_file>" >&2
    exit 1
fi

YAML_FILE="$1"

if [ ! -f "$YAML_FILE" ]; then
    echo "Error: $YAML_FILE not found." >&2
    exit 1
fi

if ! command -v shyaml &> /dev/null; then
    echo "Error: shyaml is not installed." >&2
    exit 1
fi

# We use shyaml get-values to iterate over the dkms_modules list.
# Each entry is itself a list.
# shyaml get-values dkms_modules will output each entry separated by \0 if we use -0
# but let's try a more robust approach if -0 is not available.

# The requirement is to output something that another script can interpret as an array.
# e.g., ( "entry1" "entry2" ... )

echo -n "ARRAY=("
index=0
while true; do
    # Try to get the module name (first element of the N-th entry)
    module=$(shyaml get-value dkms_modules.$index.0 < "$YAML_FILE" 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$module" ]; then
        break
    fi

    # Try to get the prefix (third element of the N-th entry)
    prefix=$(shyaml get-value dkms_modules.$index.2 < "$YAML_FILE" 2>/dev/null)
    
    # Construct the entry
    if [ -n "$prefix" ]; then
        # Remove trailing slash from prefix if it exists
        prefix_clean=${prefix%/}
        entry="$prefix_clean/$module"
    else
        entry="$module"
    fi

    echo -n " \"$entry\""
    
    index=$((index + 1))
done

echo " )"
