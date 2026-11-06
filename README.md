# Matt Hartley

I build Rust tools for investigating networks, hosts, disks and the Linux kernel.
My focus is making system behaviour easier to inspect from the terminal.

Sydney, Australia · [NetWatch Labs](https://netwatchlabs.com) · [LinkedIn](https://www.linkedin.com/in/matt-hartley-b5b28b40/)

## Start with netwatch

[**netwatch**](https://github.com/matthart1983/netwatch) brings network traffic, connections and process activity into one terminal.

<p align="center">
  <a href="https://raw.githubusercontent.com/matthart1983/matthart1983/main/assets/netwatch.gif">
    <img src="assets/netwatch.gif" width="800" alt="Netwatch demo showing download and upload throughput, interface rates, hop latency and connections grouped by process.">
  </a>
</p>

<p align="center"><em>Demo traffic in the dense view: throughput above, interfaces and hop latency in the middle, connections below. Click to view at full size.</em></p>

<p align="center"><b><a href="https://github.com/matthart1983/netwatch#install">Install netwatch</a></b> · <a href="https://github.com/matthart1983/netwatch#run">Run and explore</a></p>

[Terminal Trove's Tool of the Week](https://terminaltrove.com/tool-of-the-week/) · 14 April 2026.

## Choose a diagnostics tool

Start with the part of the system you need to investigate. Netwatch, syswatch and diskwatch share a terminal layout and palette, making it familiar to move between them.

| Tool | What to use it for |
|---|---|
| [**netwatch**](https://github.com/matthart1983/netwatch) | Inspect traffic, connections and network behaviour. |
| [**syswatch**](https://github.com/matthart1983/syswatch) | Investigate resource use and revisit recent system activity. |
| [**diskwatch**](https://github.com/matthart1983/diskwatch) | Inspect disk activity, capacity, health and busy files. |
| [**kernwatch**](https://github.com/matthart1983/kernwatch) | Investigate Linux scheduling, memory pressure and block I/O. |

Each project's documentation explains its platform support, permissions and measurement limits.

## Engineering notes

- [**Process attribution: identity, freshness and coverage**](https://github.com/matthart1983/netwatch/blob/main/docs/attribution.md) — how netwatch checks ownership evidence, handles stale observations and reports what remains unknown.
- [**Designing netwatch's terminal views**](https://github.com/matthart1983/netwatch/blob/main/docs/DESIGN-0.30.md) — the version 0.30 design document covering layout, visual hierarchy and dense and lite views.

## Other selected work

- [**essh**](https://github.com/matthart1983/essh) — remote shells that survive connection drops, built on OpenSSH and tmux.
- [**nanofix**](https://github.com/matthart1983/nanofix) — a Rust FIX engine. NewOrderSingle serialisation benchmarked at 28.7× faster than QuickFIX/J on Apple Silicon; [results and methodology](https://github.com/matthart1983/nanofix/blob/main/BENCHMARKS.md).

[Browse all projects](https://github.com/matthart1983?tab=repositories).

## Get in touch

For netwatch questions and ideas, use [Discussions](https://github.com/matthart1983/netwatch/discussions).
For professional conversations, connect on [LinkedIn](https://www.linkedin.com/in/matt-hartley-b5b28b40/).

