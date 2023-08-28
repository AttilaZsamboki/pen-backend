import os

ssh_key_filename = "Peneszmentesites-key.ppk"  # or "Peneszmentesites-key" without extension
ssh_key_path = os.path.expanduser("~/.ssh/" + ssh_key_filename)

if os.path.isfile(ssh_key_path):
    print("SSH key file found: ", ssh_key_path)
else:
    print("SSH key file not found.")