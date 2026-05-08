# ClusterFS: Virtual File System Emulator

## Overview
ClusterFS is a Python-based educational project that simulates a simplified virtual file system inspired by FAT architecture. It demonstrates how operating systems manage storage using clusters, FAT tables, directories, and a shell interface.

The system runs entirely on top of a single binary file acting as a virtual disk.

---

## Key Concepts

- **Virtual Disk**: A file acting as a raw storage device
- **Clusters**: Fixed-size storage blocks (1024 bytes each)
- **FAT (File Allocation Table)**: Manages allocation and linking of clusters
- **Directory System**: Stores file and folder metadata
- **Shell Interface**: Command-line interface for interacting with the system

---

## Features

### File System Core
- Cluster-based storage model
- FAT-based allocation and deallocation
- Linked-cluster file storage
- Directory entry management

### File Operations
- Create, read, write, delete files
- Rename and copy files
- Append and overwrite support

### Directory Operations
- Create and remove directories
- Navigate between directories
- List directory contents

### Shell Interface
- Interactive CLI environment
- Command-based interaction (ls, cd, touch, cat, echo, etc.)
- Safe error handling (prevents system crash on invalid input)

---

## Supported Commands
- # ClusterFS: Virtual File System Emulator

## Overview
ClusterFS is a Python-based educational project that simulates a simplified virtual file system inspired by FAT architecture. It demonstrates how operating systems manage storage using clusters, FAT tables, directories, and a shell interface.

The system runs entirely on top of a single binary file acting as a virtual disk.

---

## Key Concepts

- **Virtual Disk**: A file acting as a raw storage device
- **Clusters**: Fixed-size storage blocks (1024 bytes each)
- **FAT (File Allocation Table)**: Manages allocation and linking of clusters
- **Directory System**: Stores file and folder metadata
- **Shell Interface**: Command-line interface for interacting with the system

---

## Features

### File System Core
- Cluster-based storage model
- FAT-based allocation and deallocation
- Linked-cluster file storage
- Directory entry management

### File Operations
- Create, read, write, delete files
- Rename and copy files
- Append and overwrite support

### Directory Operations
- Create and remove directories
- Navigate between directories
- List directory contents

### Shell Interface
- Interactive CLI environment
- Command-based interaction (ls, cd, touch, cat, echo, etc.)
- Safe error handling (prevents system crash on invalid input)

---

## Supported Commands


- cd [dir] Change directory
- ls List directory contents
- touch <file> Create empty file
- cat <file> Display file content
- echo "text" Write to file
- echo --append Append to file
- cp <src> <dst> Copy file
- mv <src> <dst> Move/rename file
- rm <file> Delete file
- mkdir <dir> Create directory
- rmdir <dir> Remove empty directory
- clear Clear screen
- exit Exit shell
- help Show available commands

---


## Architecture

The system is divided into multiple layers:

- **VirtualDisk Layer**
  - Handles raw read/write operations on the binary file

- **FAT Manager**
  - Manages cluster allocation and chaining

- **Directory Manager**
  - Handles file/folder metadata and lookup

- **File System Layer**
  - Implements high-level file operations

- **Shell Layer**
  - Provides user interface for interaction

---

## Learning Goals

This project demonstrates:

- How file systems manage storage internally
- How FAT-based allocation works
- How directories map names to physical storage
- How operating systems abstract hardware complexity
- Basic design of CLI-based system tools

---

## Limitations

- Single-user system (no concurrency support)
- No permissions or security model
- No journaling or crash recovery
- Simplified FAT implementation
- No real disk optimization or caching

---

## Future Improvements

- Multi-user support
- File permissions system
- Journaling for crash recovery
- Directory tree optimization
- Disk fragmentation handling improvements

---

## How to Run

```bash
python main.py
  

