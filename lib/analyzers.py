"""Smart analysis features: duplicates, junk, stale, large, reclaim, recency, stats."""

import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from .config import C
from .utils import (
    is_junk, is_screenshot, get_category, get_category_icon,
    human_size, human_age, file_hash, clean_filename,
    print_divider, print_section, ask_yes_no, notify,
)
from .core import scan_files


def find_duplicates(target_dir, recursive=False):
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Duplicate File Scanner", "🔍")
    print(f"  {C.DIM}Hashing {len(files)} files...{C.RESET}\n")

    by_size = defaultdict(list)
    for f in files:
        try:
            by_size[f.stat().st_size].append(f)
        except OSError:
            pass

    hash_map = defaultdict(list)
    for size, group in by_size.items():
        if len(group) < 2:
            continue
        for f in group:
            h = file_hash(f)
            if h:
                hash_map[h].append(f)

    dup_groups = {h: fs for h, fs in hash_map.items() if len(fs) > 1}

    if not dup_groups:
        print(f"  {C.GREEN}✓ No duplicates found!{C.RESET} All {len(files)} files are unique.")
        return

    total_wasted = 0
    total_dup_files = 0

    for i, (h, dups) in enumerate(sorted(dup_groups.items(),
            key=lambda x: x[1][0].stat().st_size, reverse=True)):
        size = dups[0].stat().st_size
        total_wasted += size * (len(dups) - 1)
        total_dup_files += len(dups) - 1

        print(f"  {C.BOLD}Group {i+1}{C.RESET} {C.DIM}({human_size(size)} each, {len(dups)} copies){C.RESET}")
        for j, f in enumerate(dups):
            age = human_age(time.time() - f.stat().st_mtime)
            tag = f"{C.GREEN}(original){C.RESET}" if j == 0 else f"{C.RED}(duplicate){C.RESET}"
            print(f"    {tag} {f.name} {C.DIM}{age}{C.RESET}")
        print()

    print_divider()
    print(f"  {C.BOLD}{C.RED}{total_dup_files} duplicates{C.RESET} wasting {C.BOLD}{human_size(total_wasted)}{C.RESET}")
    print(f"  {C.DIM}Review and delete the duplicates manually to reclaim space{C.RESET}")


def find_junk(target_dir, recursive=False, do_delete=False):
    target = Path(target_dir).expanduser().resolve()
    all_files = list(target.iterdir()) if not recursive else list(target.rglob("*"))
    all_files = [f for f in all_files if f.is_file()]

    print_section("Junk & Temp File Scanner", "🗑️ ")

    empty_files = []
    broken_downloads = []
    junk_files = []

    for f in all_files:
        try:
            size = f.stat().st_size
        except OSError:
            continue
        ext = f.suffix.lower()

        if size == 0:
            empty_files.append(f)
        elif ext in {".crdownload", ".part", ".download"}:
            broken_downloads.append(f)
        elif is_junk(f):
            junk_files.append(f)

    total = len(empty_files) + len(broken_downloads) + len(junk_files)
    if total == 0:
        print(f"  {C.GREEN}✓ No junk found!{C.RESET} Folder is clean.")
        return

    if empty_files:
        print(f"\n  {C.YELLOW}Empty files ({len(empty_files)}):{C.RESET}")
        for f in empty_files[:10]:
            print(f"    {C.DIM}○{C.RESET} {f.name}")
        if len(empty_files) > 10:
            print(f"    {C.DIM}... and {len(empty_files) - 10} more{C.RESET}")

    if broken_downloads:
        bsize = sum(f.stat().st_size for f in broken_downloads)
        print(f"\n  {C.RED}Broken downloads ({len(broken_downloads)}, {human_size(bsize)}):{C.RESET}")
        for f in broken_downloads[:10]:
            print(f"    {C.RED}✗{C.RESET} {f.name} {C.DIM}({human_size(f.stat().st_size)}, {human_age(time.time() - f.stat().st_mtime)}){C.RESET}")

    if junk_files:
        jsize = sum(f.stat().st_size for f in junk_files)
        print(f"\n  {C.YELLOW}Temp/junk files ({len(junk_files)}, {human_size(jsize)}):{C.RESET}")
        for f in junk_files[:10]:
            print(f"    {C.YELLOW}~{C.RESET} {f.name} {C.DIM}({human_size(f.stat().st_size)}){C.RESET}")

    all_junk = empty_files + broken_downloads + junk_files
    total_size = sum(f.stat().st_size for f in all_junk)
    print()
    print_divider()
    print(f"  {C.BOLD}{total} junk files{C.RESET} taking {C.BOLD}{human_size(total_size)}{C.RESET}")

    if do_delete:
        if ask_yes_no(f"Delete all {total} junk files?", default=False):
            deleted = 0
            for f in all_junk:
                try:
                    f.unlink()
                    deleted += 1
                except OSError as e:
                    print(f"  {C.RED}✗{C.RESET} {f.name}: {e}")
            print(f"  {C.GREEN}✓ Deleted {deleted} files, freed {human_size(total_size)}{C.RESET}")
        else:
            print(f"  {C.DIM}No files deleted.{C.RESET}")
    else:
        print(f"  {C.DIM}Add --run to be prompted to delete them{C.RESET}")


