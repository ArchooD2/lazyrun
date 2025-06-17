import sys
import subprocess
from snaparg import SnapArgumentParser as ArgumentParser
from .store import get_all, set_shortcut, del_shortcut

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
    """LazyRun: Shortcut your commands."""
    shortcuts = get_all()

    # --- No-arg splash screen ---
    if len(sys.argv) == 1:
        print(ASCII_BANNER)
        print("lazyrun – Task Runner With Memory")
        print("Save and run your most-used shell commands as easy shortcuts.")
        print()
        print("Example:")
        print("  lazyrun save build \"python setup.py sdist bdist_wheel\"")
        return

    # --- Bare invocation: run a shortcut by name ---
    if len(sys.argv) > 1 and sys.argv[1] not in ("save", "list", "remove"):
        name = sys.argv[1]
        if name in shortcuts:
            cmd = shortcuts[name]
            print(f"▶ | Running command: {cmd}")
            subprocess.run(cmd, shell=True)
            return

    # --- Subcommand parser ---
    parser = ArgumentParser(prog="lazyrun", description=cli.__doc__)
    subs = parser.add_subparsers(dest="command", required=True)

    # save
    save_p = subs.add_parser(
        "save",
        help="Save a command as a shortcut.",
        description="Save a command as a shortcut."
    )
    save_p.add_argument("name", help="Shortcut name")
    save_p.add_argument(
        "cmd",
        nargs="+",
        help="The full shell command to save (wrap in quotes if needed)"
    )

    # list
    subs.add_parser(
        "list",
        help="List all saved shortcuts.",
        description="List all saved shortcuts."
    )

    # remove
    rem_p = subs.add_parser(
        "remove",
        help="Remove a saved shortcut.",
        description="Remove a saved shortcut."
    )
    rem_p.add_argument(
        "name",
        choices=list(shortcuts.keys()),
        help="Name of the shortcut to remove"
    )

    args = parser.parse_args()

    if args.command == "save":
        cmd_str = " ".join(args.cmd)
        set_shortcut(args.name, cmd_str)
        print(f"✔ | Shortcut saved. '{args.name}' → {cmd_str}")

    elif args.command == "list":
        shortcuts = get_all()
        if not shortcuts:
            print("No shortcuts saved.")
        else:
            print("Saved shortcuts:")
            for name, c in shortcuts.items():
                print(f"  {name}: {c}")

    elif args.command == "remove":
        if args.name in shortcuts:
            del_shortcut(args.name)
            print(f"✔ | Shortcut '{args.name}' removed.")
        else:
            print(f"✘ | No shortcut found with the name '{args.name}'.")