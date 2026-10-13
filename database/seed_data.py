import json
from models import db, Lesson, AssessmentQuiz, AssessmentQuestion

def seed_curriculum():
    """Seeds rich Linux command lessons and assessments into the database."""
    if Lesson.query.count() > 0:
        return

    lessons_data = [
        # -------------------------------------------------------------
        # Category 1: Basic Navigation (Beginner)
        # -------------------------------------------------------------
        {
            "slug": "pwd",
            "title": "Print Working Directory (pwd)",
            "category": "Basic Navigation",
            "difficulty": "Beginner",
            "command": "pwd",
            "purpose": "Displays the absolute path of the current working directory where your shell session is currently situated.",
            "syntax": "pwd [-L | -P]",
            "explanation": "In Linux, every process operates within a working directory. The `pwd` command queries the operating system kernel for the current directory inode and prints the full hierarchical path starting from the root `/` directory. It is the essential command for orienting yourself in the virtual filesystem.",
            "examples": json.dumps([
                {"command": "pwd", "desc": "Print current working directory", "output": "/home/user"},
                {"command": "cd documents && pwd", "desc": "Change directory and print new location", "output": "/home/user/documents"}
            ]),
            "expected_output": "/home/user",
            "step_by_step": "1. Shell looks up the $PWD environment variable or asks the kernel via getcwd() system call.\n2. Inode path is traversed up to root '/'.\n3. The absolute path string is output to stdout followed by a newline.",
            "common_mistakes": "• Confusing `pwd` with `passwd` (which changes user passwords).\n• Typing `PWD` in uppercase (Linux command names are case-sensitive).",
            "practice_task": "Check your current directory in the simulator by executing the `pwd` command.",
            "practice_expected_command": "pwd",
            "order": 1
        },
        {
            "slug": "ls",
            "title": "List Directory Contents (ls)",
            "category": "Basic Navigation",
            "difficulty": "Beginner",
            "command": "ls",
            "purpose": "Lists files and subdirectories in the current or specified directory.",
            "syntax": "ls [options] [path]",
            "explanation": "The `ls` command reads directory entries and prints their names. By passing options such as `-l` (long format) you view permissions, owner, group, file size, and modification date. Option `-a` shows hidden files (files beginning with a dot). Combining them as `ls -la` gives complete visibility into directory contents.",
            "examples": json.dumps([
                {"command": "ls", "desc": "List entries in current directory", "output": "documents  notes.txt  scripts  welcome.txt"},
                {"command": "ls -l", "desc": "Detailed long listing", "output": "-rw-r--r-- 1 user user 184 Oct 13 12:00 welcome.txt\ndrwxr-xr-x 1 user user 4096 Oct 13 12:00 documents"},
                {"command": "ls -la", "desc": "List all entries including hidden files and . / ..", "output": "total 16\ndrwxr-xr-x 2 user user 4096 Oct 13 12:00 .\ndrwxr-xr-x 2 user user 4096 Oct 13 12:00 .."}
            ]),
            "expected_output": "documents  notes.txt  scripts  welcome.txt",
            "step_by_step": "1. Reads directory descriptor using opendir() / readdir().\n2. Filters hidden items unless -a or -A is provided.\n3. Formats entries into grid columns or rows with color coding.",
            "common_mistakes": "• Forgetting that hidden files (like .bashrc) require the `-a` flag.\n• Forgetting that `-l` uses lowercase L, not the number 1.",
            "practice_task": "Execute `ls -l` in the simulated terminal to inspect detailed file metadata.",
            "practice_expected_command": "ls -l",
            "order": 2
        },
        {
            "slug": "cd",
            "title": "Change Working Directory (cd)",
            "category": "Basic Navigation",
            "difficulty": "Beginner",
            "command": "cd",
            "purpose": "Changes the current working directory to a target directory in the filesystem.",
            "syntax": "cd [directory_path]",
            "explanation": "The `cd` command is a shell built-in that changes the current working directory for the active shell session. Special symbols include: `.` (current directory), `..` (parent directory), `~` (current user's home directory `/home/user`), and `-` (previous working directory).",
            "examples": json.dumps([
                {"command": "cd documents", "desc": "Move into 'documents' subfolder", "output": ""},
                {"command": "cd ..", "desc": "Move up one level to parent directory", "output": ""},
                {"command": "cd ~", "desc": "Jump directly to user home directory", "output": ""}
            ]),
            "expected_output": "(Prompt updates to user@linux-assistant:~/documents$)",
            "step_by_step": "1. Resolves relative or absolute path against virtual filesystem root.\n2. Verifies target exists and is a directory with execute (+x) permissions.\n3. Updates the shell session's internal working directory pointer and prompt.",
            "common_mistakes": "• Typing `cd documents/` when already inside `documents`.\n• Forgetting the space between `cd` and `..` (typing `cd..` causes command not found in bash).",
            "practice_task": "Navigate into the `documents` directory by typing `cd documents`.",
            "practice_expected_command": "cd documents",
            "order": 3
        },

        # -------------------------------------------------------------
        # Category 2: File and Directory Management (Beginner)
        # -------------------------------------------------------------
        {
            "slug": "mkdir",
            "title": "Make Directories (mkdir)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "mkdir",
            "purpose": "Creates one or more new directories in the file system.",
            "syntax": "mkdir [options] <directory_name>",
            "explanation": "The `mkdir` command creates new directory inodes. If you need to create nested directories in one command (e.g. `projects/python/app`), use the `-p` (parents) flag, which creates any missing intermediate parent folders without raising an error.",
            "examples": json.dumps([
                {"command": "mkdir projects", "desc": "Create a directory called 'projects'", "output": ""},
                {"command": "mkdir -p web/src/components", "desc": "Create nested folder tree", "output": ""}
            ]),
            "expected_output": "(Directory created in virtual filesystem)",
            "step_by_step": "1. Evaluates target directory path.\n2. Verifies parent directory exists and write permission is granted.\n3. Creates the directory node and initializes entries for '.' and '..'.",
            "common_mistakes": "• Trying to create nested folders without `-p`.\n• Including spaces in folder names without quotes (e.g. `mkdir my folder` creates two separate folders).",
            "practice_task": "Create a new folder named `projects` using `mkdir projects`.",
            "practice_expected_command": "mkdir projects",
            "order": 4
        },
        {
            "slug": "touch",
            "title": "Create Empty Files & Update Timestamps (touch)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "touch",
            "purpose": "Creates a new empty file if it does not exist, or updates access and modification timestamps if it already exists.",
            "syntax": "touch [options] <file_name>",
            "explanation": "`touch` is the standard Linux utility for creating new zero-byte files rapidly from the command line. If the file already exists, `touch` updates its metadata modification time without altering its contents.",
            "examples": json.dumps([
                {"command": "touch app.py", "desc": "Create a new empty Python file", "output": ""},
                {"command": "touch file1.txt file2.txt", "desc": "Create multiple files at once", "output": ""}
            ]),
            "expected_output": "(File created in virtual filesystem)",
            "step_by_step": "1. Checks if target file exists in current directory.\n2. If absent, allocates a new inode with default permissions (rw-r--r--).\n3. If present, modifies the file's atime and mtime timestamps.",
            "common_mistakes": "• Expecting `touch` to open an editor like nano or vim.\n• Accidentally overwriting timestamp metadata on critical configuration files.",
            "practice_task": "Create a new file named `server.py` using `touch server.py`.",
            "practice_expected_command": "touch server.py",
            "order": 5
        },
        {
            "slug": "cp",
            "title": "Copy Files and Directories (cp)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "cp",
            "purpose": "Copies files and directories from a source path to a destination path.",
            "syntax": "cp [options] <source> <destination>",
            "explanation": "The `cp` command duplicates files or directories. When copying directories, the recursive `-r` or `-R` option is mandatory; without it, `cp` will omit the directory with an error. You can copy a file to a new name in the same directory or into a different directory.",
            "examples": json.dumps([
                {"command": "cp notes.txt notes_backup.txt", "desc": "Duplicate notes.txt into notes_backup.txt", "output": ""},
                {"command": "cp -r documents backup_docs", "desc": "Recursively copy the documents directory", "output": ""}
            ]),
            "expected_output": "(File duplicated to destination)",
            "step_by_step": "1. Opens source file and reads content streams.\n2. Creates destination file descriptor.\n3. Copies bytes from source to destination and sets matching permissions.",
            "common_mistakes": "• Omitting `-r` when copying folders.\n• Accidentally overwriting an existing destination file without `-i` (interactive prompt).",
            "practice_task": "Copy `notes.txt` to `notes_backup.txt` using `cp notes.txt notes_backup.txt`.",
            "practice_expected_command": "cp notes.txt notes_backup.txt",
            "order": 6
        },
        {
            "slug": "mv",
            "title": "Move or Rename Files and Directories (mv)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "mv",
            "purpose": "Moves files and directories from one path to another, or renames them.",
            "syntax": "mv [options] <source> <destination>",
            "explanation": "In Linux, renaming a file and moving a file are the identical operation: updating the directory link to point to the file inode. `mv` does both seamlessly without needing a separate rename utility.",
            "examples": json.dumps([
                {"command": "mv notes.txt todo.txt", "desc": "Rename notes.txt to todo.txt", "output": ""},
                {"command": "mv welcome.txt documents/", "desc": "Move welcome.txt into the documents folder", "output": ""}
            ]),
            "expected_output": "(File moved/renamed)",
            "step_by_step": "1. Checks source and destination paths.\n2. In same filesystem, updates directory table link without copying data blocks.\n3. Unlinks source name from old directory.",
            "common_mistakes": "• Moving a file to a directory name that doesn't exist, accidentally renaming the file to that word.\n• Overwriting existing target files unknowingly.",
            "practice_task": "Rename `notes.txt` to `todo.txt` using `mv notes.txt todo.txt`.",
            "practice_expected_command": "mv notes.txt todo.txt",
            "order": 7
        },
        {
            "slug": "rm",
            "title": "Remove Files and Directories (rm)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "rm",
            "purpose": "Removes (deletes) files and directory structures permanently from the file system.",
            "syntax": "rm [options] <target>",
            "explanation": "Linux does not have a trash can or Recycle Bin by default. When you run `rm`, the file inode is unlinked and the blocks are marked as free immediately. Use `-r` to recursively delete directories, and `-f` to force deletion without prompting.",
            "examples": json.dumps([
                {"command": "rm welcome.txt", "desc": "Delete regular file welcome.txt", "output": ""},
                {"command": "rm -r scripts", "desc": "Recursively remove scripts folder and its contents", "output": ""}
            ]),
            "expected_output": "(Target deleted from filesystem)",
            "step_by_step": "1. Decrements link count of the file inode.\n2. When link count drops to 0 and no processes hold the file open, blocks are freed.\n3. The directory entry is cleared.",
            "common_mistakes": "• Running `rm -rf /` or deleting files without double-checking the path.\n• Forgetting that `rm` has no built-in undo mechanism.",
            "practice_task": "Remove `welcome.txt` by executing `rm welcome.txt`.",
            "practice_expected_command": "rm welcome.txt",
            "order": 8
        },
        {
            "slug": "rmdir",
            "title": "Remove Empty Directories (rmdir)",
            "category": "File and Directory Management",
            "difficulty": "Beginner",
            "command": "rmdir",
            "purpose": "Removes empty directories only, preventing accidental data loss.",
            "syntax": "rmdir [options] <directory_name>",
            "explanation": "Unlike `rm -r`, `rmdir` refuses to delete any directory that contains files or subdirectories. This provides a safe, non-destructive way to clean up obsolete empty directories in scripts and interactive terminal sessions.",
            "examples": json.dumps([
                {"command": "mkdir empty_folder && rmdir empty_folder", "desc": "Create and safely remove empty folder", "output": ""}
            ]),
            "expected_output": "(Empty directory removed)",
            "step_by_step": "1. Verifies target is a directory.\n2. Inspects directory contents; errors if any file or subfolder is found.\n3. Removes directory inode if empty.",
            "common_mistakes": "• Trying to use `rmdir` on a directory containing files (causes 'Directory not empty' error).",
            "practice_task": "Create an empty folder `temp` and remove it using `mkdir temp && rmdir temp` or `rmdir temp`.",
            "practice_expected_command": "rmdir temp",
            "order": 9
        },

        # -------------------------------------------------------------
        # Category 3: File Viewing (Beginner - Intermediate)
        # -------------------------------------------------------------
        {
            "slug": "cat",
            "title": "Concatenate and Display Files (cat)",
            "category": "File Viewing",
            "difficulty": "Beginner",
            "command": "cat",
            "purpose": "Reads files sequentially, writing their full contents to standard output.",
            "syntax": "cat [options] [file_name...]",
            "explanation": "`cat` is one of the most frequently used Linux utilities. It prints the entire text of a file directly to your terminal. It can also concatenate multiple files into a single stream, or be combined with redirects to write content.",
            "examples": json.dumps([
                {"command": "cat welcome.txt", "desc": "Display full contents of welcome.txt", "output": "Welcome to Linux Commands Learning Assistant!\nUse commands like ls, pwd, mkdir, and cat to explore.\nType 'help' to see all available simulated commands."},
                {"command": "cat /etc/hosts", "desc": "Display virtual network hosts configuration", "output": "127.0.0.1 localhost\n127.0.1.1 linux-learning-assistant"}
            ]),
            "expected_output": "Welcome to Linux Commands Learning Assistant!\nUse commands like ls, pwd, mkdir, and cat to explore.\nType 'help' to see all available simulated commands.",
            "step_by_step": "1. Opens file in read mode.\n2. Streams file buffer chunks to stdout until EOF (End of File) is reached.\n3. Closes file descriptor.",
            "common_mistakes": "• Using `cat` to view massive log files (which floods the terminal screen; use `head` or `less` instead).\n• Viewing binary files, which can scramble terminal character encodings.",
            "practice_task": "Read `welcome.txt` using `cat welcome.txt`.",
            "practice_expected_command": "cat welcome.txt",
            "order": 10
        },
        {
            "slug": "head",
            "title": "Output First Part of Files (head)",
            "category": "File Viewing",
            "difficulty": "Beginner",
            "command": "head",
            "purpose": "Prints the first 10 lines (or specified count) of one or more files.",
            "syntax": "head [-n count] <file_name>",
            "explanation": "When working with large datasets, CSVs, or server logs, you often want to peek at the beginning of the file to see headers or the earliest records without loading the whole file. `head -n 5 file` shows exactly the first 5 lines.",
            "examples": json.dumps([
                {"command": "head -n 2 documents/report.log", "desc": "Print first 2 lines of log file", "output": "2026-10-13 10:00:01 INFO System booted successfully.\n2026-10-13 10:05:22 WARNING High memory usage."}
            ]),
            "expected_output": "2026-10-13 10:00:01 INFO System booted successfully.\n2026-10-13 10:05:22 WARNING High memory usage.",
            "step_by_step": "1. Reads stream line by line.\n2. Counts newline characters until requested count is reached.\n3. Terminates reading early for optimal performance.",
            "common_mistakes": "• Forgetting that default line count is 10 lines.\n• Forgetting the `-n` flag when passing a line count number.",
            "practice_task": "View the first 2 lines of `documents/report.log` using `head -n 2 documents/report.log`.",
            "practice_expected_command": "head -n 2 documents/report.log",
            "order": 11
        },
        {
            "slug": "tail",
            "title": "Output Last Part of Files (tail)",
            "category": "File Viewing",
            "difficulty": "Beginner",
            "command": "tail",
            "purpose": "Prints the last 10 lines (or specified count) of files, commonly used for monitoring live logs.",
            "syntax": "tail [-n count] [-f] <file_name>",
            "explanation": "In system administration, errors and recent events always appear at the end of log files. `tail` lets you inspect the most recent records. In real Linux environments, `tail -f` continuously follows appending data in real time.",
            "examples": json.dumps([
                {"command": "tail -n 2 documents/report.log", "desc": "View the most recent 2 log lines", "output": "2026-10-13 10:12:00 ERROR Connection timeout on port 8080.\n2026-10-13 10:15:30 INFO Service recovered."}
            ]),
            "expected_output": "2026-10-13 10:12:00 ERROR Connection timeout on port 8080.\n2026-10-13 10:15:30 INFO Service recovered.",
            "step_by_step": "1. Seeks toward the end of the file descriptor.\n2. Collects the trailing N lines.\n3. Flushes them to stdout.",
            "common_mistakes": "• Confusing `head` (top of file) with `tail` (bottom of file).",
            "practice_task": "View the last 2 lines of `documents/report.log` using `tail -n 2 documents/report.log`.",
            "practice_expected_command": "tail -n 2 documents/report.log",
            "order": 12
        },

        # -------------------------------------------------------------
        # Category 4: Text Searching & Processing (Intermediate)
        # -------------------------------------------------------------
        {
            "slug": "grep",
            "title": "Print Lines Matching a Pattern (grep)",
            "category": "Text Searching",
            "difficulty": "Intermediate",
            "command": "grep",
            "purpose": "Searches for matching text strings or regular expressions within files.",
            "syntax": "grep [options] <pattern> <file_name>",
            "explanation": "`grep` (Global Regular Expression Print) is the gold standard for searching text in Linux. It filters streams and files, outputting only lines that contain the pattern. Flags include `-i` (case-insensitive), `-v` (invert match), and `-n` (show line numbers).",
            "examples": json.dumps([
                {"command": "grep ERROR documents/report.log", "desc": "Find lines containing 'ERROR'", "output": "2026-10-13 10:12:00 ERROR Connection timeout on port 8080."},
                {"command": "grep -i info documents/report.log", "desc": "Case-insensitive search for 'info'", "output": "2026-10-13 10:00:01 INFO System booted successfully.\n2026-10-13 10:15:30 INFO Service recovered."}
            ]),
            "expected_output": "2026-10-13 10:12:00 ERROR Connection timeout on port 8080.",
            "step_by_step": "1. Compiles search string into regex pattern.\n2. Iterates over each line in the target file.\n3. Evaluates pattern match; if matched, writes line to stdout with highlighting.",
            "common_mistakes": "• Forgetting that grep is case-sensitive by default (use `-i` for case-insensitivity).\n• Searching phrases with spaces without enclosing them in quotes.",
            "practice_task": "Search for lines containing `ERROR` in `documents/report.log` using `grep ERROR documents/report.log`.",
            "practice_expected_command": "grep ERROR documents/report.log",
            "order": 13
        },
        {
            "slug": "find",
            "title": "Search for Files in a Directory Hierarchy (find)",
            "category": "Text Searching",
            "difficulty": "Intermediate",
            "command": "find",
            "purpose": "Recursively searches directories for files and folders matching specified criteria.",
            "syntax": "find <starting_path> -name '<pattern>'",
            "explanation": "Unlike `ls`, `find` recursively crawls subdirectories to locate files based on name, size, type, or modification time. The `-name` parameter matches file globbing patterns like `*.txt` or `*.sh`.",
            "examples": json.dumps([
                {"command": "find . -name \"*.txt\"", "desc": "Find all text files in current directory and subdirectories", "output": "./notes.txt\n./welcome.txt"},
                {"command": "find /home/user -name \"*.sh\"", "desc": "Find all shell scripts in user home", "output": "/home/user/scripts/backup.sh"}
            ]),
            "expected_output": "./notes.txt\n./welcome.txt",
            "step_by_step": "1. Begins directory tree traversal at designated root path.\n2. Checks each file node against filter predicates (-name, -type, -size).\n3. Emits matching paths to stdout.",
            "common_mistakes": "• Not enclosing wildcard patterns like `*.txt` in quotes, which causes the shell to expand them before find runs.\n• Forgetting the starting directory parameter.",
            "practice_task": "Find all `.txt` files in the current folder using `find . -name \"*.txt\"`.",
            "practice_expected_command": "find . -name \"*.txt\"",
            "order": 14
        },
        {
            "slug": "wc",
            "title": "Word, Line, and Character Count (wc)",
            "category": "Text Searching",
            "difficulty": "Intermediate",
            "command": "wc",
            "purpose": "Counts newlines, words, and byte counts for files or piped input.",
            "syntax": "wc [options] <file_name>",
            "explanation": "`wc` (word count) provides statistics about text streams. Using `wc -l` counts lines, `wc -w` counts words, and `wc -c` counts characters/bytes. It is frequently combined with pipes to count search matches.",
            "examples": json.dumps([
                {"command": "wc -l notes.txt", "desc": "Count lines in notes.txt", "output": "2 notes.txt"},
                {"command": "wc notes.txt", "desc": "Display lines, words, and characters", "output": "   2   14   95 notes.txt"}
            ]),
            "expected_output": "2 notes.txt",
            "step_by_step": "1. Scans text buffer.\n2. Increments counters on newline characters and whitespace delimiters.\n3. Formats and prints totals.",
            "common_mistakes": "• Assuming `wc` without flags only counts words (it outputs lines, words, and bytes).",
            "practice_task": "Count total lines in `notes.txt` using `wc -l notes.txt`.",
            "practice_expected_command": "wc -l notes.txt",
            "order": 15
        },

        # -------------------------------------------------------------
        # Category 5: File Permissions (Intermediate)
        # -------------------------------------------------------------
        {
            "slug": "chmod",
            "title": "Change File Mode Bits and Permissions (chmod)",
            "category": "File Permissions",
            "difficulty": "Intermediate",
            "command": "chmod",
            "purpose": "Modifies access permissions (read, write, execute) for user, group, and others.",
            "syntax": "chmod [mode] <file_or_directory>",
            "explanation": "Linux permissions are divided into three tiers: User (Owner), Group, and Others. Permissions consist of Read (r=4), Write (w=2), and Execute (x=1). Octal modes sum these values: 7 (rwx), 6 (rw-), 5 (r-x). Mode `755` grants full rights to the owner and read/execute to group and others.",
            "examples": json.dumps([
                {"command": "chmod 755 scripts/backup.sh", "desc": "Make script executable (rwxr-xr-x)", "output": ""},
                {"command": "chmod 644 notes.txt", "desc": "Set standard read/write for user and read for others", "output": ""}
            ]),
            "expected_output": "(Permissions updated in virtual filesystem)",
            "step_by_step": "1. Parses octal or symbolic permission mask.\n2. Verifies calling user is file owner or superuser.\n3. Updates inode permission bitmask in the virtual filesystem.",
            "common_mistakes": "• Setting `777` permissions carelessly in production environments (major security risk).\n• Forgetting that executing a directory requires the +x permission bit.",
            "practice_task": "Set permissions on `scripts/backup.sh` to `755` using `chmod 755 scripts/backup.sh`.",
            "practice_expected_command": "chmod 755 scripts/backup.sh",
            "order": 16
        },
        {
            "slug": "chown",
            "title": "Change File Owner and Group (chown)",
            "category": "File Permissions",
            "difficulty": "Intermediate",
            "command": "chown",
            "purpose": "Changes the user and/or group ownership of files and directories.",
            "syntax": "chown [owner][:group] <target>",
            "explanation": "Every Linux file is tagged with a UID (owner) and GID (group). `chown` allows system administrators to transfer file ownership to another user or group.",
            "examples": json.dumps([
                {"command": "chown user:user notes.txt", "desc": "Set owner and group of notes.txt to 'user'", "output": ""}
            ]),
            "expected_output": "(Ownership updated in virtual filesystem)",
            "step_by_step": "1. Resolves username and groupname to UID/GID.\n2. Invokes chown inode update.\n3. Refreshes file entry properties.",
            "common_mistakes": "• Non-root users cannot change file ownership to another user in standard Linux without sudo.",
            "practice_task": "Update ownership of `notes.txt` using `chown user:user notes.txt`.",
            "practice_expected_command": "chown user:user notes.txt",
            "order": 17
        },

        # -------------------------------------------------------------
        # Category 6: Process Management (Intermediate)
        # -------------------------------------------------------------
        {
            "slug": "ps",
            "title": "Report Current Process Snapshot (ps)",
            "category": "Process Management",
            "difficulty": "Intermediate",
            "command": "ps",
            "purpose": "Displays information about active processes currently running on the system.",
            "syntax": "ps [options]",
            "explanation": "The `ps` command inspects the Linux `/proc` filesystem and summarizes executing programs. Common invocations include `ps` for current shell processes, and `ps aux` or `ps -ef` to list every active system daemon across all users.",
            "examples": json.dumps([
                {"command": "ps", "desc": "Show processes running in current terminal", "output": "  PID TTY          TIME CMD\n 1042 pts/0    00:00:01 bash\n 1580 pts/0    00:00:01 python"},
                {"command": "ps aux", "desc": "Detailed snapshot of all system processes", "output": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.1  15240  4200 ?        Ss   10:00   0:00 systemd"}
            ]),
            "expected_output": "  PID TTY          TIME CMD\n 1042 pts/0    00:00:01 bash\n 1580 pts/0    00:00:01 python",
            "step_by_step": "1. Scans virtual process table.\n2. Retrieves PID, execution state, memory, and command invocation line.\n3. Formats tabular process report.",
            "common_mistakes": "• Believing `ps` is live/continuous (it is a static single-frame snapshot; use `top` for live monitoring).",
            "practice_task": "List active processes by running `ps`.",
            "practice_expected_command": "ps",
            "order": 18
        },
        {
            "slug": "top",
            "title": "Display Live Process Activity (top)",
            "category": "Process Management",
            "difficulty": "Intermediate",
            "command": "top",
            "purpose": "Displays dynamic, real-time CPU, memory, and task performance metrics.",
            "syntax": "top",
            "explanation": "`top` displays a dashboard of system health, showing uptime, load average, CPU breakdown (user, system, idle), memory usage, and a sorted list of top resource-consuming processes.",
            "examples": json.dumps([
                {"command": "top", "desc": "Inspect real-time CPU and process metrics", "output": "Tasks: 5 total, 1 running, 4 sleeping\n%Cpu(s): 1.5 us, 0.8 sy, 97.5 id\nMiB Mem : 3900 total, 2400 free"}
            ]),
            "expected_output": "Tasks: 5 total, 1 running, 4 sleeping\n%Cpu(s): 1.5 us, 0.8 sy, 97.5 id\nMiB Mem : 3900 total, 2400 free",
            "step_by_step": "1. Queries kernel cpu and memory counters.\n2. Calculates differential utilization rates.\n3. Paints console dashboard.",
            "common_mistakes": "• In real shells, not knowing that pressing `q` exits the top dashboard.",
            "practice_task": "Run `top` to view system performance and running tasks.",
            "practice_expected_command": "top",
            "order": 19
        },
        {
            "slug": "kill",
            "title": "Send Signals to Terminate Processes (kill)",
            "category": "Process Management",
            "difficulty": "Intermediate",
            "command": "kill",
            "purpose": "Sends a termination signal (such as SIGTERM or SIGKILL) to a process by its PID.",
            "syntax": "kill [-signal] <PID>",
            "explanation": "When an application hangs or needs to be stopped, `kill` delivers an OS signal to the target Process ID. Default is `kill <PID>` which sends SIGTERM (Signal 15), giving the program a chance to save and exit cleanly. `kill -9 <PID>` sends SIGKILL, forcing immediate termination.",
            "examples": json.dumps([
                {"command": "kill 1580", "desc": "Gracefully terminate Python process PID 1580", "output": ""}
            ]),
            "expected_output": "(Process terminated)",
            "step_by_step": "1. Looks up process table by target PID.\n2. Dispatches kernel signal to process thread group.\n3. Process handles signal or is evicted from memory.",
            "common_mistakes": "• Jumping immediately to `kill -9` without attempting a graceful `kill` first.\n• Passing program name instead of PID (use `pkill` for program names).",
            "practice_task": "Terminate process PID 1580 using `kill 1580`.",
            "practice_expected_command": "kill 1580",
            "order": 20
        },

        # -------------------------------------------------------------
        # Category 7: System Information (Beginner)
        # -------------------------------------------------------------
        {
            "slug": "uname",
            "title": "Print System and Kernel Information (uname)",
            "category": "System Information",
            "difficulty": "Beginner",
            "command": "uname",
            "purpose": "Prints details about the operating system kernel, architecture, and hostname.",
            "syntax": "uname [options]",
            "explanation": "`uname` (Unix Name) tells you the operating system kernel release and architecture. Running `uname -a` displays all parameters: OS name, network node hostname, kernel release version, build timestamp, machine architecture (e.g. x86_64), and platform.",
            "examples": json.dumps([
                {"command": "uname", "desc": "Print kernel name", "output": "Linux"},
                {"command": "uname -a", "desc": "Print all system kernel information", "output": "Linux linux-learning-assistant 6.8.0-45-generic #45-Ubuntu x86_64 GNU/Linux"}
            ]),
            "expected_output": "Linux",
            "step_by_step": "1. Executes sysinfo() system call.\n2. Retrieves kernel release and machine hardware details.\n3. Prints formatted string.",
            "common_mistakes": "• Expecting `uname` to print Linux distribution name like Ubuntu or Debian (distribution info is found in `/etc/os-release`).",
            "practice_task": "Print kernel details using `uname -a`.",
            "practice_expected_command": "uname -a",
            "order": 21
        },
        {
            "slug": "whoami",
            "title": "Print Effective User ID (whoami)",
            "category": "System Information",
            "difficulty": "Beginner",
            "command": "whoami",
            "purpose": "Prints the username of the user currently logged in and executing commands.",
            "syntax": "whoami",
            "explanation": "Indispensable when switching users or troubleshooting permissions. `whoami` confirms whether your shell is running as an unprivileged user (`user`) or as the superuser (`root`).",
            "examples": json.dumps([
                {"command": "whoami", "desc": "Print current username", "output": "user"}
            ]),
            "expected_output": "user",
            "step_by_step": "1. Retrieves effective user ID (euid).\n2. Queries user database for corresponding username.\n3. Prints username string.",
            "common_mistakes": "• Assuming `whoami` shows all logged-in users (use `who` or `w` for all logged-in users).",
            "practice_task": "Check your active username with `whoami`.",
            "practice_expected_command": "whoami",
            "order": 22
        },
        {
            "slug": "date",
            "title": "Display or Set System Date and Time (date)",
            "category": "System Information",
            "difficulty": "Beginner",
            "command": "date",
            "purpose": "Displays the current system date, time, and timezone.",
            "syntax": "date [options] [+format]",
            "explanation": "`date` reads the system clock and prints the formatted date and time. It can also format custom timestamps using formatting specifiers (e.g. `date +%Y-%m-%d`), which is invaluable in automated backup scripts.",
            "examples": json.dumps([
                {"command": "date", "desc": "Display full current date and time", "output": "Tue Oct 13 12:00:00 UTC 2026"}
            ]),
            "expected_output": "Tue Oct 13 12:00:00 UTC 2026",
            "step_by_step": "1. Queries the hardware real-time clock and kernel time counter.\n2. Applies local timezone offset.\n3. Prints formatted calendar time.",
            "common_mistakes": "• Attempting to set system date without root/sudo privileges.",
            "practice_task": "Display current date and time by executing `date`.",
            "practice_expected_command": "date",
            "order": 23
        },
        {
            "slug": "df",
            "title": "Report File System Disk Space Usage (df)",
            "category": "System Information",
            "difficulty": "Beginner",
            "command": "df",
            "purpose": "Displays available and used disk space across mounted filesystems.",
            "syntax": "df [options]",
            "explanation": "`df` (Disk Free) shows the capacity, used space, free space, and mount points of all attached storage partitions. Passing `-h` displays sizes in human-readable units (Gigabytes, Megabytes) instead of raw 1K blocks.",
            "examples": json.dumps([
                {"command": "df -h", "desc": "Display human-readable disk utilization", "output": "Filesystem Size Used Avail Use% Mounted on\n/dev/root 50G 14G 34G 30% /"}
            ]),
            "expected_output": "Filesystem Size Used Avail Use% Mounted on\n/dev/root 50G 14G 34G 30% /",
            "step_by_step": "1. Inspects /proc/mounts and /etc/fstab.\n2. Reads filesystem superblock metadata for block allocations.\n3. Formats table showing utilization percentages.",
            "common_mistakes": "• Confusing `df` (disk partition space) with `du` (individual file or directory space).",
            "practice_task": "Check disk space in human-readable format using `df -h`.",
            "practice_expected_command": "df -h",
            "order": 24
        },
        {
            "slug": "free",
            "title": "Display Amount of Free and Used Memory (free)",
            "category": "System Information",
            "difficulty": "Beginner",
            "command": "free",
            "purpose": "Displays the total, used, and available physical RAM and swap space.",
            "syntax": "free [options]",
            "explanation": "`free` extracts memory metrics from `/proc/meminfo`. Option `-m` displays figures in Megabytes, while `-h` displays human-readable units. The 'available' column shows how much memory can be allocated to new applications without swapping.",
            "examples": json.dumps([
                {"command": "free -m", "desc": "Display memory statistics in Megabytes", "output": " total used free shared buff/cache available\nMem: 3900 850 2400 15 650 2900\nSwap: 2048 0 2048"}
            ]),
            "expected_output": " total used free shared buff/cache available\nMem: 3900 850 2400 15 650 2900\nSwap: 2048 0 2048",
            "step_by_step": "1. Reads /proc/meminfo.\n2. Computes active, inactive, buffered, cached, and swap amounts.\n3. Displays summary table.",
            "common_mistakes": "• Panic over low 'free' memory: in Linux, unused RAM is automatically used for disk caching (buff/cache) and is instantly reclaimed when applications need it.",
            "practice_task": "Display memory usage in megabytes using `free -m`.",
            "practice_expected_command": "free -m",
            "order": 25
        },

        # -------------------------------------------------------------
        # Category 8: User and Group Management (Intermediate)
        # -------------------------------------------------------------
        {
            "slug": "id",
            "title": "Print Real and Effective User and Group IDs (id)",
            "category": "User and Group Management",
            "difficulty": "Intermediate",
            "command": "id",
            "purpose": "Displays user identity number (UID), primary group ID (GID), and all supplementary groups.",
            "syntax": "id [options] [username]",
            "explanation": "Access control in Linux is grounded in numeric UIDs and GIDs. Running `id` tells you exactly which security groups your user account belongs to (e.g. `sudo`, `adm`, `docker`), determining whether you can perform administrative tasks.",
            "examples": json.dumps([
                {"command": "id", "desc": "Display current user identity and group memberships", "output": "uid=1000(user) gid=1000(user) groups=1000(user),4(adm),27(sudo)"}
            ]),
            "expected_output": "uid=1000(user) gid=1000(user) groups=1000(user),4(adm),27(sudo)",
            "step_by_step": "1. Reads user identity database.\n2. Gathers primary and secondary group memberships from /etc/group.\n3. Prints combined UID/GID listing.",
            "common_mistakes": "• Editing /etc/passwd or /etc/group directly with a regular text editor instead of using safe administrative tools like vipw or usermod.",
            "practice_task": "Inspect your UID and group memberships using `id`.",
            "practice_expected_command": "id",
            "order": 26
        },

        # -------------------------------------------------------------
        # Category 9: Package Management (Intermediate - Advanced)
        # -------------------------------------------------------------
        {
            "slug": "apt",
            "title": "Advanced Package Tool (apt)",
            "category": "Package Management",
            "difficulty": "Intermediate",
            "command": "apt",
            "purpose": "Manages software packages (installation, update, removal) on Debian and Ubuntu systems.",
            "syntax": "apt [options] command [package_name]",
            "explanation": "`apt` is the user-friendly interface for package management. Common workflows include: `apt update` (refreshes package index lists from internet repositories), `apt install <package>` (downloads and installs applications with dependencies), and `apt remove <package>`.",
            "examples": json.dumps([
                {"command": "apt update", "desc": "Update local package index lists", "output": "Reading package lists... Done\nBuilding dependency tree... Done\nAll packages are up to date."},
                {"command": "apt install nginx", "desc": "Install Nginx web server", "output": "Reading package lists... Done\nUnpacking nginx... Done\nSetting up nginx... Done"}
            ]),
            "expected_output": "Reading package lists... Done\nBuilding dependency tree... Done\nAll packages are up to date.",
            "step_by_step": "1. Fetches repository package manifests.\n2. Computes dependency graph and resolves version conflicts.\n3. Downloads .deb archives, unpacks binaries, and triggers post-install configuration scripts.",
            "common_mistakes": "• Confusing `apt update` (updates repository lists) with `apt upgrade` (actually upgrades installed software).\n• Forgetting that software installation requires administrative (sudo) privileges.",
            "practice_task": "Refresh repository package lists using `apt update`.",
            "practice_expected_command": "apt update",
            "order": 27
        },

        # -------------------------------------------------------------
        # Category 10: Networking Commands (Advanced)
        # -------------------------------------------------------------
        {
            "slug": "ping",
            "title": "Send ICMP ECHO_REQUEST to Network Hosts (ping)",
            "category": "Networking Commands",
            "difficulty": "Advanced",
            "command": "ping",
            "purpose": "Tests network connectivity and measures round-trip latency to a remote host.",
            "syntax": "ping [options] <host>",
            "explanation": "`ping` sends ICMP (Internet Control Message Protocol) packets to a target IP address or domain name and listens for ICMP Echo Reply packets. It reports packet loss percentages and round-trip times (RTT) in milliseconds.",
            "examples": json.dumps([
                {"command": "ping -c 3 google.com", "desc": "Send 3 ping packets to google.com", "output": "3 packets transmitted, 3 received, 0% packet loss\nrtt min/avg/max = 13.8/14.0/14.2 ms"}
            ]),
            "expected_output": "3 packets transmitted, 3 received, 0% packet loss\nrtt min/avg/max = 13.8/14.0/14.2 ms",
            "step_by_step": "1. Resolves hostname to IP address via DNS.\n2. Constructs raw ICMP packet and dispatches over network interface.\n3. Awaits reply and computes timestamp latency delta.",
            "common_mistakes": "• In Linux, pinging without `-c` sends packets infinitely until you press Ctrl+C.",
            "practice_task": "Send 3 ping packets to google.com using `ping -c 3 google.com`.",
            "practice_expected_command": "ping -c 3 google.com",
            "order": 28
        },
        {
            "slug": "curl",
            "title": "Transfer Data to or from a Server (curl)",
            "category": "Networking Commands",
            "difficulty": "Advanced",
            "command": "curl",
            "purpose": "Transfers data using supported protocols (HTTP, HTTPS, FTP, etc.) directly in the terminal.",
            "syntax": "curl [options] <URL>",
            "explanation": "`curl` is the essential tool for testing REST APIs, downloading web pages, sending HTTP headers, and inspecting web server responses directly from the command line.",
            "examples": json.dumps([
                {"command": "curl http://example.com", "desc": "Fetch HTML content of example.com", "output": "<!doctype html>\n<html>\n<h1>Connected to http://example.com</h1>\n</html>"}
            ]),
            "expected_output": "<!doctype html>\n<html>\n<h1>Connected to http://example.com</h1>\n</html>",
            "step_by_step": "1. Establishes TCP connection and TLS handshake with remote host.\n2. Dispatches HTTP request verb (GET, POST).\n3. Streams response payload to terminal stdout.",
            "common_mistakes": "• Forgetting that curl prints output to screen by default; use `-O` or `-o <file>` to save output to a file.",
            "practice_task": "Fetch web response from example.com using `curl http://example.com`.",
            "practice_expected_command": "curl http://example.com",
            "order": 29
        },

        # -------------------------------------------------------------
        # Category 11: Shell Scripting & Pipes (Advanced)
        # -------------------------------------------------------------
        {
            "slug": "pipes_redirection",
            "title": "Pipes and Redirection (|, >, >>)",
            "category": "Shell Scripting and Pipes",
            "difficulty": "Advanced",
            "command": "echo",
            "purpose": "Combines modular Linux utilities together using standard streams (stdin, stdout, stderr).",
            "syntax": "command1 | command2   OR   command > file.txt   OR   command >> file.txt",
            "explanation": "The Unix philosophy is built around small programs that do one thing well, combined together through pipes. The pipe `|` sends the stdout of the left program directly into the stdin of the right program. The `>` operator redirects output to overwrite a file, while `>>` appends to the file.",
            "examples": json.dumps([
                {"command": "echo \"Hello Linux\" > notes.txt", "desc": "Write text into notes.txt", "output": ""},
                {"command": "echo \"More content\" >> notes.txt", "desc": "Append text to notes.txt", "output": ""},
                {"command": "cat documents/report.log | grep ERROR", "desc": "Pipe log file into grep filter", "output": "2026-10-13 10:12:00 ERROR Connection timeout on port 8080."}
            ]),
            "expected_output": "Hello Linux",
            "step_by_step": "1. Shell creates an anonymous inter-process pipe buffer.\n2. Left process writes to pipe write descriptor.\n3. Right process reads from pipe read descriptor simultaneously.",
            "common_mistakes": "• Using `>` instead of `>>`, accidentally obliterating existing file content.\n• Forgetting that pipes connect stdout to stdin (not to command arguments).",
            "practice_task": "Pipe log file through grep by executing `cat documents/report.log | grep ERROR`.",
            "practice_expected_command": "cat documents/report.log | grep ERROR",
            "order": 30
        }
    ]

    for item in lessons_data:
        lesson = Lesson(
            lesson_slug=item["slug"],
            title=item["title"],
            category=item["category"],
            difficulty_level=item["difficulty"],
            command_name=item["command"],
            purpose=item["purpose"],
            syntax=item["syntax"],
            explanation=item["explanation"],
            practical_examples=item["examples"],
            expected_output=item["expected_output"],
            step_by_step=item["step_by_step"],
            common_mistakes=item["common_mistakes"],
            practice_task=item["practice_task"],
            practice_expected_command=item["practice_expected_command"],
            lesson_order=item["order"]
        )
        db.session.add(lesson)

    # -------------------------------------------------------------
    # Seed Assessment Quizzes & Questions
    # -------------------------------------------------------------
    quizzes = [
        {
            "slug": "beginner-linux-foundations",
            "title": "Beginner Linux Fundamentals Quiz",
            "description": "Test your core knowledge of directory navigation, file creation, listing flags, and directory manipulation.",
            "difficulty": "Beginner",
            "passing_score": 70,
            "time_limit": 10,
            "questions": [
                {
                    "text": "Which Linux command displays the absolute path of your current working directory?",
                    "type": "mcq",
                    "a": "dir",
                    "b": "pwd",
                    "c": "cd",
                    "d": "whereami",
                    "correct": "B",
                    "explanation": "`pwd` stands for Print Working Directory and prints the absolute path from the root directory."
                },
                {
                    "text": "Which flag should be passed to `ls` to display hidden files that start with a period (.)?",
                    "type": "syntax",
                    "a": "-l",
                    "b": "-h",
                    "c": "-a",
                    "d": "-r",
                    "correct": "C",
                    "explanation": "The `-a` (all) flag instructs `ls` not to ignore entries starting with `.`."
                },
                {
                    "text": "What happens if you run `mkdir -p projects/python/app` when none of the folders exist yet?",
                    "type": "scenario",
                    "a": "It errors with 'Parent directory does not exist'",
                    "b": "It creates all missing intermediate directories (projects, python, and app)",
                    "c": "It only creates the 'app' directory in the current folder",
                    "d": "It prompts you for confirmation for each directory",
                    "correct": "B",
                    "explanation": "The `-p` (parents) flag creates parent directories as needed without throwing an error."
                },
                {
                    "text": "How do you navigate up one directory level to the parent directory in bash?",
                    "type": "syntax",
                    "a": "cd /",
                    "b": "cd ~",
                    "c": "cd ..",
                    "d": "cd -",
                    "correct": "C",
                    "explanation": "`..` refers to the parent directory in Unix directory structures."
                },
                {
                    "text": "Which command is used to duplicate a regular file named `data.txt` to `data_backup.txt`?",
                    "type": "mcq",
                    "a": "mv data.txt data_backup.txt",
                    "b": "cp data.txt data_backup.txt",
                    "c": "touch data_backup.txt data.txt",
                    "d": "cat data.txt > backup",
                    "correct": "B",
                    "explanation": "`cp <source> <dest>` makes an exact duplicate of the file."
                }
            ]
        },
        {
            "slug": "intermediate-linux-sysadmin",
            "title": "Intermediate Operations & Text Manipulation",
            "description": "Assess your skills with file permissions, grep, process inspection, redirection, and system monitoring.",
            "difficulty": "Intermediate",
            "passing_score": 70,
            "time_limit": 15,
            "questions": [
                {
                    "text": "What does the permission string `-rwxr-xr--` signify for user, group, and others?",
                    "type": "mcq",
                    "a": "User has rwx (7), Group has r-x (5), Others have r-- (4)",
                    "b": "User has rw- (6), Group has rwx (7), Others have --- (0)",
                    "c": "User has rwx (7), Group has rwx (7), Others have rwx (7)",
                    "d": "User has r-x (5), Group has r-x (5), Others have r-- (4)",
                    "correct": "A",
                    "explanation": "Splitting `-rwxr-xr--`: User=rwx (4+2+1=7), Group=r-x (4+1=5), Others=r-- (4)."
                },
                {
                    "text": "Which command searches case-insensitively for the string 'error' in file `syslog`?",
                    "type": "syntax",
                    "a": "find -i 'error' syslog",
                    "b": "grep -i 'error' syslog",
                    "c": "cat syslog | find error",
                    "d": "search -case error syslog",
                    "correct": "B",
                    "explanation": "`grep -i` performs a case-insensitive search."
                },
                {
                    "text": "Which Linux signal does `kill <PID>` send by default when no signal number is specified?",
                    "type": "scenario",
                    "a": "SIGKILL (Signal 9)",
                    "b": "SIGTERM (Signal 15)",
                    "c": "SIGINT (Signal 2)",
                    "d": "SIGHUP (Signal 1)",
                    "correct": "B",
                    "explanation": "Default kill sends SIGTERM (15), enabling the process to perform cleanup before exit."
                },
                {
                    "text": "What is the key difference between output redirection operators `>` and `>>`?",
                    "type": "syntax",
                    "a": "`>` appends to file, `>>` overwrites file",
                    "b": "`>` overwrites file, `>>` appends to file",
                    "c": "Both overwrite files identically",
                    "d": "`>>` is only for error output (stderr)",
                    "correct": "B",
                    "explanation": "`>` overwrites target file content; `>>` appends to the end of the file."
                },
                {
                    "text": "Which command displays free and used physical memory and swap in Megabytes?",
                    "type": "mcq",
                    "a": "df -m",
                    "b": "free -m",
                    "c": "mem -m",
                    "d": "du -m",
                    "correct": "B",
                    "explanation": "`free -m` queries /proc/meminfo and formats memory values in Megabytes."
                }
            ]
        },
        {
            "slug": "certification-mastery-exam",
            "title": "Comprehensive Linux Certification Examination",
            "description": "Comprehensive practical and theoretical examination required for the Linux Commands Learning Assistant Certificate of Competency.",
            "difficulty": "Comprehensive",
            "passing_score": 75,
            "time_limit": 20,
            "questions": [
                {
                    "text": "You want to find all files ending in `.log` modified in the last 7 days under `/var/log`. Which tool is designed for this?",
                    "type": "scenario",
                    "a": "ls",
                    "b": "grep",
                    "c": "find",
                    "d": "cat",
                    "correct": "C",
                    "explanation": "`find` recursively traverses directories matching attributes like name, time, and size."
                },
                {
                    "text": "What octal value sets file permissions so the owner has full read/write/execute, while group and others have read and execute only?",
                    "type": "syntax",
                    "a": "777",
                    "b": "755",
                    "c": "644",
                    "d": "600",
                    "correct": "B",
                    "explanation": "Owner=rwx (7), Group=r-x (5), Others=r-x (5) -> 755."
                },
                {
                    "text": "What does `cat access.log | grep 404 | wc -l` compute?",
                    "type": "output",
                    "a": "Prints all lines with 404 error",
                    "b": "Counts the total number of lines in access.log containing '404'",
                    "c": "Deletes lines containing 404 from access.log",
                    "d": "Searches for files with 404 in their filename",
                    "correct": "B",
                    "explanation": "Piping grep output to `wc -l` counts matching lines."
                },
                {
                    "text": "Which command updates package list metadata from configured Debian/Ubuntu repositories without upgrading installed packages?",
                    "type": "mcq",
                    "a": "apt upgrade",
                    "b": "apt update",
                    "c": "apt install",
                    "d": "dpkg -i",
                    "correct": "B",
                    "explanation": "`apt update` synchronizes repository package index files."
                },
                {
                    "text": "Which network command sends ICMP ECHO requests to verify if a remote host is reachable?",
                    "type": "mcq",
                    "a": "curl",
                    "b": "ifconfig",
                    "c": "netstat",
                    "d": "ping",
                    "correct": "D",
                    "explanation": "`ping` verifies network host reachability using ICMP echo requests."
                }
            ]
        }
    ]

    for q_data in quizzes:
        quiz = AssessmentQuiz(
            slug=q_data["slug"],
            title=q_data["title"],
            description=q_data.get("description", "Assessment Quiz"),
            difficulty_level=q_data["difficulty"],
            passing_score=q_data["passing_score"],
            time_limit_minutes=q_data["time_limit"]
        )
        db.session.add(quiz)
        db.session.flush()

        for idx, item in enumerate(q_data["questions"], 1):
            question = AssessmentQuestion(
                quiz_id=quiz.id,
                question_text=item["text"],
                question_type=item["type"],
                option_a=item["a"],
                option_b=item["b"],
                option_c=item["c"],
                option_d=item["d"],
                correct_option=item["correct"],
                explanation=item["explanation"],
                order_num=idx
            )
            db.session.add(question)

    db.session.commit()
