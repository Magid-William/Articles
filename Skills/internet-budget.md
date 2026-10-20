---
name: internet-budget
description: Use before any action that downloads data over the network: package installs (pip, npm, apt, cargo), git clones, Docker image pulls, model or dataset downloads, bulk scraping, large file fetches, or system updates. The user's connection is metered, so check size first and ask before anything sizeable.
---

# Internet budget

The connection is metered: 150 GB per recharge, ~20 GB/day typical use, so a recharge lasts only ~7–8 days. Every extra GB shortens it. Never assume unlimited bandwidth.

## Before downloading

1. **Check what's already local.** Look in caches (pip, pnpm, HF, Docker layers), existing clones, and files already on disk before fetching anything.
2. **Estimate size.** Don't guess if you can measure.
3. **Apply the threshold:**
   - **Under ~100 MB:** proceed, and mention it in a line if it's non-trivial.
   - **100 MB and up (or unknown size):** state the estimate and ask before starting.
   - **1 GB and up:** ask, and offer a smaller alternative (quantized model, subset, shallow clone).
4. **Pick the cheapest option.** Smaller variants, pinned versions, targeted file fetches (`--include` patterns, sparse checkout) over whole repos. No speculative or "just in case" downloads, and no needless upgrades (`apt upgrade`, `pip install -U`, re-pulling `latest`).

## During a big download

- Run it **once**, in the background (`nohup ... > dl.log 2>&1 &`) or with no timeout, then wait. Waiting hours is normal.
- Use resumable tools: `wget -c`, `curl -C -`, `aria2c -c`, `rsync --partial`, `huggingface-cli download` (resumes automatically).
- To check progress, read the log or `ls -l` / `du -h` the partial file. Don't start another request.
- **Never** kill, restart, or re-run it to "check" or "speed up". That discards progress and costs bandwidth again.

## If it fails

Only step in on a real error exit. Then **resume** (same command with the resume flag, same destination) rather than restart. If resuming isn't possible, tell the user how much was lost before retrying.

## After

If you fetched something large, say so in one line (what and roughly how big) and where it's cached, so it isn't downloaded again.
