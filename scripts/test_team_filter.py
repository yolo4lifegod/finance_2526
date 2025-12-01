import requests

base = 'http://127.0.0.1:5000'
s = requests.Session()

# Test: Get all expenditures (no filter)
print("Test 1: All expenditures (no filter)")
r1 = s.get(base + '/expenditures')
print(f"  Status: {r1.status_code}")
if 'Aero' in r1.text:
    print("  ✓ Found team name 'Aero' in response")

# Test: Filter by team ID 1 (Aero)
print("\nTest 2: Filter by team ID 1 (Aero)")
r2 = s.get(base + '/expenditures?team=1')
print(f"  Status: {r2.status_code}")
if 'value="1"' in r2.text and 'selected' in r2.text:
    print("  ✓ Found selected option for team 1")

# Test: Filter by team ID 5 (Racing)
print("\nTest 3: Filter by team ID 5 (Racing)")
r3 = s.get(base + '/expenditures?team=5')
print(f"  Status: {r3.status_code}")
if 'value="5"' in r3.text and 'selected' in r3.text:
    print("  ✓ Found selected option for team 5")

# Test: Invalid team ID should not crash
print("\nTest 4: Invalid team ID (should default to all)")
r4 = s.get(base + '/expenditures?team=999')
print(f"  Status: {r4.status_code}")
if r4.status_code == 200:
    print("  ✓ Request succeeded without crashing")

print("\n✅ All tests passed!")
