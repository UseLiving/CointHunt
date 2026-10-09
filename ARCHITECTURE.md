# Architecture

Everything is in `index.html` (HTML + CSS + one `<script>`). Sections in the script, in order:

1. **Core**: `W` (saved state), `save()`, `spend(n)` / `earn(n)` (coin ledger), daily bonus, `ui()`, `openGame(id, mode)` / `finish(score, coins, note)` / `closeStage()`.
2. **Sound engine**: tiny WebAudio synth. `sfx(name, arg)`, `SND` (effects), `loopStart/Set/Stop` (e.g. rocket hum). Audio is created lazily on the first user gesture.
3. **Leaderboard**: weekly points (`pts`, `total`, caps in `CAPS`), week ids (Monday 00:00 UTC), name rules, shared board via the platform db (`lb/<userId>`), countdown.
4. **Wallet**: read-only connect. `walletProviders()` merges classic injected wallets (Phantom, Solflare, Backpack) with **Wallet Standard** wallets (`initStd`, `regStd`, `STD`). `connectWallet(id)`, `useAddress(addr)` (paste-your-address fallback, never stored), `restoreWallet()` (silent reconnect, stores the wallet name only). On phones with no injected wallet the menu offers official "open this page in the wallet app" links (`appLinks`). Never calls sign/send.
5. **Shared art helpers**: `lg`, `rg` (gradients), `eyeC` (canvas eye), `abBar` (ability buttons), `ICO` (icons).
6. **Games**: each registered as `GM.<id>`.
7. **Background**: `BG` treasure-hunt canvas (`#bg`).
8. **Contributions and skins**: `SKINS`, `SKINP()`, `applySkin()`, and `PAY` (`verify`, `claim`, `refreshBal`, `equip`). `verify` calls `getTransaction` (jsonParsed, confirmed) and requires a System Program transfer from the **connected wallet** to the prize wallet, no failure, under 30 days old, not already redeemed. Highest tier whose SOL amount is covered wins. Rewards: `earn(coins)`, skin added to `W.skins`, signature stored in `W.red`.
9. **Start-up** and `window.__co` (test hooks).

## Game object shape
`{id, name, cost, bg, gc, desc, hint, svg, fmtBest(v), start(root), stop()}` plus `this.t` (hooks the tests use) set inside `start`. Games call `finish(score, coins, note)` exactly once. Use `recordBest` for personal bests. Abilities use `abBar([...])` and must work by button and key.

## Ids and classes the tests rely on
`#grid .gt`, `#stage`, `#stBody`, `#res`, `#sndb`, `#wbtn`, `#wmenu`, `#coiny`, `#bg`, `#board`, `#lbb`, `#pot`, `#tiers`, `#potSig`, `#potClaim`, `#potMsg`, `#skinsRow`, `.ab[data-ab=...]`, `.cell`, `.tile`, `.card`, `.big-coin`.

## Saved data (localStorage)
`coinop` (state; the old name is kept so players keep progress), `coinop_wal` (wallet name only, never the address), and inside the main state: `skins`, `skin`, `red` (redeemed signatures).

## Leaderboard data
Collection `lb`, one doc per user `{n, wk, wb, ab, pwk, pp, t}`. Values are clamped to `CAPS` on read. The browser is not trusted (see TASKS T1/T2).

## Conventions
No dependencies. No network calls except Google Fonts. Respect `prefers-reduced-motion`. Colours via CSS variables.