def find_stale(target_dir, recursive=False):
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Stale File Finder", "🕸️ ")

    now = time.time()
    buckets = {"1+ year": [], "180+ days": [], "90+ days": [], "30+ days": []}

    for f in files:
        try:
            age_days = (now - f.stat().st_mtime) / 86400
        except OSError:
            continue
        if age_days >= 365:
            buckets["1+ year"].append((f, age_days))
        elif age_days >= 180:
            buckets["180+ days"].append((f, age_days))
        elif age_days >= 90:
            buckets["90+ days"].append((f, age_days))
        elif age_days >= 30:
            buckets["30+ days"].append((f, age_days))

    total_stale = sum(len(v) for v in buckets.values())
    if total_stale == 0:
        print(f"  {C.GREEN}✓ No stale files!{C.RESET} Everything was touched in the last 30 days.")
        return

    icons = {"30+ days": "🟡", "90+ days": "🟠", "180+ days": "🔴", "1+ year": "💀"}
    colors = {"30+ days": C.YELLOW, "90+ days": C.YELLOW, "180+ days": C.RED, "1+ year": C.RED}

    for label in ["1+ year", "180+ days", "90+ days", "30+ days"]:
        items = buckets[label]
        if not items:
            continue
        items.sort(key=lambda x: x[1], reverse=True)
        total_size = sum(f.stat().st_size for f, _ in items)
        print(f"\n  {icons[label]} {colors[label]}{C.BOLD}{label}{C.RESET} {C.DIM}({len(items)} files, {human_size(total_size)}){C.RESET}")
        for f, age in items[:8]:
            cat_icon = get_category_icon(get_category(f))
            print(f"    {cat_icon} {f.name} {C.DIM}({human_size(f.stat().st_size)}, {human_age(age * 86400)}){C.RESET}")
        if len(items) > 8:
            print(f"    {C.DIM}... and {len(items) - 8} more{C.RESET}")

    total_size = sum(f.stat().st_size for b in buckets.values() for f, _ in b)
    print()
    print_divider()
    print(f"  {C.BOLD}{total_stale} stale files{C.RESET} taking {C.BOLD}{human_size(total_size)}{C.RESET}")


