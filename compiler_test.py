#!/usr/bin/env python

import json
import random

class Node:
    def __init__(self, name, parent=None, content=""):
        self.name = name
        self.parent = parent
        self.children = []
        self.content = content
        self.attributes = {}

    def add_child(self, child):
        self.children.append(child)

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def render(self, dsl_mapping):
        element_mapping = dsl_mapping.get(self.name, "")
        if not element_mapping:
            return self.name  # Return the name if no mapping is found

        result = element_mapping

        for key, value in self.attributes.items():
            result = result.replace(f"${key}", value)

        child_content = "".join(child.render(dsl_mapping) for child in self.children)
        result = result.replace("{}", child_content)

        return result

class Compiler:
    def __init__(self, dsl_mapping_file_path):
        with open(dsl_mapping_file_path) as data_file:
            self.dsl_mapping = json.load(data_file)

        self.opening_tag = self.dsl_mapping["opening-tag"]
        self.closing_tag = self.dsl_mapping["closing-tag"]

    def compile(self, input_dsl, output_file_path):
        root = self.parse_dsl(input_dsl)
        html_content = root.render(self.dsl_mapping)
        
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
{html_content}
</body>
</html>
        """
        
        with open(output_file_path, 'w') as output_file:
            output_file.write(full_html)

    def parse_dsl(self, input_dsl):
        lines = input_dsl.split('\n')
        root = Node("root")
        stack = [root]

        for line in lines:
            # line = line.strip()
            if not line:
                continue

            if line.startswith(self.opening_tag):
                name = line[len(self.opening_tag):].strip()
                node = Node(name, stack[-1])
                stack[-1].add_child(node)
                stack.append(node)
            elif line == self.closing_tag:
                stack.pop()
            else:
                parts = line.split(',')
                for part in parts:
                    node = Node(part.strip(), stack[-1])
                    stack[-1].add_child(node)

        return root

# Example usage
if __name__ == "__main__":
    dsl_mapping_file_path = "dsl_mapping.json"
    compiler = Compiler(dsl_mapping_file_path)

    # This is an example DSL input. In practice, this would be generated from your rules.
    input_dsl = """
{root
    {header
{nav
navlink,navlink,navlink
}
}
{container
{row
{div-6
text,paragraph,image
}
{div-6
card,button
}
}
}
{footer
text
}
}
    """

    compiler.compile(input_dsl, "output.html")
    print("HTML file has been generated.")