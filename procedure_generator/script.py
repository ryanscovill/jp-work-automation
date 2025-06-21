# Script that extracts data from a pdf and uses it to fill another pdf

import sys
import codecs
from gooey import Gooey, GooeyParser
from procedure_generator.swp.swp import generate_pdf, update_master
from procedure_generator.worksafe_nop.fill import fill_nop, fill_nop_from_pdf
from procedure_generator.config_loader import config
from procedure_generator.excel_pdf.excel_pdf import excel_pdf


# Handle encodings
if sys.stdout.encoding != "UTF-8":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
if sys.stderr.encoding != "UTF-8":
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


def setDebug(args):
    args.action = "Update_Master"
    args.source_pdf = config.debug_paths.source_pdf
    args.template_folder = config.debug_paths.template_folder
    args.work_procedure_folder = config.debug_paths.work_procedure_folder
    return args


@Gooey(
    program_name="Work Procedure PDF Generator",
    tabbed_groups=True,
    navigation="Tabbed",
    default_size=tuple(config.ui_settings.default_window_size),
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
    default_template_folder = config.paths.default_template_folder
    default_work_procedure_folder = config.paths.default_work_procedure_folder

    parser = GooeyParser(description="Automate creating a work procedure PDF")

    subparsers = parser.add_subparsers(help="Choose an action", dest="action")

    excel_pdf_group = subparsers.add_parser(
        "Excel_PDF",
        prog="Excel PDF",
        help="Fill PDF forms from Excel data",
        description="Fill PDF forms using data from Excel files with field mapping"
    )
    
    excel_pdf_options = excel_pdf_group.add_argument_group(
        'Excel to PDF',
        description='Essential files for PDF form filling',
        gooey_options={'show_border': False, 'columns': 1}
    )
    excel_pdf_options.add_argument(
        'excel_file',
        widget='FileChooser',
        help="Excel file with vertical data",
        gooey_options={'wildcard': "Excel files (*.xlsx)|*.xlsx"}    )
    excel_pdf_options.add_argument(
        'pdf_template',
        widget='FileChooser',
        help="PDF form to fill",
        gooey_options={'wildcard': "PDF files (*.pdf)|*.pdf"}
    )
    excel_pdf_options.add_argument(
        'output_pdf',
        widget='FileSaver',
        help="Save filled PDF as...",
        gooey_options={'wildcard': "PDF files (*.pdf)|*.pdf"}
    )

    generator_group = subparsers.add_parser(
        "Generate_PDF", prog="Generate PDF", help="Generate a PDF from a template"
    )

    generator_options = generator_group.add_argument_group(
        'Generate PDF',
        description='Create a SWP',
        gooey_options={'show_border': False, 'columns': 1}
    )
    
    generator_options.add_argument(
        "--source_pdf",
        metavar="Source PDF",
        widget="FileChooser",
        gooey_options={"wildcard": "PDF files (*.pdf)|*.pdf", "full_width": True},
        help="The source PDF",
    )
    generator_options.add_argument(
        "--template_folder",
        metavar="Template Folder",
        widget="DirChooser",
        help="The folder containing the template PDFs",
        default=default_template_folder,
        gooey_options={"default_path": default_template_folder, "full_width": True},
    )
    generator_options.add_argument(
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

    fill_nop_options = fill_nop_group.add_argument_group(
        'Fill NOP',
        description='Fill the NOP form on the WorkSafeBC website',
        gooey_options={'show_border': False, 'columns': 1}
    )
    fill_nop_options.add_argument(
        "--data_file",
        metavar="NOP PDF",
        widget="FileChooser",
        gooey_options={"wildcard": "PDF files (*.pdf)|*.pdf", "full_width": True},
        help="The NOP PDF file",
        required=True,
    )

    procedure_group = subparsers.add_parser(
        "Update_Master",
        prog="Update Master",
        help="Updates the Master Document with the list of templates and work procedures",
        description="Updates the master template dropdown fields for listed templates and work procedures",
    )
    procedure_options = procedure_group.add_argument_group(
        'Update Master PDF',
        description='Update the master PDF with new templates and work procedures',
        gooey_options={'show_border': False, 'columns': 1}
    )
    procedure_options.add_argument(
        "--source_pdf",
        metavar="Master PDF",
        widget="FileChooser",
        gooey_options={"wildcard": "PDF files (*.pdf)|*.pdf", "full_width": True},
        help="The master PDF",
    )
    procedure_options.add_argument(
        "--template_folder",
        metavar="Template Folder",
        widget="DirChooser",
        default=default_template_folder,
        gooey_options={"default_path": default_template_folder, "full_width": True},        help="The folder containing the template PDFs",
    )
    procedure_options.add_argument(
        "--work_procedure_folder",
        metavar="Work Procedure Folder",
        widget="DirChooser",
        default=default_work_procedure_folder,
        gooey_options={"default_path": default_work_procedure_folder, "full_width": True},
        help="The folder containing the work procedure documents",
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
        fill_nop_from_pdf(data_file)
    elif args.action == "Excel_PDF":
        excel_pdf(
            excel_file=args.excel_file,
            pdf_template=args.pdf_template,
            output_pdf=args.output_pdf
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
