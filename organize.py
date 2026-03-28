#!/usr/bin/env python3
"""
Smart Local File Organizer v2 — CLI Entry Point
Run `python3 organize.py --help` for usage.
"""

import argparse
from pathlib import Path

from lib.config import C
from lib.utils import print_header, print_divider
from lib.core import scan_files, plan_moves, preview_moves, execute_moves, execute_moves_interactive
from lib.analyzers import (
    find_duplicates, find_junk, find_stale, find_large,
    reclaim_space, show_recency, preview_clean_names, show_stats,
)
from lib.history import undo_last, undo_all, show_history, watch_mode


def main():
    parser = argparse.ArgumentParser(
        description="Smart Local File Organizer v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  organize.py                           Preview organizing ~/Downloads
  organize.py --run                     Actually organize the files
  organize.py --interactive --run       Approve each category
  organize.py --clean-names             Preview filename cleanups
  organize.py --clean-names --run       Organize + clean filenames
  organize.py --duplicates              Find duplicate files
  organize.py --junk                    Find junk/temp files
  organize.py --junk --run              Delete junk files
  organize.py --stale                   Find old untouched files
  organize.py --large                   Find space hogs
  organize.py --reclaim                 Disk space reclaimer (all-in-one)
  organize.py --reclaim --run           Reclaim with interactive deletion
  organize.py --recency                 View by recency
  organize.py --stats                   Full intelligence report
  organize.py --watch                   Auto-organize new files
  organize.py --undo                    Reverse last operation
  organize.py --undo-all                Reverse ALL operations
        """,
    )

    parser.add_argument("--path", "-p", default="~/Downloads", help="Target directory")
    parser.add_argument("--run", "-r", action="store_true", help="Execute (default: dry-run)")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch & auto-organize")
    parser.add_argument("--undo", "-u", action="store_true", help="Undo last operation")
    parser.add_argument("--undo-all", action="store_true", help="Undo ALL operations")
    parser.add_argument("--stats", "-s", action="store_true", help="Intelligence report")
    parser.add_argument("--history", action="store_true", help="Operation history")
    parser.add_argument("--no-dates", action="store_true", help="No date subfolders")
    parser.add_argument("--recursive", action="store_true", help="Scan recursively")
    parser.add_argument("--duplicates", "-d", action="store_true", help="Find duplicates")
    parser.add_argument("--junk", "-j", action="store_true", help="Find junk files")
    parser.add_argument("--stale", action="store_true", help="Find stale files")
    parser.add_argument("--large", "-l", action="store_true", help="Find largest files")
    parser.add_argument("--reclaim", action="store_true", help="Disk space reclaimer")
    parser.add_argument("--recency", action="store_true", help="View by recency")
    parser.add_argument("--clean-names", action="store_true", help="Clean messy filenames")
    parser.add_argument("--interactive", "-i", action="store_true", help="Approve per category")

    args = parser.parse_args()
    target_dir = str(Path(args.path).expanduser().resolve())
    use_dates = not args.no_dates

    print_header()

    if args.undo_all:
        undo_all(); print(); return
    if args.undo:
        undo_last(); print(); return
    if args.history:
        show_history(); print(); return
    if args.duplicates:
        find_duplicates(target_dir, args.recursive); print(); return
    if args.junk:
        find_junk(target_dir, args.recursive, args.run); print(); return
    if args.stale:
        find_stale(target_dir, args.recursive); print(); return
    if args.large:
        find_large(target_dir, args.recursive); print(); return
    if args.reclaim:
        reclaim_space(target_dir, args.recursive, args.run); print(); return
    if args.recency:
        show_recency(target_dir, args.recursive); print(); return
    if args.clean_names and not args.run:
        preview_clean_names(target_dir, args.recursive); print(); return
    if args.stats:
        show_stats(target_dir); print(); return
    if args.watch:
        watch_mode(target_dir, use_dates, args.clean_names); print(); return

    # Default: organize
    print(f"  {C.BOLD}Target: {C.CYAN}{target_dir}{C.RESET}")
    mode = f"{C.GREEN}LIVE{C.RESET}" if args.run else f"{C.YELLOW}DRY RUN{C.RESET}"
    itag = f" {C.MAGENTA}(interactive){C.RESET}" if args.interactive else ""
    print(f"  {C.BOLD}Mode:   {mode}{itag}")
    flags = [f for f, v in [("dates", use_dates), ("clean-names", args.clean_names),
             ("recursive", args.recursive)] if v]
    print(f"  {C.BOLD}Flags:  {C.DIM}{', '.join(flags) or 'none'}{C.RESET}")
    print()
    print_divider()
    print()

    files = scan_files(target_dir, args.recursive)
    moves = plan_moves(files, target_dir, use_dates, args.clean_names)
    preview_moves(moves)

    if not moves:
        print(); return

    if args.run:
        print_divider()
        print()
        if args.interactive:
            execute_moves_interactive(moves, target_dir)
        else:
            execute_moves(moves, target_dir)
    else:
        print_divider()
        print()
        print(f"  {C.YELLOW}{C.BOLD}Preview only.{C.RESET} No files moved.")
        print(f"  {C.DIM}{C.WHITE}--run{C.DIM} to organize  ·  {C.WHITE}--interactive --run{C.DIM} to approve each  ·  {C.WHITE}--stats{C.DIM} for insights{C.RESET}")

    print()


if __name__ == "__main__":
    main()
