# Contributing (people and agents)

## Hard rules
1. **The page never signs or sends.** Do not add code that signs, sends or requests transactions, and never add private keys or seed phrases anywhere. Players pay from their own wallet app. The only blockchain access allowed is **read-only verification** (`getTransaction`, `getBalance`), and the UI may only show a payment as received after it was read from confirmed on-chain data. Never fake a confirmation.
2. **Keep entry to the weekly prize free**, and keep contributions giving cosmetics and play coins only (no gameplay or prize advantage), unless legal sign-off exists in writing and is linked in the PR.
3. **Honesty over polish.** Test modes must say TEST MODE. Never invent confirmations, balances or results.
4. **Don't weaken disclaimers** that protect players (coins are play money, rules page, never ask for a recovery phrase).

## Working together
- Claim a task by adding your name and branch to `TASKS.md` in your first commit. One owner per task.
- Small PRs. One concern per PR. Explain what changed and how you tested it.
- Do not break test hooks: `window.__co`, `GM.<id>.t`, and the ids/classes listed in `docs/ARCHITECTURE.md`. If you must change one, update the suites in the same PR.
- Run **all** suites in `tests/` before asking for review. Add tests for new behaviour. A change without tests is not done.
- Match the existing style: plain ES5-style JS in one file, no dependencies, CSS variables for theme colours.
- Accessibility is required: keyboard access, labels, contrast (suite t10 audits text contrast), reduced-motion support.

## Definition of done
Tests pass, no console errors, works at 390px and 1280px wide, sound can be muted, and the change is described in the PR.
