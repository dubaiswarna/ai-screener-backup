"""
Remove ONLY fake AI/Hybrid Screener sections
Keep the REAL S&R Analysis (yfinance)
"""

with open('enhanced_screener.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Step 1: Remove AI Screener section (lines 349-476, i.e., index 348-475)
# Keep everything before line 349 and from line 477 onwards
part1 = lines[:348]
part2 = lines[476:]  # This starts with Hybrid Screener

print(f"After removing AI Screener: {len(part1) + len(part2)} lines")

# Combine
temp = part1 + part2

# Step 2: Remove Hybrid Screener section
# In the new temp, Hybrid Screener starts at old line 477 = new line 349 (348 lines before + line 1)
# Hybrid Screener section is from line 477-727 (251 lines)
# S&R Analysis starts at line 728
# So remove lines 349-599 (251 lines) from temp
final = temp[:348] + temp[599:]

print(f"After removing Hybrid Screener: {len(final)} lines")
print(f"Total removed: {len(lines) - len(final)} lines")

# Write cleaned file
with open('enhanced_screener.py', 'w', encoding='utf-8') as f:
    f.writelines(final)

print("✅ Cleaned! Only REAL S&R Analysis remains!")

