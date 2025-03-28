# !pip install transformers spacy
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from transformers import AutoModelForSeq2SeqLM
from transformers import pipeline as hf_pipeline  # Rename to avoid conflict
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import torch
from transformers import LongformerTokenizer, LongformerForSequenceClassification
import numpy as np
import pandas as pd
import re
import json
# import fitz  # PyMuPDF (for extracting text from PDF)
import os
# from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer, AutoModelForSeq2SeqLM
# # from typing import Union
# import fitz
import os
import fitz
import json
import logging
import os
import logging
import json
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import re
import logging
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer, LongformerTokenizer, LongformerForSequenceClassification
import shutil
import warnings
import torchvision
import tensorflow as tf
import warnings
import tensorflow as tf
import torchvision

# ===== TensorFlow Fixes =====
# Option 1: Use compat.v1 for backward compatibility
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# Option 2: Disable TensorFlow warnings entirely
# warnings.filterwarnings("ignore", category=DeprecationWarning)
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs

# ===== PyTorch Fixes =====
torchvision.disable_beta_transforms_warning()  # Disable torchvision beta warnings

# Optional: Suppress all warnings (not recommended)
# warnings.filterwarnings("ignore")
# shutil.rmtree('~/.cache/huggingface', ignore_errors=True)
# logging.basicConfig(level=logging.INFO)
# print("imported all packages")

from transformers import (
    AutoTokenizer, AutoModelForTokenClassification, AutoModelForSeq2SeqLM,
    pipeline, LongformerTokenizer, LongformerForSequenceClassification, 
    GPT2LMHeadModel, GPT2Tokenizer
)
import os

# ✅ Define cache directory in a permanent location
CACHE_DIR = "D:/cahc_models_folder"  # Change this to a suitable directory

# ✅ 1. Load Bi-BERT Model For NER Pipeline
model_name_biobert = "blackshadow1/biobert-ner-model"
ner_tokenizer = AutoTokenizer.from_pretrained(model_name_biobert, cache_dir=CACHE_DIR)
ner_model = AutoModelForTokenClassification.from_pretrained(model_name_biobert, cache_dir=CACHE_DIR,torch_dtype=torch.float16)
nlp_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, grouped_entities=True)

# ✅ 2. Load Sentiment Analysis Pipeline Model 
model_name_sentiment = "blackshadow1/sentiment-model"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name_sentiment)

# ✅ 3. Load the Summarization Model Pipeline 
model_name_summarization = "blackshadow1/t5-summarization-model"
summarization_tokenizer = AutoTokenizer.from_pretrained(model_name_summarization, cache_dir=CACHE_DIR)
summarization_model = AutoModelForSeq2SeqLM.from_pretrained(model_name_summarization, cache_dir=CACHE_DIR)

# ✅ 4. Load the Longformer Model Pipeline 
model_name_longformer = "blackshadow1/longformer-model"
longformer_tokenizer = LongformerTokenizer.from_pretrained(model_name_longformer, cache_dir=CACHE_DIR)
longformer_model = LongformerForSequenceClassification.from_pretrained(model_name_longformer, cache_dir=CACHE_DIR)

# ✅ 5. Initialize the GPT-2 Model & Tokenizer
gpt2_model_name = "blackshadow1/gpt2-model"
gpt2_tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_name, cache_dir=CACHE_DIR)
gpt2_model = GPT2LMHeadModel.from_pretrained(gpt2_model_name, cache_dir=CACHE_DIR)

# # Load BioBERT Model for NER
# ner_model = AutoModelForTokenClassification.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
# ner_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")

# # Create an NER Pipeline
# ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, grouped_entities=True)


# # Load models for Context-Aware Sentiment Analysis
# context_sentiment_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
# context_sentiment_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")






# Move the model to the GPU if available (optional but recommended for large models)
# Move the model to the GPU if available (optional but recommended for large models)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gpt2_model.to(device)

# Max File size
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# Load the  File validation and extraction functions 

