import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_files_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

SYSTEM_PROMPT = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan.
You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not
need to specify the working directory in your function calls as it is
automatically injected for security reasons.
"""
AVAILABLE_TOOLS = types.Tool(function_declarations=[
    schema_get_files_info,
    schema_get_files_content,
    schema_run_python_file,
    schema_write_file,
])
AVAILABLE_FUNCTIONS = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}


def main():
    parser = argparse.ArgumentParser("Boot.Dev AI")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(dest="prompt", nargs="+")
    args = parser.parse_args()
    prompt = " ".join(args.prompt)

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    for i in range(10):
        try:
            res = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT, tools=[AVAILABLE_TOOLS]))
            if res.candidates:
                for candidate in res.candidates:
                    messages.append(candidate.content)

            if args.verbose:
                print(
                    f"Prompt tokens: {res.usage_metadata.prompt_token_count}")
                print(
                    f"Response tokens: {res.usage_metadata.candidates_token_count}"
                )

            if not res.function_calls:
                print(f"Gemini: {res.text}")
                break

            function_responses = []
            for fn_part in res.function_calls:
                fn_res = call_function(fn_part, args.verbose)
                if not fn_res.parts or not fn_res.parts[0].function_response:
                    raise Exception("no function response")
                if args.verbose:
                    print(f"-> {fn_res}")
                function_responses.append(fn_res.parts[0])

            messages.append(
                types.Content(role="user", parts=function_responses))

        except Exception as e:
            print("Something went horribly wrong!", e)
            break


def call_function(fn_part, verbose=False):
    if verbose:
        print(f"Calling function: {fn_part.name}({fn_part.args})")
    else:
        print(f" - Calling function: {fn_part.name}")

    if fn_part.name not in AVAILABLE_FUNCTIONS:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=fn_part.name,
                    response={"error": f"Unknown function: {fn_part.name}"})
            ])

    args = dict(fn_part.args)
    args["working_directory"] = "./calculator"
    res = AVAILABLE_FUNCTIONS[fn_part.name](**args)

    return types.Content(role="tool",
                         parts=[
                             types.Part.from_function_response(
                                 name=fn_part.name, response={"result": res})
                         ])


if __name__ == "__main__":
    main()
