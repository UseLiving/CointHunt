# Hosting CoinHunt so payments can be verified

The private preview host blocks outside network connections, so the "Verify and claim" step cannot read the Solana blockchain there. Host `index.html` on any normal web host and it works. It is a single static file.

## Quickest options (pick one)
- **Netlify Drop:** go to app.netlify.com/drop and drag `index.html` onto the page. You get a link in about a minute.
- **GitHub Pages:** put the repo on GitHub, then Settings, Pages, deploy from the main branch.
- **Cloudflare Pages / Vercel:** import the repo, no build command, output folder is the repo root.

## Before you announce
1. **Dedicated prize wallet.** Edit `ADDR` in the `PAY` module of `index.html` and use an address that is only for this. The page shows its public balance.
2. **Private RPC (optional but recommended).** The public Solana node rate-limits. Get a free RPC URL from a provider and add this line before the main script: `<script>window.COINHUNT_RPC='https://your-rpc-url'</script>`. Use a key restricted to your domain.
3. **Devnet test.** Run locally (`python3 -m http.server`) and open `http://localhost:8000/?devnet=1`. The badge says DEVNET TEST. Get devnet SOL from the Solana faucet, send 0.05 devnet SOL to your prize wallet's address from a wallet set to devnet, copy the signature, connect that wallet on the page, paste the signature and press Verify. `?devnet=1` is ignored on any real domain.
4. **One small mainnet test:** send 0.05 SOL, claim, confirm the Gold Hunter skin and 500 coins appear.
5. **Legal.** Get advice for your region (TASKS.md T4). Keep the disclosure on the contribution panel and the rules page.

## What the player does
Press Send on a tier, send from their own wallet (on a phone, "Open my wallet app" opens it; on desktop use the copy buttons), copy the transaction signature from the wallet's activity list, connect the same wallet on the page, paste the signature and press Verify and claim.