def validate_file_size(file_path: str) -> None:
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File is too large ({file_size} bytes). Maximum allowed size is {MAX_FILE_SIZE} bytes.")
    
    
def extract_text_from_file(file_path: str) -> str:
    """
    Extracts text from a file based on its type (txt, pdf, json).
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file does not exist: {file_path}")
    
    # Validate file size
    validate_file_size(file_path)

    file_extension = os.path.splitext(file_path)[1].lower()
    logging.info(f"Extracting text from {file_path} with extension {file_extension}")

    if file_extension == '.txt':
        return extract_text_from_txt(file_path)
    
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    
    elif file_extension == '.json':
        return extract_text_from_json(file_path)
    
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    
def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except Exception as e:
        raise RuntimeError(f"Error reading text file: {e}")
    
    
def extract_text_from_pdf(pdf_file: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    """
    try:
        doc = fitz.open(pdf_file)
        text = ""
        for page in doc:
            text += page.get_text("text")
        if not text.strip():  # If no text found, use OCR
            images = convert_from_path(pdf_file)
            text = ' '.join([pytesseract.image_to_string(img) for img in images])
            logging.warning(f"Using OCR for PDF: {pdf_file}")
        return text
    except Exception as e:
        raise RuntimeError(f"Error reading PDF file: {e}")


def extract_text_from_json(json_file: str) -> str:
    """
    Extracts text content from a JSON file.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("text", "")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON file: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading JSON file: {e}")
    
    
import re
import logging

# Pre-compile regex patterns for better performance
PATTERNS = {
    'names': re.compile(r"(Patient(?: Name)?:)\s+[A-Za-z ]+"),
    'dates': re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b|\b\d{4}-\d{2}-\d{2}\b"),
    'ids': re.compile(r"(Medical Record ID|Patient ID|Case ID): \d+"),
    'phone': re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    'email': re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    'icd_codes': re.compile(r"(ICD(?:-10|-9)?:?\s?)[A-Za-z0-9.]+"),
    'medication': re.compile(r"(Medication|Drug|Prescription):\s+[A-Za-z0-9., ]+"),
    'health_metrics': re.compile(r"(BP|Blood Pressure|BMI|Heart Rate|Respiratory Rate):\s?\d{1,3}(/\d{1,3})?"),
    'lab_results': re.compile(r"(HbA1c|Glucose|Cholesterol|Triglycerides):?\s?\d{1,3}(\.\d+)?%?"),
    'insurance': re.compile(r"(Insurance Policy|Policy No|Billing ID):\s?\d+"),
    'room_ids': re.compile(r"(Room No|Hospital ID):\s?[A-Za-z0-9]+"),
    'general_terms': re.compile(r"\b(patient|hospital|doctor|nurse|specialist|clinic|facility|caregiver|medical history|referral)\b"),
    'conditions': re.compile(r"\b(cancer|hypertension|diabetes|heart disease|stroke|asthma|COPD|pneumonia|migraine|epilepsy)\b"),
    'procedures': re.compile(r"\b(surgery|operation|biopsy|chemo|radiation therapy|endoscopy|CT scan|MRI|X-ray)\b"),
    'medications': re.compile(r"\b(paracetamol|ibuprofen|aspirin|insulin|metformin|amoxicillin|prednisone|lipitor|antibiotic|painkillers)\b"),
    'test_results': re.compile(r"\b(CBC|ECG|X-ray result|CT scan result|MRI result|blood test|urine test|pregnancy test)\b"),
    'personal_info': re.compile(r"\b(patient name|address|phone number|email|social security number|insurance ID)\b"),
    'procedural_terms': re.compile(r"\b(emergency|urgent care|hospitalization|outpatient|inpatient)\b"),
}

def preprocess_text(text: str, to_lowercase: bool = True) -> str:
    """
    Cleans and preprocesses raw medical text.
    Enhancements:
    - Anonymizes sensitive data (names, dates, IDs, phone numbers, emails).
    - Handles medical-specific data: ICD codes, test results, vitals, etc.
    - Removes unwanted special characters.
    - Normalizes whitespace.
    - Converts to lowercase (optional).
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")
    
    logging.info("Starting text preprocessing...")

    # Anonymize sensitive data
    for key, pattern in PATTERNS.items():
        if key in ['names', 'dates', 'ids', 'phone', 'email']:
            text = re.sub(pattern, lambda m: m.group(0).split()[0] + " [REDACTED]", text)
        else:
            text = re.sub(pattern, lambda m: "[REDACTED]", text)
    
    # Remove unwanted special characters
    text = re.sub(r"[^\w\s.,%-]", "", text)
    logging.info("Special characters removed.")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase if enabled
    if to_lowercase:
        text = text.lower()
    
    logging.info("Text preprocessing complete.")
    return text


