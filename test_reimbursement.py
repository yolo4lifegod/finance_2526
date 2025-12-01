import requests
import time

# Base URL for the Flask app
base_url = 'http://127.0.0.1:5000'

# Test data for reimbursement
test_data = {
    'name': 'Test User',
    'completed_before': 'y',
    'address': '123 Test St',
    'phone': '123-456-7890',
    'design_team': '1',  # Assuming design team ID 1 exists
    'proof_of_purchase': '',  # File upload, will skip for simplicity
    'proof_of_delivery': '',  # File upload, will skip for simplicity
    'line_item': 'Test Item',
    'description': 'Test reimbursement',
    'amount': '100.00',
    'apf_file': ''
}

# Submit reimbursement request
response = requests.post(f'{base_url}/reimbursement', data=test_data)
print(f"Reimbursement submission status: {response.status_code}")
if response.status_code == 200:
    print("Reimbursement submitted successfully")
else:
    print(f"Error: {response.text}")

# Wait a bit for processing
time.sleep(1)

# Check expenditures page
exp_response = requests.get(f'{base_url}/expenditures')
print(f"Expenditures page status: {exp_response.status_code}")
if exp_response.status_code == 200:
    content = exp_response.text
    if '100.0' in content:
        print("SUCCESS: Amount 100.0 found in expenditures table")
    else:
        print("FAILURE: Amount 100.0 not found in expenditures table")
        # Print a snippet of the content for debugging
        print("Expenditures page content snippet:")
        print(content[:1000])  # First 1000 characters
else:
    print(f"Error fetching expenditures: {exp_response.text}")
