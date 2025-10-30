#!/bin/bash

# Get the directory from which the script was called
project_dir="$(pwd)"

# Create overlay directory inside the project folder
mkdir -p "$project_dir/overlay"

# Find .bit and .hwh files in the project folder
bitfile=$(find "$project_dir" -name "*.bit" | grep "impl_1" | sort | tail -n 1)

# Handle missing .bit file
if [ -z "$bitfile" ]; then
  echo "❌ No .bit file found in $project_dir. Make sure synthesis and implementation are complete."
  exit 1
fi

# Find corresponding .hwh file.  If the .bit file is named <name>_wrapper.bit, 
# look for <name>.hwh
bitbase=$(basename "$bitfile" .bit | sed 's/_wrapper$//')
hwhfile=$(find "$project_dir" -name "${bitbase}.hwh" | head -n 1)

# Handle missing .hwh file
if [ -z "$hwhfile" ]; then
  echo "❌ No .hwh file found in $project_dir. Make sure synthesis and implementation are complete."
  exit 1
fi

# Match .tcl file in same directory as .bit
bitdir=$(dirname "$bitfile")
tclfile=$(find "$bitdir" -name "*.tcl" | head -n 1)

# Handle missing .tcl file
if [ -z "$tclfile" ]; then
  echo "❌ No .tcl file found in $bitdir. Make sure synthesis and implementation are complete."
  exit 1
fi

# Derive base name
base=$(basename "$project_dir")

# Copy and rename
cp "$bitfile" "$project_dir/overlay/${base}.bit"
cp "$hwhfile" "$project_dir/overlay/${base}.hwh"
cp "$tclfile" "$project_dir/overlay/${base}.tcl"

echo "Overlay files copied to: $project_dir/overlay/"
echo "  ${base}.bit"
echo "  ${base}.hwh"
echo "  ${base}.tcl"