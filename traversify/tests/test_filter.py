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

# filter
source = Traverser(data).filter(['source.0.annotations.source_name', 'source.0.annotations.topic', 'source.0.annotations.subtopic'])
print(source)

# extract list of subtree's and query using list comprehension, filter nation and year
data_list = [data.filter(['Year','Nation']) for data in Traverser(data).subTreeArray("data")]
print(data_list)

# extract list of subtree's and query using list comprehension, filter nation and year
data_list = [data.prune(['ID Nation','ID Year']) for data in Traverser(data).subTreeArray("data")]
print(data_list)