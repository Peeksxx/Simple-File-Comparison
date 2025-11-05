import os
import hashlib
import paramiko


def hash_file(local_path, sftp=None, remote_path=None):
    """Return SHA256 hash of a local or remote file."""
    sha = hashlib.sha256()
    if sftp and remote_path:
        with sftp.open(remote_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
    else:
        with open(local_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
    return sha.hexdigest()


def compare_folders_sftp(local_dir, sftp, remote_dir):
    print(f"\nComparing local {local_dir} with remote {remote_dir}\n")

    for root, dirs, files in os.walk(local_dir):
        rel_path = os.path.relpath(root, local_dir)
        remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")

        try:
            remote_items = sftp.listdir(remote_path)
        except IOError:
            print(f"Missing remote directory: {remote_path}")
            continue

        for f in files:
            local_file = os.path.join(root, f)
            remote_file = f"{remote_path}/{f}"
            if f not in remote_items:
                print(f"Remote missing file: {remote_file}")
                continue

            local_hash = hash_file(local_file)
            remote_hash = hash_file(None, sftp, remote_file)

            if local_hash != remote_hash:
                print(f"File differs: {remote_file}")
            else:
                print(f"Match: {remote_file}")

        local_files = set(files)
        extra_remote = [
            f
            for f in remote_items
            if f not in local_files and not sftp.stat(f"{remote_path}/{f}").st_mode & 0o40000
        ]
        for f in extra_remote:
            print(f"Extra file on remote: {remote_path}/{f}")


if __name__ == "__main__":
    import getpass

    host = input("Remote server IP (Tailscale): ").strip()
    username = input("SSH username: ").strip()
    password = getpass.getpass("SSH password (or leave blank if using key): ")
    local_dir = input("Path to local folder: ").strip('" ')
    remote_dir = input("Path to remote folder: ").strip('" ')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"\nConnecting to {host}...")
    if password:
        ssh.connect(host, username=username, password=password)
    else:
        ssh.connect(host, username=username)

    sftp = ssh.open_sftp()
    compare_folders_sftp(local_dir, sftp, remote_dir)

    sftp.close()
    ssh.close()
    print("\nComparison complete.")
