import re
import copy
import json
from datetime import datetime

class VirtualLinuxSimulator:
    """
    Controlled, safe virtual Linux command execution engine.
    Executes commands completely inside an isolated virtual filesystem (VFS)
    and virtual operating system state without using host OS subprocesses.
    """

    def __init__(self, vfs=None, cwd="/home/user", user="user"):
        self.user = user
        self.cwd = cwd
        self.vfs = vfs if vfs else self.get_default_vfs()
        self.processes = [
            {"pid": 1, "user": "root", "cpu": 0.0, "mem": 0.1, "cmd": "systemd"},
            {"pid": 284, "user": "root", "cpu": 0.0, "mem": 0.2, "cmd": "sshd"},
            {"pid": 512, "user": "root", "cpu": 0.1, "mem": 0.3, "cmd": "cron"},
            {"pid": 1042, "user": "user", "cpu": 0.2, "mem": 0.8, "cmd": "bash"},
            {"pid": 1580, "user": "user", "cpu": 1.2, "mem": 1.5, "cmd": "python app.py"},
        ]

    @classmethod
    def get_default_vfs(cls):
        """Returns the standard default virtual filesystem tree."""
        return {
            "type": "dir",
            "name": "",
            "owner": "root",
            "group": "root",
            "perms": "rwxr-xr-x",
            "children": {
                "bin": {
                    "type": "dir",
                    "name": "bin",
                    "owner": "root",
                    "group": "root",
                    "perms": "rwxr-xr-x",
                    "children": {
                        "ls": {"type": "file", "name": "ls", "owner": "root", "group": "root", "perms": "rwxr-xr-x", "size": 142104, "content": "[binary]"},
                        "bash": {"type": "file", "name": "bash", "owner": "root", "group": "root", "perms": "rwxr-xr-x", "size": 1183448, "content": "[binary]"}
                    }
                },
                "etc": {
                    "type": "dir",
                    "name": "etc",
                    "owner": "root",
                    "group": "root",
                    "perms": "rwxr-xr-x",
                    "children": {
                        "os-release": {
                            "type": "file",
                            "name": "os-release",
                            "owner": "root",
                            "group": "root",
                            "perms": "rw-r--r--",
                            "size": 382,
                            "content": "NAME=\"Ubuntu\"\nVERSION=\"24.04 LTS (Noble Numbat)\"\nID=ubuntu\nID_LIKE=debian\nPRETTY_NAME=\"Ubuntu 24.04 LTS\"\nVERSION_ID=\"24.04\""
                        },
                        "passwd": {
                            "type": "file",
                            "name": "passwd",
                            "owner": "root",
                            "group": "root",
                            "perms": "rw-r--r--",
                            "size": 1420,
                            "content": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nuser:x:1000:1000:Linux Learner,,,:/home/user:/bin/bash"
                        },
                        "hosts": {
                            "type": "file",
                            "name": "hosts",
                            "owner": "root",
                            "group": "root",
                            "perms": "rw-r--r--",
                            "size": 158,
                            "content": "127.0.0.1 localhost\n127.0.1.1 linux-learning-assistant\n::1 ip6-localhost ip6-loopback"
                        }
                    }
                },
                "var": {
                    "type": "dir",
                    "name": "var",
                    "owner": "root",
                    "group": "root",
                    "perms": "rwxr-xr-x",
                    "children": {
                        "log": {
                            "type": "dir",
                            "name": "log",
                            "owner": "root",
                            "group": "root",
                            "perms": "rwxr-xr-x",
                            "children": {
                                "syslog": {
                                    "type": "file",
                                    "name": "syslog",
                                    "owner": "root",
                                    "group": "adm",
                                    "perms": "rw-r-----",
                                    "size": 420,
                                    "content": "Oct 13 10:00:01 kernel: Linux version 6.8.0-generic (buildd@linux)\nOct 13 10:00:02 systemd[1]: Started System Logging Service.\nOct 13 10:05:14 sshd[284]: Server listening on 0.0.0.0 port 22."
                                }
                            }
                        }
                    }
                },
                "home": {
                    "type": "dir",
                    "name": "home",
                    "owner": "root",
                    "group": "root",
                    "perms": "rwxr-xr-x",
                    "children": {
                        "user": {
                            "type": "dir",
                            "name": "user",
                            "owner": "user",
                            "group": "user",
                            "perms": "rwxr-xr-x",
                            "children": {
                                "welcome.txt": {
                                    "type": "file",
                                    "name": "welcome.txt",
                                    "owner": "user",
                                    "group": "user",
                                    "perms": "rw-r--r--",
                                    "size": 184,
                                    "content": "Welcome to Linux Commands Learning Assistant!\nUse commands like ls, pwd, mkdir, and cat to explore.\nType 'help' to see all available simulated commands."
                                },
                                "notes.txt": {
                                    "type": "file",
                                    "name": "notes.txt",
                                    "owner": "user",
                                    "group": "user",
                                    "perms": "rw-r--r--",
                                    "size": 95,
                                    "content": "Linux Rule #1: Everything is a file.\nLinux Rule #2: Small, modular tools combined with pipes."
                                },
                                "documents": {
                                    "type": "dir",
                                    "name": "documents",
                                    "owner": "user",
                                    "group": "user",
                                    "perms": "rwxr-xr-x",
                                    "children": {
                                        "report.log": {
                                            "type": "file",
                                            "name": "report.log",
                                            "owner": "user",
                                            "group": "user",
                                            "perms": "rw-r--r--",
                                            "size": 178,
                                            "content": "2026-10-13 10:00:01 INFO System booted successfully.\n2026-10-13 10:05:22 WARNING High memory usage.\n2026-10-13 10:12:00 ERROR Connection timeout on port 8080.\n2026-10-13 10:15:30 INFO Service recovered."
                                        }
                                    }
                                },
                                "scripts": {
                                    "type": "dir",
                                    "name": "scripts",
                                    "owner": "user",
                                    "group": "user",
                                    "perms": "rwxr-xr-x",
                                    "children": {
                                        "backup.sh": {
                                            "type": "file",
                                            "name": "backup.sh",
                                            "owner": "user",
                                            "group": "user",
                                            "perms": "rwxr-xr-x",
                                            "size": 65,
                                            "content": "#!/bin/bash\necho \"Starting virtual backup...\"\necho \"Backup complete!\""
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    # -------------------------------------------------------------
    # Path resolution & VFS Traversal
    # -------------------------------------------------------------
    def normalize_path(self, path):
        if not path or path == "~":
            return "/home/user"
        if path.startswith("~/"):
            path = "/home/user" + path[1:]
        if not path.startswith("/"):
            # relative path
            if self.cwd == "/":
                path = "/" + path
            else:
                path = f"{self.cwd}/{path}"
        
        # Resolve '.' and '..'
        parts = []
        for segment in path.split("/"):
            if not segment or segment == ".":
                continue
            if segment == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(segment)
        return "/" + "/".join(parts) if parts else "/"

    def get_node(self, abs_path):
        """Finds a file or directory node in the VFS at the absolute path."""
        if abs_path == "/":
            return self.vfs
        parts = [p for p in abs_path.split("/") if p]
        curr = self.vfs
        for p in parts:
            if curr.get("type") != "dir":
                return None
            children = curr.get("children", {})
            if p not in children:
                return None
            curr = children[p]
        return curr

    def get_parent_and_name(self, abs_path):
        """Returns (parent_node, item_name) for a path."""
        if abs_path == "/":
            return None, "/"
        parts = [p for p in abs_path.split("/") if p]
        item_name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        parent_node = self.get_node(parent_path)
        return parent_node, item_name

    # -------------------------------------------------------------
    # Command Execution Entrypoint
    # -------------------------------------------------------------
    def execute(self, raw_command):
        """
        Executes a single command line (or piped commands),
        updates the VFS and state, and returns rich telemetry.
        """
        raw = raw_command.strip()
        if not raw:
            return {
                "command": raw_command,
                "output": "",
                "status": "success",
                "cwd": self.cwd,
                "visual_changes": [],
                "explanation": "No command entered.",
                "vfs": self.vfs
            }

        # Handle piping (e.g., cat file | grep term)
        if "|" in raw:
            return self._handle_pipe(raw)

        # Handle output redirection (e.g. echo "text" > file or >> file)
        if ">>" in raw:
            parts = raw.split(">>", 1)
            cmd_part = parts[0].strip()
            target_file = parts[1].strip()
            return self._handle_redirect(cmd_part, target_file, append=True)
        elif ">" in raw:
            parts = raw.split(">", 1)
            cmd_part = parts[0].strip()
            target_file = parts[1].strip()
            return self._handle_redirect(cmd_part, target_file, append=False)

        # Tokenize preserving quotes
        tokens = self._tokenize(raw)
        if not tokens:
            return {"command": raw, "output": "", "status": "success", "cwd": self.cwd, "vfs": self.vfs}

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Dispatch
        handler_map = {
            "pwd": self._cmd_pwd,
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "mkdir": self._cmd_mkdir,
            "touch": self._cmd_touch,
            "rm": self._cmd_rm,
            "rmdir": self._cmd_rmdir,
            "cp": self._cmd_cp,
            "mv": self._cmd_mv,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "grep": self._cmd_grep,
            "find": self._cmd_find,
            "head": self._cmd_head,
            "tail": self._cmd_tail,
            "wc": self._cmd_wc,
            "chmod": self._cmd_chmod,
            "chown": self._cmd_chown,
            "whoami": self._cmd_whoami,
            "uname": self._cmd_uname,
            "id": self._cmd_id,
            "date": self._cmd_date,
            "df": self._cmd_df,
            "du": self._cmd_du,
            "free": self._cmd_free,
            "ps": self._cmd_ps,
            "top": self._cmd_top,
            "kill": self._cmd_kill,
            "ping": self._cmd_ping,
            "curl": self._cmd_curl,
            "ifconfig": self._cmd_ifconfig,
            "ip": self._cmd_ip,
            "netstat": self._cmd_netstat,
            "apt": self._cmd_apt,
            "apt-get": self._cmd_apt,
            "dpkg": self._cmd_dpkg,
            "clear": self._cmd_clear,
            "help": self._cmd_help,
            "history": self._cmd_history,
            "exit": self._cmd_exit
        }

        if cmd in handler_map:
            res = handler_map[cmd](args)
        else:
            res = {
                "output": f"bash: {cmd}: command not found\nTip: Type 'help' to see supported Linux commands in this simulator.",
                "status": "error",
                "visual_changes": [],
                "explanation": f"The shell attempted to look for executable '{cmd}' in $PATH, but it was not found or is not supported in the simulator."
            }

        res["command"] = raw
        res["cwd"] = self.cwd
        res["vfs"] = self.vfs
        return res

    def _tokenize(self, s):
        pattern = r'''[^\s"']+|"([^"]*)"|'([^']*)' '''
        matches = re.finditer(pattern, s)
        tokens = []
        for m in matches:
            if m.group(1) is not None:
                tokens.append(m.group(1))
            elif m.group(2) is not None:
                tokens.append(m.group(2))
            else:
                tokens.append(m.group(0))
        return tokens

    # -------------------------------------------------------------
    # Handlers for Individual Commands
    # -------------------------------------------------------------
    def _cmd_pwd(self, args):
        return {
            "output": self.cwd,
            "status": "success",
            "visual_changes": [],
            "explanation": f"`pwd` (Print Working Directory) queries the current shell directory environment variable and prints '{self.cwd}'."
        }

    def _cmd_cd(self, args):
        target = args[0] if args else "~"
        new_path = self.normalize_path(target)
        node = self.get_node(new_path)
        if not node:
            return {
                "output": f"bash: cd: {target}: No such file or directory",
                "status": "error",
                "visual_changes": [],
                "explanation": f"Failed to change directory: target path '{target}' does not exist in the virtual filesystem."
            }
        if node.get("type") != "dir":
            return {
                "output": f"bash: cd: {target}: Not a directory",
                "status": "error",
                "visual_changes": [],
                "explanation": f"Target '{target}' is a regular file, not a directory."
            }
        old_cwd = self.cwd
        self.cwd = new_path
        return {
            "output": "",
            "status": "success",
            "visual_changes": [f"Changed directory from '{old_cwd}' to '{self.cwd}'"],
            "explanation": f"`cd` changed the active shell working directory to '{self.cwd}'. Notice how the terminal prompt updates!"
        }

    def _cmd_ls(self, args):
        show_all = False
        show_long = False
        target_path = None

        for arg in args:
            if arg.startswith("-"):
                if "a" in arg:
                    show_all = True
                if "l" in arg:
                    show_long = True
            else:
                target_path = arg

        abs_path = self.normalize_path(target_path) if target_path else self.cwd
        node = self.get_node(abs_path)

        if not node:
            return {
                "output": f"ls: cannot access '{target_path or abs_path}': No such file or directory",
                "status": "error",
                "visual_changes": [],
                "explanation": "Target directory or file not found."
            }

        if node.get("type") == "file":
            if show_long:
                out = f"-{node.get('perms', 'rw-r--r--')} 1 {node.get('owner', 'user')} {node.get('group', 'user')} {node.get('size', 0):>6} {node['name']}"
            else:
                out = node["name"]
            return {"output": out, "status": "success", "visual_changes": [], "explanation": "Listed file details."}

        # Directory listing
        children = node.get("children", {})
        names = sorted(list(children.keys()))
        if show_all:
            names = [".", ".."] + names

        if show_long:
            lines = [f"total {len(children) * 4}"]
            for name in names:
                if name in [".", ".."]:
                    lines.append(f"drwxr-xr-x 2 {self.user} {self.user}   4096 Oct 13 12:00 {name}")
                    continue
                child = children[name]
                is_dir = child.get("type") == "dir"
                prefix = "d" if is_dir else "-"
                perms = child.get("perms", "rwxr-xr-x" if is_dir else "rw-r--r--")
                owner = child.get("owner", self.user)
                group = child.get("group", self.user)
                size = child.get("size", 4096 if is_dir else 0)
                lines.append(f"{prefix}{perms} 1 {owner} {group} {size:>6} Oct 13 12:00 {name}")
            out = "\n".join(lines)
        else:
            out = "  ".join(names)

        return {
            "output": out,
            "status": "success",
            "visual_changes": [],
            "explanation": f"`ls` read the directory '{abs_path}' and displayed {len(names)} entries with flags (show_all={show_all}, show_long={show_long})."
        }

    def _cmd_mkdir(self, args):
        if not args:
            return {"output": "mkdir: missing operand\nTry 'mkdir --help' for more information.", "status": "error", "visual_changes": [], "explanation": "mkdir requires a directory name argument."}

        create_parents = "-p" in args
        dir_names = [a for a in args if not a.startswith("-")]

        if not dir_names:
            return {"output": "mkdir: missing directory operand", "status": "error", "visual_changes": [], "explanation": "Specify directory name to create."}

        changes = []
        for target in dir_names:
            abs_path = self.normalize_path(target)
            parent, name = self.get_parent_and_name(abs_path)
            if not parent:
                if create_parents:
                    # Create parent recursively
                    parts = [p for p in abs_path.split("/") if p]
                    curr = self.vfs
                    for p in parts:
                        if p not in curr.setdefault("children", {}):
                            curr["children"][p] = {"type": "dir", "name": p, "owner": self.user, "group": self.user, "perms": "rwxr-xr-x", "children": {}}
                        curr = curr["children"][p]
                    changes.append(f"Created directory tree '{abs_path}'")
                    continue
                else:
                    return {"output": f"mkdir: cannot create directory '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Parent directory does not exist. Use 'mkdir -p' to create parent directories."}

            if name in parent.setdefault("children", {}):
                return {"output": f"mkdir: cannot create directory '{target}': File exists", "status": "error", "visual_changes": [], "explanation": f"Directory or file '{name}' already exists."}

            parent["children"][name] = {
                "type": "dir",
                "name": name,
                "owner": self.user,
                "group": self.user,
                "perms": "rwxr-xr-x",
                "children": {}
            }
            changes.append(f"Created directory '{name}' in '{abs_path}'")

        return {
            "output": "",
            "status": "success",
            "visual_changes": changes,
            "explanation": f"`mkdir` successfully allocated and initialized directory entry '{', '.join(dir_names)}' in the virtual filesystem."
        }

    def _cmd_touch(self, args):
        if not args:
            return {"output": "touch: missing file operand", "status": "error", "visual_changes": [], "explanation": "touch requires a filename argument."}

        changes = []
        for target in args:
            abs_path = self.normalize_path(target)
            parent, name = self.get_parent_and_name(abs_path)
            if not parent:
                return {"output": f"touch: cannot touch '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Parent directory does not exist."}

            children = parent.setdefault("children", {})
            if name in children:
                changes.append(f"Updated timestamp of existing file '{name}'")
            else:
                children[name] = {
                    "type": "file",
                    "name": name,
                    "owner": self.user,
                    "group": self.user,
                    "perms": "rw-r--r--",
                    "size": 0,
                    "content": ""
                }
                changes.append(f"Created new empty file '{name}'")

        return {
            "output": "",
            "status": "success",
            "visual_changes": changes,
            "explanation": f"`touch` created or updated the timestamp of the specified file(s)."
        }

    def _cmd_cat(self, args):
        if not args:
            return {"output": "cat: missing file operand", "status": "error", "visual_changes": [], "explanation": "cat requires a filename."}

        out = []
        for target in args:
            abs_path = self.normalize_path(target)
            node = self.get_node(abs_path)
            if not node:
                return {"output": f"cat: {target}: No such file or directory", "status": "error", "visual_changes": [], "explanation": f"File '{target}' was not found."}
            if node.get("type") == "dir":
                return {"output": f"cat: {target}: Is a directory", "status": "error", "visual_changes": [], "explanation": "Cannot read a directory with cat."}
            out.append(node.get("content", ""))

        content = "\n".join(out)
        return {
            "output": content if content else "(file is empty)",
            "status": "success",
            "visual_changes": [],
            "explanation": f"`cat` (concatenate) read the byte contents of '{args[0]}' and streamed it to standard output (stdout)."
        }

    def _cmd_echo(self, args):
        text = " ".join(args)
        return {
            "output": text,
            "status": "success",
            "visual_changes": [],
            "explanation": f"`echo` printed the argument string '{text}' to stdout."
        }

    def _cmd_rm(self, args):
        if not args:
            return {"output": "rm: missing operand", "status": "error", "visual_changes": [], "explanation": "Specify file or directory to remove."}

        recursive = "-r" in args or "-rf" in args or "-R" in args
        targets = [a for a in args if not a.startswith("-")]

        changes = []
        for target in targets:
            abs_path = self.normalize_path(target)
            if abs_path == "/":
                return {"output": "rm: it is dangerous to operate recursively on '/'", "status": "error", "visual_changes": [], "explanation": "Safety guard: cannot remove root directory."}

            parent, name = self.get_parent_and_name(abs_path)
            if not parent or name not in parent.get("children", {}):
                return {"output": f"rm: cannot remove '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Target does not exist."}

            node = parent["children"][name]
            if node.get("type") == "dir" and not recursive:
                return {"output": f"rm: cannot remove '{target}': Is a directory (use -r to remove recursively)", "status": "error", "visual_changes": [], "explanation": "Directories require -r flag to delete."}

            del parent["children"][name]
            changes.append(f"Removed '{target}' from virtual filesystem")

        return {
            "output": "",
            "status": "success",
            "visual_changes": changes,
            "explanation": f"`rm` unlinked and freed the inode(s) for '{', '.join(targets)}'."
        }

    def _cmd_rmdir(self, args):
        if not args:
            return {"output": "rmdir: missing operand", "status": "error", "visual_changes": [], "explanation": "Specify directory to remove."}

        changes = []
        for target in args:
            abs_path = self.normalize_path(target)
            parent, name = self.get_parent_and_name(abs_path)
            if not parent or name not in parent.get("children", {}):
                return {"output": f"rmdir: failed to remove '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Directory not found."}

            node = parent["children"][name]
            if node.get("type") != "dir":
                return {"output": f"rmdir: failed to remove '{target}': Not a directory", "status": "error", "visual_changes": [], "explanation": "Target is not a directory."}

            if node.get("children"):
                return {"output": f"rmdir: failed to remove '{target}': Directory not empty", "status": "error", "visual_changes": [], "explanation": "rmdir only deletes empty directories. Use 'rm -r' for non-empty directories."}

            del parent["children"][name]
            changes.append(f"Removed empty directory '{name}'")

        return {"output": "", "status": "success", "visual_changes": changes, "explanation": "Successfully removed empty directory."}

    def _cmd_cp(self, args):
        recursive = "-r" in args or "-R" in args
        clean_args = [a for a in args if not a.startswith("-")]
        if len(clean_args) < 2:
            return {"output": "cp: missing destination file operand after source", "status": "error", "visual_changes": [], "explanation": "cp requires: cp <source> <destination>"}

        src_path = self.normalize_path(clean_args[0])
        dst_path = self.normalize_path(clean_args[1])

        src_node = self.get_node(src_path)
        if not src_node:
            return {"output": f"cp: cannot stat '{clean_args[0]}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Source file not found."}

        if src_node.get("type") == "dir" and not recursive:
            return {"output": f"cp: -r not specified; omitting directory '{clean_args[0]}'", "status": "error", "visual_changes": [], "explanation": "Copying directories requires the -r flag."}

        dst_node = self.get_node(dst_path)
        if dst_node and dst_node.get("type") == "dir":
            # Copy into destination directory
            dst_node["children"][src_node["name"]] = copy.deepcopy(src_node)
            change = f"Copied '{src_node['name']}' into '{dst_path}'"
        else:
            parent, name = self.get_parent_and_name(dst_path)
            if not parent:
                return {"output": f"cp: cannot create regular file '{clean_args[1]}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Destination directory path does not exist."}
            new_copy = copy.deepcopy(src_node)
            new_copy["name"] = name
            parent.setdefault("children", {})[name] = new_copy
            change = f"Copied '{src_path}' to '{dst_path}'"

        return {"output": "", "status": "success", "visual_changes": [change], "explanation": f"`cp` duplicated the node and its content to the destination path."}

    def _cmd_mv(self, args):
        if len(args) < 2:
            return {"output": "mv: missing destination file operand after source", "status": "error", "visual_changes": [], "explanation": "mv requires: mv <source> <destination>"}

        src_path = self.normalize_path(args[0])
        dst_path = self.normalize_path(args[1])

        src_parent, src_name = self.get_parent_and_name(src_path)
        if not src_parent or src_name not in src_parent.get("children", {}):
            return {"output": f"mv: cannot stat '{args[0]}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Source not found."}

        src_node = src_parent["children"][src_name]
        dst_node = self.get_node(dst_path)

        if dst_node and dst_node.get("type") == "dir":
            dst_node.setdefault("children", {})[src_name] = src_node
            del src_parent["children"][src_name]
            change = f"Moved '{src_name}' into directory '{dst_path}'"
        else:
            dst_parent, dst_name = self.get_parent_and_name(dst_path)
            if not dst_parent:
                return {"output": f"mv: cannot move to '{args[1]}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Destination directory does not exist."}
            src_node["name"] = dst_name
            dst_parent.setdefault("children", {})[dst_name] = src_node
            del src_parent["children"][src_name]
            change = f"Renamed/Moved '{args[0]}' to '{args[1]}'"

        return {"output": "", "status": "success", "visual_changes": [change], "explanation": f"`mv` updated directory pointers to move/rename the target entry."}

    def _cmd_grep(self, args):
        if not args:
            return {"output": "Usage: grep [OPTION]... PATTERNS [FILE]...", "status": "error", "visual_changes": [], "explanation": "Specify search pattern and target file."}

        ignore_case = "-i" in args
        clean_args = [a for a in args if not a.startswith("-")]

        if len(clean_args) < 2:
            return {"output": "grep: missing file operand", "status": "error", "visual_changes": [], "explanation": "Specify file to search."}

        pattern = clean_args[0]
        target = clean_args[1]

        abs_path = self.normalize_path(target)
        node = self.get_node(abs_path)
        if not node or node.get("type") != "file":
            return {"output": f"grep: {target}: No such file or directory", "status": "error", "visual_changes": [], "explanation": "Target file does not exist."}

        lines = node.get("content", "").split("\n")
        matched = []
        flags = re.IGNORECASE if ignore_case else 0
        try:
            regex = re.compile(pattern, flags)
            for line in lines:
                if regex.search(line):
                    matched.append(line)
        except Exception:
            for line in lines:
                if pattern.lower() in line.lower() if ignore_case else pattern in line:
                    matched.append(line)

        return {
            "output": "\n".join(matched) if matched else "",
            "status": "success",
            "visual_changes": [],
            "explanation": f"`grep` searched for regular expression '{pattern}' in '{target}' and matched {len(matched)} line(s)."
        }

    def _cmd_find(self, args):
        target_dir = "."
        name_pattern = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-name" and i + 1 < len(args):
                name_pattern = args[i + 1].strip("'\"")
                i += 2
            elif not arg.startswith("-"):
                target_dir = arg
                i += 1
            else:
                i += 1

        abs_path = self.normalize_path(target_dir)
        results = []

        def recurse(node, current_path):
            name = node.get("name", "")
            if name_pattern:
                clean_p = name_pattern.replace("*", ".*")
                if re.match(f"^{clean_p}$", name):
                    results.append(current_path)
            else:
                results.append(current_path)

            if node.get("type") == "dir":
                for child_name, child_node in node.get("children", {}).items():
                    sub_path = f"{current_path}/{child_name}".replace("//", "/")
                    recurse(child_node, sub_path)

        start_node = self.get_node(abs_path)
        if not start_node:
            return {"output": f"find: '{target_dir}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Search path not found."}

        recurse(start_node, target_dir)
        return {
            "output": "\n".join(results),
            "status": "success",
            "visual_changes": [],
            "explanation": f"`find` recursively walked the filesystem hierarchy starting from '{target_dir}' and matched {len(results)} items."
        }

    def _cmd_head(self, args):
        n = 10
        filename = None
        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    n = 10
                i += 2
            else:
                filename = args[i]
                i += 1

        if not filename:
            return {"output": "head: missing file operand", "status": "error", "visual_changes": [], "explanation": "head requires a filename."}

        node = self.get_node(self.normalize_path(filename))
        if not node or node.get("type") != "file":
            return {"output": f"head: cannot open '{filename}' for reading: No such file or directory", "status": "error", "visual_changes": [], "explanation": "File not found."}

        lines = node.get("content", "").split("\n")
        return {"output": "\n".join(lines[:n]), "status": "success", "visual_changes": [], "explanation": f"`head` displayed the first {n} lines of '{filename}'."}

    def _cmd_tail(self, args):
        n = 10
        filename = None
        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    n = 10
                i += 2
            else:
                filename = args[i]
                i += 1

        if not filename:
            return {"output": "tail: missing file operand", "status": "error", "visual_changes": [], "explanation": "tail requires a filename."}

        node = self.get_node(self.normalize_path(filename))
        if not node or node.get("type") != "file":
            return {"output": f"tail: cannot open '{filename}' for reading: No such file or directory", "status": "error", "visual_changes": [], "explanation": "File not found."}

        lines = node.get("content", "").split("\n")
        return {"output": "\n".join(lines[-n:]), "status": "success", "visual_changes": [], "explanation": f"`tail` displayed the last {n} lines of '{filename}'."}

    def _cmd_wc(self, args):
        lines_only = "-l" in args
        words_only = "-w" in args
        chars_only = "-c" in args
        clean_args = [a for a in args if not a.startswith("-")]

        if not clean_args:
            return {"output": "wc: missing file operand", "status": "error", "visual_changes": [], "explanation": "wc requires a filename."}

        filename = clean_args[0]
        node = self.get_node(self.normalize_path(filename))
        if not node or node.get("type") != "file":
            return {"output": f"wc: {filename}: No such file or directory", "status": "error", "visual_changes": [], "explanation": "File not found."}

        content = node.get("content", "")
        lines = len(content.split("\n")) if content else 0
        words = len(content.split()) if content else 0
        chars = len(content.encode("utf-8")) if content else 0

        if lines_only:
            out = f"{lines} {filename}"
        elif words_only:
            out = f"{words} {filename}"
        elif chars_only:
            out = f"{chars} {filename}"
        else:
            out = f" {lines:>4} {words:>4} {chars:>4} {filename}"

        return {"output": out, "status": "success", "visual_changes": [], "explanation": f"`wc` (word count) counted lines, words, and byte length for '{filename}'."}

    def _cmd_chmod(self, args):
        if len(args) < 2:
            return {"output": "chmod: missing operand", "status": "error", "visual_changes": [], "explanation": "chmod requires: chmod <mode> <file>"}

        mode = args[0]
        target = args[1]
        abs_path = self.normalize_path(target)
        node = self.get_node(abs_path)

        if not node:
            return {"output": f"chmod: cannot access '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "File or directory not found."}

        old_perms = node.get("perms", "rw-r--r--")
        new_perms = old_perms

        # Octal mode conversion (e.g. 755, 644, 777)
        if mode.isdigit() and len(mode) == 3:
            perm_map = {
                "7": "rwx", "6": "rw-", "5": "r-x",
                "4": "r--", "3": "-wx", "2": "-w-",
                "1": "--x", "0": "---"
            }
            new_perms = perm_map.get(mode[0], "r--") + perm_map.get(mode[1], "r--") + perm_map.get(mode[2], "r--")
        elif "+x" in mode:
            new_perms = "rwxr-xr-x"
        elif "-w" in mode:
            new_perms = "r--r--r--"

        node["perms"] = new_perms
        return {
            "output": "",
            "status": "success",
            "visual_changes": [f"Updated permissions on '{target}' from '{old_perms}' to '{new_perms}' ({mode})"],
            "explanation": f"`chmod` updated file mode bits to '{new_perms}'. User, group, and others permissions have been adjusted."
        }

    def _cmd_chown(self, args):
        if len(args) < 2:
            return {"output": "chown: missing operand", "status": "error", "visual_changes": [], "explanation": "chown requires: chown <user>[:<group>] <target>"}

        owner_spec = args[0]
        target = args[1]
        node = self.get_node(self.normalize_path(target))

        if not node:
            return {"output": f"chown: cannot access '{target}': No such file or directory", "status": "error", "visual_changes": [], "explanation": "Target not found."}

        parts = owner_spec.split(":")
        new_owner = parts[0]
        new_group = parts[1] if len(parts) > 1 else new_owner

        node["owner"] = new_owner
        node["group"] = new_group

        return {
            "output": "",
            "status": "success",
            "visual_changes": [f"Changed owner of '{target}' to {new_owner}:{new_group}"],
            "explanation": f"`chown` updated inode ownership to user '{new_owner}' and group '{new_group}'."
        }

    def _cmd_whoami(self, args):
        return {"output": self.user, "status": "success", "visual_changes": [], "explanation": f"`whoami` printed the effective username of the currently logged-in user."}

    def _cmd_id(self, args):
        return {
            "output": "uid=1000(user) gid=1000(user) groups=1000(user),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev)",
            "status": "success",
            "visual_changes": [],
            "explanation": "`id` printed real user ID, group ID, and supplementary groups membership."
        }

    def _cmd_uname(self, args):
        if "-a" in args or "--all" in args:
            out = "Linux linux-learning-assistant 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC Wed Oct 13 10:00:00 UTC 2026 x86_64 GNU/Linux"
        elif "-r" in args:
            out = "6.8.0-45-generic"
        else:
            out = "Linux"
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`uname` queried system information and printed architecture and kernel release version."}

    def _cmd_date(self, args):
        now = datetime.now()
        out = now.strftime("%a %b %d %H:%M:%S UTC %Y")
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`date` printed current system clock time and timezone."}

    def _cmd_df(self, args):
        human = "-h" in args
        if human:
            out = "Filesystem      Size  Used Avail Use% Mounted on\n/dev/root        50G   14G   34G  30% /\ntmpfs           1.9G  1.2M  1.9G   1% /run\n/dev/sda1       512M  6.1M  506M   2% /boot/efi"
        else:
            out = "Filesystem     1K-blocks     Used Available Use% Mounted on\n/dev/root       52428800 14680064  35648736  30% /\ntmpfs            1986560     1228   1985332   1% /run"
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`df` (Disk Free) reported file system disk space usage across mounts."}

    def _cmd_du(self, args):
        human = "-h" in args
        unit = "K" if human else ""
        out = f"4{unit}\t./documents\n4{unit}\t./scripts\n16{unit}\t."
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`du` (Disk Usage) estimated file space usage of directories."}

    def _cmd_free(self, args):
        human = "-m" in args or "-h" in args
        if human:
            out = "               total        used        free      shared  buff/cache   available\nMem:            3900         850        2400          15         650        2900\nSwap:           2048           0        2048"
        else:
            out = "               total        used        free      shared  buff/cache   available\nMem:         3993600      870400     2457600       15360      665600     2969600\nSwap:        2097152           0     2097152"
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`free` displayed total amount of free and used physical memory (RAM) and swap space."}

    def _cmd_ps(self, args):
        full = "aux" in "".join(args) or "-ef" in "".join(args)
        if full:
            lines = ["USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"]
            for p in self.processes:
                lines.append(f"{p['user']:<8} {p['pid']:>5} {p['cpu']:>4.1f} {p['mem']:>4.1f}  15240  4200 pts/0    Ss+  10:00   0:00 {p['cmd']}")
            out = "\n".join(lines)
        else:
            lines = ["  PID TTY          TIME CMD"]
            for p in self.processes:
                if p["user"] == "user":
                    lines.append(f"{p['pid']:>5} pts/0    00:00:01 {p['cmd']}")
            out = "\n".join(lines)
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`ps` reported a snapshot of the current active virtual processes."}

    def _cmd_top(self, args):
        out = (
            "top - 12:00:00 up 2:15, 1 user, load average: 0.08, 0.04, 0.01\n"
            "Tasks: 5 total, 1 running, 4 sleeping, 0 stopped, 0 zombie\n"
            "%Cpu(s):  1.5 us,  0.8 sy,  0.0 ni, 97.5 id,  0.2 wa,  0.0 hi,  0.0 si\n"
            "MiB Mem :   3900.0 total,   2400.0 free,    850.0 used,    650.0 buff/cache\n"
            "MiB Swap:   2048.0 total,   2048.0 free,      0.0 used\n\n"
            "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n"
            " 1580 user      20   0   42150  14500   8200 S   1.2   1.5   0:04.12 python\n"
            " 1042 user      20   0   14200   4100   2900 S   0.2   0.8   0:01.05 bash\n"
            "  512 root      20   0    8500   2200   1800 S   0.1   0.3   0:00.30 cron"
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`top` displayed real-time Linux process resource utilization snapshot."}

    def _cmd_kill(self, args):
        if not args:
            return {"output": "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ...", "status": "error", "visual_changes": [], "explanation": "kill requires a PID."}

        try:
            pid = int(args[-1])
        except ValueError:
            return {"output": f"bash: kill: {args[-1]}: arguments must be process or job IDs", "status": "error", "visual_changes": [], "explanation": "Invalid PID number."}

        found = None
        for p in self.processes:
            if p["pid"] == pid:
                found = p
                break

        if not found:
            return {"output": f"bash: kill: ({pid}) - No such process", "status": "error", "visual_changes": [], "explanation": f"Process {pid} does not exist."}

        self.processes = [p for p in self.processes if p["pid"] != pid]
        return {
            "output": "",
            "status": "success",
            "visual_changes": [f"Terminated process {pid} ({found['cmd']})"],
            "explanation": f"`kill` sent SIGTERM (Signal 15) to process PID {pid}, gracefully terminating it."
        }

    def _cmd_ping(self, args):
        host = args[-1] if args else "google.com"
        out = (
            f"PING {host} (142.250.190.46) 56(84) bytes of data.\n"
            f"64 bytes from 142.250.190.46: icmp_seq=1 ttl=117 time=14.2 ms\n"
            f"64 bytes from 142.250.190.46: icmp_seq=2 ttl=117 time=13.8 ms\n"
            f"64 bytes from 142.250.190.46: icmp_seq=3 ttl=117 time=14.1 ms\n\n"
            f"--- {host} ping statistics ---\n"
            f"3 packets transmitted, 3 received, 0% packet loss, time 2003ms\n"
            f"rtt min/avg/max/mdev = 13.812/14.033/14.218/0.171 ms"
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": f"`ping` sent ICMP ECHO_REQUEST packets to '{host}' and received responses."}

    def _cmd_curl(self, args):
        url = args[-1] if args else "http://example.com"
        out = (
            f"<!doctype html>\n<html>\n<head>\n  <title>Simulated Response</title>\n</head>\n<body>\n"
            f"  <h1>Connected to {url}</h1>\n  <p>HTTP/1.1 200 OK — Linux Learning Assistant Network Gateway.</p>\n</body>\n</html>"
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": f"`curl` executed an HTTP GET transfer to '{url}'."}

    def _cmd_ifconfig(self, args):
        out = (
            "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
            "        inet 192.168.1.105  netmask 255.255.255.0  broadcast 192.168.1.255\n"
            "        inet6 fe80::a00:27ff:fe4e:66a1  prefixlen 64  scopeid 0x20<link>\n"
            "        ether 08:00:27:4e:66:a1  txqueuelen 1000  (Ethernet)\n"
            "        RX packets 24108  bytes 18920401 (18.9 MB)\n"
            "        TX packets 15201  bytes 3140510 (3.1 MB)\n\n"
            "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536\n"
            "        inet 127.0.0.1  netmask 255.0.0.0\n"
            "        inet6 ::1  prefixlen 128  scopeid 0x10<host>"
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`ifconfig` configured and displayed network interface parameters."}

    def _cmd_ip(self, args):
        out = (
            "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default\n"
            "    inet 127.0.0.1/8 scope host lo\n"
            "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default\n"
            "    inet 192.168.1.105/24 brd 192.168.1.255 scope global dynamic eth0"
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`ip` displayed network IP addresses and routing devices."}

    def _cmd_netstat(self, args):
        out = (
            "Active Internet connections (only servers)\n"
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State      \n"
            "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     \n"
            "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN     \n"
            "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN     "
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "`netstat` printed network connections, routing tables, and interface statistics."}

    def _cmd_apt(self, args):
        if not args:
            return {"output": "apt 2.8.0 (amd64)\nUsage: apt [options] command\nCommands: update, install, remove", "status": "success", "visual_changes": [], "explanation": "apt package management CLI."}

        sub = args[0]
        if sub == "update":
            out = (
                "Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\n"
                "Get:2 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]\n"
                "Fetched 126 kB in 1s (115 kB/s)\n"
                "Reading package lists... Done\n"
                "Building dependency tree... Done\n"
                "All packages are up to date."
            )
            return {"output": out, "status": "success", "visual_changes": ["Synchronized package indexes"], "explanation": "`apt update` refreshed list of available packages and versions from repositories."}
        elif sub == "install":
            pkg = args[1] if len(args) > 1 else "package"
            out = f"Reading package lists... Done\nBuilding dependency tree... Done\nUnpacking {pkg} (latest)... Done\nSetting up {pkg}... Done"
            return {"output": out, "status": "success", "visual_changes": [f"Installed package '{pkg}'"], "explanation": f"`apt install` downloaded, unpacked, and configured package '{pkg}'."}
        return {"output": f"apt: action '{sub}' completed.", "status": "success", "visual_changes": [], "explanation": "Executed simulated apt command."}

    def _cmd_dpkg(self, args):
        return {"output": "Desired=Unknown/Install/Remove/Purge/Hold\n| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\nii  bash  5.2.21-2ubuntu4  amd64  GNU Bourne Again SHell\nii  coreutils  9.4-3ubuntu6  amd64  GNU core utilities", "status": "success", "visual_changes": [], "explanation": "`dpkg` low-level Debian package manager query."}

    def _cmd_clear(self, args):
        return {"output": "__CLEAR__", "status": "success", "visual_changes": [], "explanation": "Terminal display cleared."}

    def _cmd_history(self, args):
        return {"output": "  1  pwd\n  2  ls -la\n  3  mkdir projects\n  4  cd projects\n  5  touch app.py", "status": "success", "visual_changes": [], "explanation": "`history` showed list of executed session commands."}

    def _cmd_help(self, args):
        out = (
            "Linux Commands Learning Assistant — Simulator Shell v2.4\n"
            "Supported commands categorized by topic:\n\n"
            "• Navigation:        pwd, ls, cd\n"
            "• File Management:   mkdir, touch, cp, mv, rm, rmdir\n"
            "• File Viewing:      cat, head, tail\n"
            "• Text Searching:    grep, find, wc\n"
            "• Permissions:       chmod, chown\n"
            "• Processes:         ps, top, kill\n"
            "• System Info:       uname, whoami, id, date, df, du, free\n"
            "• Networking:        ping, curl, ifconfig, ip, netstat\n"
            "• Packages:          apt, apt-get, dpkg\n"
            "• Shell & Pipes:     echo, |, >, >>, clear, history, help\n\n"
            "All commands run in a fully persistent simulated environment."
        )
        return {"output": out, "status": "success", "visual_changes": [], "explanation": "Displayed simulated shell command manual."}

    def _cmd_exit(self, args):
        return {"output": "exit\n[Simulation session closed. Type any command to resume.]", "status": "success", "visual_changes": [], "explanation": "Session exit signal."}

    # -------------------------------------------------------------
    # Output redirection & Piping
    # -------------------------------------------------------------
    def _handle_redirect(self, cmd_part, target_file, append=False):
        res = self.execute(cmd_part)
        content_to_write = res.get("output", "")
        if res.get("status") != "success":
            return res

        abs_path = self.normalize_path(target_file)
        parent, name = self.get_parent_and_name(abs_path)
        if not parent:
            return {"output": f"bash: {target_file}: No such file or directory", "status": "error", "visual_changes": [], "explanation": "Destination directory not found."}

        children = parent.setdefault("children", {})
        if name in children:
            file_node = children[name]
            if file_node.get("type") != "file":
                return {"output": f"bash: {target_file}: Is a directory", "status": "error", "visual_changes": [], "explanation": "Cannot redirect output to a directory."}
            if append:
                file_node["content"] = file_node.get("content", "") + ("\n" if file_node.get("content") else "") + content_to_write
                action = f"Appended output to '{name}'"
            else:
                file_node["content"] = content_to_write
                action = f"Overwrote content in '{name}'"
            file_node["size"] = len(file_node["content"].encode("utf-8"))
        else:
            children[name] = {
                "type": "file",
                "name": name,
                "owner": self.user,
                "group": self.user,
                "perms": "rw-r--r--",
                "size": len(content_to_write.encode("utf-8")),
                "content": content_to_write
            }
            action = f"Created '{name}' with output"

        return {
            "output": "",
            "status": "success",
            "visual_changes": [action],
            "explanation": f"Redirection operator ({'>>' if append else '>'}) redirected command output into file '{target_file}'."
        }

    def _handle_pipe(self, raw):
        parts = [p.strip() for p in raw.split("|")]
        current_input = ""
        for i, cmd_str in enumerate(parts):
            if i == 0:
                res = self.execute(cmd_str)
                current_input = res.get("output", "")
                if res.get("status") != "success":
                    return res
            else:
                tokens = self._tokenize(cmd_str)
                if not tokens:
                    continue
                cmd = tokens[0].lower()
                if cmd == "grep":
                    pattern = tokens[1] if len(tokens) > 1 else ""
                    lines = current_input.split("\n")
                    matched = [l for l in lines if pattern.lower() in l.lower()]
                    current_input = "\n".join(matched)
                elif cmd == "wc":
                    lines = len(current_input.split("\n")) if current_input else 0
                    if "-l" in tokens:
                        current_input = str(lines)
                    else:
                        words = len(current_input.split())
                        chars = len(current_input.encode("utf-8"))
                        current_input = f" {lines:>4} {words:>4} {chars:>4}"
                elif cmd == "head":
                    n = 10
                    if "-n" in tokens:
                        try:
                            n = int(tokens[tokens.index("-n") + 1])
                        except Exception:
                            n = 10
                    current_input = "\n".join(current_input.split("\n")[:n])
                elif cmd == "tail":
                    n = 10
                    if "-n" in tokens:
                        try:
                            n = int(tokens[tokens.index("-n") + 1])
                        except Exception:
                            n = 10
                    current_input = "\n".join(current_input.split("\n")[-n:])

        return {
            "output": current_input,
            "status": "success",
            "visual_changes": [],
            "explanation": f"Pipeline (|) successfully piped stdout of initial process into stdin of subsequent filter command(s)."
        }
