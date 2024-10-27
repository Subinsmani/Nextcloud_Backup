
# Nextcloud Backup Script

This script automates the backup of your Nextcloud instance, including web files, data files, and the database. The backups are stored locally and managed through [Restic](https://restic.net/), with support for email notifications on success or failure. This guide walks through the setup and configuration required to run the script.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [SMTP Configuration](#smtp-configuration)
  - [Database Credentials](#database-credentials)
  - [Restic Repository Setup](#restic-repository-setup)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Testing Notifications](#testing-notifications)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Automated Nextcloud Backup**: Back up the Nextcloud web files, data directory, and database.
- **Restic Integration**: Use Restic for secure and efficient backup storage and pruning.
- **Email Notifications**: Receive email notifications for successful and failed backups.
- **Error Handling**: Includes error handling and logs for troubleshooting.
- **Customizable Paths**: Easily configure backup directories and credentials.

---

## Requirements

- **Python 3.6+**
- **Restic** (Download and install from [here](https://restic.net/))
- **MySQL/MariaDB** for database management
- **SMTP Server** for email notifications (e.g., Office365, Gmail)

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Subinsmani/Nextcloud_Backup.git
   cd Nextcloud_Backup
   ```

2. **Install Dependencies**:
   Ensure Python 3 and Restic are installed on your system.

3. **Install Restic**:
   ```bash
   sudo apt update
   sudo apt install restic
   ```

4. **Create Backup Directories**:
   Create the necessary directories for backups:
   ```bash
   sudo mkdir -p /path/to/backup/webui  # Replace /path/to/backup with your actual backup directory
   sudo mkdir -p /path/to/backup/data
   sudo mkdir -p /path/to/backup/database
   ```

---

## Configuration

### SMTP Configuration

1. **Create `smtp.conf`**:
   In the root directory of the script, create an `smtp.conf` file with your SMTP settings:
   ```ini
   [smtp]
   host = your_smtp_host  # e.g., smtp.office365.com
   port = your_smtp_port  # e.g., 587
   username = your_smtp_username  # e.g., your_email@example.com
   password = your_smtp_password  # Your SMTP password
   from_email = your_from_email  # e.g., your_email@example.com
   to_email = recipient1@example.com, recipient2@example.com  # Comma-separated list of recipients
   ```

### Database Credentials

Update the database credentials in the script:
```python
DB_USER = "your_db_user"  # Database username
DB_PASS = "your_db_password"  # Database password
DB_NAME = "your_db_name"  # Database name
```

### Restic Repository Setup

1. **Initialize the Restic Repository**:
   ```bash
   restic init --repo /path/to/restic-repo  # Replace /path/to/restic-repo with your actual Restic repository path
   ```

2. **Set up Restic Password File**:
   Create a file to store the Restic password:
   ```bash
   echo "your_secure_password" > /path/to/restic-password.txt  # Replace with the actual path for storing Restic password
   chmod 600 /path/to/restic-password.txt
   ```

3. **Update the Script**:
   Set the `RESTIC_REPO` and `RESTIC_PASSWORD_FILE` paths in the script:
   ```python
   RESTIC_REPO = "/path/to/restic-repo"  # Restic repository path
   RESTIC_PASSWORD_FILE = "/path/to/restic-password.txt"  # Path to the Restic password file
   ```

### Environment Variables

To avoid exposing sensitive information, you can set environment variables for sensitive values (optional):
```bash
export RESTIC_PASSWORD="your_secure_password"
export DB_PASS="your_db_password"
```

---

## Usage

1. **Run the Backup Script**:
   Execute the script to perform a backup:
   ```bash
   python3 nextcloud_backup_sync.py
   ```

2. **Options**:
   - `-test-success`: Send a test success email notification.
   - `-test-failure`: Send a test failure email notification.
   - `-restore`: Run the restoration process (functionality should be added).

---

## Testing Notifications

Test the email notification system to ensure it's correctly configured:

- **Success Test**:
   ```bash
   python3 nextcloud_backup_sync.py -test-success
   ```

- **Failure Test**:
   ```bash
   python3 nextcloud_backup_sync.py -test-failure
   ```

---

## Troubleshooting

1. **Backup Directory Not Mounted**:
   - If you see an error about the backup directory not being mounted, ensure your backup storage is correctly mounted:
     ```bash
     mount | grep /path/to/backup  # Replace /path/to/backup with your actual backup path
     ```

2. **SMTP Configuration Errors**:
   - If emails are not sent, verify your `smtp.conf` configuration and ensure the SMTP server is accessible.

3. **Restic Repository Errors**:
   - If you see errors related to the Restic repository, reinitialize it:
     ```bash
     restic unlock --repo /path/to/restic-repo
     restic init --repo /path/to/restic-repo
     ```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

---

## Support

For support or questions, please open an issue in the [GitHub repository](https://github.com/Subinsmani/Nextcloud_Backup/issues).

---