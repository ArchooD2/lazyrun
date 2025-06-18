import sys
import subprocess
from snaparg import SnapArgumentParser as ArgumentParser
from .store import get_all, set_shortcut, del_shortcut, _load, _save

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

    # direct run: lazyrun name
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
            entry = shortcuts[name]
            cmd = entry.get("cmd") if isinstance(entry, dict) else entry
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

    tag_run = tag_sub.add_parser("run", help="Run all commands with a tag")
    tag_run.add_argument("tag")
    tag_run.add_argument("--sync", action="store_true",
                         help="Run commands sequentially instead of async")
    
    # --- group ---
    group = subs.add_parser("group", help="Group commands")
    group_sub = group.add_subparsers(dest="subcommand", required=True)
    
    group_add = group_sub.add_parser("add", help="Add command to group")
    group_add.add_argument("name")
    group_add.add_argument("group")
    group_add.add_argument("--priority", type=int,
                           help="Position in the group (0-based; default=end)")
    
    group_rem = group_sub.add_parser("remove", help="Remove command from group")
    group_rem.add_argument("name")
    group_rem.add_argument("group")
    
    group_list = group_sub.add_parser("list", help="List all commands in a group")
    group_list.add_argument("group")
    
    group_run = group_sub.add_parser("run", help="Run all commands in a group")
    group_run.add_argument("group")
    
    # --- lrgui ---
    gui_p = subs.add_parser("lrgui", help="Launch the LazyRun web dashboard.")
    gui_p.add_argument("--port", type=int, default=5000, help="Port to run the dashboard on")
    args = parser.parse_args()

    # --- save ---
    if args.command == "save":
        cmd_str = " ".join(args.cmd)
        set_shortcut(args.name, cmd_str)
        print(f"✔ | Shortcut saved. '{args.name}' → {cmd_str}")

    # --- list ---
    elif args.command == "list":
        if not shortcuts:
            print("No shortcuts saved.")
        else:
            print("Saved shortcuts:")
            for name, entry in shortcuts.items():
                if isinstance(entry, str):
                    print(f"  {name}: {entry}")
                else:
                    tags = ", ".join(entry.get("tags", [])) or "None"
                    groups = ", ".join(entry.get("groups", [])) or "None"
                    print(f"  {name}: {entry['cmd']} [tags: {tags}] [groups: {groups}]")

    # --- remove ---
    elif args.command == "remove":
        del_shortcut(args.name)
        print(f"✔ | Shortcut '{args.name}' removed.")

    # --- tag cmds ---
    elif args.command == "tag":
        data = _load()
        if args.subcommand in ("add", "remove", "list"):
            entry = data.get(args.name)
            if not entry and args.subcommand != "list":
                return print(f"No shortcut named '{args.name}'.")
        
        if args.subcommand == "add":
            if not entry:
                return print(f"No shortcut named '{args.name}'.")
            entry.setdefault("tags", [])
            if args.tag not in entry["tags"]:
                entry["tags"].append(args.tag)
                _save(data)
                print(f"✔ | Tag '{args.tag}' added to '{args.name}'")

        elif args.subcommand == "remove":
            if not entry or args.tag not in entry.get("tags", []):
                return print(f"Tag '{args.tag}' not found on '{args.name}'.")
            entry["tags"].remove(args.tag)
            _save(data)
            print(f"✔ | Tag '{args.tag}' removed from '{args.name}'")

        elif args.subcommand == "list":
            tags = entry.get("tags", []) if entry else []
            print(f"Tags for '{args.name}': {', '.join(tags) or 'None'}")
        
        elif args.subcommand == "list-tags":
            if not shortcuts:
                return print("No shortcuts saved.")
            print("All tags in use:")
            all_tags = set()
            for entry in shortcuts.values():
                if isinstance(entry, dict):
                    all_tags.update(entry.get("tags", []))
            if not all_tags:
                return print("No tags found.")
            print(", ".join(sorted(all_tags)))

        elif args.subcommand == "run":
            # find and run by tag
            found = sorted(
                (n, e) for n, e in shortcuts.items() if args.tag in e.get("tags", [])
            )
            if not found:
                return print(f"No shortcuts tagged '{args.tag}'.")
            procs = []
            for n, e in found:
                cmd = e.get("cmd", "")
                print(f"▶ | {n}: {cmd}")
                p = subprocess.Popen(cmd, shell=True)
                procs.append(p)
            if not args.sync:
                for p in procs:
                    p.wait()

    # --- group cmds ---
    elif args.command == "group":
        data = _load()
        meta = data.setdefault("_meta", {})
        group_meta = meta.setdefault("groups", {})

        if args.subcommand == "add":
            entry = data.get(args.name)
            if not entry:
                return print(f"No shortcut named '{args.name}'.")
            # update ordering meta
            grp_list = group_meta.setdefault(args.group, [])
            if args.name not in grp_list:
                if args.priority is not None:
                    pos = min(max(0, args.priority), len(grp_list))
                    grp_list.insert(pos, args.name)
                else:
                    grp_list.append(args.name)
            # update entry's membership
            entry.setdefault("groups", [])
            if args.group not in entry["groups"]:
                entry["groups"].append(args.group)

            _save(data)
            pos_desc = args.priority if args.priority is not None else "end"
            print(f"✔ | Added '{args.name}' to group '{args.group}' at position {pos_desc}")

        elif args.subcommand == "remove":
            entry = data.get(args.name)
            if not entry or args.group not in entry.get("groups", []):
                return print(f"No shortcut '{args.name}' in group '{args.group}'.")
            # remove from ordering
            grp_list = group_meta.get(args.group, [])
            if args.name in grp_list:
                grp_list.remove(args.name)
            # remove from entry
            entry["groups"].remove(args.group)

            _save(data)
            print(f"✔ | Removed '{args.name}' from group '{args.group}'")

        elif args.subcommand == "list":
            grp_list = group_meta.get(args.group, [])
            if not grp_list:
                return print(f"No commands found in group '{args.group}'.")
            print(f"Commands in group '{args.group}' (in order):")
            for n in grp_list:
                print(f"  - {n}")
        
        elif args.subcommand == "list-groups":
            if not group_meta:
                return print("No groups defined.")
            print("Defined groups:")
            for group, commands in group_meta.items():
                print(f"  {group}: {', '.join(commands) if commands else 'No commands'}")

        elif args.subcommand == "run":
            grp_list = group_meta.get(args.group, [])
            if not grp_list:
                return print(f"No commands to run in group '{args.group}'.")
            print(f"▶ Running group '{args.group}' in defined order:")
            for n in grp_list:
                entry = shortcuts.get(n)
                if not entry:
                    continue
                cmd = entry.get("cmd", "") if isinstance(entry, dict) else entry
                print(f"   • {n}: {cmd}")
                subprocess.run(cmd, shell=True)
        # --- lrgui ---
    elif args.command == "lrgui":
        from .webui import app
        print(f"🌐 | Starting LazyRun Web UI at http://127.0.0.1:{args.port}/")
        app.run(debug=True, port=args.port)
