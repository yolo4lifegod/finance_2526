import requests

base = 'http://127.0.0.1:5000'
s = requests.Session()

print("Test 1: Grants page (should work)")
r1 = s.get(base + '/grants')
print(f"  Status: {r1.status_code}")
if r1.status_code == 200:
    print("  ✓ Grants page loaded successfully")
else:
    print(f"  ✗ Unexpected status: {r1.status_code}")

print("\nTest 2: Non-existent route (should show error page)")
r2 = s.get(base + '/this-does-not-exist')
print(f"  Status: {r2.status_code}")
if r2.status_code == 404 and 'Oops' in r2.text:
    print("  ✓ Custom 404 error page displayed")
elif r2.status_code == 404:
    print("  ✗ 404 page found but custom error page not shown")
    print(f"  Response snippet: {r2.text[:200]}")
else:
    print(f"  ✗ Unexpected status: {r2.status_code}")

print("\nTest 3: Bad grant ID (should show 404 error page)")
r3 = s.get(base + '/grant/99999')
print(f"  Status: {r3.status_code}")
if r3.status_code == 404 and 'Oops' in r3.text:
    print("  ✓ Custom 404 error page displayed for invalid grant")
elif r3.status_code == 404:
    print("  ✗ 404 page found but custom error page not shown")
else:
    print(f"  ✗ Unexpected status: {r3.status_code}")
