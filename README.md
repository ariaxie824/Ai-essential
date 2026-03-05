# 1. Prepare your tools

Feel free to skip these steps if you have already installed the tools.

## 1.1 Install Visual Studio Code (VSCode)

1. Go to the [VSCode download page](https://code.visualstudio.com/download).
2. Download and follow the installation instructions for your platform.

## 1.2 Download and Open This Repository

1. Download this repository as a ZIP file and extract it.
2. In VSCode, go to **File > Open Folder** and select the extracted folder.

## 1.3 Install Miniconda

1. Go to the [Miniconda download page](https://www.anaconda.com/docs/getting-started/miniconda/install).
2. Follow the installer instructions.
3. Verify by typing `conda --version` in your terminal.

---

# 2. Install Environment 

You will create a new conda environment named `chatbot` and install the necessary libraries using the requirements file.

```bash
# Create a new conda environment
conda create -n chatbot python=3.11 -y

# Activate the environment
conda activate chatbot

# Install all dependencies at once
pip install -r requirements.txt


# 3. Choose your engine 

This project supports two engines. You can switch between them instantly in the app's sidebar.

## 3.1 Option A: Hybrid Mode (Gemini 2.5 + Local Embeddings)

This mode uses a cloud-based "brain" for high-performance reasoning but processes your PDFs locally to avoid API limits.

1. **Get API Key**: Obtain your key from [Google AI Studio](https://aistudio.google.com/apikey).
2. **Configure Key**: The key is already pre-set in `app_final.py`, or you can replace the `GOOGLE_API_KEY` variable with your own.
3. **Local Embedding**: The app will automatically download `BAAI/bge-small-en-v1.5` to your CPU for free, unlimited indexing.

## 3.2 Option B: Privacy Mode (Ollama 100% Local)

This mode runs entirely on your machine for maximum data privacy.

1. **Install Ollama**: Download from [ollama.com/download](https://ollama.com/download).
2. **Pull Models**: Open your terminal and run:
```bash
ollama pull mistral

```


3. **Verify**: Ensure Ollama is running in the background before launching the app.

---

# 4. Run the Integrated Chatbot

You no longer need to run separate files for different models. Everything is integrated into the final application.

## 4.1 Launch the App

In the VSCode terminal, run the following command:

```bash
streamlit run app_final.py

```

## 4.2 Using the Interface

* **Upload**: Drag and drop your financial PDFs (e.g., Amazon 10K).
* **Toggle Engine**: Use the **sidebar** to switch between **Gemini 2.5 Flash** and **Ollama (Mistral)**.
* **Historical Context**: The chatbot automatically tracks your conversation history for better multi-turn analysis.
* **Source Context**: Click the **"View Reference Context"** expander under any response to see the exact PDF chunks used.

---

# 5. Project Structure

* `app_final.py`: The main integrated application supporting both Hybrid and Local modes.
* `chat_with_pdf_gemini_with_history.py`: (Legacy) Original Gemini-only version.
* `chat_with_pdf_ollama_with_history.py`: (Legacy) Original Ollama-only version.