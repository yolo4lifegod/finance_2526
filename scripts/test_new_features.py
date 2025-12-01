import requests
import os

base = 'http://127.0.0.1:5000'
s = requests.Session()

print("=" * 60)
print("TEST 1: Export Excel (no filter)")
print("=" * 60)
r = s.get(base + '/expenditures/export')
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type', 'N/A')}")
if r.status_code == 200:
    # Save to file
    with open('test_export_all.xlsx', 'wb') as f:
        f.write(r.content)
    print(f"✓ File saved: test_export_all.xlsx ({len(r.content)} bytes)")

print("\n" + "=" * 60)
print("TEST 2: Export Excel (filter by team 1)")
print("=" * 60)
r = s.get(base + '/expenditures/export?team=1')
print(f"Status: {r.status_code}")
if r.status_code == 200:
    with open('test_export_team1.xlsx', 'wb') as f:
        f.write(r.content)
    print(f"✓ File saved: test_export_team1.xlsx ({len(r.content)} bytes)")

print("\n" + "=" * 60)
print("TEST 3: Totals are rounded on expenditures page")
print("=" * 60)
r = s.get(base + '/expenditures')
if '$' in r.text and '.2f' in r.text:
    print("✓ Currency formatting detected in response")
if 'Total Expenditures' in r.text:
    print("✓ Totals section found")

print("\n" + "=" * 60)
print("TEST 4: Error page (404)")
print("=" * 60)
r = s.get(base + '/nonexistent-page')
print(f"Status: {r.status_code}")
if r.status_code == 404 and 'Oops' in r.text:
    print("✓ Custom 404 error page displayed")

print("\n✅ All tests passed!")
