import gradio as gr
import json
from src.text_to_json_parser import parse_question_to_json, _call, _txt
from src.utils import find_by_json


def normalize_results(raw_results, force_depth=1):
    """
    Convert MeTTa raw results into a list of (name, depth) tuples.
    Handles multiple matches per row and can hardcode depth.
    """
    parsed = []
    for row in raw_results:
        if not row:
            continue
        for expr in row:  # iterate over all matches in this row
            if isinstance(expr, tuple) and len(expr) == 2:
                name, depth = expr
            else:
                parts = str(expr).strip("()").split()
                if len(parts) >= 1:
                    name = parts[0]
                    depth = parts[1] if len(parts) > 1 else force_depth
                else:
                    continue
            if force_depth is not None:
                depth = force_depth
            parsed.append((name, depth))
    return parsed

# --- Chat Function ---
def chat_with_rag(question):
    if not question.strip():
        return "Please enter a question.", ""
    
    # Step 1: Parse into JSON query
    try:
        parsed_query = parse_question_to_json(question, assumed_subject="Alice")
    except Exception as e:
        return f"Error parsing question: {e}", ""
    
    # Step 2: Run search
    raw_results = find_by_json(parsed_query)

    # Step 3: Normalize results and build context
    results = normalize_results(raw_results, force_depth=1)
    if not results:
        context = "No matching people found in the network."
    else:
        context_lines = [f"- {name} (found at depth {depth})" for name, depth in results]
        context = "\n".join(context_lines)

    # Step 4: Ask LLM to generate friendly answer
    llm_prompt = f"""
You are a helpful assistant.
User asked: "{question}"
Structured query: {json.dumps(parsed_query, indent=2)}

Here is the search result from the database:
{context}

Example: Query Result: ((() (Friend Alice Bob 2)) (Colleague Bob Carol 1)), (() (Friend Alice Carol 2))
         Interpretation: Carol , who is a colleague of Bob who is a friend of Alice plays Chess.

Please provide a concise, user-friendly answer.
If there are multiple people, list them in order of depth (closer first).
Optionally mention the search depth in your answer.
If no results, politely say that none were found. If you found unique friends, mention their name and the relation with Alice as the example provided above.
    """.strip()

    try:
        llm_resp = _call(llm_prompt)
        answer_text = _txt(llm_resp).strip()
    except Exception as e:
        answer_text = f"Error generating answer: {e}"
    
    # Step 5: Sources info
    sources_info = f"Query JSON:\n{json.dumps(parsed_query, indent=2)}"
    if results:
        sources_info += "\n\nMatches:\n" + context

    return answer_text, sources_info

# --- Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Relationship Network Search")
    gr.Markdown("Ask a question about Alice's network and get AI-generated answers with the matching search results.")

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Enter your question",
                placeholder="e.g., Who in Alice's network is a nurse?",
                lines=2
            )
            submit_btn = gr.Button("Ask")
            clear_btn = gr.Button("Clear")

        with gr.Column(scale=5):
            answer_output = gr.Textbox(label="AI Answer", lines=6)
            sources_output = gr.Textbox(label="Sources Used", lines=12)

    # Button actions
    submit_btn.click(
        fn=chat_with_rag,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )

    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=[],
        outputs=[answer_output, sources_output]
    )
    clear_btn.click(
        fn=lambda: "",
        inputs=[],
        outputs=question_input
    )

# --- Launch App ---
if __name__ == "__main__":
    demo.launch()


# "Do I have someone who is a doctor in my network?",
#         "Is there a nurse within 2 hops from me?",
#         "Who in my connections is a scientist? Max depth 3.",
#         "Find classmates who have the hobby 'Chess' up to depth 2."
