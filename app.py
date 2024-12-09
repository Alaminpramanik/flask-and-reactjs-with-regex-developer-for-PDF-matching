from flask import Flask, request, jsonify
import pdfplumber
import pandas as pd

app = Flask(__name__)

def extract_pdf_data(pdf):
    """
    Extract relevant data from the PDF.
    """
    data = []
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            text = page.extract_text()
            # Split lines and process
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ["R&R", "Dumpster"]):  # Adjust keywords as needed
                    parts = line.split()
                    try:
                        description = " ".join(parts[:-3])  # Extract description
                        quantity = parts[-3]
                        unit_cost = parts[-2]
                        rcv_value = parts[-1]
                        data.append({
                            "Description": description,
                            "Quantity": quantity,
                            "Unit Cost": unit_cost,
                            "RCV Value": rcv_value
                        })
                    except IndexError:
                        continue
    return data

def clean_string_to_float(value):
    """
    Utility function to clean currency strings and convert to float safely.
    """
    try:
        return float(value.replace('$', '').replace(',', ''))
    except ValueError:
        return 0.0  # Fallback if the conversion fails

def compare_pdfs(data1, data2):
    """
    Compare two sets of extracted data.
    """
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    comparison = df1.replace('$','').merge(df2.replace('$',''), on="Description", suffixes=('_Your_Estimate', '_Carrier_Estimate'))
    print('comparison', comparison)
    # comparison['Difference_RCV'] = comparison['RCV Value_Your_Estimate'].astype(float) - comparison['RCV Value_Carrier_Estimate'].astype(float)
    # comparison['Difference_Quantity'] = comparison['Quantity_Your_Estimate'].astype(float) - comparison['Quantity_Carrier_Estimate'].astype(float)
    # comparison['Difference_Unit_Cost'] = comparison['Unit Cost_Your_Estimate'].astype(float) - comparison['Unit Cost_Carrier_Estimate'].astype(float)
 # Clean and convert values to floats
    comparison['RCV Value_Your_Estimate'] = comparison['RCV Value_Your_Estimate'].apply(clean_string_to_float)
    comparison['RCV Value_Carrier_Estimate'] = comparison['RCV Value_Carrier_Estimate'].apply(clean_string_to_float)

    comparison['Quantity_Your_Estimate'] = comparison['Quantity_Your_Estimate'].apply(lambda x: float(x.replace('SF', '').replace(',', '')) if isinstance(x, str) else float(x))
    comparison['Quantity_Carrier_Estimate'] = comparison['Quantity_Carrier_Estimate'].apply(lambda x: float(x.replace('SF', '').replace(',', '')) if isinstance(x, str) else float(x))

    comparison['Unit Cost_Your_Estimate'] = comparison['Unit Cost_Your_Estimate'].apply(clean_string_to_float)
    comparison['Unit Cost_Carrier_Estimate'] = comparison['Unit Cost_Carrier_Estimate'].apply(clean_string_to_float)

    # Calculate the differences
    comparison['Difference_RCV'] = comparison['RCV Value_Your_Estimate'] - comparison['RCV Value_Carrier_Estimate']
    comparison['Difference_Quantity'] = comparison['Quantity_Your_Estimate'] - comparison['Quantity_Carrier_Estimate']
    comparison['Difference_Unit_Cost'] = comparison['Unit Cost_Your_Estimate'] - comparison['Unit Cost_Carrier_Estimate']
    return comparison.to_dict(orient='records')

@app.route('/compare', methods=['POST'])
def compare():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Please upload both PDFs"}), 400
    
    pdf1 = request.files['file1']
    pdf2 = request.files['file2']

    data1 = extract_pdf_data(pdf1)
    data2 = extract_pdf_data(pdf2)

    result = compare_pdfs(data1, data2)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