# Pre-compile regex patterns for better performance
PATTERNS = {
    'names': re.compile(r"(Patient(?: Name)?:)\s+[A-Za-z ]+"),
    'dates': re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b|\b\d{4}-\d{2}-\d{2}\b"),
    'ids': re.compile(r"(Medical Record ID|Patient ID|Case ID): \d+"),
    'phone': re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    'email': re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    'icd_codes': re.compile(r"(ICD(?:-10|-9)?:?\s?)[A-Za-z0-9.]+"),
    'medication': re.compile(r"(Medication|Drug|Prescription):\s+[A-Za-z0-9., ]+"),
    'health_metrics': re.compile(r"(BP|Blood Pressure|BMI|Heart Rate|Respiratory Rate):\s?\d{1,3}(/\d{1,3})?"),
    'lab_results': re.compile(r"(HbA1c|Glucose|Cholesterol|Triglycerides):?\s?\d{1,3}(\.\d+)?%?"),
    'insurance': re.compile(r"(Insurance Policy|Policy No|Billing ID):\s?\d+"),
    'room_ids': re.compile(r"(Room No|Hospital ID):\s?[A-Za-z0-9]+"),
    'general_terms': re.compile(r"\b(patient|hospital|doctor|nurse|specialist|clinic|facility|caregiver|medical history|referral)\b"),
    'conditions': re.compile(r"\b(cancer|hypertension|diabetes|heart disease|stroke|asthma|COPD|pneumonia|migraine|epilepsy)\b"),
    'procedures': re.compile(r"\b(surgery|operation|biopsy|chemo|radiation therapy|endoscopy|CT scan|MRI|X-ray)\b"),
    'medications': re.compile(r"\b(paracetamol|ibuprofen|aspirin|insulin|metformin|amoxicillin|prednisone|lipitor|antibiotic|painkillers)\b"),
    'test_results': re.compile(r"\b(CBC|ECG|X-ray result|CT scan result|MRI result|blood test|urine test|pregnancy test)\b"),
    'personal_info': re.compile(r"\b(patient name|address|phone number|email|social security number|insurance ID)\b"),
    'procedural_terms': re.compile(r"\b(emergency|urgent care|hospitalization|outpatient|inpatient)\b"),
}

