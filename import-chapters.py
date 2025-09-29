import os
import re

SPEAKQL_FILE = "./spql_2_research_survey/main.tex"
SNAILS_FILE = "./schemas-for-nl-paper/SNAILS-SIGMOD-2025 and TR.tex"
SKALPEL_FILE = "./skalpel-paper/schema-knowledge-focus.tex"

PROJECTS = ["speakql", "snails", "skalpel"]

project_files = {
    project: file for project, file in zip(PROJECTS, [SPEAKQL_FILE, SNAILS_FILE, SKALPEL_FILE])
}
project_end_sections = {
    "speakql": "\\bibliographystyle",
    "snails": "\\begin{acks",
    "skalpel": "\\bibliographystyle"
}

def extract_command(input_text) -> str:
    brace_count = 0
    if "\\newcommand" in input_text:
        command_name = input_text.split("{")[1].split("}")[0]
        input_text = "}".join(input_text.split("}")[1:])
    for ix, c in enumerate(input_text):
        if c == "{":
            brace_count += 1
        elif c == "}" and brace_count > 0:
            brace_count -= 1
        if c == "}" and brace_count == 0:
            return "\\newcommand{" + command_name + "}" + input_text[:ix + 1]
        

print(extract_command("""
\\newcommand{\\test}{\\foo{bar}}
"""))


related_work = {}
all_commands = []
all_packages = set()
for project in project_files:

    with open(project_files[project]) as f:
        project_tex = f.read()

    # Embed includes to avoid nested includes error
    includes = [incl.split("\n")[0][:-1] for incl in project_tex.split("\\include{") if "%" not in incl.split("\n")[0][:-1]]
    for include in includes:
        with open(os.path.dirname(project_files[project]) + "/" + include + ".tex") as f:
            incl_text = f.read()
            project_tex = project_tex.replace("\\include{" + include + "}", incl_text)

    # Extract sections
    project_tex = project_tex.split(project_end_sections[project])[0]
    sections = project_tex.split("\\section{")[1:]
    section_dict = {section.split("}")[0]: "}".join(section.split("}")[1:]) for section in sections}
    related_work[project] = section_dict.get("Related Work", None)

    with open(f"{project}-chapter.tex", "wt") as f:
        f.write("\n".join(["\\section{" + section + "}\n" + section_dict[section] for section in section_dict]))

    # Extract commands
    commands = project_tex.split("\n\\newcommand")
    commands = [extract_command("\\newcommand" + command) for command in commands]
    commands = [command for command in commands if command is not None and command not in all_commands]
    all_commands.extend(commands)

    with open(f"{project}-commands.tex", "wt") as f:
        f.write("\n".join(commands))

    # Extract packages
    proj_packages = [
        "\\usepackage" + package.split("\n")[0] for package in project_tex.split("\\usepackage")
        if "%" not in package.split("\n")[0]
        ]
    all_packages = all_packages.union(set(proj_packages))


with open("related-work-chapter.tex", "wt") as f:
    f.write("\n".join([
        "\\section{Related Work for " + project.capitalize() + "}\n" + related_work[project]
        for project in related_work if related_work[project] is not None
        ]))

with open("luoma-thesis-template.tex", "rt") as tf:
    template = tf.read()
    dissertation = template.replace("%__PACKAGES__%", "\n".join(all_packages))
    dissertation = dissertation.replace("%__CUSTOM_COMMANDS__%", "\n".join([
        "\\input{" + project + "-commands}" for project in project_end_sections.keys() 
        ]))

with open("luoma-thesis.tex", "wt") as tf:
    tf.write(dissertation)

