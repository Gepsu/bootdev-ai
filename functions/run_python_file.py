import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    try:
        working_directory = os.path.abspath(working_directory)
        file_path_abs = os.path.join(working_directory, file_path)
        file_path_abs = os.path.abspath(file_path_abs)

        if not file_path_abs.startswith(working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside ' + \
                    'the permitted working directory'

        if not os.path.exists(file_path_abs):
            return f'Error: File "{file_path}" not found.'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        final_args = ["uv", "run", file_path]
        final_args.extend(args)
        proc = subprocess.run(final_args,
                              timeout=30,
                              cwd=working_directory,
                              capture_output=True,
                              text=True)

        output = []
        if len(proc.stdout) > 0:
            output.append(f"STDOUT: {proc.stdout}")
        if len(proc.stderr) > 0:
            output.append(f"STDERR: {proc.stderr}")
        if proc.returncode != 0:
            output.append(f"Process exited with code {proc.returncode}")
        if len(output) == 0:
            output.append("No output produced.")
        return "\n".join(output)
    except Exception as e:
        return f"Error: executing Python file: {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a python file found in the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file that is executed on command." +
                            "The file must be a python file ending" +
                            "with '.py'.",
                ),
            "args": types.Schema(
                type=types.Type.OBJECT,
                description="Additional arguments that can be passed" +
                            "to the called python file in a list form." +
                            "These arguments are optional."
                ),
            },
        ),
    )
