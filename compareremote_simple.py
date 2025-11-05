import os
import stat
import paramiko
from datetime import datetime


def compare_folders_metadata(local_dir, sftp, remote_dir):
    print(f"\nComparing local {local_dir} with remote {remote_dir}\n")

    for root, dirs, files in os.walk(local_dir):
        rel_path = os.path.relpath(root, local_dir)
        remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")

        try:
            remote_items = {}
            for f in sftp.listdir(remote_path):
                remote_stat = sftp.stat(f"{remote_path}/{f}")
                if stat.S_ISREG(remote_stat.st_mode):
                    remote_items[f] = remote_stat
            remote_dirs = [
                f
                for f in sftp.listdir(remote_path)
                if stat.S_ISDIR(sftp.stat(f"{remote_path}/{f}").st_mode)
            ]
        except IOError:
            print(f"Missing remote directory: {remote_path}")
            continue

        for f in files:
            local_file = os.path.join(root, f)
            if f not in remote_items:
                print(f"Remote missing file: {remote_path}/{f}")
                continue

            local_size = os.path.getsize(local_file)
            local_mtime = int(os.path.getmtime(local_file))
            remote_stat = remote_items[f]
            remote_size = remote_stat.st_size
            remote_mtime = int(remote_stat.st_mtime)

            if local_size != remote_size or abs(local_mtime - remote_mtime) > 2:
                lm = datetime.fromtimestamp(local_mtime)
                rm = datetime.fromtimestamp(remote_mtime)
                print(f"Mismatch: {remote_path}/{f}")
                print(f"   Local size/time: {local_size} bytes, {lm}")
                print(f"   Remote size/time: {remote_size} bytes, {rm}")
            else:
                print(f"Match: {remote_path}/{f}")

        local_files = set(files)
        extra_remote = [f for f in remote_items.keys() if f not in local_files]
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
    compare_folders_metadata(local_dir, sftp, remote_dir)

    sftp.close()
    ssh.close()
    print("\nMetadata comparison complete.")
