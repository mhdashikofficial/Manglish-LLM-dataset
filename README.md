# Manglish LLM Dataset 🚀

An incredibly dense, elite-tier **Malayalam and Manglish Conversational Dataset** specifically built and perfected for fine-tuning Large Language Models (LLMs) like **LLaMA 3**.

*Brought to you by [mhdashikofficial](https://github.com/mhdashikofficial)*.

---

## 📌 Overview

This dataset was rigorously extracted and heavily filtered over **9 complete data processing pipelines** to build the absolute cleanest Malayalam/Manglish set available. Starting from large translation models and raw Alpaca parameters, we transformed the content into an exclusively human-like, flowing conversational matrix.

It contains precisely **12,676 flawless dialogue points**.

### Features
✔️ **Zero Hallucinations**: Heavily guarded against numeric artifacts and random context-less text generation errors native to LLMs.
✔️ **Unsloth & HuggingFace Ready**: Formatted directly to default `messages` → `role` / `content` layouts ensuring instant out-of-the-box training setups.
✔️ **Strict Language Isolation**: Scripts never mix intrinsically. Prompts seamlessly traverse between Roman Manglish and standard Malayalam seamlessly but adhere to pure-script representations.
✔️ **Elite Normalization**: All artificial or hyper-phonetic loan words (`phamgshan`, `dibagg`, `matrrka`) have been carefully smoothed to universally used typing structures (`function`, `debug`, `mathrika`).

---

## 🛠 Usage

This dataset is engineered natively to support immediate fine-tuning workflows via Unsloth or traditional Hugging Face loaders.

Example Dataset Structure:
```json
{
  "messages": [
    {"role": "system", "content": "You are a friendly AI that speaks natural Malayalam and Manglish. Keep responses human-like, clear, and helpful."},
    {"role": "user", "content": "Nalla oru malayalam cinema suggest cheyyamo?"},
    {"role": "assistant", "content": "Theevandi kanaam, nalla comedy aanu."}
  ]
}
```

The master file you need is: **`unsloth_ready_dataset.json`** (~28MB)

---

## 🧬 Repository Layout

- `unsloth_ready_dataset.json` : The finalized elite-quality training dataset.
- `clean_dataset_*.py` : Original python pipeline scripts used to purge hallucinations, instruction leakages, and phonetic irregularities.
- `generate_dataset.py` : Base initial layout extractor grabbing sets recursively.

---

## 📄 License & Credits
- **Dataset Author & Curator**: [mhdashikofficial](https://github.com/mhdashikofficial).
- Built heavily utilizing refined parsing of the `VishnuPJ/Alpaca_Instruct_Malayalam` and related public multi-lingual translation sets.
