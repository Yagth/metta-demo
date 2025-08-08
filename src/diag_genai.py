# diag_genai.py
import importlib
import inspect
import sys
import google.generativeai as genai

print("Python executable:", sys.executable)
# Try to get installed distribution/version
try:
    # Python >=3.8
    from importlib.metadata import version, PackageNotFoundError
    try:
        v = version("google-generativeai")
    except PackageNotFoundError:
        try:
            v = version("google-generativeai")  # double-check name
        except PackageNotFoundError:
            v = "package not found via importlib.metadata"
except Exception as e:
    v = f"could not determine version: {e}"

print("google-generativeai version:", v)
print("\n--- top-level genai attributes ---")
attrs = [a for a in dir(genai) if not a.startswith("_")]
print(attrs)
print("\n--- which helpers exist ---")
for name in ("configure", "generate_text", "generate", "chat", "GenerativeModel", "create"):
    print(f"{name}: {hasattr(genai, name)}")

# If GenerativeModel exists, inspect its callables
if hasattr(genai, "GenerativeModel"):
    gm = genai.GenerativeModel
    print("\nGenerativeModel is available; its attrs (first 50):")
    print([a for a in dir(gm) if not a.startswith("_")][:50])

# Print signatures for common functions if present
def print_sig(obj_name):
    try:
        obj = getattr(genai, obj_name)
        print(f"\nSignature for genai.{obj_name}:")
        try:
            print(inspect.signature(obj))
        except Exception:
            print("  (could not get signature)")
    except AttributeError:
        pass

for n in ("generate_text", "generate", "chat", "create"):
    print_sig(n)

print("\n--- quick existence check complete ---")
