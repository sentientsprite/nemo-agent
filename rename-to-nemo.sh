#!/bin/bash
# Rename all NEMO references to NEMO

echo "Renaming NEMO to NEMO..."

# Find and replace in all files
find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    if [ -f "$file" ]; then
        # Replace text content
        sed -i '' 's/nemo/nemo/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO/NEMO/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO/NEMO/g' "$file" 2>/dev/null || true
        sed -i '' 's/nemo-agent/nemo-agent/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO-Agent/NEMO-Agent/g' "$file" 2>/dev/null || true
        sed -i '' 's/nemo-agent/nemo-agent/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO-Agent/NEMO-Agent/g' "$file" 2>/dev/null || true
        sed -i '' 's/nemo/nemo/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO/NEMO/g' "$file" 2>/dev/null || true
        sed -i '' 's/nemo/nemo/g' "$file" 2>/dev/null || true
        sed -i '' 's/NEMO/NEMO/g' "$file" 2>/dev/null || true
    fi
done

# Rename directories
find . -depth -type d -not -path "./.git/*" -not -path "./node_modules/*" | while read dir; do
    newdir=$(echo "$dir" | sed 's/nemo/nemo/g' | sed 's/nemo/nemo/g' | sed 's/nemo/nemo/g')
    if [ "$dir" != "$newdir" ]; then
        mv "$dir" "$newdir" 2>/dev/null || true
    fi
done

# Rename files
find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | while read file; do
    newfile=$(echo "$file" | sed 's/nemo/nemo/g' | sed 's/nemo/nemo/g' | sed 's/nemo/nemo/g')
    if [ "$file" != "$newfile" ]; then
        mv "$file" "$newfile" 2>/dev/null || true
    fi
done

echo "Rename complete!"
