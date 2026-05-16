# Pretraining Checklist

Use this reference to turn an ML/DL project into a cheap pre-flight validation
sequence before starting long GPU/TPU/cloud training.

## Table Of Contents

- Task Fingerprint
- Gate 1: Data And Split Integrity
- Gate 2: Tensor And Dataloader Contract
- Gate 3: Pipeline Smoke Test
- Gate 4: Single-Batch Overfit
- Gate 5: Gradient Health
- Gate 6: Loss And Metric Sanity
- Gate 7: Testable Architecture
- Gate 8: Reproducibility And Resources
- Go/No-Go Report Template
- Failure Symptoms

## Task Fingerprint

Capture these facts first:

| Field | What To Record |
| --- | --- |
| Task | binary, multiclass, multilabel, regression, segmentation, detection, sequence, contrastive, generative |
| Unit | sample, patient, visit, image, slice, volume, window, token sequence, batch |
| Model output | logits, probabilities, masks, boxes, embeddings, scalar values |
| Labels | dtype, shape, valid range, class encoding, missing-label policy |
| Loss | exact class/function, expected input format, reduction, class weights |
| Metrics | train/val/test metrics and operating threshold policy |
| Data transforms | normalization, augmentation, resizing, tokenization, imputation, encoding |
| Splits | split unit, leakage boundaries, fold IDs, external/temporal/site holdout |
| Budget | expected runtime, memory, accelerator, batch size, checkpoint cadence |

## Gate 1: Data And Split Integrity

Verify:

- No unexpected null, NaN, Inf, empty image, corrupt file, invalid token, or
  missing label reaches the training loader.
- Labels use the expected encoding. For classification, class IDs must align
  with loss expectations and model output columns.
- Class prevalence is known. For rare events, accuracy must not be the main
  proof of usefulness.
- Duplicate or near-duplicate samples do not cross train/validation/test
  boundaries.
- Patient-, subject-, site-, time-, or group-level leakage is impossible under
  the split policy.
- Scalers, imputers, encoders, feature selectors, calibration models, and
  augmentation statistics are fitted on train folds only.
- Value ranges match model assumptions. Examples: images normalized to the
  expected range, tabular features scaled as expected, masks remain discrete.

Evidence to collect:

- Dataset counts by split and class
- Missingness/NaN/Inf summary
- Label distribution and invalid-label count
- Split leakage audit notes
- A few visual or textual samples after preprocessing

## Gate 2: Tensor And Dataloader Contract

Verify one batch from each split:

- Inputs have the expected shape. Examples: `NCHW` vs `NHWC`, sequence length,
  segmentation mask dimensions, tabular feature count.
- Labels have the expected shape and dtype. For PyTorch `CrossEntropyLoss`,
  labels are usually integer class IDs and model outputs are raw logits.
- Tensors are on the expected device when the model runs.
- Batch dimension is stable, including the final partial batch when applicable.
- Augmentations preserve label alignment, laterality, mask geometry, token
  order, and physical units.
- Dataloader shuffling is enabled only where intended.

Evidence to collect:

- Printed or asserted input, target, output, and loss shapes
- Min/max/mean/std for numeric tensors after transforms
- One transformed sample inspection

## Gate 3: Pipeline Smoke Test

Run a tiny end-to-end path with synthetic data or a tiny real subset:

1. Build model from the same config system used for real training.
2. Load one or two batches.
3. Run forward pass.
4. Compute loss.
5. Run backward pass.
6. Run optimizer step and zero gradients.
7. Compute metrics.
8. Write a checkpoint.
9. Resume from checkpoint if the project supports resume.

Pass criteria:

- No crash.
- Loss is finite.
- Model parameters change after optimizer step.
- Metrics code accepts the model output format.
- Checkpoint paths and permissions work.

This gate proves wiring. It does not prove learning quality.

## Gate 4: Single-Batch Overfit

Force the model to memorize a tiny fixed batch, commonly 4 to 32 examples.

Setup:

- Disable stochastic augmentation unless the purpose is to test augmentation.
- Disable or reduce dropout, weight decay, label smoothing, mixup, cutmix, and
  other regularizers that fight memorization.
- Use a learning rate suitable for a short debug run.
- Reuse exactly the same batch each step.
- Track loss and predictions.

Pass criteria:

- Loss collapses strongly compared with the initial value.
- Predictions become correct on the fixed batch for classification-like tasks.
- For regression or segmentation, training error becomes very small on the
  fixed batch.

If it fails, inspect:

- Labels paired with the wrong inputs
- Output activation/loss mismatch
- Frozen parameters or missing optimizer parameters
- Missing `optimizer.step()`, wrong `zero_grad()` placement, or accidental
  `no_grad`
- Detached tensors or broken computation graph
- Learning rate too high or too low
- Augmentation corrupting labels
- Model capacity too small

## Gate 5: Gradient Health

After backward pass, inspect per-parameter or per-layer gradients.

Required checks:

