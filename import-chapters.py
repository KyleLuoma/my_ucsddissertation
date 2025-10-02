import os
import re

# SPEAKQL_FILE = "./spql_2_research_survey/speakql-thesis-chapter.tex"
SPEAKQL_FILE = "./speakql-vldb-2022/UIST-2023/speakql-thesis-chapter.tex"
SNAILS_FILE = "./schemas-for-nl-paper/SNAILS-thesis-chapter.tex"
SKALPEL_FILE = "./skalpel-paper/schema-knowledge-focus.tex"

PROJECTS = ["SpeakQL", "SNAILS", "SKALPEL"]

project_files = {
    project: file for project, file in zip(PROJECTS, [SPEAKQL_FILE, SNAILS_FILE, SKALPEL_FILE])
}
project_end_sections = {
    "SpeakQL": "\\bibliographystyle",
    "SNAILS": "\\begin{acks",
    "SKALPEL": "\\bibliographystyle"
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
future_work = {}
conclusions = {}
all_commands = []
all_packages = set()
for project in project_files:

    with open(project_files[project]) as f:
        project_tex = f.read()

    # Extract future work
    future_work_section = project_tex.split("%BEGIN-FUTURE-WORK")[1].split("%END-FUTURE-WORK")[0]
    project_tex = project_tex.replace(future_work_section, "\n")
    if "}\n" in future_work_section:
        future_work_section = future_work_section.split("}\n")[1]
    future_work[project] = future_work_section
    
    # Extract conclusions
    if "%END-CONCLUSIONS" in project_tex:
        conclusions_section = project_tex.split("%BEGIN-CONCLUSIONS")[1].split("%END-CONCLUSIONS")[0]
        project_tex = project_tex.replace(conclusions_section, "\n")
        if "}\n" in conclusions_section:
            conclusions_section = conclusions_section.split("}\n")[1]
        conclusions[project] = conclusions_section
    else:
        conclusions[project] = ""

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
    related_work[project] = section_dict.pop("Related Work", None)

    with open(f"{project}-chapter.tex", "wt") as f:
        f.write("\n".join(["\\section{" + section + "}\n" + section_dict[section] for section in section_dict]))

    # Extract commands
    commands = project_tex.split("\n\\newcommand")[1:]
    commands = [extract_command("\\newcommand" + command) for command in commands if "vldb" not in command]
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


with open("future-work-chapter.tex", "wt") as f:
    f.write("\n".join([
        "\\section{Conclusions and Future Work for " + project + "}\n" + 
        "\\paragraph{\\textbf{Conclusions" + "}}\n" + conclusions[project] +
        "\\paragraph{\\textbf{Future Work" + "}}\n" + future_work[project]
        for project in future_work if future_work[project] is not None
    ]))


with open("related-work-chapter.tex", "wt") as f:
    f.write("\n".join([
        "\\section{Related Work for " + project + "}\n" + related_work[project]
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

