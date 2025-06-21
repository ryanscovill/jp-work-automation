import pandas as pd
from fillpdf import fillpdfs
from typing import Optional
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
        
        pdf_field = None
        for config_excel_field, config_pdf_field in field_map.items():
            if config_excel_field.lower() == excel_field_clean.lower():
                pdf_field = config_pdf_field
                break
        
        if pdf_field:
            # Always trim value if it's a string
            if isinstance(value, str):
                value = value.strip()
            pdf_data[str(pdf_field).strip()] = value

    # Fill the PDF
    fillpdfs.write_fillable_pdf(pdf_template, output_pdf, pdf_data)

    print(f"\nFilled PDF saved as: {output_pdf}")
    print(f"Mapped {len(pdf_data)} fields from Excel to PDF")