# parser.py (compact, attempts only allowed shapes)
import os, json
from dotenv import load_dotenv
import google.generativeai as genai
import inspect

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
if not KEY:
    raise RuntimeError("GEMINI_API_KEY missing")
genai.configure(api_key=KEY)

# try model object
try:
    MODEL = genai.GenerativeModel("gemini-1.5-flash")
    MODEL_IS_OBJ = True
except Exception:
    MODEL = "models/text-bison-001"
    MODEL_IS_OBJ = False

SCHEMA = ('Reply with ONLY one JSON object like: '
          '{"subject":<string|null>,"relation":"any"|"Friend"|"Colleague"|"Family"|"Neighbor"|"Classmate",'
          '"target_attribute":{"type":"Profession"|"Hobby","value":"<string>"},"max_depth":<int>}')

def _call(prompt):
    last = None
    # If model object exists, try positional/allowed shapes (no kwargs)
    if MODEL_IS_OBJ:
        try_calls = [
            ([{"type":"text","text":prompt}],),                     # single positional list
            (([{"content":[{"type":"text","text":prompt}]}],),),    # weird wrapper as positional
            (({"content":[{"type":"text","text":prompt}]},),),     # single dict positional
            ((prompt,),),                                         # raw prompt positional
        ]
        for args_tuple in ([ [{"type":"text","text":prompt}] ], [ {"content":[{"type":"text","text":prompt}]} ], [prompt] ):
            try:
                return MODEL.generate_content(*args_tuple)
            except Exception as e:
                last = e
                continue
        # try start_chat as last resort (positional)
        if hasattr(MODEL, "start_chat"):
            try:
                return MODEL.start_chat([{"author":"user","content":[{"type":"text","text":prompt}]}])
            except Exception as e:
                last = e
    # fallback to function API if present
    if hasattr(genai, "generate_text"):
        try:
            return genai.generate_text(model=MODEL, input=prompt)
        except Exception as e:
            last = e
    raise RuntimeError("All call shapes failed. Last error: " + (str(last) if last else "none"))

def _txt(resp):
    if hasattr(resp, "candidates") and resp.candidates:
        c = resp.candidates[0]
        content = getattr(c, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, (list, tuple)) and content:
            first = content[0]
            if isinstance(first, dict):
                return first.get("text") or first.get("content") or json.dumps(first)
            return getattr(first, "text", str(first))
    if hasattr(resp, "text"):
        return resp.text
    return str(resp)

def parse_question_to_json(q, assumed_subject=None):
    if not q or not q.strip():
        raise ValueError("Empty question")
    prompt = SCHEMA + "\n\nUser question: " + (f"(Assume subject: {assumed_subject}) " if assumed_subject else "") + q.strip()
    resp = _call(prompt)
    text = _txt(resp).strip()
    i, j = text.find("{"), text.rfind("}")
    if i == -1 or j == -1 or j <= i:
        raise ValueError("No JSON in model output:\n" + text)
    parsed = json.loads(text[i:j+1])
    parsed["subject"] = parsed.get("subject") or assumed_subject
    parsed["max_depth"] = max(1, min(5, int(parsed.get("max_depth", 1))))
    return parsed

if __name__ == "__main__":
    tests = [
        "Do I have Family who is a doctor in my network?",
        "Is there a nurse within 2 hops from me?"
    ]
    for q in tests:
        print("Q:", q)
        try:
            print(json.dumps(parse_question_to_json(q, assumed_subject="Alice"), indent=2))
        except Exception as e:
            print("Error:", e)
            # helpful debug: show generate_content signature if object exists
            if MODEL_IS_OBJ and hasattr(MODEL, "generate_content"):
                print("generate_content signature:", inspect.signature(MODEL.generate_content))
            if MODEL_IS_OBJ and hasattr(MODEL, "start_chat"):
                print("start_chat signature:", inspect.signature(MODEL.start_chat))
