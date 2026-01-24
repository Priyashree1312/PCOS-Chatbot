import requests
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# -----------------------------
# Step 0: Data folder
# -----------------------------
data_folder = Path("data")
data_folder.mkdir(exist_ok=True)
urls_file = data_folder / "urls.txt"

# -----------------------------
# Step 1: Download PDFs from urls.txt if missing
# -----------------------------
if urls_file.exists():
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for url in urls:
        try:
            filename = data_folder / url.split("/")[-1]

            if filename.exists():
                print(f"[ℹ️] Already exists: {filename}")
                continue

            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=20
            )
            response.raise_for_status()

            with open(filename, "wb") as file:
                file.write(response.content)

            print(f"[✅] Downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"[❌] Failed to download {url}: {e}")
else:
    print(f"[⚠️] urls.txt not found. Skipping download step.")

# -----------------------------
# Step 2: Load all PDFs in data folder
# -----------------------------
pdf_files = list(data_folder.glob("*.pdf"))

if not pdf_files:
    print("[⚠️] No PDFs found in data folder!")
    exit()
else:
    print("[ℹ️] PDFs ready for processing:")
    for pdf in pdf_files:
        print(f" - {pdf.name}")

# -----------------------------
# Step 3: Load PDF content
# -----------------------------
documents = []
for pdf_path in pdf_files:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    documents.extend(docs)

print(f"[✅] Loaded {len(documents)} documents for RAG pipeline")

# -----------------------------
# Step 4: Split documents into chunks
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

docs_split = text_splitter.split_documents(documents)
print(f"[✅] Split into {len(docs_split)} chunks")

# -----------------------------
# Step 5: Create embeddings (FREE, LOCAL)
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("[ℹ️] Creating embeddings (HuggingFace, no API key needed)...")

# -----------------------------
# Step 6: Create Chroma vector store
# -----------------------------
vectordb = Chroma.from_documents(
    docs_split,
    embedding=embeddings,
    persist_directory="chroma_db"
)

vectordb.persist()
print("[✅] Vector store created and saved to 'chroma_db'")
