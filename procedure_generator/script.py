# Script that extracts data from a pdf and uses it to fill another pdf

from fillpdf import fillpdfs
import docx
import os
import argparse
import sys
import codecs
from gooey import Gooey, GooeyParser
import fitz
from worksafe_nop.fill import fill_nop


# Handle encodings
if sys.stdout.encoding != "UTF-8":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
if sys.stderr.encoding != "UTF-8":
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# The default folder for the template PDFs
default_template_folder = r"T:\Safe Work Procedures\SOP-SWP-RA-ECP - templates"

# The default folder for the work procedure documents
default_work_procedure_folder = r"T:\Safe Work Procedures"

# Default paths for NOP files
default_nop_mappings_file = r"T:\procedure_generator_mappings.json"

# The select field name to get the templates
template_select_field = "TEMPLATE_SELECT"

# The select field name to get the work procedure
# X is replaced by a number from 1 to number of work procedure fields
work_procedure_select_field = "WORK_PROCEDURE_SELECTX"

# The hidden select field name that stores all the work procedures
work_procedure_select_all_field = "WORK_PROCEDURE_SELECT_ALL"

# The text field to input the work procedure text
# In the template PDF, name the text field "SWP", "SWP2", "SWP3" etc for each cooresponding page
# Additional pages are automatically added as needed
# X is replaced by a number, except for the first page, which has no number
work_procedure_text_field = "SWPX"
num_work_procedure_fields = 12


# Extracts the data from a pdf into a dictionary
def extract_fillable_data(pdf_path) -> dict:
    fields = fillpdfs.get_form_fields(pdf_path)
    fields = {k: v for k, v in fields.items() if "check box" not in k.lower()}

    return fields


# Gets the value of a field from the dictionary of fields
def get_dropdown_value(file_name, dict, field_name, error=True) -> str:
    data = dict.get(field_name, "")
    if error and not data:
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
def get_data_from_word_file(file_name, work_procedure_folder) -> list[str]:
    file_name_docx = f"{file_name}.docx"
    file_path = get_single_filepath_from_folder(work_procedure_folder, file_name_docx)

    # Get the text from a word document
    doc = docx.Document(file_path)
    result = []
    for paragraph in doc.paragraphs:
        result.append(paragraph.text)
    text = "\n".join(result)

    # Split the text into pages
    return split_text_into_pages(text, 3300)


# Splits text into pages
def split_text_into_pages(text, max_chars_per_page):
    lines = text.split("\n")
    pages = []
    current_page = ""
    current_page_chars = 0

    for line in lines:
        # Add 1 for the newline character
        line_length = len(line) + 1

        # Check if adding this line will exceed the page character limit
        if current_page_chars + line_length > max_chars_per_page:
            # Save the current page and start a new one
            pages.append(current_page.rstrip())
            current_page = ""
            current_page_chars = 0

        # Add the line to the current page
        current_page += line + "\n"
        current_page_chars += line_length

    # Add the last page if it's not empty
    if current_page:
        pages.append(current_page.rstrip())

    return pages


def _find_last_annot(doc, starts_with):
    last_page_index = 0
    field_name = None
    for page_index, page in enumerate(doc):
        for annot in page.widgets():
            if annot.field_name.startswith(starts_with):
                last_page_index = page_index
                field_name = annot.field_name
    return last_page_index, field_name


def find_last_swp_page(doc):
    page_index, field_name = _find_last_annot(doc, "SWP")
    last_swp_index = 0

    if field_name is None:
        return 0, 0

    if field_name:
        last_swp_index = int(field_name[3:])

    return page_index, last_swp_index


def add_swp_page(doc: fitz.Document, page_index, swp_index):
    doc.fullcopy_page(page_index - 1, page_index)
    new_page: fitz.Page = doc[page_index]
    for annot in new_page.widgets():
        if annot.field_name.startswith("SWP"):
            annot.field_name = "SWP" + str(swp_index)
            annot.update()


def add_swp_pages(file, num_required_pages, output_pdf):
    doc = fitz.open(file)
    last_swp_page_index, last_swp_index = find_last_swp_page(doc)
    required_pages = num_required_pages - last_swp_index
    for i in range(required_pages):
        add_swp_page(doc, last_swp_page_index + i + 1, last_swp_index + i + 1)
    doc.save(output_pdf)
    doc.close()


def get_select_field_values(doc, field_name):
    values = []
    for page in doc:
        for annot in page.widgets():
            if annot.field_name == field_name:
                if hasattr(annot, "choice_values"):
                    values = annot.choice_values
                    break
    return values


def update_select_field(doc, field_name, options):
    field_updated = False
    for page in doc:
        for annot in page.widgets():
            if annot.field_name == field_name:
                annot.choice_values = options
                annot.update()
                field_updated = True
                break
        if field_updated:
            break

    if not field_updated:
        print(f"Warning: No field found with the name {field_name}.")


