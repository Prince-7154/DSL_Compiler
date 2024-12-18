#!/usr/bin/env python

import json
import random
import os

class Node:
    def __init__(self, name, parent=None, content=""):
        self.name = name
        self.parent = parent
        self.children = []
        self.attributes = {}
        self.content = content

    def add_child(self, child):
        self.children.append(child)

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def render(self, dsl_mapping, image_folder=None):
        element_mapping = dsl_mapping.get(self.name, "")
        
        if not element_mapping:
            # If no element mapping, use default rendering
            return f"<{self.name}>{self.content}</{self.name}>"

        result = element_mapping
        for key, value in self.attributes.items():
            result = result.replace(f"${key}", value)

        # Generate random text for text-based nodes
        if self.name in ['text', 'text-c', 'text-r']:
            self.content = generate_random_text()

        child_content = "".join(child.render(dsl_mapping, image_folder) for child in self.children)
        result = result.replace("{}", child_content or self.content)

        if self.name == 'image':
            img_src = generate_local_image(image_folder)
            result = result.replace('<img alt="Dynamic image" class="image">', f'<img src="../{img_src}" alt="Dynamic image" class="image">')

        return result

class Compiler:
    def __init__(self, dsl_mapping_file_path, image_folder):
        with open(dsl_mapping_file_path) as data_file:
            self.dsl_mapping = json.load(data_file)
        self.image_folder = image_folder

    def compile(self, input_dsl, output_html_path, output_css_path):
        try:
            root = self.parse_dsl(input_dsl)
            html_content = root.render(self.dsl_mapping, self.image_folder)
            
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
            
            with open(output_html_path, 'w') as output_file:
                output_file.write(full_html)

            print(f"Successfully compiled: {output_html_path}")
        except Exception as e:
            print(f"Error compiling {output_html_path}: {str(e)}")

    def parse_dsl(self, input_dsl):
        lines = input_dsl.split('\n')
        root = Node("root")
        stack = [root]
        
        for line_number, line in enumerate(lines, 1):
            if not line:
                continue

            try:
                indent = len(line) - len(line.lstrip())
                line = line.strip()

                while indent < len(stack) - 1:
                    stack.pop()

                if line.endswith('{'):
                    name = line[:-1].strip()
                    node = Node(name, stack[-1])
                    stack[-1].add_child(node)
                    stack.append(node)
                elif line == '}':
                    if len(stack) > 1:
                        stack.pop()
                else:
                    node = Node(line, stack[-1])
                    stack[-1].add_child(node)

            except Exception as e:
                print(f"Error parsing line {line_number}: {line}")
                print(f"Error details: {str(e)}")

        return root

def generate_random_text(min_words=5, max_words=15):
    lorem_ipsum = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.",
    ]
    num_words = random.randint(min_words, max_words)
    words = " ".join(random.choice(lorem_ipsum).split()[:num_words])
    return words

def generate_local_image(image_folder):
    try:
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        if not image_files:
            return "placeholder.jpg"
        image_filename = random.choice(image_files)
        return os.path.join(image_folder, image_filename)
    except Exception as e:
        print(f"Error generating image: {e}")
        return "placeholder.jpg"

def generate_css(custom_vars=None):
    # Default CSS variables
    default_vars = {
        'primary-color': '#6a11cb',
        'secondary-color': '#2ecc71',
        'accent-color': '#e74c3c',
        'text-color': '#2c3e50',
        'background-color': '#ecf0f1',
        'font-family-base': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif",
        'font-size-base': '17px',
        'line-height-base': '1.6',
        'spacing-xs': '0.5rem',
        'spacing-sm': '1rem',
        'spacing-md': '1.5rem',
        'spacing-lg': '2rem',
        'border-radius-sm': '4px',
        'border-radius-md': '8px',
        'border-radius-lg': '12px'
    }

    # Override default variables with custom variables if provided
    if custom_vars:
        default_vars.update(custom_vars)

    # Create CSS variable declarations
    css_vars = "\n".join([f"    --{key}: {value};" for key, value in default_vars.items()])

    return f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

:root {{
{css_vars}
}}

*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

.header {{
    background-color: #2b2b2b; /* Dark shade of black */
    color: white; /* Text should be white for contrast */
    padding: 1rem;
    width: 100%
}}

.footer {{
    background-color: #3a3a3a; /* Slightly lighter black */
    color: white;
    padding: 1rem;
    text-align: center;
}}

.nav {{
    display: flex;
    justify-content: flex-end; /* Align navigation links to the left */
    gap: 0.5rem; /* Add space between links */
}}

