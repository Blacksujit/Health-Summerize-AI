# # Step 1: Install packages with exact versions (skip pip check)
# !pip install --upgrade --force-reinstall numpy==1.26.2 --quiet
# !pip install gradio==4.24.0 --quiet
# !pip install langchain-community==0.0.34 transformers==4.41.2 sentence-transformers==2.7.0 --quiet
# !pip install bitsandbytes==0.43.1 accelerate==0.29.3 faiss-cpu==1.8.0 --quiet

# # Step 2: Import libraries
# import sys
# from langchain_community.llms import HuggingFacePipeline
# from langchain.prompts import ChatPromptTemplate
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from google.colab import files
# import gradio as gr
# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
# import numpy as np

# # Step 1: Install required packages
# !pip install -U transformers accelerate gradio sentence-transformers huggingface-hub

# # Step 2: Authenticate with Hugging Face
# from huggingface_hub import notebook_login
# notebook_login()  # Follow the prompt to enter your Hugging Face token

# # Step 3: Load Mistral with authentication
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# model_name = "mistralai/Mistral-7B-Instruct-v0.1"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     device_map="auto",
#     load_in_4bit=True  # Reduces memory usage
# )

# mistral_pipe = pipeline(
#     "text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     max_new_tokens=200
# )

# # Step 4: Knowledge Base Setup
# print("Please upload your medical knowledge text file:")
# uploaded = files.upload()
# kb_filename = next(iter(uploaded))

# from langchain_community.document_loaders import TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# loader = TextLoader(kb_filename)
# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=100
# )
# split_docs = text_splitter.split_documents(docs)

# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"}
# )
# vectorstore = FAISS.from_documents(split_docs, embeddings)

# # Step 5: Create LangChain QA System
# prompt_template = """[INST] You are a medical assistant. Use this context:
# {context}

# Question: {question}
# Provide a concise answer and recommend consulting a doctor. [/INST]"""

# prompt = ChatPromptTemplate.from_template(prompt_template)

# qa_chain = RetrievalQA.from_chain_type(
#     llm=HuggingFacePipeline(pipeline=mistral_pipe),
#     chain_type="stuff",
#     retriever=vectorstore.as_retriever(),
#     chain_type_kwargs={"prompt": prompt}
# )

# # Step 6: Gradio Interface
# def respond(message, history):
#     # Emergency detection
#     emergencies = ["chest pain", "can't breathe", "unconscious", "severe bleeding"]
#     if any(term in message.lower() for term in emergencies):
#         return "🆘 EMERGENCY: Call local emergency services immediately!"

#     try:
#         response = qa_chain.invoke({"query": message})["result"]
#         return f"{response}\n\n⚠️ Always consult a qualified doctor"
#     except Exception as e:
#         return f"🚨 Please try again later. Error: {str(e)}"

# with gr.Blocks(theme=gr.themes.Soft()) as app:
#     gr.Markdown("# 🏥 Medical Assistant (Mistral 7B)")
#     chatbot = gr.Chatbot(height=300)
#     msg = gr.Textbox(label="Your health question", placeholder="Describe your symptoms...")
#     clear = gr.ClearButton([msg, chatbot])

#     msg.submit(respond, [msg, chatbot], [chatbot])

# print("Launching interface...")
# app.launch(share=True, debug=False)