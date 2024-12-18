#!/usr/bin/env python3

import json
import os
import random

class JSONCompiler:
    def __init__(self, dsl_mapping_path, output_folder, image_folder='images'):
        """
        Initialize the compiler with DSL mapping and output configurations
        
        :param dsl_mapping_path: Path to the DSL mapping JSON file
        :param output_folder: Folder where HTML files will be generated
        :param image_folder: Folder containing images for dynamic image generation
        """
        # Load DSL mapping
        with open(dsl_mapping_path, 'r') as f:
            self.dsl_mapping = json.load(f)
        
        # Create output folder if it doesn't exist
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Image folder for dynamic image generation
        self.image_folder = image_folder
        
        # Ensure image folder exists
        os.makedirs(image_folder, exist_ok=True)

    def generate_random_text(self, min_words=3, max_words=10):
        """
        Generate random placeholder text
        
        :param min_words: Minimum number of words
        :param max_words: Maximum number of words
        :return: Random text string
        """
        lorem_ipsum = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.",
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia."
        ]
        
        num_words = random.randint(min_words, max_words)
        words = " ".join(random.choice(lorem_ipsum).split()[:num_words])
        return words

    def generate_local_image(self):
        """
        Select a random image from the image folder
        
        :return: Relative path to a random image
        """
        try:
            image_files = [f for f in os.listdir(self.image_folder) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            
            if not image_files:
                return "placeholder.jpg"
            
            return os.path.join(self.image_folder, random.choice(image_files))
        except Exception as e:
            print(f"Error generating image: {e}")
            return "placeholder.jpg"

    def render_node(self, node):
        """
        Recursively render a JSON node to HTML
        
        :param node: JSON node to render
        :return: Rendered HTML string
        """
        element = node.get('element', '')

        if element == 'carousel':
            # Fetch all image files from the images folder
            try:
                image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            except Exception as e:
                print(f"Error fetching images: {e}")
                image_files = ["placeholder.jpg"]

            # Limit to 3 images for the carousel
            images = image_files[:3]

            # Carousel HTML template
            carousel_html = """
            <div class="carousel-container">
                <div id="carouselExample" class="carousel slide" data-bs-ride="carousel">
                    <div class="carousel-inner">
                        {slides}
                    </div>
                    <button class="carousel-control-prev" type="button" data-bs-target="#carouselExample" data-bs-slide="prev">
                        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                        <span class="visually-hidden">Previous</span>
                    </button>
                    <button class="carousel-control-next" type="button" data-bs-target="#carouselExample" data-bs-slide="next">
                        <span class="carousel-control-next-icon" aria-hidden="true"></span>
                        <span class="visually-hidden">Next</span>
                    </button>
                </div>
            </div>
            """

            
            # Generate slides using images from the folder
            slides = ""
            for i, img in enumerate(images):
                active_class = "active" if i == 0 else ""
                img_path = os.path.join(self.image_folder, img)
                slides += f"""
                <div class="carousel-item {active_class}">
                    <img src="..\{img_path}" class="d-block w-100" alt="Carousel Image {i+1}">
                </div>
                """

            # Replace placeholder with slides
            return carousel_html.format(slides=slides)

        
        # Special handling for dynamic content
        if element == 'text':
            return self.dsl_mapping.get('text', '').format(
                node.get('text', self.generate_random_text())
            )
        
        if element == 'text-c':
            return self.dsl_mapping.get('text-c', '').format(
                self.generate_random_text()
            )
        
        if element == 'image':
            img_path = self.generate_local_image()
            return self.dsl_mapping.get('image', '').replace(
                '<img alt="Dynamic image" class="image">', 
                f'<img src="..\{img_path}" alt="Dynamic image" class="image">'
            )
        if element == 'navlink':
            return self.dsl_mapping.get('navlink', '').replace(
                '<a href="#" class="navlink"></a>',
                f"<a class='navlink' href='{node.get('href', '#')}'>{node.get('text', 'Link')}</a>"
            )

        
        if element == 'button':
            return self.dsl_mapping.get('button', '').replace(
                '<button class="button"></button>',
                f"<button class='button'>{node.get('text', 'click here')}</button>"
            )
            
        
        # Render children for container-like elements
        children_html = ''
        if 'nodes' in node:
            children_html = ''.join(self.render_node(child) for child in node['nodes'])
        
        # Use mapping template or fallback to generic div
        template = self.dsl_mapping.get(element, '<div class="{}">{}</div>'.format(element, '{}'))
        return template.format(children_html)

    def compile_json(self, input_json_path):
        """
        Compile a JSON file to HTML
        
        :param input_json_path: Path to input JSON file
        """
        # Read JSON file
        with open(input_json_path, 'r') as f:
            data = json.load(f)


        # Extract the base filename (without extension) for the JSON file
        base_filename = os.path.splitext(os.path.basename(input_json_path))[0]

        # Generate the corresponding CSS filename
        css_filename = f"{base_filename}_styles.css"
        
        # Render the root node
        html_content = self.render_node(data)
        
        # Generate full HTML document
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
    <link rel="stylesheet" href="{css_filename}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # Generate output filename
        base_filename = os.path.splitext(os.path.basename(input_json_path))[0]
        output_html_path = os.path.join(self.output_folder, f"{base_filename}.html")
        
        # Write HTML file
        with open(output_html_path, 'w') as f:
            f.write(full_html)
        
        print(f"Successfully compiled: {output_html_path}")

def generate_css(custom_vars=None):
    """
    Generate a comprehensive CSS stylesheet
    
    :param custom_vars: Optional dictionary of custom CSS variables
    :return: CSS stylesheet as a string
    """
    # Use the existing CSS generation from the previous compiler
    default_vars = {
        'primary-color': '#6a11cd',
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

    # Full CSS with the existing styling from the previous compiler
    css_content = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

:root {{
{css_vars}
}}

*, *::before, *::after {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    width: 100%;
    font-family: var(--font-family-base);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
    color: var(--text-color);
    background-color: var(--background-color);
    margin: 0 auto;
    padding: var(--spacing-md);
}}

.header {{
    background-color: #2b2b2b;
    color: white;
    padding: 1rem;
    width: 100%;
}}

.footer {{
    background-color: #2b2b2c;
    color: white;
    padding: 2rem; /* Increase padding for more height */
    width: 100%;  
    min-height: 100px; /* Ensure a minimum height for the footer */
    box-sizing: border-box; /* Include padding in height calculation */
}}


.button, .button-c, .button-r {{
    display: inline-block;
    padding: var(--spacing-sm) var(--spacing-md); /* Increase padding */
    font-size: 1.2rem; /* Larger font size */
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--border-radius-md); /* Rounded corners */
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease; /* Smooth hover effect */
}}