.navlink {{
    display: inline-block;
    width: 12rem; /* Ensure enough space for one-letter links */
    text-align: center; /* Center align text inside the link */
    font-size: 1rem;
    color: white;
    text-decoration: none;
    padding: 0.5rem;
    background-color: var(--primary-color); /* Add a background for visibility */
    border-radius: 4px;
    transition: background-color 0.3s ease;
}}

.navlink:hover {{
    background-color: color-mix(in srgb, var(--primary-color) 80%, black); /* Slight darkening on hover */
}}


body {{
    font-family: var(--font-family-base);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
    color: var(--text-color);
    background-color: var(--background-color);
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-md);
}}
/* Button Styling */
/* Button Styling */
.button, .button-c, .button-r {{
    display: inline-block;
    width: auto;  /* Changed from 100% to auto */
    max-width: 150px;  /* Reduced from 200px */
    padding: calc(var(--spacing-xs) * 0.75) var(--spacing-sm);
    font-size: calc(var(--font-size-base) * 0.9);
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    text-decoration: none;
    line-height: 1.5;
    margin-top: var(--spacing-sm);
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    white-space: nowrap;  /* Prevent text from wrapping */
    overflow: visible;    /* Ensure text is always visible */
}}

.button:hover, .button-c:hover, .button-r:hover {{
    background-color: color-mix(in srgb, var(--primary-color) 80%, black);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}}

.button:active, .button-c:active, .button-r:active {{
    transform: translateY(1px);
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}}

.button:focus, .button-c:focus, .button-r:focus {{
    outline: none;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.4);
}}

/* Responsive Grid and Layout Improvements */
.row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: var(--spacing-sm);
}}

.div-3, .div-6, .div-9, .div-12 {{
    display: flex;
    flex-direction: column;
    align-items: center;
}}

.div-3 {{ flex: 0 0 calc(25% - var(--spacing-sm)); }}
.div-6 {{ flex: 0 0 calc(50% - var(--spacing-sm)); }}
.div-9 {{ flex: 0 0 calc(75% - var(--spacing-sm)); }}
.div-12 {{ flex: 0 0 100%; }}

/* Card Sizing and Styling */
.card {{
    width: 100%;
    max-width: 300px;
    height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: white;
    border-radius: var(--border-radius-md);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    overflow: hidden;
}}

/* Responsive Image within Card */
.card .image {{
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: var(--border-radius-sm);
    margin-bottom: var(--spacing-sm);
}}

/* Button Styling within Card */
.card .button, .card .button-c, .card .button-r {{
    width: 100%;
    max-width: 200px;
    padding: calc(var(--spacing-xs) * 0.75) var(--spacing-sm);
    font-size: calc(var(--font-size-base) * 0.9);
    margin-top: var(--spacing-sm);
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    transition: background-color 0.3s ease;
}}

.card .button:hover, .card .button-c:hover, .card .button-r:hover {{
    background-color: color-mix(in srgb, var(--primary-color) 80%, black);
}}

/* Text within Card */
.card .text, .card .textc, .card .textr {{
    text-align: center;
    font-size: calc(var(--font-size-base) * 0.9);
    margin-bottom: var(--spacing-sm);
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}}

/* Responsive Adjustments */
@media (max-width: 768px) {{
    .div-3, .div-6, .div-9, .div-12 {{
        flex: 0 0 100%;
    }}
}}

/* Additional Utility Styles */
.image {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}}

.text-center {{ text-align: center; }}
.text-right {{ text-align: right; }}

.site-footer {{
    background-color: var(--text-color);
    color: white;
    text-align: center;
    padding: var(--spacing-md);
    margin-top: var(--spacing-lg);
}}
"""


def process_dsl_files(dsl_folder, output_folder, dsl_mapping_file_path, image_folder, custom_css_vars=None):
    compiler = Compiler(dsl_mapping_file_path, image_folder)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    css_path = os.path.join(output_folder, "styles.css")
    css_content = generate_css(custom_css_vars)
    with open(css_path, 'w') as css_file:
        css_file.write(css_content)

    for filename in os.listdir(dsl_folder):
        if filename.endswith(".dsl"):
            input_path = os.path.join(dsl_folder, filename)
            output_html_path = os.path.join(output_folder, f"{filename[:-4]}.html")

            with open(input_path, 'r') as dsl_file:
                input_dsl = dsl_file.read()

            compiler.compile(input_dsl, output_html_path, css_path)
            print(f"Processed {filename} -> {output_html_path}")

if __name__ == "__main__":
    dsl_mapping_file_path = "dsl_mapping.json"
    dsl_folder = "dsl"
    output_folder = "output"
    image_folder = "images"

    custom_vars = {
        'primary-color': '#6a11cb',
        'font-size-base': '17px'
    }

    process_dsl_files(dsl_folder, output_folder, dsl_mapping_file_path, image_folder, custom_vars)
    print("All DSL files have been processed.")
