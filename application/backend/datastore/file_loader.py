from llama_index import SimpleDirectoryReader


reader = SimpleDirectoryReader(
    input_dir=r"C:\Users\4bluemelhuber\OneDrive - TUM\Dokumente - MGTChatbot",
    recursive=True,
)

all_docs = []
for docs in reader.iter_data():
    print(docs)
    for doc in docs:
        # do something with the doc
        doc.text = doc.text.upper()
        all_docs.append(doc)
