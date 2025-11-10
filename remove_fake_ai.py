"""
Remove fake AI/Hybrid screener sections from enhanced_screener.py
Keeps only REAL technical analysis (S&R)
"""

with open('enhanced_screener.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Delete lines 491-1234 (Hybrid Screener + duplicate S&R)
# Keep everything before line 491 and everything from line 1235 onwards
cleaned_lines = lines[:490] + lines[1234:]

with open('enhanced_screener.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("✅ Removed fake AI sections!")
print(f"   Original: {len(lines)} lines")
print(f"   Cleaned:  {len(cleaned_lines)} lines")
print(f"   Deleted:  {len(lines) - len(cleaned_lines)} lines")

