# Matt Hartley

Systems engineer building terminal diagnostics tools in Rust. Sydney, Australia.
[netwatchlabs.com](https://netwatchlabs.com)

<p align="center">
  <a href="https://github.com/matthart1983/netwatch">
    <img src="assets/netwatch.gif" width="800" alt="netwatch's dense view: a mirrored braille throughput graph with download above the axis and upload below, per-interface rates with sparklines, four-hop latency budgets, and a connection table with the selected socket's kernel TCP state">
  </a>
</p>

<p align="center"><b><a href="https://github.com/matthart1983/netwatch#install">Install netwatch</a></b></p>

netwatch was [Terminal Trove's Tool of the Week](https://terminaltrove.com/netwatch/), was covered by [Habr](https://habr.com/en/news/1094358/) and was featured in Github Awesome's [35 Self-Hosted Projects on GitHub](https://www.youtube.com/watch?v=TBOtZ3mBktM&t=112s). It ships in Homebrew, conda-forge, nixpkgs, the AUR and Alpine (testing). Across the tools: 120k+ downloads (Nov 2026).

## Diagnostics tools

netwatch, syswatch and diskwatch share one layout and palette.

- **[netwatch](https://github.com/matthart1983/netwatch)**: live capture with L7 decode, TLS 1.3 decryption, eBPF process attribution on Linux and baseline-driven diagnosis. [![stars](https://img.shields.io/github/stars/matthart1983/netwatch?style=flat&label=stars)](https://github.com/matthart1983/netwatch/stargazers)
- **[syswatch](https://github.com/matthart1983/syswatch)**: CPU, memory, disks, processes, GPU and power on macOS and Linux, with recent history you can scrub. [![stars](https://img.shields.io/github/stars/matthart1983/syswatch?style=flat&label=stars)](https://github.com/matthart1983/syswatch/stargazers)
- **[diskwatch](https://github.com/matthart1983/diskwatch)**: disk activity, capacity, health and busy files in one terminal. Read-only, no config. [![stars](https://img.shields.io/github/stars/matthart1983/diskwatch?style=flat&label=stars)](https://github.com/matthart1983/diskwatch/stargazers)
- **[kernwatch](https://github.com/matthart1983/kernwatch)**: CPU contention, scheduling, memory pressure and block IO on Linux, with stack profiles and incident reports. [![stars](https://img.shields.io/github/stars/matthart1983/kernwatch?style=flat&label=stars)](https://github.com/matthart1983/kernwatch/stargazers)
- **[essh](https://github.com/matthart1983/essh)**: remote shells that survive connection drops, built on OpenSSH and tmux. [![stars](https://img.shields.io/github/stars/matthart1983/essh?style=flat&label=stars)](https://github.com/matthart1983/essh/stargazers)
- **[netscan](https://github.com/matthart1983/netscan)**: an nmap workflow with target inventory, saved profiles, live results and scan diffs. *Paused.* [![stars](https://img.shields.io/github/stars/matthart1983/netscan?style=flat&label=stars)](https://github.com/matthart1983/netscan/stargazers)

## Low-latency work

- **[nanofix](https://github.com/matthart1983/nanofix)**: a zero-allocation FIX engine, benchmarked on Apple Silicon at 29× faster serialisation than QuickFIX/J ([methodology](https://github.com/matthart1983/nanofix/blob/main/BENCHMARKS.md)).
- **[ticktape](https://github.com/matthart1983/ticktape)**: a framework for deterministic, replicated services on the sequencer architecture, with simulation testing built in. *Paused.*

## Also

[soundwatch](https://github.com/matthart1983/soundwatch): audio diagnostics for macOS and Linux ·
[agentwatch](https://github.com/matthart1983/agentwatch): run and watch AI agent workflows *(paused)* ·
[logwatch](https://github.com/matthart1983/logwatch): log templating and novel-pattern detection *(paused)*

`Rust` · `ratatui` · `tokio` · `eBPF` · `FIX` · `Aeron`

<sub>Paused: no commits in the last 90 days.</sub>
