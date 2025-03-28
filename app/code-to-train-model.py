# -------------------------------------------------------------------------------This is the commented code to train the model and save it only uncomment it if u need to train the model---------------------------------------------------------------------------------------


#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️







# from transformers import pipeline, TFAutoModelForTokenClassification, TFAutoModelForSeq2SeqLM, AutoTokenizer
# import os
# from transformers import TFAutoModelForSequenceClassification
# from transformers import TFAutoModelForCausalLM


# # Directory to save models
# save_directory = "./saved_models"
# os.makedirs(save_directory, exist_ok=True)

# # Sentiment Pipeline (DistilBERT-based)
# sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
# sentiment_pipeline.model.save_pretrained(os.path.join(save_directory, "sentiment_model"))
# sentiment_pipeline.tokenizer.save_pretrained(os.path.join(save_directory, "sentiment_model"))

# # BioBERT NER - Convert to TensorFlow model
# model_name = "dmis-lab/biobert-base-cased-v1.1"
# ner_model = TFAutoModelForTokenClassification.from_pretrained(model_name, from_pt=True)  # Load from PyTorch weights
# ner_tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Save BioBERT as TensorFlow model in SavedModel format (default format)
# ner_model.save_pretrained(os.path.join(save_directory, "biobert_ner_model"))
# ner_model.save(os.path.join(save_directory, "biobert_ner_model"))  # SavedModel format (no .h5)

# # Save tokenizer
# ner_tokenizer.save_pretrained(os.path.join(save_directory, "biobert_ner_model"))

# # T5 Summarization Model - Convert to TensorFlow model
# summarization_model = TFAutoModelForSeq2SeqLM.from_pretrained("t5-base")
# summarization_tokenizer = AutoTokenizer.from_pretrained("t5-base")

# # Save T5 as TensorFlow model in SavedModel format
# summarization_model.save_pretrained(os.path.join(save_directory, "t5_summarization_model"))
# summarization_model.save(os.path.join(save_directory, "t5_summarization_model"))  # SavedModel format
# summarization_tokenizer.save_pretrained(os.path.join(save_directory, "t5_summarization_model"))

# # Longformer - Convert to TensorFlow model
# longformer_model = TFAutoModelForSequenceClassification.from_pretrained("allenai/longformer-base-4096")
# longformer_tokenizer = AutoTokenizer.from_pretrained("allenai/longformer-base-4096")

# # Save Longformer as TensorFlow model in SavedModel format
# longformer_model.save_pretrained(os.path.join(save_directory, "longformer_model"))
# longformer_model.save(os.path.join(save_directory, "longformer_model"))  # SavedModel format
# longformer_tokenizer.save_pretrained(os.path.join(save_directory, "longformer_model"))

# # GPT-2 - Convert to TensorFlow model
# gpt2_model = TFAutoModelForCausalLM.from_pretrained("gpt2")
# gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")

# # Save GPT-2 as TensorFlow model in SavedModel format
# gpt2_model.save_pretrained(os.path.join(save_directory, "gpt2_model"))
# gpt2_model.save(os.path.join(save_directory, "gpt2_model"))  # SavedModel format
# gpt2_tokenizer.save_pretrained(os.path.join(save_directory, "gpt2_model"))

# print(f"Models saved in TensorFlow SavedModel format at {save_directory}")







#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️
#⚠️⚠️⚠️⚠️ These  Models r not in use currently dont uncomment the script or train the models as it is alerady deployed on the hugging face model hub⚠️⚠️⚠️⚠️









# ---------------------------------------------------------------------This is the commented code to train the model and save it only uncomment it if u need to train the model---------------------------------------------------------------------------------------