def reclaim_space(target_dir, recursive=False, do_delete=False):
    """Combined disk space reclaimer: duplicates + junk + stale in one pass."""
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    target = Path(target_dir).expanduser().resolve()
    all_files_for_junk = [f for f in target.iterdir() if f.is_file()] if not recursive \
        else [f for f in target.rglob("*") if f.is_file()]

    print_section("Disk Space Reclaimer", "💾")
    print(f"  {C.DIM}Scanning {len(files)} files...{C.RESET}")

    # Junk
    empty_files, broken_downloads, junk_files = [], [], []
    for f in all_files_for_junk:
        try:
            size = f.stat().st_size
        except OSError:
            continue
        ext = f.suffix.lower()
        if size == 0:
            empty_files.append(f)
        elif ext in {".crdownload", ".part", ".download"}:
            broken_downloads.append(f)
        elif is_junk(f):
            junk_files.append(f)

    all_junk = empty_files + broken_downloads + junk_files
    junk_size = sum(f.stat().st_size for f in all_junk)

    # Duplicates
    by_size = defaultdict(list)
    for f in files:
        try:
            by_size[f.stat().st_size].append(f)
        except OSError:
            pass
    hash_map = defaultdict(list)
    for size, group in by_size.items():
        if len(group) < 2:
            continue
        for f in group:
            h = file_hash(f)
            if h:
                hash_map[h].append(f)
    dup_groups = {h: fs for h, fs in hash_map.items() if len(fs) > 1}
    dup_files = []
    for h, dups in dup_groups.items():
        dup_files.extend(dups[1:])
    dup_size = sum(f.stat().st_size for f in dup_files)

    # Stale (90+ days)
    now = time.time()
    stale_files = []
    for f in files:
        try:
            age_days = (now - f.stat().st_mtime) / 86400
            if age_days >= 90:
                stale_files.append((f, age_days))
        except OSError:
            pass
    stale_files.sort(key=lambda x: x[1], reverse=True)
    stale_size = sum(f.stat().st_size for f, _ in stale_files)

    total_reclaimable = junk_size + dup_size
    print()

    if all_junk:
        print(f"  {C.RED}🗑  Junk & Temp Files{C.RESET} {C.DIM}— {len(all_junk)} files, {human_size(junk_size)} reclaimable{C.RESET}")
        for f in all_junk[:5]:
            size = human_size(f.stat().st_size) if f.stat().st_size > 0 else "empty"
            print(f"    {C.DIM}•{C.RESET} {f.name} {C.DIM}({size}){C.RESET}")
        if len(all_junk) > 5:
            print(f"    {C.DIM}... and {len(all_junk) - 5} more{C.RESET}")
        print()
    else:
        print(f"  {C.GREEN}✓ No junk files{C.RESET}\n")

    if dup_files:
        print(f"  {C.MAGENTA}🔍 Duplicate Files{C.RESET} {C.DIM}— {len(dup_files)} duplicates in {len(dup_groups)} groups, {human_size(dup_size)} reclaimable{C.RESET}")
        shown = 0
        for h, dups in sorted(dup_groups.items(), key=lambda x: x[1][0].stat().st_size, reverse=True):
            if shown >= 3:
                remaining = len(dup_groups) - 3
                if remaining > 0:
                    print(f"    {C.DIM}... and {remaining} more groups{C.RESET}")
                break
            size = human_size(dups[0].stat().st_size)
            print(f"    {C.DIM}•{C.RESET} {C.BOLD}{dups[0].name}{C.RESET} {C.DIM}({size} × {len(dups)} copies){C.RESET}")
            shown += 1
        print()
    else:
        print(f"  {C.GREEN}✓ No duplicates{C.RESET}\n")

    if stale_files:
        print(f"  {C.YELLOW}🕸  Stale Files (90+ days){C.RESET} {C.DIM}— {len(stale_files)} files, {human_size(stale_size)}{C.RESET}")
        for f, age in stale_files[:5]:
            cat_icon = get_category_icon(get_category(f))
            print(f"    {cat_icon} {f.name} {C.DIM}({human_size(f.stat().st_size)}, {human_age(age * 86400)}){C.RESET}")
        if len(stale_files) > 5:
            print(f"    {C.DIM}... and {len(stale_files) - 5} more{C.RESET}")
        print()
    else:
        print(f"  {C.GREEN}✓ No stale files{C.RESET}\n")

    print_divider()
    print()
    print(f"  {C.BOLD}📊 Space Recovery Summary{C.RESET}")
    print(f"     Junk files:       {C.BOLD}{human_size(junk_size)}{C.RESET} {C.DIM}({len(all_junk)} files){C.RESET}")
    print(f"     Duplicates:       {C.BOLD}{human_size(dup_size)}{C.RESET} {C.DIM}({len(dup_files)} files){C.RESET}")
    print(f"     {C.DIM}Stale (review):    {human_size(stale_size)} ({len(stale_files)} files){C.RESET}")
    print()
    print(f"  {C.GREEN}{C.BOLD}  → {human_size(total_reclaimable)} instantly reclaimable{C.RESET}")
    print(f"  {C.DIM}  → {human_size(total_reclaimable + stale_size)} total if stale files are also removed{C.RESET}")

    if not do_delete:
        print(f"\n  {C.DIM}Add --run to interactively delete{C.RESET}")
        return

    if total_reclaimable == 0 and not stale_files:
        print(f"\n  {C.GREEN}Nothing to reclaim!{C.RESET}")
        return

    freed = 0
    deleted_count = 0

    if all_junk:
        print()
        if ask_yes_no(f"Delete {len(all_junk)} junk/temp files ({human_size(junk_size)})?", default=True):
            for f in all_junk:
                try:
                    f.unlink()
                    deleted_count += 1
                except OSError:
                    pass
            freed += junk_size
            print(f"  {C.GREEN}✓ Deleted {len(all_junk)} junk files{C.RESET}")

    if dup_files:
        if ask_yes_no(f"Delete {len(dup_files)} duplicate files ({human_size(dup_size)})?", default=False):
            del_count = 0
            for f in dup_files:
                try:
                    f.unlink()
                    del_count += 1
                except OSError:
                    pass
            freed += dup_size
            deleted_count += del_count
            print(f"  {C.GREEN}✓ Deleted {del_count} duplicates{C.RESET}")

    if stale_files:
        if ask_yes_no(f"Delete {len(stale_files)} stale files ({human_size(stale_size)})?", default=False):
            del_count = 0
            for f, _ in stale_files:
                try:
                    f.unlink()
                    del_count += 1
                except OSError:
                    pass
            freed += stale_size
            deleted_count += del_count
            print(f"  {C.GREEN}✓ Deleted {del_count} stale files{C.RESET}")

    print()
    print_divider()
    if freed > 0:
        print(f"  {C.GREEN}{C.BOLD}Reclaimed {human_size(freed)}!{C.RESET} {C.DIM}({deleted_count} files deleted){C.RESET}")
        notify("File Organizer", f"Reclaimed {human_size(freed)} by removing {deleted_count} files")
    else:
        print(f"  {C.DIM}No files deleted.{C.RESET}")


