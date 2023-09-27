# Script that extracts data from a pdf and uses it to fill another pdf

from fillpdf import fillpdfs
import docx
import os
import argparse
from gooey import Gooey, GooeyParser

# The default folder for the template PDFs
default_template_folder = "T:\Safe Work Procedures\SOP-SWP-RA-ECP - templates"

# The default folder for the work procedure documents
default_work_procedure_folder = "T:\Safe Work Procedures"

# The select field name to get the templates
template_select_field = "TEMPLATE_SELECT"

# The select field name to get the work procedure
work_procedure_select_field = "WORK_PROCEDURE_SELECT"

# The hidden select field name that stores all the work procedures
work_procedure_select_all_field = "WORK_PROCEDURE_SELECT_ALL"

# The text field to input the work procedure text
# In the template PDF, name the text field "SWP", "SWP2", "SWP3" etc for each cooresponding page
# X is replaced by a number, except for the first page, which has no number
work_procedure_text_field = "SWPX"
# The number of pages for the work procedure
num_work_procedure_pages = 3

# Extracts the data from a pdf into a dictionary
def extract_fillable_data(pdf_path) -> dict:
    fields = fillpdfs.get_form_fields(pdf_path)
    return fields

# Gets the value of a field from the dictionary of fields
def get_dropdown_value(file_name, dict, field_name) -> str:
    data = dict.get(field_name, "")
    if not data:
        raise ValueError(f"No dropdown field found with the name {field_name} in {file_name}")
    return data

# Returns the path of the file by name
def get_pdf_file(file_name, template_folder) -> str:
    file_path = os.path.join(template_folder, f"{file_name}.pdf")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found with the name {file_path}.")
    return file_path

# Returns the data array from a word file
def get_data_from_word_file(file_name, work_procedure_folder) -> [str]:
    matches = []
    file_name_docx = f"{file_name}.docx"
    file_path = ""

    # Walk through all subdirectories of the base folder
    for dirpath, dirnames, filenames in os.walk(work_procedure_folder):
        for filename in filenames:
            if filename == file_name_docx:
                matches.append(os.path.join(dirpath, filename))

    # Check if more than one file with the target name was found
    if len(matches) > 1:
        raise Exception(f"More than one file named {file_name_docx} was found!")
    elif len(matches) == 0:
        raise Exception(f"No proecdure document file named {file_name_docx} was found!")
    else:
        file_path = matches[0]

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No document procedure file found with the name {file_path}.")
    
    # Get the text from a word document
    doc = docx.Document(file_path)
    result = []
    for paragraph in doc.paragraphs:
        result.append(paragraph.text)
    text = "\n".join(result)

    # Split the text into pages
    return split_text_into_pages(text, 1200, num_work_procedure_pages)

# Splits text into pages
def split_text_into_pages(text, max_chars_per_page, max_pages):
    lines = text.split('\n')
    pages = []
    current_page = ''
    current_page_chars = 0

    for line in lines:
        # Add 1 for the newline character
        line_length = len(line) + 1  

        # Check if adding this line will exceed the page character limit
        if current_page_chars + line_length > max_chars_per_page:
            # Save the current page and start a new one
            pages.append(current_page.rstrip())
            current_page = ''
            current_page_chars = 0

        # Add the line to the current page
        current_page += line + '\n'
        current_page_chars += line_length

    # Add the last page if it's not empty
    if current_page:
        pages.append(current_page.rstrip())

    while len(pages) < max_pages :
        pages.append('')

    return pages


def print_javascript_procedure_select(work_procedure_folder):
    docx_files = []
    
    # Walk through root_folder, including all its subdirectories
    for dirpath, dirnames, filenames in os.walk(work_procedure_folder):
        for filename in filenames:
            # Check if the file is a .docx file
            if filename.endswith('.docx'):
                
                # Add the full path to the docx_files list without the .docx extension
                docx_files.append(os.path.splitext(filename)[0])
                
    print(f'''var dropdown = this.getField("{work_procedure_select_all_field}");
var newOptions = {str(docx_files)};
dropdown.clearItems();
for (var i = 0; i < newOptions.length; i++) {{
    dropdown.insertItemAt(newOptions[i], newOptions[i], i);
}}''')


@Gooey(program_name="Work Procedure PDF Generator", tabbed_groups=True, navigation='Tabbed', default_size=(800, 600))
def main():
    parser = GooeyParser(description='Automate creating a work procedure PDF')

    subparsers = parser.add_subparsers(help='Choose an action', dest='action')

    generator_group = subparsers.add_parser("Generate_PDF", prog="Generate PDF", help="Generate a PDF from a template")
    generator_group.add_argument('--source_pdf', metavar="Source PDF", widget="FileChooser", gooey_options={'wildcard': "PDF files (*.pdf)|*.pdf", 'full_width': True}, help='The source PDF')
    generator_group.add_argument("--template_folder", metavar="Template Folder", widget="DirChooser", help="The folder containing the template PDFs", default=default_template_folder, gooey_options={'default_path': default_template_folder, 'full_width': True})
    generator_group.add_argument("--work_procedure_folder", metavar="Work Procedure Folder", widget="DirChooser", default=default_work_procedure_folder, gooey_options={'default_path': default_work_procedure_folder, 'full_width': True}, help="The folder containing the work procedure documents")
    
    procedure_group = subparsers.add_parser("Procedure_List", prog="Procedure List", help="Generate a javascript file to update the work procedure list dropdown")
    procedure_group.add_argument("--work_procedure_folder", metavar="Work Procedure Folder", widget="DirChooser", default=default_work_procedure_folder, gooey_options={'default_path': default_work_procedure_folder, 'full_width': True}, help="The folder containing the work procedure documents")

    args = parser.parse_args()

    if args.action == "Generate_PDF":
        source_pdf = args.source_pdf
        template_folder = args.template_folder
        work_procedure_folder = args.work_procedure_folder
    elif args.action == "Procedure_List":
        work_procedure_folder = args.work_procedure_folder
        print_javascript_procedure_select(work_procedure_folder)
        return

    # Extract the data from the source pdf
    extracted_data = extract_fillable_data(source_pdf)

    # Get the template file from the source pdf
    template_file_name = get_dropdown_value(source_pdf, extracted_data, template_select_field)
    template_pdf = get_pdf_file(template_file_name, template_folder)

    # Get the work procedure text from the lookup word file
    lookup_file_name = get_dropdown_value(source_pdf, extracted_data, work_procedure_select_field)
    work_procedure_texts = get_data_from_word_file(lookup_file_name, work_procedure_folder)

    # Add the work procedure text to the extracted data
    for n in range(num_work_procedure_pages):
        index = n + 1
        if index == 1:
            text_field_name = work_procedure_text_field.replace("X", "")
        else:
            text_field_name = work_procedure_text_field.replace("X", str(index))
        extracted_data[text_field_name] = work_procedure_texts[n]

    # Print the data in a nice way
    print("\n----------------------- Data -----------------------")
    print("{" + ",\n".join("{!r}: {!r}".format(k, v) for k, v in extracted_data.items()) + "}")

    # Create a new pdf from the template and fill it with the combined data
    new_pdf_path = os.path.join(os.path.dirname(source_pdf), f"{os.path.splitext(source_pdf)[0]}_SWP.pdf")
    print(f"Created new pdf: {new_pdf_path}")

    fillpdfs.write_fillable_pdf(template_pdf, new_pdf_path, extracted_data)

if __name__ == "__main__":
    main()
    
