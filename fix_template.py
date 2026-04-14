import re

f = r'c:\bloodbank_project\bloodbank_app\templates\bloodbank_app\patient_request_blood.html'

# Read all contents
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

# Replace all occurrences of value==' with value == '
new_content = re.sub(r"value==\'", "value == '", content)

# Write back strictly
with open(f, 'w', encoding='utf-8') as file:
    file.write(new_content)

print('Done')
