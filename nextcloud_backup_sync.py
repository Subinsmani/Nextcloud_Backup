import os
import subprocess
import signal
import sys
import smtplib
import configparser
from email.mime.text import MIMEText
from datetime import datetime

# Configuration variables (replace these with actual values or load from a secure source)
NEXTCLOUD_WEBUI_DIR = "/path/to/nextcloud/webui"  # Path to Nextcloud web UI directory
NEXTCLOUD_DATA_DIR = "/path/to/nextcloud/data"  # Path to Nextcloud data directory
BACKUP_DIR = "/path/to/backup"  # Path to the main backup directory
WEBUI_BACKUP_DIR = f"{BACKUP_DIR}/webui"
DATA_BACKUP_DIR = f"{BACKUP_DIR}/data"
DB_BACKUP_DIR = f"{BACKUP_DIR}/database"
DB_USER = "your_db_user"  # Database username
DB_PASS = "your_db_password"  # Database password
DB_NAME = "your_db_name"  # Database name
RESTIC_REPO = "/path/to/restic/repo"  # Restic repository path
RESTIC_PASSWORD_FILE = "/path/to/restic-password-file"  # Path to Restic password file
CUSTOMER_NAME = "Customer_Name"  # Replace with customer name when configuring

# Ctrl+C handler
def terminate_script(signal_received, frame):
    print("\nCtrl+C detected. Terminating backup process...")
    subprocess.run(["restic", "unlock", "--password-file", RESTIC_PASSWORD_FILE])
    sys.exit(1)

# Load SMTP configuration
def load_smtp_config():
    config = configparser.ConfigParser()
    config.read("smtp.conf")  # Path to your SMTP configuration file
    smtp_config = {
        "host": config["smtp"]["host"],
        "port": int(config["smtp"]["port"]),
        "username": config["smtp"]["username"],
        "password": config["smtp"]["password"],
        "from_email": config["smtp"]["from_email"],
        "to_email": config["smtp"]["to_email"],
    }
    return smtp_config

# Send email
def send_email(subject, body):
    smtp_config = load_smtp_config()
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_config["from_email"]
    msg["To"] = smtp_config["to_email"]

    # Convert the to_email string into a list of addresses
    recipients = smtp_config["to_email"].split(", ")
    
    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])
            server.sendmail(smtp_config["from_email"], recipients, msg.as_string())
        print("Notification email sent.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")

# Load email template
def load_email_template(template_file, placeholders):
    with open(template_file) as f:
        template = f.read()
    return template.format(**placeholders)

# Notify based on backup status
def notify_backup_status(success=True, step=""):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    placeholders = {"date": date, "backup_dir": BACKUP_DIR, "step": step, "customer_name": CUSTOMER_NAME}
    
    if success:
        subject = f"🔹 Success: {CUSTOMER_NAME} Nextcloud Backup Completed - [Backup Summary]"
        body = load_email_template("email_success_template", placeholders)
    else:
        subject = f"🔻 Alert: {CUSTOMER_NAME} Nextcloud Backup Failed - Immediate Attention Required"
        body = load_email_template("email_failure_template", placeholders)
    
    send_email(subject, body)

# Test email notification
def test_email_notification(success=True):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    placeholders = {"date": date, "backup_dir": BACKUP_DIR, "step": "Test notification", "customer_name": CUSTOMER_NAME}

    if success:
        print("Testing success notification...")
        subject = f"Test: {CUSTOMER_NAME} Nextcloud Backup Success"
        body = load_email_template("email_success_template", placeholders)
    else:
        print("Testing failure notification...")
        subject = f"Test: {CUSTOMER_NAME} Nextcloud Backup Failure"
        body = load_email_template("email_failure_template", placeholders)

    send_email(subject, body)
    print("Test email sent successfully.")

# Check if backup directory is mounted
def check_backup_mount():
    result = subprocess.run(["grep", "-qs", "/mnt/backup", "/proc/mounts"])
    if result.returncode != 0:
        print("Error: Backup directory is not mounted. Please check the CIFS mount.")
        sys.exit(1)
    print("Backup directory is mounted correctly.")

# Perform backup
def perform_backup():
    try:
        # Database backup
        print("Backing up the Nextcloud database...")
        db_backup_result = subprocess.run(
            ["mysqldump", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME],
            stdout=open(f"{DB_BACKUP_DIR}/nextcloud_db_backup.sql", "w")
        )
        if db_backup_result.returncode != 0:
            raise Exception("Database backup failed.")

        # Web UI files sync
        print("Syncing Nextcloud web files...")
        sync_webui_result = subprocess.run(["rsync", "-ah", "--delete", "--info=progress2", "--stats", NEXTCLOUD_WEBUI_DIR, WEBUI_BACKUP_DIR])
        if sync_webui_result.returncode != 0:
            raise Exception("rsync failed while syncing web files.")

        # Data files sync
        print("Syncing Nextcloud data files...")
        sync_data_result = subprocess.run(["rsync", "-ah", "--delete", "--info=progress2", "--stats", NEXTCLOUD_DATA_DIR, DATA_BACKUP_DIR])
        if sync_data_result.returncode != 0:
            raise Exception("rsync failed while syncing data files.")

        # Restic backups
        for path, tag in [(WEBUI_BACKUP_DIR, "webui-backup"), (DATA_BACKUP_DIR, "data-backup"), (f"{DB_BACKUP_DIR}/nextcloud_db_backup.sql", "database-backup")]:
            subprocess.run(["restic", "backup", path, "--repo", RESTIC_REPO, "--password-file", RESTIC_PASSWORD_FILE, "--tag", tag])

        # Pruning old backups
        print("Pruning old backups...")
        subprocess.run(["restic", "forget", "--repo", RESTIC_REPO, "--password-file", RESTIC_PASSWORD_FILE, "--keep-daily", "7", "--prune"])

        print("Backup completed successfully.")
        notify_backup_status(success=True)

    except Exception as e:
        print(f"Backup failed at step: {e}")
        notify_backup_status(success=False, step=str(e))

# Main script logic
if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate_script)
    check_backup_mount()
    
    # Check for test argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "-restore":
            perform_restore()
        elif sys.argv[1] == "-test-success":
            test_email_notification(success=True)
        elif sys.argv[1] == "-test-failure":
            test_email_notification(success=False)
        else:
            print("Invalid option. Use '-restore', '-test-success', or '-test-failure'.")
    else:
        perform_backup()
