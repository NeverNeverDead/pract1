import os
import tarfile
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

class ShellEmulator:
    def __init__(self, hostname, fs_path, log_path):
        self.hostname = hostname
        self.log_path = log_path
        self.current_dir = '/'
        self.fs = {}
        self.load_fs(fs_path)
        self.root = tk.Tk()
        self.root.withdraw()
        self.init_log()

    def load_fs(self, fs_path):
        """Load the virtual file system from the provided tar file."""
        try:
            with tarfile.open(fs_path, "r") as tar:
                for member in tar.getmembers():
                    self.fs[member.name] = {'type': 'dir' if member.isdir() else 'file', 'size': member.size}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file system: {e}")
            exit(1)

    def init_log(self):
        """Initialize the XML log file."""
        root = ET.Element("log")
        tree = ET.ElementTree(root)
        tree.write(self.log_path)

    def log_action(self, action, details):
        """Log an action to the XML log file."""
        tree = ET.parse(self.log_path)
        root = tree.getroot()
        entry = ET.SubElement(root, "entry")
        ET.SubElement(entry, "action").text = action
        ET.SubElement(entry, "details").text = details
        tree.write(self.log_path)

    def command_ls(self, args):
        """List directory contents."""
        path = self.resolve_path(args[0] if args else '.')
        if path in self.fs and self.fs[path]['type'] == 'dir':
            contents = [name for name in self.fs if name.startswith(path) and name != path]
            self.log_action("ls", path)
            return '\n'.join(contents)
        else:
            return f"ls: cannot access '{path}': No such file or directory"

    def command_cd(self, args):
        """Change directory."""
        path = self.resolve_path(args[0]) if args else '/'
        if path in self.fs and self.fs[path]['type'] == 'dir':
            self.current_dir = path
            self.log_action("cd", path)
            return ""
        else:
            return f"cd: {path}: No such file or directory"

    def command_exit(self, args):
        """Exit the shell emulator."""
        self.log_action("exit", "")
        exit(0)

    def command_uname(self, args):
        """Display system information."""
        self.log_action("uname", "")
        return "UNIX Shell Emulator"

    def command_chmod(self, args):
        """Change file permissions (simulated)."""
        if len(args) != 2:
            return "chmod: missing operand"
        path = self.resolve_path(args[1])
        if path in self.fs:
            self.log_action("chmod", f"{args[0]} {path}")
            return ""
        else:
            return f"chmod: cannot access '{path}': No such file or directory"

    def command_du(self, args):
        """Estimate file space usage."""
        path = self.resolve_path(args[0]) if args else self.current_dir
        if path in self.fs:
            size = sum(self.fs[name]['size'] for name in self.fs if name.startswith(path))
            self.log_action("du", path)
            return f"{size}\t{path}"
        else:
            return f"du: cannot access '{path}': No such file or directory"

    def resolve_path(self, path):
        """Resolve a path to an absolute path."""
        if not path.startswith('/'):
            path = os.path.join(self.current_dir, path)
        return os.path.normpath(path)

    def run_command(self, command_line):
        """Run a shell command."""
        parts = command_line.strip().split()
        if not parts:
            return ""
        command, args = parts[0], parts[1:]
        commands = {
            'ls': self.command_ls,
            'cd': self.command_cd,
            'exit': self.command_exit,
            'uname': self.command_uname,
            'chmod': self.command_chmod,
            'du': self.command_du,
        }
        if command in commands:
            return commands[command](args)
        else:
            return f"{command}: command not found"

    def start_gui(self):
        """Start the GUI for the shell emulator."""
        self.root = tk.Tk()
        self.root.title("Shell Emulator")

        self.text = tk.Text(self.root, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self.root)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.pack(fill=tk.X)

        self.display_prompt()
        self.root.mainloop()

    def display_prompt(self):
        """Display the shell prompt."""
        prompt = f"{self.hostname}:{self.current_dir}$ "
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, prompt)
        self.text.config(state=tk.DISABLED)

    def on_enter(self, event):
        """Handle the Enter key press."""
        command_line = self.entry.get()
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, command_line + '\n')
        self.text.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        
        output = self.run_command(command_line)
        if output:
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, output + '\n')
            self.text.config(state=tk.DISABLED)

        self.display_prompt()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--hostname", required=True, help="Hostname for the shell prompt")
    parser.add_argument("--fs_path", required=True, help="Path to the tar file representing the virtual file system")
    parser.add_argument("--log_path", required=True, help="Path to the log file")

    args = parser.parse_args()

    emulator = ShellEmulator(args.hostname, args.fs_path, args.log_path)
    emulator.start_gui()
