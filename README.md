# Manglish LLM Dataset 🚀

An incredibly dense, elite-tier **Malayalam and Manglish Conversational Dataset** specifically built and perfected for fine-tuning Large Language Models (LLMs) like **LLaMA 3**.

*Brought to you by [mhdashikofficial](https://github.com/mhdashikofficial)*.

---

## 📌 Overview

This dataset was rigorously extracted and heavily filtered over **9 complete data processing pipelines** to build the absolute cleanest Malayalam/Manglish set available. Starting from large translation models and raw Alpaca parameters, we transformed the content into an exclusively human-like, flowing conversational matrix.

It contains precisely **20,000 ultra-high-quality dialogue points**, meticulously balanced for superior conversational performance.

### Features
✔️ **Optimized Balance**: Strictly enforced **50/20/30 distribution** (Conversational / Instruction / Dictionary) to ensure natural speech without losing task accuracy.
✔️ **Synthetic Dictionary Anchor**: Includes ~6,000 synthetically generated dictionary-style mappings to ground the model in pure phonetics and translation logic.
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

The master file you need is: **`final_manglish_llama3_dataset.json`** (~42MB)

---

## 🧬 Repository Layout

- `final_balanced_dataset.json` : The finalized, balanced elite-quality training dataset (20,000 samples).
- `final_manglish_llama3_dataset.json` : The prior merged dataset version.
- `dictionary_training_data_enriched.json` : The expanded synthetic dictionary component.
- `extract_and_clean_tasks.py` : Script used to pull high-quality instructions from raw sources.
- `merge_and_balance.py` : The master script enforcing the final 50/20/30 ratio.
- `final_clean_dataset.py` : The final cleaning pass that purged leftover phonetic artifacts.
- `generate_dataset.py` : Base initial layout extractor grabbing sets recursively.

---

## 📄 License & Credits
- **Dataset Author & Curator**: [mhdashikofficial](https://github.com/mhdashikofficial).
- Built heavily utilizing refined parsing of the `VishnuPJ/Alpaca_Instruct_Malayalam` and related public multi-lingual translation sets.
