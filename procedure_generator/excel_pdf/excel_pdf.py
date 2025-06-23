import argparse
from typing import Optional
import pandas as pd
from fillpdf import fillpdfs
from ..config_loader import config

def excel_pdf(excel_file: str, pdf_template: str, output_pdf: str):
    # Use default sheet name from config, or first sheet if empty
    sheet_name = config.excel_to_pdf.processing.default_sheet_name
    if not sheet_name:  # If empty string, use first sheet
        sheet_name = 0
    
    # Read Excel file without headers (first column as keys, second as values)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    
    # Convert to dictionary with first column as keys, second as values
    if len(df.columns) >= 2:
        excel_data = dict(zip(df[0], df[1]))
    else:
        raise ValueError("Excel file must have at least 2 columns")

    # Skip empty rows (always enabled)
    excel_data = {k: v for k, v in excel_data.items() if pd.notna(k) and pd.notna(v)}

    # Get field mappings from config
    field_map = config.excel_to_pdf.field_mappings

    # Map Excel data to PDF fields
    pdf_data = {}
    for excel_field, value in excel_data.items():
        # Always trim whitespace
        excel_field_clean = str(excel_field).strip()
        
        # Find matching field mapping
        field_config = None
        for config_excel_field, mapping_config in field_map.items():
            if config_excel_field.lower() == excel_field_clean.lower():
                field_config = mapping_config
                break
        
        if field_config:
            # Extract PDF field name and type from Pydantic model
            try:
                pdf_field = field_config.pdf_field
                field_type = field_config.type
                
                if not pdf_field:
                    print(f"Warning: No pdf_field specified for '{excel_field}' in configuration")
                    continue
            except AttributeError:
                print(f"Warning: Invalid configuration format for '{excel_field}' - missing required attributes")
                continue
            
            # Always trim value if it's a string
            if isinstance(value, str):
                value = value.strip()
            
            # Handle checkbox values - only convert if field type is checkbox
            if field_type == "checkbox" and isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ["yes", "true", "1", "on"]:
                    value = 'Yes'
                elif value_lower in ["no", "false", "0", "off"]:
                    value = 'Off'
            
            pdf_data[str(pdf_field).strip()] = value

    # Fill the PDF
    fillpdfs.write_fillable_pdf(pdf_template, output_pdf, pdf_data)

    print(f"\nFilled PDF saved as: {output_pdf}")
    print(f"Mapped {len(pdf_data)} fields from Excel to PDF")

def main():
    parser = argparse.ArgumentParser(description='Fill PDF form from Excel data')
    parser.add_argument('excel_file', help='Path to the Excel file')
    parser.add_argument('pdf_template', help='Path to the PDF template file')
    parser.add_argument('output_pdf', help='Path for the output PDF file')
    
    args = parser.parse_args()
    
    try:
        excel_pdf(args.excel_file, args.pdf_template, args.output_pdf)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())