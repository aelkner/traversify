import requests
import sys
from pathlib import Path

# Get the parent directory of the test script
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.append(str(parent_dir))
from traverser import Traverser

data = requests.get("https://datausa.io/api/data?drilldowns=Nation&measures=Population").json()
print(data)

# extract subtree of sources
source = Traverser(data).subTree('source.0.annotations')
print(source)

#extract list of subtree's 
data_list = Traverser(data).subTreeArray("data")
print(data_list[0])

# extract list of subtree's and query using list comprehension
data_list = [data for data in Traverser(data).subTreeArray("data") if data.Year == "2020"]
print(data_list)