.button:hover {{
    background-color: var(--secondary-color); /* Change color on hover */
    transform: scale(1.05); /* Slightly enlarge on hover */
}}

.nav {{
    display: flex; /* Use flexbox for layout */
    justify-content: flex-end; /* Align items to the right */
    gap: var(--spacing-sm); /* Add spacing between links */
}}

.navlink {{
    text-align: center;
    font-size: 1rem;
    padding: 0.75rem 1.25rem;
    color: white;
    text-decoration: none;
    border: 2px solid var(--primary-color);
    border-radius: var(--border-radius-md);
    background-color: var(--primary-color);
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}}

.navlink:hover {{
    background-color: var(--secondary-color); /* Hover color */
    transform: translateY(-3px); /* Lift effect */
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15); /* Deeper shadow */
}}





.carousel {{
    width: 400px; /* Fixed width */
    height: 250px; /* Fixed height */
    margin: 0 auto; /* Center the carousel horizontally */
    overflow: hidden; /* Ensure no content overflows */
    border-radius: var(--border-radius-md); /* Optional: rounded corners */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: subtle shadow */
}}

.carousel img {{
    width: 400px; /* Match the carousel's width */
    height: 250px; /* Match the carousel's height */
    object-fit: cover; /* Ensure images fill the space while maintaining proportions */
}}


.row {{
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}}



/* Flexbox alignment for div containers */
.div-3, .div-6, .div-12 {{
    display: flex;
    justify-content: center; /* Center elements horizontally */
    align-items: center;    /* Center elements vertically */
    text-align: center;     /* Optional: Center-align text */
    padding: 1rem;          /* Add some padding for spacing */
    box-sizing: border-box; /* Ensure padding doesn't affect width */
}}

.div-3 {{
    flex: 0 0 calc(25% - var(--spacing-sm));
}}

.div-6 {{
    flex: 0 0 calc(50% - var(--spacing-sm));
}}

.div-12 {{
    flex: 0 0 100%;
}}

# .div-3 {{ flex: 0 0 calc(25% - var(--spacing-sm)); }}
# .div-6 {{ flex: 0 0 calc(50% - var(--spacing-sm)); }}
# .div-9 {{ flex: 0 0 calc(75% - var(--spacing-sm)); }}
# .div-12 {{ flex: 0 0 100%; }}

.flex, .flex-sb, .flex-c, .flex-r {{
    display: flex;
    gap: var(--spacing-sm);
}}

.flex-sb {{ justify-content: space-between; }}
.flex-c {{ justify-content: center; align-items: center; }}
.flex-r {{ flex-direction: row; }}



.card {{
    background-color: white;
    border-radius: var(--border-radius-md);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: var(--spacing-sm);
    max-width: 300px;
}}

.image {{
    max-width: 100%;
    height: auto;
    border-radius: var(--border-radius-sm);
}}

.text, .textc, .textr {{
    margin-bottom: var(--spacing-sm);
}}

.textc {{ text-align: center; }}
.textr {{ text-align: right; }}

@media (max-width: 768px) {{
    .div-3, .div-6, .div-9 {{
        flex: 0 0 100%;
    }}
}}
"""
    return css_content

def process_json_files(json_folder, output_folder, dsl_mapping_path, image_folder=None):
    """
    Process all JSON files in a folder and generate HTML and CSS dynamically.
    
    :param json_folder: Folder containing JSON files
    :param output_folder: Folder to store generated HTML and CSS
    :param dsl_mapping_path: Path to DSL mapping file
    :param image_folder: Optional folder for dynamic images
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Create an instance of the JSON compiler
    compiler = JSONCompiler(dsl_mapping_path, output_folder, image_folder)
    
    # Process each JSON file
    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            json_path = os.path.join(json_folder, filename)
            
            # Load the JSON file
            with open(json_path, 'r') as f:
                json_data = json.load(f)

            # Extract the style from the JSON file
            style_from_json = json_data.get('styles', {})

            print(style_from_json)

            # Generate CSS using the style from JSON
            css_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_styles.css")
            css_content = generate_css(style_from_json)
            with open(css_path, 'w') as f:
                f.write(css_content)

            # Compile the JSON file to HTML
            compiler.compile_json(json_path)
    
    print("HTML and CSS generation complete.")

if __name__ == "__main__":
    # Configuration
    json_folder = 'json'  # Current directory
    output_folder = 'output'
    dsl_mapping_path = 'dsl_mapping.json'
    image_folder = 'images'
    
    # Optional custom CSS variables
    custom_vars = {
        'primary-color': '#6a11cb',
        'font-size-base': '17px'
    }
    
    # Run the compiler
    process_json_files(json_folder, output_folder, dsl_mapping_path, image_folder)