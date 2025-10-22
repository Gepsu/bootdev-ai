import os
from google.genai import types


def get_files_info(working_directory, directory="."):
    try:
        working_directory = os.path.abspath(working_directory)
        path = os.path.join(working_directory, directory)
        path = os.path.abspath(path)

        if not path.startswith(working_directory):
            return f"Error: Cannot list \"{directory}\" as it " + \
                    "is outside the permitted working directory"

        if not os.path.isdir(path):
            return f"Error: \"{directory}\" is not a directory"

        res = [f"Result for '{directory}' directory:"]
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path)
            res.append(f"- {file}: file_size={size} bytes, is_dir={is_dir}")
        return "\n".join(res)
    except Exception as e:
        return f"Error: {str(e)}"


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their " +
                "sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to " +
                            "the working directory. If not provided, lists " +
                            "files in the working directory itself.",
            ),
        },
    ),
)