def preprocess_text(text: str, to_lowercase: bool = True) -> str:
    """
    Cleans and preprocesses raw medical text.
    Enhancements:
    - Anonymizes sensitive data (names, dates, IDs, phone numbers, emails).
    - Handles medical-specific data: ICD codes, test results, vitals, etc.
    - Removes unwanted special characters.
    - Normalizes whitespace.
    - Converts to lowercase (optional).
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")
    
    logging.info("Starting text preprocessing...")

    # Anonymize sensitive data
    for key, pattern in PATTERNS.items():
        if key in ['names', 'dates', 'ids', 'phone', 'email']:
            text = re.sub(pattern, lambda m: m.group(0).split()[0] + " [REDACTED]", text)
        else:
            text = re.sub(pattern, lambda m: "[REDACTED]", text)
    
    # Remove unwanted special characters
    text = re.sub(r"[^\w\s.,%-]", "", text)
    logging.info("Special characters removed.")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase if enabled
    if to_lowercase:
        text = text.lower()
    
    logging.info("Text preprocessing complete.")
    return text



# New Prompt Engineering Step 

# New Prompt Engineering Step 

# New Prompt Engineering Step 

logging.basicConfig(level=logging.INFO)

def apply_prompt_engineering(cleaned_text: str , max_new_tokens=150, top_p=0.95, temperature=0.7) -> dict:
    """
    Applies prompt engineering to guide the language model in generating outputs based on the cleaned medical text.

    Args:
        cleaned_text (str): The preprocessed medical text.
        tokenizer: Pretrained tokenizer for text processing.
        model: Pretrained language model for text generation.
        max_new_tokens (int): Maximum number of tokens to generate.
        top_p (float): Top-p sampling parameter for text generation.
        temperature (float): Temperature parameter for text generation.

    Returns:
        dict: A dictionary where keys are prompts and values are generated outputs or error messages.
    """
    if not isinstance(cleaned_text, str) or not cleaned_text.strip():
        raise ValueError("cleaned_text must be a non-empty string.")

    logging.info("Applying prompt engineering to the cleaned text...")

    # Set pad_token to eos_token if not set already
    if gpt2_tokenizer.pad_token is None:
        gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token
    if gpt2_tokenizer.pad_token_id is None:
        gpt2_tokenizer.pad_token_id = gpt2_tokenizer.eos_token_id

    prompts = [
    # "Summarize the medical document in a few sentences.",
    # "Extract key medical conditions, diseases, or diagnoses mentioned in the document.",
    # "Identify and list any medical procedures or surgeries discussed in the document.",
    # "Highlight any prescribed medications or treatments mentioned in the document.",
    # "Extract patient demographic information, if available.",
    # "Summarize lab and test results mentioned in the document.",
    # "Extract vital signs and health metrics (e.g., BP, Heart Rate, BMI) from the document.",
    # "Identify any insurance or billing information in the document.",
    # "Categorize and list the medications and treatments prescribed in the document.",
    # "Extract family medical history, if provided.",
    # "Identify allergies or sensitivities mentioned in the document.",
    # "Identify and list any immunizations or vaccines discussed in the document.",
    # "Extract emergency contact information if provided in the document.",
    # "Summarize the patient’s medical history.",
    # "Identify and list any smoking or alcohol consumption habits mentioned in the document.",
    # "Extract any surgical history, including dates and types of procedures.",
    # "Identify and list the patient's chronic conditions.",
    # "List any referrals to specialists or healthcare providers mentioned in the document.",
    # "Summarize any physical therapy or rehabilitation information provided.",
    # "Identify any genetic information, such as inherited conditions, if mentioned.",
    # "Extract patient’s height, weight, and body mass index (BMI), if available.",
    # "Identify any recent hospitalizations or inpatient admissions.",
    # "Summarize any mental health concerns or diagnoses in the document.",
    # "Extract information about the patient’s social history, including occupation and lifestyle factors.",
    # "Identify any laboratory test names (e.g., blood tests, cultures) mentioned in the document.",
    # "Extract the results of any diagnostic imaging (e.g., X-rays, MRIs, CT scans).",
    # "List any medical devices mentioned in the document (e.g., pacemakers, prosthetics).",
    # "Identify any fertility or reproductive health information mentioned.",
    # "Summarize any substance abuse history, including alcohol, drugs, or tobacco use.",
    # "Identify any hereditary diseases or genetic markers mentioned.",
    # "Summarize the patient's risk factors for chronic conditions (e.g., obesity, hypertension).",
    # "Identify the patient's current and past medications, including dosages.",
    # "List any over-the-counter medications or supplements mentioned.",
    # "Identify any changes in the patient's medications or dosage history.",
    # "Summarize any dietary restrictions or nutrition-related information provided.",
    # "Identify any issues related to the patient’s sleep patterns or disorders.",
    # "Summarize any vision or hearing impairments mentioned in the document.",
    # "Extract any dental health information, including treatments or issues.",
    # "Summarize the patient's blood pressure readings and any relevant trends.",
    # "Identify and list any test results related to the liver, kidney, or heart functions.",
    # "Extract information on blood glucose levels, including diabetes-related data.",
    # "Summarize the patient’s neurological health, including any diagnoses or conditions.",
    # "Identify any respiratory issues or diagnoses (e.g., asthma, COPD).",
    # "Extract any information related to the patient’s cardiovascular health (e.g., heart disease).",
    # "Summarize any information on the patient’s gastrointestinal health (e.g., IBS, ulcers).",
    # "List any skin conditions or dermatological treatments mentioned.",
    # "Identify any chronic pain conditions and their management.",
    # "Summarize the patient's immunological health (e.g., autoimmune diseases, allergies).",
    # "List any psychological or psychiatric evaluations or treatments discussed.",
    # "Extract information on any cancer diagnoses, treatments, or outcomes.",
    # "Identify and summarize any infectious diseases or conditions diagnosed.",
    # "Extract any family planning or contraception-related information.",
    # "Identify any alternative or complementary treatments mentioned.",
    # "List any follow-up visits or procedures recommended for the patient.",
    # "Summarize the treatment plan provided in the document, including medications and interventions.",
    # "Extract any notes regarding the patient’s recovery or rehabilitation process.",
    # "Identify any concerns or red flags noted by the healthcare provider.",
    # "List the patient's immunization history, including vaccine types and dates.",
    # "Extract any cardiovascular risk assessments or screenings performed.",
    # "Summarize any smoking cessation or alcohol reduction programs mentioned.",
    # "Identify any genetic testing or counseling discussed.",
    # "List any healthcare screenings, such as mammograms or colonoscopies, discussed in the document.",
    # "Summarize any pain management strategies mentioned, including medications and non-pharmacological treatments.",
    # "Identify any treatments for mental health or behavioral conditions (e.g., anxiety, depression).",
    # "Summarize any reproductive health concerns, including fertility treatments or gynecological conditions.",
    # "Extract any end-of-life care or palliative care discussions in the document.",
    # "Summarize the patient's rehabilitation or physical therapy plan.",
    # "Identify any therapies or treatments for musculoskeletal conditions (e.g., arthritis, osteoporosis).",
    # "Summarize any skin care treatments or dermatology-related information.",
    # "Identify any diagnostic or therapeutic interventions for mental health issues.",
    # "Extract information regarding the patient's compliance with the treatment plan.",
    # "Summarize any surgical complications or adverse reactions described.",
    # "Identify any references to clinical trials or experimental treatments the patient is participating in.",
    # "Extract information on any medications or treatments being discontinued or adjusted.",
    # "Summarize any preventive health measures, such as screenings, vaccinations, or wellness checks.",
    # "List any lifestyle modifications suggested by the healthcare provider (e.g., exercise, diet).",
    # "Summarize any genetic counseling or testing related to specific conditions.",
    # "Extract information on the patient's response to treatment or therapies.",
    # "Identify any concerns or recommendations regarding the patient’s mental health status.",
    # "Summarize any concerns related to maternal or fetal health in pregnancy-related documents.",
    # "Identify any diagnostic methods or tests used to evaluate the patient’s condition (e.g., bloodwork, imaging).",
    # "Extract any detailed notes on the patient's work or occupational health status.",
    # "Summarize the patient’s compliance with prescribed medical treatments or procedures.",
    # "Identify any concerns related to the patient's post-operative or post-procedural care.",
    # "Summarize the patient’s functional status and ability to perform daily activities.",
    # "List any lifestyle or behavioral factors that might be contributing to the patient’s condition.",
    # "Identify any specific dietary recommendations or restrictions discussed in the document.",
    # "Summarize any alternative medicine or holistic treatments mentioned in the document.",
    # "Extract any references to peer-reviewed studies or clinical guidelines used in the treatment decisions.",
    # "Identify any legal, ethical, or consent-related issues discussed in the document."

    ]
    
    # Initialize the dictionary to store results
    # Initialize the dictionary to store results
    results = {}
    for prompt in prompts:
        try:
            logging.info(f"Processing prompt: {prompt}")
            full_input = f"{prompt}\n\nText: {cleaned_text}"
            inputs = gpt2_tokenizer(full_input, return_tensors="pt", truncation=True, padding=True, max_length=1024)

            outputs = gpt2_model.generate(
                inputs["input_ids"],
                do_sample=True,
                max_new_tokens=max_new_tokens,
                no_repeat_ngram_size=2,
                top_p=top_p,
                temperature=temperature,
            )

            result = gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            results[prompt] = result
        except RuntimeError as e:
            logging.error(f"Runtime error while processing prompt: {prompt}. Error: {str(e)}")
            results[prompt] = f"Error: {str(e)}"

    return results
 


def extract_entities(text):
    """
    Extracts entities using keyword-based matching for symptoms, diagnoses, and medications.
    
    Args:
        text (str): Input medical text for entity extraction.

    Returns:
        dict: Extracted entities grouped by type (e.g., symptoms, diagnoses, medications).
    """

    # # If the input is structured and contains entities already
    # if isinstance(results, dict) and 'entities' in results:
    #     return results['entities']

    # else:
    #     text = apply_prompt_engineering(resulta)


    # Full keyword lists for symptoms, diagnoses, and medications (from your provided lists)
    # # If the input is raw text, perform the entity extraction
    # if isinstance(results, str):
    #     text = results
        
    symptom_keywords = set([
        "pain", "fever", "cough", "headache", "fatigue", "nausea", "dizziness", "sore", "chills", 
        "swelling", "tired", "vomiting", "diarrhea", "constipation", "drowsiness", "sweating", "appetite loss", 
        "confusion", "weakness", "bleeding", "shortness of breath", "chest pain", "back pain", "abdominal pain", 
        "muscle aches", "joint pain", "coughing up blood", "sore throat", "stomach cramps", "dysphagia", "anorexia", 
        "urinary retention", "joint stiffness", "itching", "rash", "dysuria", "hematuria", "palpitations", 
        "dizziness", "tremors", "memory loss", "insomnia", "night sweats", "cold hands", "fatigue", "burning sensation", 
        "bloating", "difficulty breathing", "weight loss", "weight gain", "numbness", "tingling", "lightheadedness", 
        "fainting", "ear pain", "tinnitus", "confusion", "uncontrolled shaking", "mood swings", "irregular heartbeat", 
        "chronic fatigue", "muscle weakness", "skin rash", "joint swelling", "shortness of breath", "palpitations", 
        "urinary incontinence", "frequent urination", "difficulty swallowing", "blurry vision", "yellowing skin", 
        "chronic cough", "leg swelling", "facial swelling", "neck stiffness", "stomach bloating", "difficulty sleeping", 
        "cold sweats", "feeling faint", "dehydration", "slow heartbeat", "congestion", "runny nose", "sinus headache", 
        "frequent headaches", "gastrointestinal discomfort", "liver pain", "hemoptysis", "chronic pain", "frequent thirst"
    ])
    
    diagnosis_keywords = set([
        "cancer", "diabetes", "heart disease", "stroke", "asthma", "pneumonia", "arthritis", "hypertension", 
        "COPD", "depression", "anxiety", "influenza", "tuberculosis", "chronic obstructive pulmonary disease", "HIV", 
        "hypertensive heart disease", "gastritis", "stroke", "schizophrenia", "epilepsy", "osteoporosis", 
        "chronic kidney disease", "chronic pain", "fibromyalgia", "sleep apnea", "obesity", "bipolar disorder", 
        "Parkinson's disease", "dementia", "multiple sclerosis", "sickle cell anemia", "irritable bowel syndrome", 
        "hepatitis", "cirrhosis", "hypothyroidism", "hyperthyroidism", "urinary tract infection", "nephropathy", 
        "stroke", "Alzheimer's disease", "autoimmune disorder", "autoimmune disease", "HIV/AIDS", "cardiomyopathy", 
        "peripheral neuropathy", "gout", "lupus", "celiac disease", "pancreatitis", "colitis", "cancer", "renal failure", 
        "bipolar disorder", "schizophrenia", "Crohn's disease", "tuberculosis", "pneumonia", "mental illness", 
        "emphysema", "anemia", "Cushing's syndrome", "Addison's disease", "sickle cell disease", "sepsis", "septicemia", 
        "heart attack", "arrhythmia", "heart failure", "chronic fatigue syndrome", "malaria", "chickenpox", 
        "tuberculosis", "meningitis", "gonorrhea", "syphilis", "hepatitis C", "HIV infection", "gonorrhea", 
        "urinary tract infection", "psoriasis", "chronic bronchitis", "eczema", "dermatitis", "hypertension", "stroke", 
        "myocardial infarction", "cirrhosis", "brain tumor", "epileptic seizures", "lymphoma", "melanoma", "bacterial infection"
    ])
    
    medication_keywords = set([
        "ibuprofen", "aspirin", "paracetamol", "amoxicillin", "metformin", "insulin", "acetaminophen", "naproxen", 
        "hydrocodone", "morphine", "antibiotics", "prednisone", "loratadine", "dextromethorphan", "fentanyl", 
        "sertraline", "fluoxetine", "alprazolam", "omeprazole", "lisinopril", "hydrochlorothiazide", "gabapentin", 
        "diclofenac", "cetirizine", "diphenhydramine", "clindamycin", "azithromycin", "levothyroxine", "amlodipine", 
        "warfarin", "hydroxychloroquine", "clopidogrel", "hydrocodone", "acetaminophen", "phenytoin", "topiramate", 
        "amlodipine", "losartan", "prednisolone", "carbamazepine", "valacyclovir", "antihistamine", "citalopram", 
        "zoloft", "paroxetine", "fluticasone", "albuterol", "salbutamol", "alendronate", "ranitidine", "esomeprazole", 
        "metoprolol", "lorazepam", "levothyroxine", "meloxicam", "simvastatin", "atorvastatin", "metformin", 
        "nifedipine", "lisinopril", "bupropion", "esomeprazole", "tramadol", "gabapentin", "cyclobenzaprine", 
        "clonazepam", "flunisolide", "captopril", "dexamethasone", "tamsulosin", "fluconazole", "amoxicillin", 
        "lorazepam", "digoxin", "hydrocodone", "doxycycline", "ketoconazole", "azithromycin", "miconazole", 
        "propranolol", "nystatin", "phenobarbital", "fluconazole", "dapoxetine", "nitroglycerin", "pantoprazole", 
        "cimetidine", "levofloxacin", "ivermectin", "sildenafil", "carvedilol", "calcium carbonate", "hydrochlorothiazide", 
        "spironolactone", "metoclopramide", "albuterol", "zolpidem", "tizanidine", "trazodone", "famotidine", 
        "prednisolone", "methylprednisolone", "hydrocortisone", "clomipramine", "dantrolene", "lamotrigine", 
        "valsartan", "topiramate", "methadone", "hydroxychloroquine"
    ])
    
    # Tokenize the input text by words (using regex for better tokenization)
    words = re.findall(r'\b\w+\b', text.lower())

    # Initialize categories
    categorized_entities = {"symptoms": set(), "diagnoses": set(), "medications": set()}

    # Classify words based on keyword matching
    for word in words:
        if word in symptom_keywords:
            categorized_entities["symptoms"].add(word)
        elif word in diagnosis_keywords:
            categorized_entities["diagnoses"].add(word)
        elif word in medication_keywords:
            categorized_entities["medications"].add(word)

    # Convert sets back to lists for the output
    for category in categorized_entities:
        categorized_entities[category] = list(categorized_entities[category])

    return categorized_entities
 
 
 
def summarize_text(text, max_input_length=3000, max_summary_length=100, beam_width=4, no_repeat_ngram_size=2, length_penalty=2.0):
    """
    Summarizes text using a pre-trained T5 model with advanced parameters.
    
    Args:
        text (str): Input text to summarize.
        max_input_length (int): Maximum length of the input text (default 1024 tokens).
        max_summary_length (int): Maximum length of the summary (default 150 tokens).
        beam_width (int): Number of beams for beam search (default 4).
        no_repeat_ngram_size (int): N-gram size to avoid repetition (default 2).
        length_penalty (float): Length penalty to control summary verbosity (default 2.0).
    
    Returns:
        str: Summarized text.
    """
    if not text.strip():
        raise ValueError("Input text is empty. Please provide valid text to summarize.")
    
    # Tokenize the input text with truncation if it's too long
    inputs = summarization_tokenizer.encode(
        "summarize: " + text, 
        return_tensors="pt", 
        max_length=max_input_length, 
        truncation=True
    )
    
    # Generate the summary
    outputs = summarization_model.generate(
        inputs,
        max_length=max_summary_length, 
        min_length=25,
        length_penalty=length_penalty, 
        num_beams=beam_width,
        no_repeat_ngram_size=no_repeat_ngram_size,
        early_stopping=True
    )
    
    # Decode and return the summary
    summary = summarization_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary



# Longformer-based Context-Aware Sentiment Analysis (Handles long texts)
def analyze_sentiment_longformer(text, chunk_size=512, stride=256):
    """
    Analyzes sentiment of long texts using Longformer model to handle larger context.
    
    Args:
        text (str): Input text for sentiment analysis (could be large documents).
        chunk_size (int): Maximum length of tokenized input for Longformer.
        stride (int): Overlap between chunks to maintain context.
    
    Returns:
        dict: Sentiment analysis result with document-level context.
    """
    # Tokenize text in chunks
    inputs = longformer_tokenizer(text, return_tensors="pt", truncation=False, padding=True)
    input_ids = inputs['input_ids'][0]
    
    # If the length exceeds the maximum length, break the text into chunks
    if len(input_ids) > chunk_size:
        sentiment_scores = []
        
        # Sliding window approach: move with stride across the document
        for i in range(0, len(input_ids), chunk_size - stride):
            chunk = input_ids[i:i+chunk_size]
            # Ensure chunk is of the correct length
            if len(chunk) < chunk_size:
                chunk = chunk + [tokenizer.pad_token_id] * (chunk_size - len(chunk))

            # Perform sentiment analysis on the chunk
            inputs_chunk = {'input_ids': torch.tensor([chunk])}
            with torch.no_grad():
                outputs = longformer_model(**inputs_chunk)
                logits = outputs.logits
                sentiment_scores.append(torch.nn.functional.softmax(logits, dim=-1).cpu().numpy()[0])

        # Average the scores from each chunk
        avg_scores = np.mean(sentiment_scores, axis=0)
        sentiment_label = "POSITIVE" if avg_scores[1] > avg_scores[0] else "NEGATIVE"
        sentiment_confidence = avg_scores[1] if avg_scores[1] > avg_scores[0] else avg_scores[0]
        return {'label': sentiment_label, 'confidence': sentiment_confidence}
    else:
        # If text is small, use the standard model
        sentiment = sentiment_pipeline(text)[0]
        return sentiment

# Function to analyze sentiment for mixed or large texts with context-awareness
def analyze_sentiment(text, long_text=False, chunk_size=512, stride=256):
    """
    Analyzes sentiment with context-awareness (Document level sentiment).
    
    Args:
        text (str): The text to analyze sentiment for.
        long_text (bool): Flag to use Longformer for large documents.
        chunk_size (int): Maximum length of each chunk.
        stride (int): Amount to overlap between chunks to maintain context.
    
    Returns:
        dict: Sentiment label and confidence.
    """
    if long_text:
        return analyze_sentiment_longformer(text, chunk_size, stride)
    else:
        # If it's small text, use regular sentiment analysis model
        sentiment = sentiment_pipeline(text)[0]
        return sentiment


def generate_ehr_report(patient_info, diagnoses, medications, lab_results, notes, recommendations):
    """
    Generate an EHR report based on the provided information.
    
    Arguments:
    - patient_info (dict): Contains patient-related information like name, age, gender.
    - diagnoses (list): List of diagnoses.
    - medications (list): List of medication dictionaries.
    - lab_results (list): List of lab results.
    - notes (str): Additional notes related to the patient's condition.
    - recommendations (list): List of medical recommendations.
    
    Returns:
    - str: Formatted EHR report as a string.
    """
    # Updated line for medication_str to handle medications as a list of dictionaries
    if medications:
        medication_str = "; ".join([f"{med['name']} ({med['dosage']}, {med['frequency']})" for med in medications if isinstance(med, dict)]) 
    else:
        medication_str = 'No medications prescribed.'
    
    # Generate lab results string
    lab_results_str = "".join([f"- **{result['test']}**: {result['value']} {result['unit']} (Normal: {result['normal_range']}, Flag: {result['flag']})\n" for result in lab_results]) if lab_results else 'No lab results available.'
    
    # Generate recommendations string
    recommendation_str = "".join([f"- {rec}\n" for rec in recommendations]) if recommendations else 'No recommendations provided.'

    # Construct the final EHR report
    report = f"""
    Patient Info:
    - Name: {patient_info.get('name', 'Unknown')}
    - Age: {patient_info.get('age', 'Unknown')}
    - Gender: {patient_info.get('gender', 'Unknown')}

    Diagnoses:
    {"; ".join(diagnoses) if diagnoses else 'No diagnoses provided.'}

    Medications:
    {medication_str}

    Lab Results:
    {lab_results_str}

    Recommendations:
    {recommendation_str}

    Notes:
    {notes if notes else 'No additional notes.'}
    """
    
    return report





class MedicalNLPipeline:
    def process_document(self, file_path: str = None, prompt: str = None):
        """
        Processes a medical document in various formats (.txt, .json, .pdf) or custom prompt through the pipeline.
        """
        # Step 1: Ensure only one input is provided
        if file_path and prompt:
            raise ValueError("Please provide either a file path or a prompt, not both.")
        
        # Step 2: Check if a file or prompt is provided
        if file_path:
            # Validate the file path
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"The file '{file_path}' does not exist. Please provide a valid file path.")
            
            # Extract text from the provided file
            extracted_text = extract_text_from_file(file_path)
        elif prompt:
            # Use the provided prompt directly
            extracted_text = prompt
        else:
            raise ValueError("No input provided. Either a file path or a prompt must be specified.")
        
        # Step 3: Preprocess the extracted text
        cleaned_text = preprocess_text(extracted_text)
        print("Cleaned Text:", cleaned_text)

        # Step 4: Prompt Engineering (Enhance or Format Text)
        engineered_prompt = apply_prompt_engineering(cleaned_text)
        print("Engineered Prompt:", engineered_prompt)
    
        # Step 5: Extract Entities using NER pipeline
        categorized_entities = extract_entities(cleaned_text)
        print("Categorized Entities:", categorized_entities)
    
        # Step 6: Summarize the text
        summary = summarize_text(cleaned_text)
        print("Summary:", summary)
        
        # Step 7: Perform sentiment analysis
        sentiment_result = analyze_sentiment(cleaned_text)
        print("Sentiment Analysis:", sentiment_result)
        
        # Step 8: Generate a structured report
        report = generate_ehr_report(
            patient_info=categorized_entities.get('patient_info', {}),
            diagnoses=categorized_entities.get('diagnoses', []),
            medications=categorized_entities.get('medications', []),
            lab_results=categorized_entities.get('lab_results', []),
            notes=summary,
            recommendations=categorized_entities.get('recommendations', [])
        )
        print("Generated Report:")
        print(report)

        # Step 9: Return all results, including the report
        return {
            'extracted_text': extracted_text,
            'cleaned_text': cleaned_text,
            'engineered_prompt': engineered_prompt,
            'categorized_entities': categorized_entities,
            'summary': summary,
            'sentiment': sentiment_result,
            'report': report
        }      
        

        
# Testing code commented out only use when there is the model testing going on -------------------------------- --------------------------------            --------------------------------


# # Instantiate the pipeline
# medical_nlp = MedicalNLPipeline()


# # Process a document
# result = medical_nlp.process_document(file_path="/kaggle/input/final-dataset/medical_document.txt")

# # Access the generated report
# print("Structured Report:")
# print(result['report'])

# # Optional: Save the report as a JSON file
# with open("ehr_report.json", "w") as f:
#     import json
#     json.dump(result['report'], f, indent=4)
# print("Report saved to ehr_report.json")


# Testing code commented out only use when there is the model testing going on ---------------------------------------------------------------------------------------- 