def find_large(target_dir, recursive=False, top_n=20):
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Large File Spotlight", "📊")

    file_sizes = []
    for f in files:
        try:
            file_sizes.append((f, f.stat().st_size))
        except OSError:
            pass

    file_sizes.sort(key=lambda x: x[1], reverse=True)
    top = file_sizes[:top_n]
    if not top:
        return

    total_size = sum(s for _, s in file_sizes)
    max_size = top[0][1]
    bar_w = 30

    print(f"  {C.DIM}Top {len(top)} of {len(file_sizes)} files · Total: {human_size(total_size)}{C.RESET}\n")

    for i, (f, size) in enumerate(top):
        bar_len = int((size / max_size) * bar_w)
        bar = "█" * bar_len + "░" * (bar_w - bar_len)
        pct = (size / total_size) * 100 if total_size else 0
        color = C.RED if size > 500_000_000 else C.YELLOW if size > 100_000_000 else C.CYAN
        icon = get_category_icon(get_category(f))
        age = human_age(time.time() - f.stat().st_mtime)
        print(f"  {C.DIM}{i+1:>2}.{C.RESET} {icon} {f.name}")
        print(f"      {color}{bar}{C.RESET} {C.BOLD}{human_size(size)}{C.RESET} {C.DIM}({pct:.1f}%, {age}){C.RESET}")

    top_size = sum(s for _, s in top)
    print()
    print_divider()
    print(f"  {C.BOLD}Top {len(top)}: {human_size(top_size)}{C.RESET} {C.DIM}({top_size / total_size * 100:.0f}% of total){C.RESET}")


def show_recency(target_dir, recursive=False):
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Recency View", "🕐")

    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = today - timedelta(days=today.weekday())
    month = today.replace(day=1)

    buckets = {"Today": [], "This Week": [], "This Month": [], "Older": []}
    icons = {"Today": "🟢", "This Week": "🔵", "This Month": "🟡", "Older": "⚪"}

    for f in files:
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
        except OSError:
            continue
        if mtime >= today:
            buckets["Today"].append(f)
        elif mtime >= week:
            buckets["This Week"].append(f)
        elif mtime >= month:
            buckets["This Month"].append(f)
        else:
            buckets["Older"].append(f)

    for label in ["Today", "This Week", "This Month", "Older"]:
        items = buckets[label]
        if not items:
            continue
        items.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        total_size = sum(f.stat().st_size for f in items)
        print(f"\n  {icons[label]} {C.BOLD}{label}{C.RESET} {C.DIM}({len(items)} files, {human_size(total_size)}){C.RESET}")
        for f in items[:6]:
            cat_icon = get_category_icon(get_category(f))
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            ts = mtime.strftime("%H:%M") if label == "Today" else mtime.strftime("%b %d")
            print(f"    {cat_icon} {f.name} {C.DIM}({human_size(f.stat().st_size)}, {ts}){C.RESET}")
        if len(items) > 6:
            print(f"    {C.DIM}... and {len(items) - 6} more{C.RESET}")


