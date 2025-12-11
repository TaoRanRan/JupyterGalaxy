# LLM Automated Feature Engineering

This project uses a local LLM (Ollama) to automate feature engineering, aiming to boost model performance (AUC) on a classification problem.

## 🛠 Features  
- **LLM Code Generation** : An LLM suggests new numeric features based on data statistics.
- **AST Validation** Code is validated for safety (only allowed arithmetic operations) before execution.
- **ML Pipeline** Integrated with a Scikit-learn pipeline.
- **Feature Selection** Features are kept only if they increase the CV AUC.

## ⚙️ How It Works (Simplified)
- Calculate Baseline AUC.
- LLM generates code for new features.
- Features are created, validated, and tested for AUC improvement in rounds.
- Improving features are kept, and the process repeats.

## 📖 Read the Full Story on Medium
[**ML Feature Engineering, Automated: The LLM Pipeline That Iterates for You**](https://medium.com/ai-advances/ml-feature-engineering-automated-the-llm-pipeline-that-iterates-for-you-064baf97fd8a)  

