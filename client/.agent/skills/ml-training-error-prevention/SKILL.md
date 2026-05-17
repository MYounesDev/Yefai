---
name: ml-training-error-prevention
description: Prevent silent failures in machine learning and deep learning training before long or expensive runs. Use when Codex needs to plan, review, debug, or harden ML/DL training pipelines, PyTorch/TensorFlow training loops, data loaders, preprocessing, tensor shapes, dtypes, loss functions, gradients, single-batch overfit tests, reproducibility settings, sanity checks, smoke tests, or pre-flight checklists for GPU/TPU/cloud training. Also use for Turkish requests about "ML eğitimlerinde hata önleme", "eğitim öncesi sağlamlık kontrolü", "model eğitimi başlamadan test", "sessiz başarısızlık", "tek batch overfit", "gradient check", "loss kontrolü", or "test edilebilir ML mimarisi".
---

# ML Training Error Prevention

## Core Stance

Treat a long ML/DL training run as something that must earn permission to
start. Passing Python without exceptions only proves that the code can execute;
it does not prove that the model can learn, the data is valid, the labels are
aligned, gradients flow, or the loss is mathematically compatible with the
task.

Default to a pre-flight review or test plan when the user asks for training
advice. Default to code edits or tests only when the user asks to modify a
project. Prioritize fast, cheap evidence before expensive full training.

## Workflow

1. Fingerprint the training task.
   Identify task type, modality, model family, framework, data unit, label
   shape, output shape, loss function, optimizer, expected input range, class
   balance, training budget, and whether GPU/TPU determinism matters.

2. Separate structural correctness from learning behavior.
   Structural checks prove that data, tensors, modules, and the training loop
   connect correctly. Behavioral checks prove that the model can actually
   learn under controlled conditions.

3. Require data and tensor invariants before model training.
   Check nulls/NaNs/Infs, feature or image value ranges, normalization
   assumptions, label validity, label alignment, split leakage, batch shape,
   channel order, dtype, device placement, and train-only fitting of
   preprocessing steps.

4. Run a tiny integration smoke test.
   Use synthetic data or a small real subset to execute data loading, forward
   pass, loss computation, backward pass, optimizer step, metric calculation,
   checkpoint writing, and resume logic. The goal is pipeline continuity, not
   high quality.

5. Prove learning capacity with a single-batch overfit test.
   Force the model to memorize a tiny fixed batch. If loss does not collapse
   and predictions do not match labels, suspect label mismatch, frozen
   parameters, wrong loss/output pairing, bad learning rate, missing optimizer
   step, aggressive regularization, broken augmentation, or insufficient model
   capacity.

6. Inspect gradient health.
   After backward pass, review per-layer gradient norms, missing gradients,
   zero gradients, exploding gradients, vanishing gradients, frozen parameters,
   accidental `.detach()`, mixed-precision overflow, and clipping behavior.

7. Validate loss behavior before scaling.
   Compare initial loss against the theoretical baseline for the task. For
   classification, confirm logits vs probabilities match the chosen loss, and
   prefer cross-entropy-style losses over MSE unless the task truly calls for
   regression. For imbalance, decide weighting, sampling, focal/Dice/Tversky
   variants, and the metric contract explicitly.

8. Lock reproducibility and testability.
   Set seeds, deterministic options where needed, controlled config files,
   small test profiles, train/validation split persistence, and artifact
   logging. Keep data, model, loss, optimizer, metrics, and training loop
   modular enough to test independently.

9. Finish with a go/no-go verdict.
   State whether full training may start, which checks passed, which checks
   failed, what must be fixed first, and which risks remain acceptable for the
   current experiment.

## Required Checks

For a serious pre-flight review, cover these gates unless the user asks for a
smaller answer:

- Data quality: missing values, NaNs/Infs, duplicates, outliers, invalid labels,
  class imbalance, leakage, and train-only preprocessing.
- Tensor contract: shape, dtype, device, channel/order convention, batch
  dimension, output dimension, and label/output compatibility.
- Pipeline smoke test: one or two batches through forward, loss, backward,
  optimizer step, metrics, checkpoint, and resume when applicable.
- Single-batch overfit: tiny fixed batch can be memorized quickly with
  augmentation and heavy regularization disabled.
- Gradient flow: non-null gradients exist where expected; norms are neither
  all zero nor unstable; clipping and mixed precision are monitored.
- Loss sanity: initial loss matches task baseline; loss receives logits or
  probabilities as required; imbalance handling matches the target metric.
- Metrics: metrics match the task and failure cost; rare-event tasks include
  PR/AUPRC or recall-oriented checks, not accuracy alone.
- Reproducibility: seed, deterministic mode, config, split version, dataset
  version, code version, and run manifest are logged.
- Resource readiness: batch size, VRAM/RAM, first inference, dataloader speed,
  checkpoint path, and expected runtime are checked before long runs.

## Reference Loading

Read `references/pretraining-checklist.md` when the user needs a detailed
training-readiness checklist, a go/no-go report, or concrete failure symptoms
and likely causes.

## Output Rules

- State evidence separately from inference. Example: "Observed: loss stays at
  0.69 on one batch. Inference: optimizer step, label alignment, or output/loss
  pairing may be broken."
- Prefer compact tables for gates, status, evidence, and fixes.
- Do not approve a long run when the single-batch overfit, gradient, or loss
  sanity check is missing unless the user explicitly accepts the risk.
- For code changes, add or update fast tests before changing training behavior
  when existing tests do not already protect it.
- For teaching requests, explain why each check prevents wasted training time
  and what failure usually means.