def add_work_procedure_text(extracted_data, work_procedure_texts):
    for n in range(len(work_procedure_texts)):
        index = n + 1
        if index == 1:
            text_field_name = work_procedure_text_field.replace("X", "")
        else:
            text_field_name = work_procedure_text_field.replace("X", str(index))
        extracted_data[text_field_name] = work_procedure_texts[n]

    return extracted_data


def get_safe_work_procedues(source_pdf, extracted_data, work_procedure_folder):
    work_procedure_texts = []
    for n in range(1, num_work_procedure_fields + 1):
        swp_field = work_procedure_select_field.replace("X", str(n))
        lookup_file_name = get_dropdown_value(source_pdf, extracted_data, swp_field, False)

        # Handle the case for older PDFs that don't number the lookup field
        if n == 1 and not lookup_file_name:
            swp_field = work_procedure_select_field.replace("X", "")
            lookup_file_name = get_dropdown_value(source_pdf, extracted_data, swp_field, True)

        if lookup_file_name and lookup_file_name != "UNUSED":
            work_procedure_texts = work_procedure_texts + get_data_from_word_file(
                lookup_file_name, work_procedure_folder
            )

    return work_procedure_texts


def get_files_from_folder(folder, file_extension):
    files_list = []

    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(file_extension):
                try:
                    file_name_without_extension = (
                        os.path.splitext(filename)[0].encode("utf-8").decode("utf-8")
                    )
                    files_list.append(file_name_without_extension)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(
                        f"Bad file name: {filename.encode('utf-8', 'ignore').decode('utf-8')}. Please change the filename to use only normal characters."
                    )

    return files_list


def generate_pdf(source_pdf, template_folder, work_procedure_folder):
    # Extract the data from the source pdf
    extracted_data = extract_fillable_data(source_pdf)

    # Get the template file from the source pdf
    template_file_name = get_dropdown_value(source_pdf, extracted_data, template_select_field)
    template_pdf = get_pdf_file(template_file_name, template_folder)

    # Get the work procedure text from the lookup word file
    work_procedure_texts = get_safe_work_procedues(
        source_pdf, extracted_data, work_procedure_folder
    )
    extracted_data = add_work_procedure_text(extracted_data, work_procedure_texts)

    # Create a temporary pdf with the extra SWP pages
    temp_pdf_path = os.path.join(
        os.path.dirname(source_pdf), f"{os.path.splitext(source_pdf)[0]}_TEMP_DELETE.pdf"
    )

    add_swp_pages(template_pdf, len(work_procedure_texts), temp_pdf_path)

    # Print the data in a nice way
    print("\n----------------------- Data -----------------------")
    print(
        "{"
        + ",\n".join(
            "{!r}: {!r}".format(
                k, v.encode("utf-8", "ignore").decode("utf-8") if v is not None else None
            )
            for k, v in extracted_data.items()
        )
        + "}"
    )

    # Create a new pdf from the template and fill it with the combined data
    new_pdf_path = os.path.join(
        os.path.dirname(source_pdf), f"{os.path.splitext(source_pdf)[0]}_SWP.pdf"
    )
    print(f"Created new pdf: {new_pdf_path}")

    try:
        fillpdfs.write_fillable_pdf(temp_pdf_path, new_pdf_path, extracted_data)
    finally:
        # delete the temporary pdf
        os.remove(temp_pdf_path)


def update_master(source_pdf, template_folder, work_procedure_folder):
    doc = fitz.open(source_pdf)

    # Get the existing templates and work procedures
    existing_templates = get_select_field_values(doc, template_select_field)
    existing_work_procedures = get_select_field_values(doc, work_procedure_select_all_field)

    # Get the new templates and work procedures
    templates = get_files_from_folder(template_folder, ".pdf")
    work_procedures = get_files_from_folder(work_procedure_folder, ".docx")
    work_procedures.append("UNUSED")

    # Print the differences
    new_templates = list(set(templates) - set(existing_templates))
    removed_templates = list(set(existing_templates) - set(templates))
    new_work_procedures = list(set(work_procedures) - set(existing_work_procedures))
    removed_work_procedures = list(set(existing_work_procedures) - set(work_procedures))

    print("Templates added:", new_templates)
    print("Templates removed:", removed_templates)
    print("Work procedures added:", new_work_procedures)
    print("Work procedures removed:", removed_work_procedures)

    # Update the template select field
    update_select_field(doc, template_select_field, templates)

    # Update the work procedure select field
    update_select_field(doc, work_procedure_select_all_field, work_procedures)

    new_pdf_path = os.path.join(
        os.path.dirname(source_pdf), f"{os.path.splitext(source_pdf)[0]}_UPDATED.pdf"
    )
    doc.save(new_pdf_path)
    doc.close()

    print(f"Created new pdf: {new_pdf_path}")


