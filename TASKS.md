# Open tasks

Claim a task by writing your name and branch next to it.

| ID | Task | Owner | Acceptance criteria |
|---|---|---|---|
| T1 | Server-side score verification | open | Scores are validated on a server (replay or signed run logs), not trusted from the browser. Forged scores are rejected. Documented threat model. |
| T2 | Real leaderboard backend | open | Accounts or signed identities, rate limits, tamper-evident storage. Public visitors can post (today only signed-in platform users can). |
| T3 | Escrow program for a paid pot | open, **blocked on T4** | Follow `docs/ESCROW_BRIEF.md`. Devnet only until audited. No keys in the client. |
| T4 | Legal review | open | Written opinion per target jurisdiction on contests, lotteries and gambling, age gating, tax, terms. Linked in the repo before T3 ships. |
| T5 | Payout transparency page | open | After each week, publish the winner and the payment transaction signature. Read from chain, not typed by hand. |
| T6 | CI | open | GitHub Actions runs all suites on every PR (`.github/workflows/tests.yml` is a starting point). |
| T7 | Real-device testing | open | Audio, wallet extensions (Phantom/Solflare/Backpack), iOS Safari, low-end Android. Report findings as issues. |
| T8 | Accessibility audit | open | Screen reader pass on every game and the leaderboard. Fix findings. |
| T9 | Anti-abuse heuristics | open | Flag impossible score rates, automation patterns and duplicate names for manual review. |
| T10 | New games or abilities | open | Each game follows the object shape in `docs/ARCHITECTURE.md`, has a character, abilities, sounds and a test suite. |
| T11 | Server-side redemption ledger | open | A claimed signature is recorded server-side so it cannot be re-claimed on another device. |
| T12 | Contribution indexer | open | Show total contributed and recent supporters from the chain (not from client claims). Needs a small backend or an indexer. |
| T13 | Dedicated prize wallet + multisig | open | Move the prize wallet to a dedicated address controlled by a multisig; update `ADDR` and the docs. |
| T14 | Self-hosting guide | open | Step-by-step guide for hosting `index.html`, setting a private RPC, and the devnet then mainnet test checklist. |
