import csv
import subprocess
import sys
import os
import argparse
from graphviz import Digraph

# Новый метод для рендеринга графа
def render_mermaid_to_png(mermaid_code, output_path):
    # Создание Graphviz графа
    dot = Digraph(format='png')

    # Извлечение связей из Mermaid-кода
    lines = mermaid_code.split("\\n")[1:]  # Пропустить первую строку "graph TD"
    for line in lines:
        if "-->" in line:
            src, dst = line.split("-->")
            dot.edge(src.strip(), dst.strip())

    # Сохранение графа
    png_output_path = output_path
    dot.render(filename=png_output_path, cleanup=True)
    print(f"PNG graph successfully created at {png_output_path}.png")

def parse_config(config_path):
    with open(config_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        config = next(reader)
        graphviz_path, repo_path, output_path, target_file = config
        graphviz_path = graphviz_path.strip('"')
        repo_path = repo_path.strip('"')
        output_path = output_path.strip('"')
        target_file = target_file.strip('"')
        return graphviz_path, repo_path, output_path, target_file

def get_commits(repo_path, target_file):
    cmd = ["git", "-C", repo_path, "log", "--pretty=%H", "--", target_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error getting commits: {result.stderr}")
        sys.exit(1)
    commits = result.stdout.strip().splitlines()
    print(f"Commits found for file {target_file}: {commits}")  # Отладочный вывод
    return commits[::-1]  # reverse to chronological order

def get_commit_parents(repo_path, commit):
    cmd = ["git", "-C", repo_path, "rev-list", "--parents", "-n", "1", commit]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error getting parents: {result.stderr}")
        sys.exit(1)
    parents = result.stdout.strip().split()
    return parents[1:] if len(parents) > 1 else []

def generate_mermaid_code(commits, repo_path):
    lines = ["graph TD"]
    for commit in commits:
        parents = get_commit_parents(repo_path, commit)
        print(f"Commit: {commit[:7]}, Parents: {[p[:7] for p in parents]}")  # Отладочный вывод
        for parent in parents:
            lines.append(f"{parent[:7]} --> {commit[:7]}")
    mermaid_code = "\\n".join(lines)
    print(f"Generated Mermaid code:\n{mermaid_code}")  # Отладочный вывод
    return mermaid_code #return "\\n".join(lines)

def output_result(mermaid_code, output_path):
    with open(output_path.replace(".png", ".md"), "w") as file:
        file.write("```mermaid\\n" + mermaid_code + "\\n```")
    print(f"Dependency graph successfully saved at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Command-line tool for visualizing commit dependencies in a git repo.")
    parser.add_argument("graphviz_path", type=str, help="Path to graphviz.")
    parser.add_argument("repo_path", type=str, help="Path to the git repository.")
    parser.add_argument("output_path", type=str, help="Output path for the dependency graph image.")
    parser.add_argument("target_file", type=str, help="Name of the file to track dependencies for.")
    args = parser.parse_args()

    graphviz_path, repo_path, output_path, target_file = args.graphviz_path, args.repo_path, args.output_path, args.target_file
    commits = get_commits(repo_path, target_file)
    if not commits:
        print(f"No commits found for file {target_file}.")
        return
    mermaid_code = generate_mermaid_code(commits, repo_path)
    output_result(mermaid_code, output_path)

    # Рендеринг в PNG
    render_mermaid_to_png(mermaid_code, output_path.replace(".png", ""))

if __name__ == "__main__":
    main()
