import sys
import subprocess
from snaparg import SnapArgumentParser as ArgumentParser
from .store import get_all, set_shortcut, del_shortcut, _save

ASCII_BANNER = r"""
  _                                  
 | |                                 
 | | __ _ _____   _ _ __ _   _ _ __  
 | |/ _` |_  / | | | '__| | | | '_ \ 
 | | (_| |/ /| |_| | |  | |_| | | | |
 |_|\__,_/___|\__, |_|   \__,_|_| |_|
               __/ |                 
              |___/                  
"""

def cli():
    shortcuts = get_all()

    if len(sys.argv) == 1:
        print(ASCII_BANNER)
        print("lazyrun – Task Runner With Memory")
        print("Save and run your most-used shell commands as easy shortcuts.")
        print("\nExample:\n  lazyrun save build \"python setup.py sdist bdist_wheel\"")
        return

    if len(sys.argv) > 1 and sys.argv[1] not in (
        "save", "list", "remove", "tag", "group"
    ):
        name = sys.argv[1]
        if name in shortcuts:
            cmd = shortcuts[name]
            if isinstance(cmd, dict):
                cmd = cmd.get("cmd", "")
            print(f"▶ | Running command: {cmd}")
            subprocess.run(cmd, shell=True)
            return

    parser = ArgumentParser(prog="lazyrun", description=cli.__doc__)
    subs = parser.add_subparsers(dest="command", required=True)

    # --- save ---
    save_p = subs.add_parser("save", help="Save a command as a shortcut.")
    save_p.add_argument("name")
    save_p.add_argument("cmd", nargs="+")

    # --- list ---
    subs.add_parser("list", help="List all saved shortcuts.")

    # --- remove ---
    rem_p = subs.add_parser("remove", help="Remove a saved shortcut.")
    rem_p.add_argument("name", choices=list(shortcuts.keys()))

    # --- tag ---
    tag = subs.add_parser("tag", help="Tag commands")
    tag_sub = tag.add_subparsers(dest="subcommand", required=True)

    tag_add = tag_sub.add_parser("add", help="Add tag to a command")
    tag_add.add_argument("name")
    tag_add.add_argument("tag")

    tag_rem = tag_sub.add_parser("remove", help="Remove tag from a command")
    tag_rem.add_argument("name")
    tag_rem.add_argument("tag")

    tag_list = tag_sub.add_parser("list", help="List tags for a command")
    tag_list.add_argument("name")

    # --- group ---
    group = subs.add_parser("group", help="Group commands")
    group_sub = group.add_subparsers(dest="subcommand", required=True)

    group_add = group_sub.add_parser("add", help="Add command to group")
    group_add.add_argument("name")
    group_add.add_argument("group")

    group_rem = group_sub.add_parser("remove", help="Remove command from group")
    group_rem.add_argument("name")
    group_rem.add_argument("group")

    group_list = group_sub.add_parser("list", help="List all commands in a group")
    group_list.add_argument("group")

    args = parser.parse_args()

    if args.command == "save":
        cmd_str = " ".join(args.cmd)
        set_shortcut(args.name, cmd_str)
        print(f"✔ | Shortcut saved. '{args.name}' → {cmd_str}")

    elif args.command == "list":
        if not shortcuts:
            print("No shortcuts saved.")
        else:
            print("Saved shortcuts:")
            for name, entry in shortcuts.items():
                if isinstance(entry, str):
                    print(f"  {name}: {entry}")
                else:
                    tags = ", ".join(entry.get("tags", []))
                    groups = ", ".join(entry.get("groups", []))
                    print(f"  {name}: {entry.get('cmd')} [tags: {tags}] [groups: {groups}]")

    elif args.command == "remove":
        del_shortcut(args.name)
        print(f"✔ | Shortcut '{args.name}' removed.")

    elif args.command == "tag":
        entry = shortcuts.get(args.name)
        if not entry:
            print(f"No command named '{args.name}' found.")
        elif args.subcommand == "add":
            entry.setdefault("tags", [])
            if args.tag not in entry["tags"]:
                entry["tags"].append(args.tag)
                _save({**shortcuts, "_meta": {"version": 2}})
                print(f"✔ | Tag '{args.tag}' added to '{args.name}'")
        elif args.subcommand == "remove":
            if args.tag in entry.get("tags", []):
                entry["tags"].remove(args.tag)
                _save({**shortcuts, "_meta": {"version": 2}})
                print(f"✔ | Tag '{args.tag}' removed from '{args.name}'")
        elif args.subcommand == "list":
            print(f"Tags for '{args.name}': {', '.join(entry.get('tags', [])) or 'None'}")

    elif args.command == "group":
        entry = shortcuts.get(args.name) if args.subcommand != "list" else None
        if args.subcommand in {"add", "remove"} and not entry:
            print(f"No command named '{args.name}' found.")
        elif args.subcommand == "add":
            entry.setdefault("groups", [])
            if args.group not in entry["groups"]:
                entry["groups"].append(args.group)
                _save({**shortcuts, "_meta": {"version": 2}})
                print(f"✔ | Command '{args.name}' added to group '{args.group}'")
        elif args.subcommand == "remove":
            if args.group in entry.get("groups", []):
                entry["groups"].remove(args.group)
                _save({**shortcuts, "_meta": {"version": 2}})
                print(f"✔ | Command '{args.name}' removed from group '{args.group}'")
        elif args.subcommand == "list":
            found = [n for n, e in shortcuts.items() if args.group in e.get("groups", [])]
            if found:
                print(f"Commands in group '{args.group}':")
                for name in found:
                    print(f"  - {name}")
            else:
                print(f"No commands found in group '{args.group}'.")
