import os

# The folder path that contains the word documents
procedure_folder = 'Procedure Documents'

# The select field name to get the work procedure
work_procedure_select_field = "WORK_PROCEDURE_SELECT"

def get_file_list():
    docx_files = []
    
    # Walk through root_folder, including all its subdirectories
    for dirpath, dirnames, filenames in os.walk(procedure_folder):
        for filename in filenames:
            # Check if the file is a .docx file
            if filename.endswith('.docx'):
                
                # Add the full path to the docx_files list without the .docx extension
                docx_files.append(os.path.splitext(filename)[0])
                
    return docx_files

def main():
    print(f'''var dropdown = this.getField("{work_procedure_select_field}");
var newOptions = {str(get_file_list())};
dropdown.clearItems();
for (var i = 0; i < newOptions.length; i++) {{
    dropdown.insertItemAt(newOptions[i], newOptions[i], i);
}}''')

    
if __name__ == "__main__":
    main()
