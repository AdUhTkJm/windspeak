# Note this application is designed for windows.
import os;
import subprocess;
import re;
import argparse;
import json;
import concurrent.futures as conf;

parser = argparse.ArgumentParser("builder")

parser.add_argument("-g", "--gdb", action="store_true", help="attach gdb")
parser.add_argument("-b", "--rebuild", action="store_true", help="rebuild even if no changes")
parser.add_argument("-r", "--run", action="store_true", help="run after build")
parser.add_argument("-p", "--precompile", action="store_true", help="use precompiled headers")

args = parser.parse_args()

# WARNING: This is ABSOLUTE PATH.
# To use precompiled header, change it to the correct path on your computer.
# This is only used if `--precompile` is specified.
SYSHEADER = \
  r"D:\Download\mingw64\lib\gcc\x86_64-w64-mingw32\13.2.0\include\c++\x86_64-w64-mingw32\bits\stdc++.h"
  
# Configuration
SUPPRESS_WARNINGS = []
suppress = ' '.join(f"-Wno-{x}" for x in SUPPRESS_WARNINGS)

INCLUDE_PATHS = [
  ".",
  "external/raylib/include"
]
include = ' '.join(f"-I{x}" for x in INCLUDE_PATHS)

LIB_PATHS = [
  "external/raylib/lib"
]
lib = ' '.join(f"-L{x}" for x in LIB_PATHS)
 
SRC_DIR = "src"
BUILD_DIR = "build"
EXECUTABLE = f"{BUILD_DIR}/windspeak"
STDCPP_PATH = f"{BUILD_DIR}/stdheader/stdcpp.pch"

precompile = f"-include {STDCPP_PATH}" if args.precompile else ""
CXX = "g++"
CXXFLAGS = f"-Wall -Wextra {suppress} -g -std=c++20 {include} {precompile}"

os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(f"{BUILD_DIR}/objects", exist_ok=True)

# All leaf folders and their content
sources: list[str] = []
for path, dirs, files in os.walk(SRC_DIR):
  sources.extend([os.path.join(path, f) for f in files])

file_amt = len(sources)
sources = [x for x in sources if x.endswith(".cpp") or x.endswith(".c")]

print(f"Found {file_amt} files, among which {len(sources)} are translation units.")

# Only compile changed files
recompile = False
object_files = []

header_regex = re.compile(r'#include "(.+)"')
cache_file = f"{BUILD_DIR}/includes_cache.json"

includes: dict[str, set[str]] = {}
timestamps: dict[str, float] = {}

# Load cache if available
if os.path.exists(cache_file):
  with open(cache_file, "r") as f:
    cache_data = json.load(f)
    includes = cache_data.get("includes", {})
    timestamps = cache_data.get("timestamps", {})

def get_mtime(file: str) -> float:
  return os.path.getmtime(file) if os.path.exists(file) else 0

include_changed = False

# Headers from external libraries.
const_headers = []
for folder in INCLUDE_PATHS:
  if folder == ".":
    continue; 
  
  for path, dirs, file in os.walk(folder):
    const_headers.extend(file)
    
const_headers = set(const_headers)
  
def find_include(file: str):
  global includes, timestamps, include_changed
  
  # Check cache validity
  current_mtime = get_mtime(file)
  if file in includes and timestamps.get(file, 0) >= current_mtime:
    return; 

  include_changed = True
  includes[file] = set()
  timestamps[file] = current_mtime  # Update modification time

  if not os.path.exists(file):  # Avoid errors for missing files
    return; 

  with open(file, "r") as f:
    for line in f:
      matches = header_regex.match(line)
      if matches:
        header = matches.groups()[0]
        if header in const_headers:
          continue; 
        
        if "/" not in header:
          header = os.path.join(os.path.dirname(file), header)

        if header not in includes[file]:
          includes[file].add(header)
          find_include(header)
          includes[file].update(includes.get(header, set()))

for file in sources:
  find_include(file)

if include_changed:
  with open(cache_file, "w") as f:
    # Sets are not serializable. Convert them to lists.
    includes = { k: list(v) for k, v in includes.items() }
    json.dump({"includes": includes, "timestamps": timestamps}, f, indent=2)

def compile_file(file: str):
  global recompile
  
  obj = os.path.join(BUILD_DIR, "objects", f"{os.path.basename(file)[:-4]}.o")
  if os.path.exists(obj):
    last_modif = os.path.getmtime(obj)
    
  if args.rebuild or not os.path.exists(obj) or \
  os.path.getmtime(file) > last_modif or \
  any(os.path.getmtime(header) > last_modif for header in includes[file]):
    recompile = True
    subprocess.run(f"{CXX} {CXXFLAGS} -c {file} -o {obj}", shell=True, check=True)
    
  return (obj, f"compiled {file}")

num_files = len(sources)
with conf.ThreadPoolExecutor() as executor:
  futures = [executor.submit(compile_file, file) for file in sources]
  for i, future in enumerate(conf.as_completed(futures)):
    obj, msg = future.result()
    object_files.append(obj)
    print(f"[{i+1}/{num_files}] {msg}".ljust(50), end="\r")

if args.precompile and not os.path.exists(STDCPP_PATH):
  subprocess.run(f"g++ -o {STDCPP_PATH} -std=c++20 -x c++-header {SYSHEADER}", shell=True, check=True)

if recompile or not os.path.exists(EXECUTABLE):
  print("\nLinking...")
  subprocess.run(
    f"{CXX} {CXXFLAGS} {lib} -o {EXECUTABLE} {' '.join(object_files)} -lraylib -lopengl32 -lgdi32 -lwinmm",
  shell=True, check=True)

linebreak = "\n" if not recompile else ""
print(f"{linebreak}Build complete.")

gdb = "gdb --args" if args.gdb else ""
if args.run:
  # Powershell only supports blackslashs to invoke executable.
  subprocess.run(f"{gdb} {os.path.relpath(EXECUTABLE)}.exe", shell=True)
