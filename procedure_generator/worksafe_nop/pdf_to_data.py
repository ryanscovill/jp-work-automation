from fillpdf import fillpdfs
import fitz  # PyMuPDF
import re
import argparse

def show_mupdf_errors(show: bool = True):
    try:
        fitz.TOOLS.mupdf_display_errors(show)
    except AttributeError:
        # Fallback for older versions
        pass
    
def extract_fillable_data(pdf_path) -> dict:
    fields = fillpdfs.get_form_fields(pdf_path)
    fields = {k: v for k, v in fields.items() if "check box" not in k.lower()}

    return fields

def extract_risk_data(pdf_path) -> dict:
    risk_data = {"low risk": 0, "moderate risk": 0, "high risk": 0}

    show_mupdf_errors(False)
    pdf = fitz.open(pdf_path)
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        # Extract text from the page
        text = page.get_text()  # type: ignore
        for risk in risk_data.keys():
            risk_data[risk] += text.lower().count(risk)
    pdf.close()
    show_mupdf_errors(True)

    return risk_data

def separate_name_and_phone(input_string):
    """
    Separates the phone number from the name in a given string.
    Also splits the name into first and last name.
    Handles cases with extra dashes, spaces, or non-standard formats.

    Args:
        input_string (str): The input string containing a name and phone number.

    Returns:
        tuple: A tuple containing the first name, last name, and phone number as separate elements.
    """
    phone_pattern = r"(\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4})"
    match = re.search(phone_pattern, input_string)
    
    if match:
        phone_number = match.group(0)
        name = input_string.replace(phone_number, "").strip(" -")
        name_parts = name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else None
        last_name = name_parts[1] if len(name_parts) > 1 else None
        return first_name, last_name, phone_number
    else:
        return None, None, None

def extract_fillable_data_with_risk(pdf_path) -> dict:
    fields = extract_fillable_data(pdf_path)
    risk_data = extract_risk_data(pdf_path)

    max_risk = max(risk_data.items(), key=lambda x: x[1])
    risk_level_map = {
        "low risk": "Low",
        "moderate risk": "Moderate",
        "high risk": "High"
    }

    fields["FIRST_NAME"], fields["LAST_NAME"], fields["PHONE"] = separate_name_and_phone(fields["PROJECT MANAGER"])
    fields["RISK_CALC"] = risk_level_map[max_risk[0]]

    return fields

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract fillable data from PDF with risk analysis")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    
    args = parser.parse_args()
    
    fields = extract_fillable_data_with_risk(args.pdf_path)
    print(fields)