import json
import os
from hyperon import MeTTa

# ---------------------------
#  Load MeTTa Data
# ---------------------------
metta = MeTTa()

data_file_path = os.path.join(os.path.dirname(__file__), 'data.metta')
with open(data_file_path, 'r') as f:
    metta.run(f.read())

RELATIONS = ["Friend", "Colleague", "Family", "Neighbor", "Classmate"]

# ---------------------------
#  Build Query for Depth 1
# ---------------------------
def json_to_metta_query(data):
    """
    Convert a JSON query spec into a MeTTa query string.
    Always hardcodes depth to 1 in results.
    Uses composite patterns for matching.
    """

    # Accept JSON string or dict
    if isinstance(data, str):
        data = json.loads(data)

    subject = data["subject"]
    relation = data["relation"]
    attr_type = data["target_attribute"]["type"]
    attr_value = data["target_attribute"]["value"].strip().title()

    depth_value = 1  # Always fixed to 1

    # Build composite pattern
    if relation.lower() == "any":
        # Relation is not specified — match any relation with a variable $rel
        pattern = f"(, ($rel {subject} $p1) ({attr_type} $p1 {attr_value}))"
    else:
        # Single relation
        pattern = f"(, ({relation} {subject} $p1) ({attr_type} $p1 {attr_value}))"

    query = f"""! (match &self
    {pattern}
    ($p1 {depth_value})
)"""

    return query


# ---------------------------
#  Run Query
# ---------------------------
def find_by_json(json_input):
    """
    Accepts JSON string or dict, builds query, runs in MeTTa, returns raw result.
    """
    query_program = json_to_metta_query(json_input)
    print("\n--- MeTTa Query ---\n")
    print(query_program)
    print("\n--- End Query ---\n")
    raw = metta.run(query_program)
    print("Raw MeTTa output:", raw)
    return raw


# ---------------------------
#  Example Usage
# ---------------------------
if __name__ == "__main__":
    example_json = {
        "subject": "Alice",
        "relation": "any",  # can be "Friend", "Family", etc., or "any"
        "target_attribute": {"type": "Profession", "value": "nurse"},
        "max_depth": 1  # ignored
    }
    find_by_json(example_json)
