# Code Gallery — Termux Repo

Extra coding tools for the **Termux** app, served as a signed APT repo from GitHub Pages.
Every package here is *not* in the official Termux repos — they work alongside them.

## Install (one line)

```bash
curl -sL https://atharv525.github.io/code-gallery-termux/install.sh | bash
```

This adds `$PREFIX/etc/apt/sources.list.d/codegallery.list`, the repo's GPG key, and runs `apt update`.
Then install anything with `pkg install <name>`.

<details><summary>Manual setup</summary>

```bash
curl -sL https://atharv525.github.io/code-gallery-termux/codegallery.gpg -o $PREFIX/etc/apt/trusted.gpg.d/codegallery.gpg
echo "deb https://atharv525.github.io/code-gallery-termux codegallery main" > $PREFIX/etc/apt/sources.list.d/codegallery.list
apt update
```
</details>

## All coding tools in one go

```bash
pkg install cg-devkit     # Python, Node.js, Git/gh, Clang/Make/CMake, Go, Rust, Java 17,
                          # Kotlin, PHP, Ruby, Perl, Lua, Vim/Neovim/Nano/Micro, tmux, OpenSSH...
# or pick groups:
pkg install cg-setup
cg-setup code             # everything
cg-setup python c editors # just some groups
```

## Packages

| Package | What it does |
|---|---|
| `cg-devkit` | Metapackage: installs the full official Termux coding toolkit at once (several GB) |
| `cg-setup` | Menu installer for toolkits by group: base, python, node, c, java, go, rust, php, ruby, perl, lua, editors, web, db, media, shell |
| `cg-run` | `cg-run file.ext` compiles and runs C, C++, Python, JS, TS, Go, Rust, Java, Kotlin, PHP, Ruby, Perl, Lua, Bash, Dart |
| `cg-new` | `cg-new <template> <name>` new project: html, python, flask, node, express, c, cpp, go, rust, java, php, bash |
| `cg-serve` | `cg-serve [folder] [port]` serves a folder as a website and shows the Wi-Fi address |
| `cg-push` | `cg-push "message"` git add + commit + pull --rebase + push in one command |
| `cg-backup` | `cg-backup [folder]` dated .tar.gz backup into phone storage (skips node_modules etc.) |
| `cg-info` | Phone, Android, storage, memory and installed language versions |
| `cg-clean` | Frees space by clearing apt, pip, npm, yarn, go and cargo caches |
| `cg-bugbounty` | `cg-bugbounty all` installs a bug-bounty/recon toolkit: subfinder, httpx, nuclei, naabu, ffuf, gobuster, amass, katana, dalfox, gau, waybackurls, sqlmap, nmap, dnsx and more — by group (recon, scan, fuzz, dns, web, passwords, utils, wordlists) |
| `code-gallery-keyring` | The repo's signing key (keeps it updated) |

## Uninstall

```bash
curl -sL https://atharv525.github.io/code-gallery-termux/uninstall.sh | bash
```

## Add a new package

```bash
scripts/new-package.sh cg-mytool       # copies packages/_template
# edit packages/cg-mytool/build.conf and packages/cg-mytool/files/bin/cg-mytool
git add -A && git commit -m "Add cg-mytool" && git push
```

`files/` maps onto `$PREFIX` (`files/bin/x` → `$PREFIX/bin/x`). `build.conf` sets `NAME`, `VERSION`,
`ARCH` (`all` or `"aarch64 arm i686 x86_64"`), `DEPENDS`, `DESCRIPTION`. Optional `postinst`/`prerm` scripts sit
next to it. Bump `VERSION` to ship an update — users get it with `pkg upgrade`.

GitHub Actions (`.github/workflows/build.yml`) builds every `.deb`, writes the `Packages` indexes for
aarch64, arm, i686 and x86_64, signs `Release`/`InRelease` with the repo key (passphrase in the
`GPG_PASSPHRASE` secret), and publishes to GitHub Pages.

## Signing key

`Code Gallery (Termux APT repo)` — fingerprint `6808 37CA ABEB EA3B F00B 1F2B 8F1C C818 9304 40BA`

MIT licensed · Code Gallery
