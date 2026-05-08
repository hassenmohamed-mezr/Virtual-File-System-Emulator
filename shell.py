from VirtualDisk import VirtualDisk
from fs_constants import FsConstants
from file_system_manager import FileSystem
from directory_manager import DirectoryManager


class Shell:
    def __init__(self):
        self.disk = VirtualDisk("virtual_disk.bin")
        self.fs = FileSystem(self.disk)
        self.dir_manager = DirectoryManager(self.disk)

        self.current_cluster = FsConstants.ROOT_DIR_FIRST_CLUSTER
        self.current_path = "H:\\"

    def run(self):
        while True:
            try:
                command = input(f"{self.current_path}> ").strip()

                if not command:
                    continue

                parts = command.split()

                cmd = parts[0].lower()

                if cmd == "exit":
                    break

                elif cmd == "help":
                    self.help()

                elif cmd == "clear":
                    self.clear()

                elif cmd == "ls":
                    self.ls()

                elif cmd == "touch":
                    self.touch(parts)

                elif cmd == "cat":
                    self.cat(parts)

                elif cmd == "rm":
                    self.rm(parts)

                elif cmd == "mkdir":
                    self.mkdir(parts)

                elif cmd == "rmdir":
                    self.rmdir(parts)

                elif cmd == "cd":
                    self.cd(parts)

                elif cmd == "echo":
                    self.echo(command)

                elif cmd == "cp":
                    self.cp(parts)

                elif cmd == "mv":
                    self.mv(parts)

                else:
                    print("Unknown command")

            except Exception as e:
                print("Error:", e)

    def help(self):
        print("\nAvailable Commands:\n")

        print("cd [dir]")
        print("  Change current directory")
        print("  Example: cd docs\n")

        print("clear")
        print("  Clear the screen\n")

        print("ls")
        print("  List directory contents\n")

        print("exit")
        print("  Exit the shell\n")

        print("cp <src> <dst>")
        print("  Copy file")
        print("  Example: cp file1.txt file2.txt\n")

        print("mv <src> <dst>")
        print("  Move or rename file")
        print("  Example: mv old.txt new.txt\n")

        print("rm <file>")
        print("  Delete file")
        print("  Example: rm test.txt\n")

        print("mkdir <dir>")
        print("  Create directory")
        print("  Example: mkdir docs\n")

        print("rmdir <dir>")
        print("  Remove empty directory")
        print("  Example: rmdir docs\n")

        print("cat <file>")
        print("  Display file content")
        print("  Example: cat notes.txt\n")

        print("touch <file>")
        print("  Create empty file")
        print("  Example: touch test.txt\n")

        print('echo "text" <file>')
        print("  Write text to file")
        print('  Example: echo "hello" test.txt\n')

        print('echo "text" <file> --append')
        print("  Append text to file")
        print('  Example: echo "world" test.txt --append\n')

    def clear(self):
        print("\n" * 50)

    def ls(self):
        entries = self.dir_manager.read_directory(self.current_cluster)

        for entry in entries:
            name = entry.parse_8dot3_name(entry.name)

            if entry.attr == 1:
                print(f"<DIR>  {name}")
            else:
                print(f"<FILE> {name}")

    def touch(self, parts):
        if len(parts) < 2:
            print("Missing filename")
            return

        self.fs.create_file(self.current_cluster, parts[1])

    def cat(self, parts):
        if len(parts) < 2:
            print("Missing filename")
            return

        entry = self.dir_manager.find_directory_entry(
            self.current_cluster,
            parts[1]
        )

        if entry is None:
            print("File not found")
            return

        data = self.fs.read_file(entry)

        print(data.decode("utf-8"))

    def rm(self, parts):
        if len(parts) < 2:
            print("Missing filename")
            return

        self.fs.delete_file(self.current_cluster, parts[1])

    def mkdir(self, parts):
        if len(parts) < 2:
            print("Missing directory name")
            return

        self.fs.create_directory(self.current_cluster, parts[1])

    def rmdir(self, parts):
        if len(parts) < 2:
            print("Missing directory name")
            return

        self.fs.remove_directory(self.current_cluster, parts[1])

    def cd(self, parts):
        if len(parts) == 1:
            print(self.current_path)
            return

        dirname = parts[1]

        if dirname == "..":
            self.current_cluster = FsConstants.ROOT_DIR_FIRST_CLUSTER
            self.current_path = "H:\\"
            return

        entry = self.dir_manager.find_directory_entry(
            self.current_cluster,
            dirname
        )

        if entry is None:
            print("Directory not found")
            return

        if entry.attr != 1:
            print("Not a directory")
            return

        self.current_cluster = entry.first_cluster

        dir_name = entry.parse_8dot3_name(entry.name)

        self.current_path += dir_name + "\\"

    def echo(self, command):
        append_mode = "--append" in command

        if append_mode:
            command = command.replace("--append", "").strip()

        first_quote = command.find('"')
        second_quote = command.find('"', first_quote + 1)

        if first_quote == -1 or second_quote == -1:
            print("Invalid format")
            return

        text = command[first_quote + 1:second_quote]

        remaining = command[second_quote + 1:].strip()

        parts = remaining.split()

        if len(parts) == 0:
            print("Missing filename")
            return

        filename = parts[0]

        entry = self.dir_manager.find_directory_entry(
            self.current_cluster,
            filename
        )

        if entry is None:
            self.fs.create_file(self.current_cluster, filename)

            entry = self.dir_manager.find_directory_entry(
                self.current_cluster,
                filename
            )

        if append_mode:
            old_data = self.fs.read_file(entry).decode("utf-8")

            text = old_data + text

        self.fs.write_file(
            self.current_cluster,
            filename,
            text.encode("utf-8")
        )

    def cp(self, parts):
        if len(parts) < 3:
            print("Missing arguments")
            return

        src = parts[1]
        dst = parts[2]

        src_entry = self.dir_manager.find_directory_entry(
            self.current_cluster,
            src
        )

        if src_entry is None:
            print("Source file not found")
            return

        self.fs.copy_file(
            src_entry,
            self.current_cluster,
            dst
        )

    def mv(self, parts):
        if len(parts) < 3:
            print("Missing arguments")
            return

        src = parts[1]
        dst = parts[2]

        entry = self.dir_manager.find_directory_entry(
            self.current_cluster,
            src
        )

        if entry is None:
            print("Source not found")
            return

        existing = self.dir_manager.find_directory_entry(
            self.current_cluster,
            dst
        )

        if existing is None:
            self.fs.rename_entry(
                self.current_cluster,
                src,
                dst
            )
        else:
            self.fs.move_file(
                self.current_cluster,
                src,
                self.current_cluster,
                dst
            )
