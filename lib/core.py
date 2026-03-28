"""Core organize logic: scan, plan, preview, execute moves."""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .config import C
from .utils import (
    get_category, get_category_icon, human_size, safe_destination,
    get_date_subfolder, clean_filename, load_history, save_history,
    print_divider, ask_yes_no, notify,
)


def scan_files(target_dir, recursive=False):
    target = Path(target_dir).expanduser().resolve()
    if not target.exists():
        print(f"  {C.RED}✗ Directory not found: {target}{C.RESET}")
        sys.exit(1)

    files = []
    skip_dirs = {".git", "__pycache__", "node_modules", ".DS_Store", "Organized"}

    if recursive:
        for item in target.rglob("*"):
            if item.is_file() and not any(sd in item.parts for sd in skip_dirs):
                if not item.name.startswith("."):
                    files.append(item)
    else:
        for item in target.iterdir():
            if item.is_file() and not item.name.startswith("."):
                files.append(item)

    return files


def plan_moves(files, target_dir, use_dates=True, do_clean=False):
    target = Path(target_dir).expanduser().resolve()
    organized_root = target / "Organized"
    moves = []

    for filepath in files:
        category = get_category(filepath)
        if use_dates:
            dest_dir = organized_root / category / get_date_subfolder(filepath)
        else:
            dest_dir = organized_root / category

        filename = filepath.name
        renamed = False
        if do_clean:
            cleaned, changed = clean_filename(filename)
            if changed:
                filename = cleaned
                renamed = True

        dest_path = safe_destination(dest_dir / filename)
        moves.append({
            "source": str(filepath),
            "destination": str(dest_path),
            "category": category,
            "size": filepath.stat().st_size,
            "original_name": filepath.name,
            "final_name": filename,
            "renamed": renamed,
        })

    return moves


def preview_moves(moves):
    if not moves:
        print(f"  {C.YELLOW}No files to organize.{C.RESET}")
        return

    by_category = defaultdict(list)
    for move in moves:
        by_category[move["category"]].append(move)

    total_size = sum(m["size"] for m in moves)
    renamed_count = sum(1 for m in moves if m["renamed"])

    print(f"  {C.BOLD}Found {C.CYAN}{len(moves)}{C.RESET}{C.BOLD} files ({human_size(total_size)}){C.RESET}")
    if renamed_count:
        print(f"  {C.MAGENTA}↳ {renamed_count} filenames will be cleaned up{C.RESET}")
    print()

    for category in sorted(by_category.keys()):
        items = by_category[category]
        icon = get_category_icon(category)
        cat_size = sum(m["size"] for m in items)
        print(f"  {icon} {C.BOLD}{category}{C.RESET} {C.DIM}({len(items)} files, {human_size(cat_size)}){C.RESET}")

        for i, move in enumerate(items[:5]):
            size = human_size(move["size"])
            prefix = "├──" if i < min(len(items), 5) - 1 else "└──"
            if move["renamed"]:
                print(f"  {C.GRAY}  {prefix} {C.RED}{move['original_name']}{C.RESET} {C.GREEN}→ {move['final_name']}{C.RESET} {C.DIM}({size}){C.RESET}")
            else:
                print(f"  {C.GRAY}  {prefix} {C.RESET}{move['original_name']} {C.DIM}({size}){C.RESET}")

        if len(items) > 5:
            print(f"  {C.GRAY}  └── ... and {len(items) - 5} more{C.RESET}")
        print()


def execute_moves(moves, target_dir):
    if not moves:
        return

    timestamp = datetime.now().isoformat()
    operation = {"timestamp": timestamp, "target_dir": str(target_dir), "moves": []}
    success = errors = 0

    print(f"  {C.BOLD}Moving files...{C.RESET}\n")

    for i, move in enumerate(moves):
        src = Path(move["source"])
        dst = Path(move["destination"])
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            operation["moves"].append({"source": str(src), "destination": str(dst)})
            success += 1
            icon = get_category_icon(move["category"])
            tag = f" {C.MAGENTA}(renamed){C.RESET}" if move.get("renamed") else ""
            print(f"  {C.GREEN}✓{C.RESET} {C.DIM}[{i+1}/{len(moves)}]{C.RESET} {icon} {move['final_name']} {C.DIM}→ {move['category']}/{C.RESET}{tag}")
        except Exception as e:
            errors += 1
            print(f"  {C.RED}✗{C.RESET} {src.name}: {e}")

    print(f"\n", end="")
    print_divider()
    print(f"  {C.GREEN}{C.BOLD}Done!{C.RESET} {success} moved, {errors} errors")

    if operation["moves"]:
        history = load_history()
        history.append(operation)
        save_history(history[-200:])
        print(f"  {C.DIM}Run with --undo to reverse this operation{C.RESET}")

    target_name = Path(target_dir).name
    notify("File Organizer", f"Organized {success} files in {target_name}")


def execute_moves_interactive(moves, target_dir):
    if not moves:
        return

    by_category = defaultdict(list)
    for move in moves:
        by_category[move["category"]].append(move)

    approved = []
    for category in sorted(by_category.keys()):
        items = by_category[category]
        icon = get_category_icon(category)
        cat_size = sum(m["size"] for m in items)

        print(f"\n  {icon} {C.BOLD}{category}{C.RESET} {C.DIM}({len(items)} files, {human_size(cat_size)}){C.RESET}")
        for move in items[:8]:
            print(f"  {C.GRAY}    {move['original_name']} ({human_size(move['size'])}){C.RESET}")
        if len(items) > 8:
            print(f"  {C.GRAY}    ... and {len(items) - 8} more{C.RESET}")

        if ask_yes_no(f"Move {len(items)} {category} files?"):
            approved.extend(items)
            print(f"  {C.GREEN}✓ Approved{C.RESET}")
        else:
            print(f"  {C.YELLOW}⊘ Skipped{C.RESET}")

    if approved:
        print()
        print_divider()
        execute_moves(approved, target_dir)
    else:
        print(f"\n  {C.YELLOW}No categories approved.{C.RESET}")