def preview_clean_names(target_dir, recursive=False):
    files = scan_files(target_dir, recursive)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Filename Cleanup Preview", "✨")

    changes = [(f, clean_filename(f.name)[0]) for f in files if clean_filename(f.name)[1]]

    if not changes:
        print(f"  {C.GREEN}✓ All filenames look clean!{C.RESET}")
        return

    print(f"  {C.BOLD}{len(changes)} filenames can be cleaned:{C.RESET}\n")
    for f, cleaned in changes[:25]:
        print(f"    {C.RED}{f.name}{C.RESET}")
        print(f"    {C.GREEN}→ {cleaned}{C.RESET}\n")
    if len(changes) > 25:
        print(f"  {C.DIM}... and {len(changes) - 25} more{C.RESET}")

    print_divider()
    print(f"  {C.DIM}Use --clean-names --run to organize with cleaned names{C.RESET}")


def show_stats(target_dir):
    files = scan_files(target_dir)
    if not files:
        print(f"  {C.YELLOW}No files found.{C.RESET}")
        return

    print_section("Directory Intelligence Report", "📊")

    by_category = defaultdict(lambda: {"count": 0, "size": 0})
    oldest = newest = None
    largest_file = None
    largest_size = 0

    for f in files:
        cat = get_category(f)
        try:
            size = f.stat().st_size
            mtime = f.stat().st_mtime
        except OSError:
            continue
        by_category[cat]["count"] += 1
        by_category[cat]["size"] += size
        if oldest is None or mtime < oldest:
            oldest = mtime
        if newest is None or mtime > newest:
            newest = mtime
        if size > largest_size:
            largest_size = size
            largest_file = f

    total_size = sum(info["size"] for info in by_category.values())

    print(f"  Total files:    {C.BOLD}{len(files)}{C.RESET}")
    print(f"  Total size:     {C.BOLD}{human_size(total_size)}{C.RESET}")
    if largest_file:
        print(f"  Largest:        {C.BOLD}{largest_file.name}{C.RESET} {C.DIM}({human_size(largest_size)}){C.RESET}")
    if oldest:
        print(f"  Oldest:         {C.DIM}{datetime.fromtimestamp(oldest).strftime('%Y-%m-%d')}{C.RESET}")
    if newest:
        print(f"  Newest:         {C.DIM}{datetime.fromtimestamp(newest).strftime('%Y-%m-%d')}{C.RESET}")

    insights = []
    junk_count = sum(1 for f in files if is_junk(f))
    screenshot_count = sum(1 for f in files if is_screenshot(f))
    now = time.time()
    stale_count = sum(1 for f in files if (now - f.stat().st_mtime) > 90 * 86400)
    size_counts = defaultdict(int)
    for f in files:
        try:
            size_counts[f.stat().st_size] += 1
        except OSError:
            pass
    dup_groups = sum(1 for c in size_counts.values() if c > 1)

    if junk_count:
        insights.append(f"{C.YELLOW}⚠{C.RESET}  {junk_count} junk/temp files → {C.WHITE}--junk{C.RESET}")
    if screenshot_count > 3:
        insights.append(f"{C.CYAN}📸{C.RESET} {screenshot_count} screenshots will be auto-grouped")
    if dup_groups:
        insights.append(f"{C.MAGENTA}🔍{C.RESET} {dup_groups} possible duplicate groups → {C.WHITE}--duplicates{C.RESET}")
    if stale_count:
        insights.append(f"{C.RED}🕸️{C.RESET}  {stale_count} files older than 90 days → {C.WHITE}--stale{C.RESET}")

    if insights:
        print(f"\n  {C.BOLD}Smart Insights:{C.RESET}")
        for line in insights:
            print(f"    {line}")
    print()

    if not by_category:
        return
    max_count = max(info["count"] for info in by_category.values())
    bar_w = 25
    for cat in sorted(by_category.keys(), key=lambda c: by_category[c]["count"], reverse=True):
        info = by_category[cat]
        icon = get_category_icon(cat)
        bar_len = int((info["count"] / max_count) * bar_w)
        bar = "█" * bar_len + "░" * (bar_w - bar_len)
        print(f"  {icon} {cat:<14} {C.CYAN}{bar}{C.RESET} {info['count']:>4}  {C.DIM}{human_size(info['size'])}{C.RESET}")
