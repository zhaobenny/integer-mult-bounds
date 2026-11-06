# Reuse checked explicit paths within one selected metadata check

This is a current-format follow-up to Arham Tahir's
[PR2793](https://github.com/CrocSwap/integer-mult-bounds/pull/2793) and
[Discussion2787](https://github.com/CrocSwap/integer-mult-bounds/discussions/2787).
The path-reuse idea and stable-filesystem argument are prior work. The older
prototype supports legacy/package inventories; this patch ports it to the newer
explicit-file inventory. No duplicate contribution PR is proposed.

An isolated opt-in patch reduces the selected metadata check's median time from
0.354271 to 0.284835 seconds, a 19.60% reduction in nine alternating warm-filesystem
pairs. The full selected source closure is checked in both versions on the same
checkout. This is an in-process timing of `check`, without interpreter startup.
[RESULT.json](RESULT.json) retains every sample and the environment, CPython
3.10.12 on Linux/WSL2. Timings are author-measured and environment-specific.

The patch is a proposal for a future checker version. **The hash-pinned selected
checker, certificate, manifests and selected frontier remain unchanged.** No
supplier/native scientific replay ran and no new kappa is claimed.

## Scope and derivation

The required orientation command passed on canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
The picker proposed verifier engineering with seed
`69b2a81ef0539cf632661c3149434a09`. The replay-runtime card is explicitly
CHANGED to source-binding overhead. The complete finite scientific replay is
still `make frontier6030-verify`, which this session did not run.

Profiling the unchanged orientation attributed 0.140 seconds of a 0.639-second
profiled `check` to the final proof-membership set comprehension. It resolves all
1,405 explicit input names again, after `explicit_file` already returned each
resolved path during byte authentication. Profiling overhead makes these figures
diagnostic, separate from the unprofiled paired timings.

[proposal.patch](proposal.patch) retains those returned paths in a set within the
same invocation. On a stable filesystem, for each explicit manifest name n,
`explicit_file(root, n)` calls `path(root, n)`, which returns
`(root / n).resolve()` after containment, canonical-name, symlink and file checks.
That is exactly the element the old set comprehension constructs. The proposal
still hashes every input and compares the complete inventory before testing proof
membership. It also retains every supplement hash and publication pointer check.
The package and legacy inventory branches retain the original comprehension,
including supported contained regular-file aliases. No cross-call state is kept.

Concurrent filesystem mutation is outside this equivalence argument. Neither
version supplies an atomic snapshot or race-proof file-descriptor confinement.
The proposal removes a later redundant resolution rather than strengthening that
contract. Do not describe this as a security or theorem-proof result.

## Evidence and reproduction

```sh
python3 -B scripts/research_package.py --package research/selected-path-reuse
# Optional timing, writes a new local receipt rather than the frozen result:
python3 -B research/selected-path-reuse/verify.py --benchmark /tmp/path-reuse-times.json
```

The registered normal and optimized commands authenticate the live pinned checker
and three predecessor test files, apply the patch only inside a temporary tree,
then compile original/proposed source bytes into separate module namespaces.
No `.pyc` file supplies the proposed code. The temporary patched source is never
installed into the checkout.

A tiny explicit-format fixture also demonstrates that PR2793's older prototype
rejects with `Selected package inventory or bytes changed`, while both the live
checker and this port accept. This is expected schema evolution, not a flaw in
the historical contribution. Its old scientific/benchmark suite is not rerun.

Each version runs 23 existing synthetic tests from `test_selected_proof_binding`,
`test_selected_explicit_inventory` and `test_selected_inventory_links`. These cover
all three inventory layouts, unpinned proofs, byte mutations, path traversal,
symlink policies, cycles, missing files, arithmetic and supplement guards. The
subprocess CLI test is deliberately excluded because it would exercise the live
unmodified checker rather than the proposal. No skipped test is accepted.

Four additional controls mutate the same explicit fixture between successful
calls: changed source bytes, deleted source, replacement with a same-byte symlink,
and a newly listed bad-digest input. Each rejects in both versions, confirming
that prior success does not bypass next-call validation. Both versions also check
the complete current selected metadata and return the same exact kappa.
All selected manifest members and supplements are declared CI inputs. The main
verifier intentionally emits deterministic receipts without a speed threshold;
system noise must not become a correctness failure. Optimized testing checks
explicit guards in the API, not a change to the checker's separate CLI policy.

## Coordination and attribution

Entry overlap refresh covered 765 open PR bodies/heads, 6,890 Discussion records
and 8,917 local notes, with complete reported pagination. It does not search all
code diffs or certify novelty. Live targeted searches for the selected checker
found PR6319's hash-pin audit and PR729's older helper-frame audit; neither is
this path-reuse proposal. The subsequent complete targeted helper search found
Discussion2787 and PR2793, prompting the explicit predecessor comparison and
a stop on duplicate PR work. PR6811 optimizes overlap inventory parsing, a separate
function and fixture. The package preserves immutable sources partly because the
selected manifest explicitly pins the checker itself.

Credit Arham Tahir for the path-reuse mechanism, original timings, controls and
stable-filesystem argument. This current explicit-format port was developed
before the targeted Discussion result exposed the prior work; it claims no
independent novelty. Credit Douglas Colkitt for the selected checker, Mihir Srivastava for the
proof-binding and baseline work, Dennis for the historical supplement path, and
the retained source-inventory/link test contributors. Source bytes and hashes
are recorded in [SOURCES.json](SOURCES.json). Their existing tests are reused
with the checker module substituted, so these are source-aware regression runs,
not an independently developed verification suite or independent review.
Produced for zhaobenny with gpt-6.1-sol at high reasoning effort through Codex.
No subagents. Apache-2.0.

## Open next questions

Should the proposal be adopted at a future selected-checker version boundary?
Review the small patch and the stable-filesystem argument, then plan explicit
successor source bindings without rewriting frozen evidence. This needs a
maintainer source-version and integration decision. First measure cumulative workflow savings as the predecessor requests, before
assigning further work. A second implementation or
platform replay could test portability; neither is claimed here. All five
selected framework assumptions remain open at their recorded scope.
