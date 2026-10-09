# CoinHunt

Crypto-themed browser games with a weekly leaderboard prize. One self-contained `index.html`, no build step.

**Live (private preview):** https://claude.ai/artifact/6kJRZZdnE4Giy6biJhNBdB

## What's in it
- 8 games, each with a character and abilities: Candle Catcher, Rug Sweeper, Block Merge, Moon Crash, HODL Clicker, Wallet Match, Chain Snake, Bull or Bear.
- Coins are **play money only**: no cash value, cannot be bought or withdrawn.
- Weekly leaderboard (6 skill games, up to 600 points) with a **50 SOL prize funded by the team, free to enter**.
- Read-only Solana wallet connect: Phantom, Solflare, Backpack and any Wallet Standard wallet. On phones it can open the page inside the wallet app, and anyone can paste an address instead. It only shows the public address and never signs or sends.
- Interactive "treasure hunt" background, sound engine, black theme.
- **Prize pot contributions.** Players send SOL from their own wallet to the prize wallet and receive a skin (Gold 0.05, Emerald 0.25, Obsidian 1 SOL) plus bonus coins. The page only *reads* the Solana blockchain to verify the payment, then unlocks the reward locally. It never signs or sends. Contributions are voluntary, non-refundable, and give no advantage in the free-entry prize.

## What is deliberately NOT built
- **Paid entry to win the prize.** The prize stays free to enter. Taking money for a chance to win needs the items in `docs/ESCROW_BRIEF.md`: an audited on-chain escrow, server-verified results and legal sign-off.
- **Anything that signs or sends from the page.** Players pay from their own wallet app. See `CONTRIBUTING.md`, rule 1.

## Going live with contributions (read this)
Verification reads the blockchain with `fetch`, so it only works where outside connections are allowed. The private preview host blocks them, so there the panel shows the address and a clear "cannot reach the network" message. **Host `index.html` on your own domain** for claims to work.

(Step by step: `docs/HOSTING.md`.)

1. Use a **dedicated prize wallet**, not a personal one (the page shows its public balance). Edit `ADDR` in the `PAY` module.
2. Set `window.COINHUNT_RPC` to your own RPC URL if you expect traffic (the public node rate-limits).
3. **Test on devnet first:** serve locally (`python3 -m http.server`) and open `http://localhost:8000/?devnet=1`. Send devnet SOL (from the Solana faucet) to the prize wallet's devnet address and claim. `?devnet=1` is ignored on any real domain, so nobody can claim rewards with free test SOL.
4. Then do one small mainnet test (0.05 SOL) before announcing.
5. Get legal advice for your region (see `TASKS.md` T4). Keep the on-page disclosure intact.

Limits to know: rewards are stored on the player's device, and a claimed signature is only blocked on that device (see `TASKS.md` T11).

## Put it online (GitHub Pages)
After pushing, open the repo on GitHub: **Settings, Pages, Source: GitHub Actions**. The included workflow (`.github/workflows/pages.yml`) publishes `index.html` at `https://<your-username>.github.io/<repo>/`. That is a normal web address, so wallet connect and payment verification can work there. See `docs/HOSTING.md` for the devnet test and the checklist before announcing.

## Run it
Open `index.html` in a browser. (Fonts load from Google Fonts; it falls back to system fonts offline.)

## Test it
```
pip install playwright pillow
python3 -m playwright install chromium
cd tests
python3 t1.py     # ... through t12.py
```
See `docs/TEST_SUITES.md`. All suites must pass before any change is merged.

## Docs
- `docs/ARCHITECTURE.md` how the single file is organised, game object shape, hooks
- `docs/ESCROW_BRIEF.md` what a safe paid pot needs (a brief for a Solana developer, not an implementation)
- `TASKS.md` open work, with acceptance criteria
- `CONTRIBUTING.md` rules for people and agents working here
