"""History management: undo, undo_all, show_history, watch_mode."""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime

from .config import C
from .utils import load_history, save_history, print_divider, print_section
from .core import plan_moves, execute_moves


def _undo_operation(op):
    """Undo a single operation. Returns (success, errors) counts."""
    moves = op["moves"]
    success = errors = 0
    for move in reversed(moves):
        src = Path(move["destination"])
        dst = Path(move["source"])
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            success += 1
            print(f"  {C.GREEN}↩{C.RESET} {src.name} {C.DIM}→ back{C.RESET}")
        except Exception as e:
            errors += 1
            print(f"  {C.RED}✗{C.RESET} {src.name}: {e}")

    organized = Path(op["target_dir"]) / "Organized"
    if organized.exists():
        for dp, _, _ in os.walk(str(organized), topdown=False):
            dp = Path(dp)
            try:
                if dp != organized and not any(dp.iterdir()):
                    dp.rmdir()
            except OSError:
                pass
        try:
            if not any(organized.iterdir()):
                organized.rmdir()
        except OSError:
            pass

    return success, errors


def undo_last():
    history = load_history()
    if not history:
        print(f"  {C.YELLOW}No operations to undo.{C.RESET}")
        return

    last = history[-1]
    print(f"  {C.BOLD}Undoing {len(last['moves'])} moves from {last['timestamp'][:19]}{C.RESET}\n")

    success, errors = _undo_operation(last)

    print()
    print_divider()
    print(f"  {C.GREEN}{C.BOLD}Undo complete!{C.RESET} {success} restored, {errors} errors")
    history.pop()
    save_history(history)


def undo_all():
    history = load_history()
    if not history:
        print(f"  {C.YELLOW}No operations to undo.{C.RESET}")
        return

    total_ops = len(history)
    total_moves = sum(len(op["moves"]) for op in history)
    print(f"  {C.BOLD}Undoing ALL {total_ops} operations ({total_moves} total file moves){C.RESET}")
    print()

    total_success = total_errors = 0

    for i, op in enumerate(reversed(history)):
        ts = op["timestamp"][:19].replace("T", " ")
        print(f"  {C.CYAN}[{i+1}/{total_ops}]{C.RESET} {C.DIM}{ts} — {len(op['moves'])} files{C.RESET}")
        success, errors = _undo_operation(op)
        total_success += success
        total_errors += errors
        print()

    print_divider()
    print(f"  {C.GREEN}{C.BOLD}Full undo complete!{C.RESET} {total_success} restored, {total_errors} errors across {total_ops} operations")
    save_history([])


def show_history():
    history = load_history()
    if not history:
        print(f"  {C.YELLOW}No history yet.{C.RESET}")
        return
    print_section("Operation History", "📜")
    for i, op in enumerate(reversed(history)):
        ts = op["timestamp"][:19].replace("T", " ")
        count = len(op["moves"])
        tag = f" {C.CYAN}(latest){C.RESET}" if i == 0 else ""
        print(f"  {C.DIM}{i+1}.{C.RESET} {ts}  {C.BOLD}{count} files{C.RESET}  {C.DIM}{op['target_dir']}{C.RESET}{tag}")


def watch_mode(target_dir, use_dates=True, do_clean=False):
    target = Path(target_dir).expanduser().resolve()
    print(f"  {C.BOLD}👁  Watching: {C.CYAN}{target}{C.RESET}")
    print(f"  {C.DIM}Press Ctrl+C to stop{C.RESET}\n")

    seen = {f.name for f in target.iterdir() if f.is_file()}

    try:
        while True:
            time.sleep(2)
            current = set()
            new_files = []
            for f in target.iterdir():
                if f.is_file() and not f.name.startswith("."):
                    current.add(f.name)
                    if f.name not in seen:
                        time.sleep(1)
                        if f.exists():
                            new_files.append(f)
            if new_files:
                moves = plan_moves(new_files, target_dir, use_dates, do_clean)
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  {C.DIM}[{now}]{C.RESET} {C.GREEN}{len(new_files)} new file(s)!{C.RESET}")
                execute_moves(moves, target_dir)
                print()
            seen = current
    except KeyboardInterrupt:
        print(f"\n  {C.YELLOW}Watch mode stopped.{C.RESET}")
