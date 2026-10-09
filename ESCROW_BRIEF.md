# Brief: what a safe paid prize pot requires

This is a **requirements brief for a Solana developer and a lawyer**. It is not an implementation, and nothing in this repo moves real funds.

## Why the current page cannot do it
- A web page cannot verify a payment. Only the chain can.
- Scores come from the player's browser and can be forged.
- Players paying a personal wallet have no guarantee the pot exists or that results are fair.
- Paid entry plus a prize is a lottery or gambling in many places.

## Minimum design
1. **On-chain escrow program** (e.g. Anchor). A program-owned vault (PDA) holds entries. No personal wallet holds player funds.
2. **Entry instruction**: the player signs a transfer of the entry fee into the vault for a specific round id. The program emits an event.
3. **Round lifecycle**: open, closed (cutoff), resolved, claimable, cancelled. Time-locks so funds cannot be trapped.
4. **Results**: determined by a **server-side verified** score pipeline, then submitted by a **multisig authority**, not a single key. Publish the verification method.
5. **Payout**: a claim instruction paying the winner from the vault, or automatic refund on cancel/timeout.
6. **Front end**: reads **confirmed** transactions and vault balance from an RPC. It shows "entered" only after confirmation. It never shows a payment as sent on its own.
7. **Keys**: never in the client. Authority keys in a hardware-backed multisig.
8. **Audit** by an independent firm before mainnet. Devnet only until then.
9. **Legal**: written opinion per jurisdiction (licensing, age and location gating, KYC thresholds, tax reporting, responsible-play requirements, terms of service). Block unsupported regions.
10. **Transparency**: publish each round's vault address, entries, result, and payout signature.

## Out of scope for the front end
Holding funds, choosing winners, or confirming payments. Those belong to the program and the verified backend.
