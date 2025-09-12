import json
import os

# Load JSON data
with open("invitees.json", "r") as f:
    invitees = json.load(f)

# Output folder
os.makedirs("emails", exist_ok=True)

for person in invitees:
    email = person.get("Email Address")
    message = person.get("Message")

    if email and message:
        # Create safe filename
        filename = os.path.join("emails", email.replace("@", "_at_").replace(".", "_") + ".txt")
        with open(filename, "w") as f:
            f.write(message)
        print(f"Saved email for {email} to {filename}")