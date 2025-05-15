
# Working Code ✅✅✅✅✅✅

# import gradio as gr
# from transformers import BlipProcessor, BlipForConditionalGeneration
# from transformers import pipeline
# import torch
# from PIL import Image
# import logging
# from typing import Dict

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# class MedicalImageAnalyzer:
#     def __init__(self):
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.image_processor = None
#         self.image_model = None
#         self.nlp_processor = None
#         self.load_models()

#     def load_models(self):
#         """Load models with proper error handling"""
#         try:
#             logger.info("Loading BLIP model for image analysis...")
            
#             # Using smaller BLIP model that's more stable
#             self.image_processor = BlipProcessor.from_pretrained(
#                 "Salesforce/blip-image-captioning-base",
#                 cache_dir="model_cache"
#             )
#             self.image_model = BlipForConditionalGeneration.from_pretrained(
#                 "Salesforce/blip-image-captioning-base",
#                 torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
#                 cache_dir="model_cache"
#             ).to(self.device)
            
#             logger.info("Loading NLP model...")
#             self.nlp_processor = pipeline(
#                 "text-generation",
#                 model="distilgpt2",  # Using smaller model for stability
#                 device=self.device
#             )
            
#             logger.info("All models loaded successfully")
#         except Exception as e:
#             logger.error(f"Model loading failed: {str(e)}")
#             # Fallback to CPU if GPU fails
#             if "CUDA" in str(e):
#                 logger.info("Trying CPU fallback...")
#                 self.device = "cpu"
#                 self.load_models()
#             else:
#                 raise RuntimeError(f"Failed to initialize models: {str(e)}")

#     def analyze_image(self, image: Image.Image, clinical_context: str = "") -> Dict:
#         """Analyze medical image with clinical context"""
#         try:
#             if not image:
#                 return {"error": "No image provided"}
            
#             # Generate initial findings
#             prompt = self._build_radiology_prompt(clinical_context)
#             inputs = self.image_processor(image, text=prompt, return_tensors="pt").to(self.device)
            
#             with torch.no_grad():
#                 outputs = self.image_model.generate(**inputs, max_new_tokens=200)
            
#             findings = self.image_processor.decode(outputs[0], skip_special_tokens=True)
#             findings = findings.replace(prompt, "").strip()
            
#             return {
#                 "findings": findings,
#                 "recommendations": self._generate_recommendations(findings)
#             }
            
#         except Exception as e:
#             logger.error(f"Analysis error: {str(e)}")
#             return {"error": str(e)}

#     def _build_radiology_prompt(self, clinical_context: str) -> str:
#         """Build structured prompt for radiology analysis"""
#         return (
#             "Analyze this medical image professionally. "
#             f"Clinical context: {clinical_context if clinical_context else 'None provided'}. "
#             "Describe:\n"
#             "1. Key anatomical features\n"
#             "2. Abnormal findings\n"
#             "3. Technical quality\n\n"
#             "Findings:"
#         )

#     def _generate_recommendations(self, findings: str) -> str:
#         """Generate clinical recommendations"""
#         prompt = (
#             "Based on these radiological findings:\n"
#             f"{findings}\n\n"
#             "Provide 3-5 clinical recommendations:"
#         )
#         try:
#             response = self.nlp_processor(
#                 prompt,
#                 max_new_tokens=150,
#                 temperature=0.7
#             )
#             return response[0]["generated_text"].replace(prompt, "").strip()
#         except Exception as e:
#             logger.error(f"Recommendation generation failed: {str(e)}")
#             return "Could not generate recommendations - please consult a radiologist."

# # Initialize with error handling
# try:
#     analyzer = MedicalImageAnalyzer()
# except Exception as e:
#     logger.error(f"Failed to initialize analyzer: {str(e)}")
#     raise RuntimeError("System initialization failed. Please check requirements and try again.")

# def analyze_medical_image(image: Image.Image, clinical_context: str = "") -> str:
#     """Wrapper for Gradio interface"""
#     try:
#         if not image:
#             return "⚠️ Please upload a medical image"
        
#         results = analyzer.analyze_image(image, clinical_context)
        
#         if "error" in results:
#             return f"❌ Error: {results['error']}"
        
#         return (
#             f"**Clinical Context**: {clinical_context if clinical_context else 'None provided'}\n\n"
#             f"**Findings**:\n{results['findings']}\n\n"
#             f"**Recommendations**:\n{results['recommendations']}\n\n"
#             "Note: This preliminary analysis requires verification by a qualified radiologist."
#         )
    
#     except Exception as e:
#         return f"❌ Processing error: {str(e)}"

# # Gradio Interface
# with gr.Blocks(theme=gr.themes.Soft()) as app:
#     gr.Markdown("# 🩺 Medical Image Analysis")
    
#     with gr.Row():
#         with gr.Column():
#             image_input = gr.Image(type="pil", label="Upload Scan")
#             context_input = gr.Textbox(
#                 label="Clinical Context (optional)", 
#                 placeholder="Patient symptoms or history..."
#             )
#             analyze_btn = gr.Button("Analyze", variant="primary")
        
#         with gr.Column():
#             report_output = gr.Markdown(label="Analysis Report")
    
#     analyze_btn.click(
#         analyze_medical_image,
#         inputs=[image_input, context_input],
#         outputs=report_output
#     )

# if __name__ == "__main__":
#     app.launch(server_name="0.0.0.0")



# Working Code ✅✅✅✅✅✅..


