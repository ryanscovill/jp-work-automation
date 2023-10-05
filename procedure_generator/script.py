# Script that extracts data from a pdf and uses it to fill another pdf

from fillpdf import fillpdfs
import docx
import os
import argparse
import sys
import codecs
from gooey import Gooey, GooeyParser


# Handle encodings
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
    fields = {k: v for k, v in fields.items() if "check box" not in k.lower()}

    return fields

# Gets the value of a field from the dictionary of fields
def get_dropdown_value(file_name, dict, field_name) -> str:
    data = dict.get(field_name, "")
    if not data:
        raise ValueError(f"No dropdown field found with the name {field_name} in {file_name}")
    return data

# Returns the path of the file by name
def get_pdf_file(file_name, template_folder) -> str:
    file_name = f"{file_name}.pdf"
    file_path = get_single_filepath_from_folder(template_folder, file_name)
    return file_path


def get_single_filepath_from_folder(base_folder, search_filename):
    matches = []
    file_path = search_filename

    # Walk through all subdirectories of the base folder
    for dirpath, dirnames, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename == search_filename:
                matches.append(os.path.join(dirpath, filename))

    # Check if more than one file with the target name was found
    if len(matches) > 1:
        raise Exception(f"More than one file named {search_filename} was found!")
    elif len(matches) == 0:
        raise Exception(f"No file named {search_filename} was found!")
    else:
        file_path = matches[0]

    return file_path

# Returns the data array from a word file
def get_data_from_word_file(file_name, work_procedure_folder) -> [str]:
    file_name_docx = f"{file_name}.docx"
    file_path = get_single_filepath_from_folder(work_procedure_folder, file_name_docx)
    
    # Get the text from a word document
    doc = docx.Document(file_path)
    result = []
    for paragraph in doc.paragraphs:
        result.append(paragraph.text)
    text = "\n".join(result)

    # Split the text into pages
    return split_text_into_pages(text, 4750, num_work_procedure_pages)

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


def get_files_from_folder(folder, file_extension):
    files_list = []
    
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(file_extension):
                try:
                    file_name_without_extension = os.path.splitext(filename)[0].encode('utf-8').decode('utf-8')
                    files_list.append(file_name_without_extension)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(f"Bad file name: {filename.encode('utf-8', 'ignore').decode('utf-8')}. Please change the filename to use only normal characters.")
    
    return files_list

def print_javascript_select_list(list, field_name):
    print(f'var dropdown = this.getField("{field_name}");')
    print('var newOptions = [' + ', '.join('"{}"'.format(item) for item in list) + '];')
    print("dropdown.clearItems();")
    print("for (var i = 0; i < newOptions.length; i++) {")
    print("    dropdown.insertItemAt(newOptions[i], newOptions[i], i);")
    print("}")

def print_javascript_procedure_select(work_procedure_folder):
    docx_files = get_files_from_folder(work_procedure_folder, '.docx')
    print_javascript_select_list(docx_files, work_procedure_select_all_field)   

def print_javascript_template_select(template_folder):
    pdf_files = get_files_from_folder(template_folder, '.pdf')
    print_javascript_select_list(pdf_files, template_select_field)


def setDebug(args):
    args.action = "Procedure_List"
    args.source_pdf = "D:\OneDrive\Documents\jp\work_automation\procedure_generator\examples\examples_new\WCB and PCF Master - 27-09-2023-2.pdf"
    args.template_folder = "D:\OneDrive\Documents\jp\work_automation\procedure_generator\examples\examples_new\Templates"
    args.work_procedure_folder = "D:\OneDrive\Documents\jp\examples_new\Procedure Documents"
    return args

@Gooey(program_name="Work Procedure PDF Generator", tabbed_groups=True, navigation='Tabbed', default_size=(800, 600),
       menu=[{'name': 'About', 'items': [{
    'type': 'AboutDialog',
    'menuTitle': 'About',
    'name': 'Work Procedure PDF Generator',
    'description': 'Automate creating a work procedure PDF',
    'version': '1.4.4',
    'copyright': '2023',
    'website': 'https://github.com/ryanscovill',
    'license': 'MIT'
}]}])
def main():
    parser = GooeyParser(description='Automate creating a work procedure PDF')

    subparsers = parser.add_subparsers(help='Choose an action', dest='action')

    generator_group = subparsers.add_parser("Generate_PDF", prog="Generate PDF", help="Generate a PDF from a template")
    generator_group.add_argument('--source_pdf', metavar="Source PDF", widget="FileChooser", gooey_options={'wildcard': "PDF files (*.pdf)|*.pdf", 'full_width': True}, help='The source PDF')
    generator_group.add_argument("--template_folder", metavar="Template Folder", widget="DirChooser", help="The folder containing the template PDFs", default=default_template_folder, gooey_options={'default_path': default_template_folder, 'full_width': True})
    generator_group.add_argument("--work_procedure_folder", metavar="Work Procedure Folder", widget="DirChooser", default=default_work_procedure_folder, gooey_options={'default_path': default_work_procedure_folder, 'full_width': True}, help="The folder containing the work procedure documents")
    
    procedure_group = subparsers.add_parser("Template_List", prog="Template List", help="Generate a javascript file to update the work template list dropdown")
    procedure_group.add_argument("--template_folder", metavar="Template Folder", widget="DirChooser", default=default_template_folder, gooey_options={'default_path': default_template_folder, 'full_width': True}, help="The folder containing the template PDFs")

    procedure_group = subparsers.add_parser("Procedure_List", prog="Procedure List", help="Generate a javascript file to update the work procedure list dropdown")
    procedure_group.add_argument("--work_procedure_folder", metavar="Work Procedure Folder", widget="DirChooser", default=default_work_procedure_folder, gooey_options={'default_path': default_work_procedure_folder, 'full_width': True}, help="The folder containing the work procedure documents")

    args = parser.parse_args()

    # uncomment to debug without GUI
    # args = setDebug(args)

    if args.action == "Generate_PDF":
        source_pdf = args.source_pdf
        template_folder = args.template_folder
        work_procedure_folder = args.work_procedure_folder
    elif args.action == "Procedure_List":
        work_procedure_folder = args.work_procedure_folder
        print_javascript_procedure_select(work_procedure_folder)
        return
    elif args.action == "Template_List":
        template_folder = args.template_folder
        print_javascript_template_select(template_folder)
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
    print("{" + ",\n".join("{!r}: {!r}".format(k, v.encode('utf-8', 'ignore').decode('utf-8') if v is not None else None) for k, v in extracted_data.items()) + "}")

    # Create a new pdf from the template and fill it with the combined data
    new_pdf_path = os.path.join(os.path.dirname(source_pdf), f"{os.path.splitext(source_pdf)[0]}_SWP.pdf")
    print(f"Created new pdf: {new_pdf_path}")

    fillpdfs.write_fillable_pdf(template_pdf, new_pdf_path, extracted_data)

if __name__ == "__main__":
    main()
    
