#!/bin/bash
# Extract changelog from base_package.yml and format for RPM spec

if [ -z "$1" ]; then
    echo "Usage: $0 <base_package.yml>"
    exit 1
fi

YAML_FILE=$1

in_changelog=0
in_entries=0
version=""
author=""

while IFS= read -r line || [ -n "$line" ]; do
    # Detect start of changelog section
    if [[ "$line" =~ ^changelog: ]]; then
        in_changelog=1
        continue
    fi

    [ $in_changelog -eq 0 ] && continue

    # Detect end of changelog
    if [[ "$line" =~ ^[a-z_]+: ]] && [[ ! "$line" =~ ^changelog: ]]; then
        in_changelog=0
        continue
    fi

    # New version block
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*version:[[:space:]]*\"?([^\"]+)\"? ]]; then
        if [ -n "$version" ]; then
            echo ""
        fi
        version="${BASH_REMATCH[1]}"
        in_entries=0
        continue
    fi

    # Author
    if [[ "$line" =~ ^[[:space:]]*author:[[:space:]]*\"?([^\"]+)\"? ]]; then
        author="${BASH_REMATCH[1]}"
        continue
    fi

    # Date
    if [[ "$line" =~ ^[[:space:]]*date:[[:space:]]*(.+) ]]; then
        raw_date="${BASH_REMATCH[1]}"
        raw_date="${raw_date%\"}"
        raw_date="${raw_date#\"}"
        
        formatted_date=$(date -d "$raw_date" "+%a %b %d %Y" 2>/dev/null)
        [ -z "$formatted_date" ] && formatted_date="$raw_date"
        
        echo "* $formatted_date $author - $version-1"
        continue
    fi

    # Entries start
    if [[ "$line" =~ ^[[:space:]]*entries: ]]; then
        in_entries=1
        continue
    fi

    # Entry items
    if [ $in_entries -eq 1 ] && [[ "$line" =~ ^[[:space:]]+-[[:space:]]*\"?([^\"]+)\"? ]]; then
        entry_text="${BASH_REMATCH[1]}"
        echo "- $entry_text"
        continue
    fi

done < "$YAML_FILE"