- Trainable parameters have gradients unless intentionally frozen.
- Gradients are finite.
- Gradient norms are not all zero.
- Gradient norms are not exploding to extreme values.
- Early layers in deep networks receive meaningful signal.
- Mixed precision reports no repeated overflow/skip behavior.
- Gradient clipping is logged when enabled.

Common thresholds are project-dependent. Prefer relative inspection: compare
layers, steps, and runs rather than relying on one universal magic number.

## Gate 6: Loss And Metric Sanity

Validate task/loss pairing:

| Task | Common Loss Pattern | Common Pitfall |
| --- | --- | --- |
| Multiclass classification | Cross entropy on logits | Passing softmax probabilities into a loss that expects logits |
| Binary classification | BCE-with-logits or equivalent | Applying sigmoid twice or using wrong target shape |
| Multilabel classification | BCE-style independent labels | Treating multilabel as mutually exclusive multiclass |
| Regression | MSE, MAE, Huber | Using classification metrics or wrong target scale |
| Segmentation | CE, Dice, BCE, Tversky variants | Mask dtype/shape mismatch or interpolating masks incorrectly |
| Imbalanced classification | class weights, sampling, focal-style loss | Optimizing accuracy while rare class recall is the objective |

Initial loss sanity:

- For balanced `K`-class classification with untrained logits, initial
  cross-entropy should often be near `log(K)`.
- For binary classification with untrained logits, initial BCE is often near
  `log(2)`.
- Large deviations can be valid, but require explanation: label imbalance,
  initialization bias, class weights, reduction, masking, or scale issues.

Metric sanity:

- Use AUROC only when ranking quality is meaningful and prevalence does not
  hide rare-event failure.
- Use AUPRC/recall/precision/F-score or threshold curves for rare events.
- For segmentation, combine overlap metrics with boundary or visual checks.
- For calibrated decisions, inspect calibration and threshold behavior, not
  only discrimination.

## Gate 7: Testable Architecture

Prefer project structure that makes checks cheap:

- Data preparation can run without constructing the model.
- Model construction is independent from the training script.
- Loss, optimizer, scheduler, metrics, checkpointing, and logging are separate
  enough to test.
- Config files define hyperparameters instead of hard-coded script constants.
- A small test profile can create a tiny model and tiny dataset quickly.
- Training loop accepts injected dataloaders, model, optimizer, and config.

Avoid monolithic notebooks or scripts where the only test is a full run.

## Gate 8: Reproducibility And Resources

Before full training, record:

- Code version or commit
- Dataset version and split version
- Config file
- Seed and derived seeds
- Deterministic flags and known nondeterministic operations
- Framework, CUDA/cuDNN, driver, and hardware versions when relevant
- Batch size, precision mode, gradient accumulation, and device count
- Expected runtime, checkpoint cadence, and resume path

Resource smoke checks:

- First forward/backward pass fits memory.
- Dataloader throughput is not the bottleneck.
- Checkpoint write path has enough space and permissions.
- Logging destination works before the long run starts.

## Go/No-Go Report Template

Use this compact report format:

| Gate | Status | Evidence | Required Fix |
| --- | --- | --- | --- |
| Data/split integrity | pass/fail/unknown | counts, summaries, leak audit | fix or "none" |
| Tensor contract | pass/fail/unknown | shapes, dtypes, ranges | fix or "none" |
| Smoke test | pass/fail/unknown | finite loss, params changed | fix or "none" |
| Single-batch overfit | pass/fail/unknown | loss curve, predictions | fix or "none" |
| Gradient health | pass/fail/unknown | grad norms, missing grads | fix or "none" |
| Loss/metrics | pass/fail/unknown | baseline loss, metric fit | fix or "none" |
| Repro/resources | pass/fail/unknown | seed, config, memory | fix or "none" |

Verdict:

- `GO`: all critical gates pass and remaining risks are acceptable.
- `NO-GO`: any critical gate fails.
- `LIMITED-GO`: full run is allowed only for a cheap exploratory run, with
  risks stated clearly.

## Failure Symptoms

| Symptom | Likely Causes | First Checks |
| --- | --- | --- |
| Loss becomes NaN | bad data, exploding gradients, too high LR, mixed precision overflow, invalid loss input | NaN/Inf scan, grad norms, LR, loss inputs |
| Loss flatlines | frozen params, no optimizer step, detached graph, LR too low, wrong labels | param change check, grads, one-batch overfit |
| Single-batch overfit fails | label mismatch, output/loss mismatch, broken loop, too much regularization | fixed batch, disable aug/reg, inspect predictions |
| Accuracy high but model useless | imbalance, leakage, wrong metric, threshold issue | prevalence, AUPRC/recall, leakage audit |
| Validation much better than expected | leakage, duplicate samples, preprocessing fitted on all data | split audit, group IDs, train-only fitting |
| Training crashes after hours | untested rare batch, corrupt file, final batch shape, checkpoint path | iterate full dataloader once, test final batch |
| Metrics disagree with loss | wrong activation, threshold, label encoding, metric input format | metric unit tests, output examples |
| GPU OOM | batch too large, activation memory, dataloader pinning, checkpointing absent | memory smoke test, smaller batch/profile |
