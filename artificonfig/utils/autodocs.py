import argparse
import subprocess


def main(path: str):
    """
    Autodoc tools: retrieve the project class and generate HTML docs

    Parameters
    ----------
    path : `str`
        Path of the project to be parsed.
    """

    # Read the README.md for index.html generation
    readme = open("readme.md")

    # Create the index file
    index = open("docs/index.rst", "w")

    # Create the header
    index_text = (
        ".. toctree::\n"
        "   :hidden:\n\n"
        "   Home page <self>\n"
        "   Jupyter tutorials <tutorials>\n"
        "   API reference <_autosummary/" + path + ">\n"
        "" + path.replace("_", " ").upper() + "\n"
        "============\n"
    )

    # Concatenate the readme text
    index_text += readme.read().replace("```shell", "```")

    # Flush the string on the text file
    index.write(index_text)

    # Close the files
    index.close()
    readme.close()

    # Make the html pages
    p = subprocess.Popen(["make", "html"], cwd="docs")
    p.wait()


parser = argparse.ArgumentParser()
parser.add_argument(
    "path",
    type=str,
    help="path of the folder to be parsed",
)
args = parser.parse_args()

if __name__ == "__main__":
    main(args.path)