def setDebug(args):
    args.action = "Update_Master"
    args.source_pdf = (
        r"D:\OneDrive\Documents\jp\examples_new\WCB and PCF Master -04-10-2023 MAIN2 - Copy_UP2.pdf"
    )
    args.template_folder = r"D:\OneDrive\Documents\jp\examples_new\Templates"
    args.work_procedure_folder = r"D:\OneDrive\Documents\jp\examples_new\Procedure Documents"
    return args


@Gooey(
    program_name="Work Procedure PDF Generator",
    tabbed_groups=True,
    navigation="Tabbed",
    default_size=(800, 600),
    menu=[
        {
            "name": "About",
            "items": [
                {
                    "type": "AboutDialog",
                    "menuTitle": "About",
                    "name": "Work Procedure PDF Generator",
                    "description": "Automate creating a work procedure PDF",
                    "version": "2.0.0",
                    "copyright": "2025",
                    "website": "https://github.com/ryanscovill",
                    "license": "MIT",
                }
            ],
        }
    ],
)
def main():
    parser = GooeyParser(description="Automate creating a work procedure PDF")

    subparsers = parser.add_subparsers(help="Choose an action", dest="action")

    generator_group = subparsers.add_parser(
        "Generate_PDF", prog="Generate PDF", help="Generate a PDF from a template"
    )
    generator_group.add_argument(
        "--source_pdf",
        metavar="Source PDF",
        widget="FileChooser",
        gooey_options={"wildcard": "PDF files (*.pdf)|*.pdf", "full_width": True},
        help="The source PDF",
    )
    generator_group.add_argument(
        "--template_folder",
        metavar="Template Folder",
        widget="DirChooser",
        help="The folder containing the template PDFs",
        default=default_template_folder,
        gooey_options={"default_path": default_template_folder, "full_width": True},
    )
    generator_group.add_argument(
        "--work_procedure_folder",
        metavar="Work Procedure Folder",
        widget="DirChooser",
        default=default_work_procedure_folder,
        gooey_options={"default_path": default_work_procedure_folder, "full_width": True},
        help="The folder containing the work procedure documents",
    )

    procedure_group = subparsers.add_parser(
        "Update_Master",
        prog="Update Master",
        help="Updates the Master Document with the list of templates and work procedures",
        description="Updates the master template dropdown fields for listed templates and work procedures",
    )
    procedure_group.add_argument(
        "--source_pdf",
        metavar="Master PDF",
        widget="FileChooser",
        gooey_options={"wildcard": "PDF files (*.pdf)|*.pdf", "full_width": True},
        help="The master PDF",
    )
    procedure_group.add_argument(
        "--template_folder",
        metavar="Template Folder",
        widget="DirChooser",
        default=default_template_folder,
        gooey_options={"default_path": default_template_folder, "full_width": True},
        help="The folder containing the template PDFs",    )
    procedure_group.add_argument(
        "--work_procedure_folder",
        metavar="Work Procedure Folder",
        widget="DirChooser",
        default=default_work_procedure_folder,
        gooey_options={"default_path": default_work_procedure_folder, "full_width": True},
        help="The folder containing the work procedure documents",
    )

    fill_nop_group = subparsers.add_parser(
        "Fill_NOP",
        prog="Fill NOP",
        help="Fill NOP forms using web automation",
        description="Automate filling of NOP (Notice of Project) forms using browser automation"
    )
    fill_nop_group.add_argument(
        "--data_file",
        metavar="Data File (JSON)",
        widget="FileChooser",
        gooey_options={"wildcard": "JSON files (*.json)|*.json", "full_width": True},
        help="The JSON file containing the form data",
        required=True,
    )
    fill_nop_group.add_argument(
        "--mappings_file",
        metavar="Mappings File (JSON)",
        widget="FileChooser",
        gooey_options={"wildcard": "JSON files (*.json)|*.json", "full_width": True},
        help="The JSON file containing the field mappings",
        default=default_nop_mappings_file,
        required=True,
    )
    args = parser.parse_args()

    # uncomment to debug without GUI
    # args = setDebug(args)

    if args.action == "Generate_PDF":
        source_pdf = args.source_pdf
        template_folder = args.template_folder
        work_procedure_folder = args.work_procedure_folder
        generate_pdf(source_pdf, template_folder, work_procedure_folder)
    elif args.action == "Update_Master":
        source_pdf = args.source_pdf
        template_folder = args.template_folder
        work_procedure_folder = args.work_procedure_folder
        update_master(source_pdf, template_folder, work_procedure_folder)
    elif args.action == "Fill_NOP":
        data_file = args.data_file
        mappings_file = args.mappings_file
        fill_nop(data_file, mappings_file)


if __name__ == "__main__":
    main()
