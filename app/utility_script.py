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
logging.basicConfig(level=logging.INFO)
print("imported all packages")




# Load ALL necessary Models
# Load Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Load BioBERT Model

ner_model = AutoModelForTokenClassification.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
ner_tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")

# Create an NER Pipeline
# ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer)
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, grouped_entities=True)


# Load T5 Model for Summarization
summarization_model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")  # Use 't5-large' for better performance
summarization_tokenizer = AutoTokenizer.from_pretrained("t5-base")


# Load models for Context-Aware Sentiment Analysis
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
sentiment_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# Load Longformer model for handling long text
longformer_tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
longformer_model = LongformerForSequenceClassification.from_pretrained("allenai/longformer-base-4096")

# # Pipeline for Sentence Level Sentiment Analysis (DistilBERT)
# sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=tokenizer)

# Initialize the GPT-2 model and tokenizer from Hugging Face
model_name = "gpt2"  # You can also use "gpt2-medium", "gpt2-large", or "gpt2-xl" for larger models
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)



# Move the model to the GPU if available (optional but recommended for large models)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)




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

    # Anonymize patient names
    text = re.sub(r"(Patient(?: Name)?:)\s+[A-Za-z ]+", r"\1 [REDACTED]", text)
    logging.info("Patient names anonymized.")

    # Anonymize dates
    text = re.sub(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", "[DATE REDACTED]", text)
    text = re.sub(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b", "[DATE REDACTED]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[DATE REDACTED]", text)
    logging.info("Dates anonymized.")

    # Anonymize IDs (e.g., Medical Record ID)
    text = re.sub(r"(Medical Record ID|Patient ID|Case ID): \d+", r"\1: [REDACTED]", text)
    logging.info("IDs anonymized.")

    # Anonymize phone numbers
    text = re.sub(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[PHONE REDACTED]", text)
    logging.info("Phone numbers anonymized.")

    # Anonymize email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL REDACTED]", text)
    logging.info("Emails anonymized.")

    # Anonymize ICD/Diagnosis Codes (e.g., "ICD-10: E11.9")
    text = re.sub(r"(ICD(?:-10|-9)?:?\s?)[A-Za-z0-9.]+", r"\1[REDACTED]", text)
    logging.info("ICD codes anonymized.")

    # Anonymize prescription drug names (e.g., "Medication: Paracetamol")
    text = re.sub(r"(Medication|Drug|Prescription):\s+[A-Za-z0-9., ]+", r"\1: [REDACTED]", text)
    logging.info("Drug and prescription names anonymized.")

    # Anonymize health metrics (e.g., "BP: 120/80", "BMI: 24.5")
    text = re.sub(r"(BP|Blood Pressure|BMI|Heart Rate|Respiratory Rate):\s?\d{1,3}(/\d{1,3})?", r"\1: [REDACTED]", text)
    logging.info("Health metrics anonymized.")

    # Anonymize lab/test results (e.g., "HbA1c: 7.5%")
    text = re.sub(r"(HbA1c|Glucose|Cholesterol|Triglycerides):?\s?\d{1,3}(\.\d+)?%?", r"\1: [REDACTED]", text)
    logging.info("Lab and test results anonymized.")

    # Anonymize insurance/billing information (e.g., "Policy No: 123456789")
    text = re.sub(r"(Insurance Policy|Policy No|Billing ID):\s?\d+", r"\1: [REDACTED]", text)
    logging.info("Insurance and billing information anonymized.")

    # Anonymize room/hospital identifiers (e.g., "Room No: 12A")
    text = re.sub(r"(Room No|Hospital ID):\s?[A-Za-z0-9]+", r"\1: [REDACTED]", text)
    logging.info("Room and hospital identifiers anonymized.")

    # Remove unwanted special characters
    text = re.sub(r"[^\w\s.,%-]", "", text)
    logging.info("Special characters removed.")


    # Anonymize General Medical Terms
    text = re.sub(r"\b(patient|hospital|doctor|nurse|specialist|clinic|facility|caregiver|medical history|referral)\b", "[REDACTED]", text)

    # Anonymize Medical Conditions / Diagnoses
    text = re.sub(r"\b(cancer|hypertension|diabetes|heart disease|stroke|asthma|COPD|pneumonia|migraine|epilepsy)\b", "[DIAGNOSIS REDACTED]", text)

    # Anonymize Medical Procedures & Surgeries
    text = re.sub(r"\b(surgery|operation|biopsy|chemo|radiation therapy|endoscopy|CT scan|MRI|X-ray)\b", "[PROCEDURE REDACTED]", text)

    # Anonymize Medications / Drugs
    text = re.sub(r"\b(paracetamol|ibuprofen|aspirin|insulin|metformin|amoxicillin|prednisone|lipitor|antibiotic|painkillers)\b", "[MEDICATION REDACTED]", text)

    # Anonymize Health Metrics & Vitals
    text = re.sub(r"\b(blood pressure|BP|heart rate|BMI|pulse rate|respiratory rate|oxygen saturation|glucose level|cholesterol level|HbA1c)\b", "[HEALTH METRIC REDACTED]", text)

    # Anonymize Test Results
    text = re.sub(r"\b(CBC|ECG|X-ray result|CT scan result|MRI result|blood test|urine test|pregnancy test)\b", "[TEST RESULT REDACTED]", text)

    # Anonymize Personal Information
    text = re.sub(r"\b(patient name|address|phone number|email|social security number|insurance ID)\b", "[REDACTED]", text)

    # Anonymize Procedural Terms
    text = re.sub(r"\b(emergency|urgent care|hospitalization|outpatient|inpatient)\b", "[PROCEDURE REDACTED]", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase if enabled
    if to_lowercase:
        text = text.lower()
    
    logging.info("Text preprocessing complete.")
    return text



# New Prompt Engineering Step 

def apply_prompt_engineering(cleaned_text: str) -> dict:
    """
    Applies prompt engineering to guide the language model in generating outputs based on the cleaned medical text.
    Uses a pretrained GPT-2 model to generate results.
    """

    logging.info("Applying prompt engineering to the cleaned text...")

    prompts = [
    "Summarize the medical document in a few sentences.",
    "Extract key medical conditions, diseases, or diagnoses mentioned in the document.",
    "Identify and list any medical procedures or surgeries discussed in the document.",
    "Highlight any prescribed medications or treatments mentioned in the document.",
    "Extract patient demographic information, if available.",
    "Summarize lab and test results mentioned in the document.",
    "Extract vital signs and health metrics (e.g., BP, Heart Rate, BMI) from the document.",
    "Identify any insurance or billing information in the document.",
    "Categorize and list the medications and treatments prescribed in the document.",
    "Extract family medical history, if provided.",
    "Identify allergies or sensitivities mentioned in the document.",
    "Identify and list any immunizations or vaccines discussed in the document.",
    "Extract emergency contact information if provided in the document.",
    "Summarize the patient’s medical history.",
    "Identify and list any smoking or alcohol consumption habits mentioned in the document.",
    "Extract any surgical history, including dates and types of procedures.",
    "Identify and list the patient's chronic conditions.",
    "List any referrals to specialists or healthcare providers mentioned in the document.",
    "Summarize any physical therapy or rehabilitation information provided.",
    "Identify any genetic information, such as inherited conditions, if mentioned.",
    "Extract patient’s height, weight, and body mass index (BMI), if available.",
    "Identify any recent hospitalizations or inpatient admissions.",
    "Summarize any mental health concerns or diagnoses in the document.",
    "Extract information about the patient’s social history, including occupation and lifestyle factors.",
    "Identify any laboratory test names (e.g., blood tests, cultures) mentioned in the document.",
    "Extract the results of any diagnostic imaging (e.g., X-rays, MRIs, CT scans).",
    "List any medical devices mentioned in the document (e.g., pacemakers, prosthetics).",
    "Identify any fertility or reproductive health information mentioned.",
    "Summarize any substance abuse history, including alcohol, drugs, or tobacco use.",
    "Identify any hereditary diseases or genetic markers mentioned.",
    "Summarize the patient's risk factors for chronic conditions (e.g., obesity, hypertension).",
    "Identify the patient's current and past medications, including dosages.",
    "List any over-the-counter medications or supplements mentioned.",
    "Identify any changes in the patient's medications or dosage history.",
    "Summarize any dietary restrictions or nutrition-related information provided.",
    "Identify any issues related to the patient’s sleep patterns or disorders.",
    "Summarize any vision or hearing impairments mentioned in the document.",
    "Extract any dental health information, including treatments or issues.",
    "Summarize the patient's blood pressure readings and any relevant trends.",
    "Identify and list any test results related to the liver, kidney, or heart functions.",
    "Extract information on blood glucose levels, including diabetes-related data.",
    "Summarize the patient’s neurological health, including any diagnoses or conditions.",
    "Identify any respiratory issues or diagnoses (e.g., asthma, COPD).",
    "Extract any information related to the patient’s cardiovascular health (e.g., heart disease).",
    "Summarize any information on the patient’s gastrointestinal health (e.g., IBS, ulcers).",
    "List any skin conditions or dermatological treatments mentioned.",
    "Identify any chronic pain conditions and their management.",
    "Summarize the patient's immunological health (e.g., autoimmune diseases, allergies).",
    "List any psychological or psychiatric evaluations or treatments discussed.",
    "Extract information on any cancer diagnoses, treatments, or outcomes.",
    "Identify and summarize any infectious diseases or conditions diagnosed.",
    "Extract any family planning or contraception-related information.",
    "Identify any alternative or complementary treatments mentioned.",
    "List any follow-up visits or procedures recommended for the patient.",
    "Summarize the treatment plan provided in the document, including medications and interventions.",
    "Extract any notes regarding the patient’s recovery or rehabilitation process.",
    "Identify any concerns or red flags noted by the healthcare provider.",
    "List the patient's immunization history, including vaccine types and dates.",
    "Extract any cardiovascular risk assessments or screenings performed.",
    "Summarize any smoking cessation or alcohol reduction programs mentioned.",
    "Identify any genetic testing or counseling discussed.",
    "List any healthcare screenings, such as mammograms or colonoscopies, discussed in the document.",
    "Summarize any pain management strategies mentioned, including medications and non-pharmacological treatments.",
    "Identify any treatments for mental health or behavioral conditions (e.g., anxiety, depression).",
    "Summarize any reproductive health concerns, including fertility treatments or gynecological conditions.",
    "Extract any end-of-life care or palliative care discussions in the document.",
    "Summarize the patient's rehabilitation or physical therapy plan.",
    "Identify any therapies or treatments for musculoskeletal conditions (e.g., arthritis, osteoporosis).",
    "Summarize any skin care treatments or dermatology-related information.",
    "Identify any diagnostic or therapeutic interventions for mental health issues.",
    "Extract information regarding the patient's compliance with the treatment plan.",
    "Summarize any surgical complications or adverse reactions described.",
    "Identify any references to clinical trials or experimental treatments the patient is participating in.",
    "Extract information on any medications or treatments being discontinued or adjusted.",
    "Summarize any preventive health measures, such as screenings, vaccinations, or wellness checks.",
    "List any lifestyle modifications suggested by the healthcare provider (e.g., exercise, diet).",
    "Summarize any genetic counseling or testing related to specific conditions.",
    "Extract information on the patient's response to treatment or therapies.",
    "Identify any concerns or recommendations regarding the patient’s mental health status.",
    "Summarize any concerns related to maternal or fetal health in pregnancy-related documents.",
    "Identify any diagnostic methods or tests used to evaluate the patient’s condition (e.g., bloodwork, imaging).",
    "Extract any detailed notes on the patient's work or occupational health status.",
    "Summarize the patient’s compliance with prescribed medical treatments or procedures.",
    "Identify any concerns related to the patient's post-operative or post-procedural care.",
    "Summarize the patient’s functional status and ability to perform daily activities.",
    "List any lifestyle or behavioral factors that might be contributing to the patient’s condition.",
    "Identify any specific dietary recommendations or restrictions discussed in the document.",
    "Summarize any alternative medicine or holistic treatments mentioned in the document.",
    "Extract any references to peer-reviewed studies or clinical guidelines used in the treatment decisions.",
    "Identify any legal, ethical, or consent-related issues discussed in the document."

    ]
    
    # Initialize the dictionary to store results
    results = {}

    # For each prompt, we use the model to generate a response
    for prompt in prompts:
        try:
            # Prepend the cleaned text to the prompt
            full_input = f"{prompt}\n\nText: {cleaned_text}"

            # Tokenize the input and prepare it for the model
            inputs = tokenizer(full_input, return_tensors="pt", truncation=True, max_length=1024).to(device)
            
            # Generate the output
            outputs = model.generate(inputs["input_ids"], max_length=150, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.95, temperature=0.7)

            # Decode the output text
            result = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

            # Store the result in the dictionary
            results[prompt] = result
            logging.info(f"Prompt '{prompt}' processed successfully.")
        
        except Exception as e:
            logging.error(f"Error while processing prompt '{prompt}': {str(e)}")
            results[prompt] = f"Error: {str(e)}"

    logging.info("Prompt engineering applied successfully.")
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



# from transformers import T5Tokenizer, T5ForConditionalGeneration

# # Load pre-trained model and tokenizer for T5 summarization
# summarization_tokenizer = T5Tokenizer.from_pretrained("t5-small")
# summarization_model = T5ForConditionalGeneration.from_pretrained("t5-small")

# from transformers import T5Tokenizer, T5ForConditionalGeneration

# # Load pre-trained model and tokenizer for T5 summarization
# summarization_tokenizer = T5Tokenizer.from_pretrained("t5-small")
# summarization_model = T5ForConditionalGeneration.from_pretrained("t5-small")

def summarize_text(text, max_input_length=1024, max_summary_length=150, temperature=1.0, top_k=50, top_p=0.95, beam_width=8, no_repeat_ngram_size=2):
    """
    Summarizes text using a pre-trained T5 model with advanced parameters.

    Args:
        text (str): Input text to summarize.
        max_input_length (int): Maximum length of the input text (default 1024 tokens).
        max_summary_length (int): Maximum length of the summary (default 150 tokens).
        temperature (float): Temperature for sampling (default 1.0).
        top_k (int): Top-k sampling (default 50).
        top_p (float): Top-p sampling (default 0.95).
        beam_width (int): Number of beams for beam search (default 8).
        no_repeat_ngram_size (int): N-gram size to avoid repetition (default 2).

    Returns:
        str: Summarized text.
    """
    # Tokenize the input text with truncation and padding
    inputs = summarization_tokenizer(
        "summarize: " + text,
        return_tensors="pt",
        max_length=max_input_length,
        truncation=True,
        padding="max_length"  # Ensures consistent length and generates attention mask
    )
    
    # Generate the summary with advanced settings
    outputs = summarization_model.generate(
        inputs["input_ids"],
        pad_token_id=summarization_tokenizer.pad_token_id,  # Explicitly set pad_token_id
        attention_mask=inputs["attention_mask"],  # Pass the attention mask
        max_length=max_summary_length, 
        min_length=25,
        length_penalty=2.0, 
        num_beams=beam_width,
        no_repeat_ngram_size=no_repeat_ngram_size, 
        early_stopping=True,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p
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
        

        # Step 8: Return all results as a dictionary for easy access
        return {
            'extracted_text': extracted_text,
            'cleaned_text': cleaned_text,
            'engineered_prompt': engineered_prompt,
            'categorized_entities': categorized_entities,
            'summary': summary,
            'sentiment': sentiment_result
        }
        
        
        
        
# Testing code commented out only use when there is the model testing going on -------------------------------- --------------------------------            --------------------------------


# # # Example Usage
# Using the EHR text 
# # raw_text = ''

# # # Instantiate the Medical NLP pipeline
# # medical_nlp = MedicalNLPipeline()

# # # Process the medical document
# # result = medical_nlp.process_document(raw_text)

# # # Output the results
# # print("Final Output:")
# # print(result)

# Example Usage
# file_path = "/kaggle/input/final-dataset/medical_document.txt"  # Can be .txt, .json, or .pdf

# # Instantiate the Medical NLP pipeline
# medical_nlp = MedicalNLPipeline()

# # Process the medical document with file or prompt
# result = medical_nlp.process_document(file_path=file_path)  # Or use: result = medical_nlp.process_document(prompt=prompt_text)

# # Output the results
# print("Final Output:")
# print(result)

# Testing code commented out only use when there is the model testing going on ---------------------------------------------------------------------------------------- 