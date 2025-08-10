# import logging
# import os
# import sys
# import tempfile
# from pathlib import Path
# import requests
# import gradio as gr
# import matplotlib.pyplot as plt
# from PIL import Image
# import json

# # Import configuration
# try:
#     from .config import get_flask_urls, get_doctors_page_urls, TIMEOUT_SETTINGS
# except ImportError:
#     # Fallback configuration if config file is not available
#     def get_flask_urls():
#         return [
#             "http://127.0.0.1:600/complete_appointment",
#             "http://localhost:600/complete_appointment",
#             "https://your-flask-app-domain.com/complete_appointment",
#             "http://your-flask-app-ip:600/complete_appointment"
#         ]
    
#     def get_doctors_page_urls():
#         return {
#             "local": "http://127.0.0.1:600/doctors",
#             "production": "https://your-flask-app-domain.com/doctors"
#         }
    
#     TIMEOUT_SETTINGS = {"connection_timeout": 5, "request_timeout": 10}

# # Add parent directory to path
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(parent_dir)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
# )
# logger = logging.getLogger(__name__)

# class MediSyncApp:
#     """
#     Main application class for the MediSync multi-modal medical analysis system.
#     """

#     def __init__(self):
#         """Initialize the application and load models."""
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("Initializing MediSync application")
#         self._temp_files = []  # Track temporary files for cleanup
#         self.fusion_model = None
#         self.image_model = None
#         self.text_model = None

#     def __del__(self):
#         """Cleanup temporary files on object destruction."""
#         self.cleanup_temp_files()

#     def cleanup_temp_files(self):
#         """Clean up temporary files."""
#         for temp_file in self._temp_files:
#             try:
#                 if os.path.exists(temp_file):
#                     os.remove(temp_file)
#                     self.logger.debug(f"Cleaned up temporary file: {temp_file}")
#             except Exception as e:
#                 self.logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
#         self._temp_files = []

#     def load_models(self):
#         """
#         Load models if not already loaded.

#         Returns:
#             bool: True if models loaded successfully, False otherwise
#         """
#         if self.fusion_model is not None:
#             return True

#         try:
#             self.logger.info("Loading models...")
#             # For now, we'll create a simple mock implementation
#             # You can replace this with your actual model loading code
#             self.logger.info("Models loaded successfully (mock implementation)")
#             return True
#         except Exception as e:
#             self.logger.error(f"Error loading models: {e}")
#             return False

#     def enhance_image(self, image):
#         """Enhance the uploaded image."""
#         if image is None:
#             return None
        
#         try:
#             # Simple image enhancement (you can replace with actual enhancement logic)
#             enhanced_image = image
#             self.logger.info("Image enhanced successfully")
#             return enhanced_image
#         except Exception as e:
#             self.logger.error(f"Error enhancing image: {e}")
#             return image

#     def analyze_image(self, image):
#         """
#         Analyze a medical image.

#         Args:
#             image: Image file uploaded through Gradio

#         Returns:
#             tuple: (image, image_results_html, plot_as_html)
#         """
#         if image is None:
#             return None, "Please upload an image first.", None

#         if not self.load_models():
#             return image, "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Analyzing image")
            
#             # Mock analysis results (replace with actual model inference)
#             results = {
#                 "primary_finding": "Normal chest X-ray",
#                 "confidence": 0.85,
#                 "has_abnormality": False,
#                 "predictions": [
#                     ("Normal", 0.85),
#                     ("Pneumonia", 0.10),
#                     ("Cardiomegaly", 0.05)
#                 ]
#             }

#             # Create visualization
#             fig = self.plot_image_prediction(
#                 image,
#                 results.get("predictions", []),
#                 f"Primary Finding: {results.get('primary_finding', 'Unknown')}"
#             )

#             # Convert to HTML for display
#             plot_html = self.fig_to_html(fig)
#             plt.close(fig)  # Clean up matplotlib figure

#             # Format results as HTML
#             html_result = self.format_image_results(results)
            
#             return image, html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in image analysis: {e}")
#             return image, f"Error analyzing image: {str(e)}", None

#     def analyze_text(self, text):
#         """
#         Analyze medical report text.

#         Args:
#             text: Medical report text

#         Returns:
#             tuple: (processed_text, text_results_html, plot_as_html)
#         """
#         if not text or text.strip() == "":
#             return "", "Please enter medical report text.", None

#         if not self.load_models():
#             return text, "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Analyzing text")
            
#             # Mock text analysis results (replace with actual model inference)
#             results = {
#                 "entities": [
#                     {"text": "chest X-ray", "type": "PROCEDURE", "confidence": 0.95},
#                     {"text": "55-year-old male", "type": "PATIENT", "confidence": 0.90},
#                     {"text": "cough and fever", "type": "SYMPTOM", "confidence": 0.88}
#                 ],
#                 "sentiment": "neutral",
#                 "key_findings": ["Normal heart size", "Clear lungs", "8mm nodular opacity"]
#             }

#             # Format results as HTML
#             html_result = self.format_text_results(results)
            
#             # Create entity visualization
#             plot_html = self.create_entity_visualization(results["entities"])
            
#             return text, html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in text analysis: {e}")
#             return text, f"Error analyzing text: {str(e)}", None

#     def analyze_multimodal(self, image, text):
#         """
#         Analyze both image and text together.

#         Args:
#             image: Medical image
#             text: Medical report text

#         Returns:
#             tuple: (results_html, plot_as_html)
#         """
#         if image is None and (not text or text.strip() == ""):
#             return "Please provide either an image or text for analysis.", None

#         if not self.load_models():
#             return "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Performing multimodal analysis")
            
#             # Mock multimodal analysis results (replace with actual model inference)
#             results = {
#                 "combined_finding": "Normal chest X-ray with minor findings",
#                 "confidence": 0.92,
#                 "image_contribution": "Normal cardiac silhouette and clear lung fields",
#                 "text_contribution": "Clinical history supports normal findings",
#                 "recommendations": [
#                     "Follow-up CT for the 8mm nodular opacity",
#                     "Monitor for any changes in symptoms"
#                 ]
#             }

#             # Format results as HTML
#             html_result = self.format_multimodal_results(results)
            
#             # Create combined visualization
#             plot_html = self.create_multimodal_visualization(results)
            
#             return html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in multimodal analysis: {e}")
#             return f"Error in multimodal analysis: {str(e)}", None

#     def format_image_results(self, results):
#         """Format image analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #007bff;">X-ray Analysis Results</h2>
#             <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#             <p><strong>Confidence:</strong> {results.get("confidence", 0):.1%}</p>
#             <p><strong>Abnormality Detected:</strong> {"Yes" if results.get("has_abnormality", False) else "No"}</p>
            
#             <h3>Top Predictions:</h3>
#             <ul>
#         """

#         for label, prob in results.get("predictions", [])[:5]:
#             html_result += f"<li>{label}: {prob:.1%}</li>"

#         html_result += "</ul></div>"
#         return html_result

#     def format_text_results(self, results):
#         """Format text analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #28a745;">Text Analysis Results</h2>
#             <p><strong>Sentiment:</strong> {results.get("sentiment", "Unknown").title()}</p>
            
#             <h3>Key Findings:</h3>
#             <ul>
#         """
        
#         for finding in results.get("key_findings", []):
#             html_result += f"<li>{finding}</li>"
        
#         html_result += "</ul>"
        
#         html_result += "<h3>Extracted Entities:</h3><ul>"
#         for entity in results.get("entities", [])[:5]:
#             html_result += f"<li><strong>{entity['text']}</strong> ({entity['type']}) - {entity['confidence']:.1%}</li>"
        
#         html_result += "</ul></div>"
#         return html_result

#     def format_multimodal_results(self, results):
#         """Format multimodal analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #6f42c1;">Multimodal Analysis Results</h2>
#             <p><strong>Combined Finding:</strong> {results.get("combined_finding", "Unknown")}</p>
#             <p><strong>Overall Confidence:</strong> {results.get("confidence", 0):.1%}</p>
            
#             <h3>Image Contribution:</h3>
#             <p>{results.get("image_contribution", "No image analysis available")}</p>
            
#             <h3>Text Contribution:</h3>
#             <p>{results.get("text_contribution", "No text analysis available")}</p>
            
#             <h3>Recommendations:</h3>
#             <ul>
#         """
        
#         for rec in results.get("recommendations", []):
#             html_result += f"<li>{rec}</li>"
        
#         html_result += "</ul></div>"
#         return html_result

#     def plot_image_prediction(self, image, predictions, title):
#         """Create visualization for image predictions."""
#         fig, ax = plt.subplots(figsize=(10, 6))
#         ax.imshow(image)
#         ax.set_title(title, fontsize=14, fontweight='bold')
#         ax.axis('off')
#         return fig

#     def create_entity_visualization(self, entities):
#         """Create visualization for text entities."""
#         if not entities:
#             return "<p>No entities found in text.</p>"
        
#         fig, ax = plt.subplots(figsize=(10, 6))
        
#         entity_types = {}
#         for entity in entities:
#             entity_type = entity['type']
#             if entity_type not in entity_types:
#                 entity_types[entity_type] = 0
#             entity_types[entity_type] += 1
        
#         if entity_types:
#             ax.bar(entity_types.keys(), entity_types.values(), color='skyblue')
#             ax.set_title('Entity Types Found in Text', fontsize=14, fontweight='bold')
#             ax.set_ylabel('Count')
#             plt.xticks(rotation=45)
        
#         return self.fig_to_html(fig)

#     def create_multimodal_visualization(self, results):
#         """Create visualization for multimodal results."""
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
#         # Confidence visualization
#         confidence = results.get("confidence", 0)
#         ax1.pie([confidence, 1-confidence], labels=['Confidence', 'Uncertainty'], 
#                 colors=['lightgreen', 'lightcoral'], autopct='%1.1f%%')
#         ax1.set_title('Analysis Confidence', fontweight='bold')
        
#         # Recommendations count
#         recommendations = results.get("recommendations", [])
#         ax2.bar(['Recommendations'], [len(recommendations)], color='lightblue')
#         ax2.set_title('Number of Recommendations', fontweight='bold')
#         ax2.set_ylabel('Count')
        
#         plt.tight_layout()
#         return self.fig_to_html(fig)

#     def fig_to_html(self, fig):
#         """Convert matplotlib figure to HTML."""
#         import io
#         import base64
        
#         buf = io.BytesIO()
#         fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
#         buf.seek(0)
#         img_str = base64.b64encode(buf.read()).decode()
#         buf.close()
        
#         return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;"/>'

# def complete_appointment(appointment_id):
#     """
#     Complete an appointment by calling the Flask API.
    
#     Args:
#         appointment_id: The appointment ID to complete
        
#     Returns:
#         dict: Response from the API
#     """
#     try:
#         # Get Flask URLs from configuration
#         flask_urls = get_flask_urls()
        
#         payload = {"appointment_id": appointment_id}
        
#         for flask_api_url in flask_urls:
#             try:
#                 logger.info(f"Trying to connect to: {flask_api_url}")
#                 response = requests.post(flask_api_url, json=payload, timeout=TIMEOUT_SETTINGS["connection_timeout"])
                
#                 if response.status_code == 200:
#                     return {"status": "success", "message": "Appointment completed successfully"}
#                 elif response.status_code == 404:
#                     return {"status": "error", "message": "Appointment not found"}
#                 else:
#                     logger.warning(f"Unexpected response from {flask_api_url}: {response.status_code}")
#                     continue
                    
#             except requests.exceptions.ConnectionError:
#                 logger.warning(f"Connection failed to {flask_api_url}")
#                 continue
#             except requests.exceptions.Timeout:
#                 logger.warning(f"Timeout connecting to {flask_api_url}")
#                 continue
#             except Exception as e:
#                 logger.warning(f"Error with {flask_api_url}: {e}")
#                 continue
        
#         # If all URLs fail, return a helpful error message
#         return {
#             "status": "error", 
#             "message": "Cannot connect to Flask app. Please ensure the Flask app is running and accessible."
#         }
            
#     except Exception as e:
#         logger.error(f"Error completing appointment: {e}")
#         return {"status": "error", "message": f"Error: {str(e)}"}

# def create_interface():
#     """Create and launch the Gradio interface."""

#     app = MediSyncApp()

#     # Example medical report for demo
#     example_report = """
#     CHEST X-RAY EXAMINATION
    
#     CLINICAL HISTORY: 55-year-old male with cough and fever.
    
#     FINDINGS: The heart size is at the upper limits of normal. The lungs are clear without focal consolidation, 
#     effusion, or pneumothorax. There is mild prominence of the pulmonary vasculature. No pleural effusion is seen. 
#     There is a small nodular opacity noted in the right lower lobe measuring approximately 8mm, which is suspicious 
#     and warrants further investigation. The mediastinum is unremarkable. The visualized bony structures show no acute abnormalities.
    
#     IMPRESSION:
#     1. Mild cardiomegaly.
#     2. 8mm nodular opacity in the right lower lobe, recommend follow-up CT for further evaluation.
#     3. No acute pulmonary parenchymal abnormality.
    
#     RECOMMENDATIONS: Follow-up chest CT to further characterize the nodular opacity in the right lower lobe.
#     """

#     # Get sample image path if available
#     sample_images_dir = Path(parent_dir) / "data" / "sample"
#     sample_images = list(sample_images_dir.glob("*.png")) + list(
#         sample_images_dir.glob("*.jpg")
#     )

#     sample_image_path = None
#     if sample_images:
#         sample_image_path = str(sample_images[0])

#     # Define interface
#     with gr.Blocks(
#         title="MediSync: Multi-Modal Medical Analysis System", theme=gr.themes.Soft()
#     ) as interface:
#         gr.Markdown("""
#         # MediSync: Multi-Modal Medical Analysis System
        
#         This AI-powered healthcare solution combines X-ray image analysis with patient report text processing 
#         to provide comprehensive medical insights.
        
#         ## How to Use
#         1. Upload a chest X-ray image
#         2. Enter the corresponding medical report text
#         3. Choose the analysis type: image-only, text-only, or multimodal (combined)
#         4. Click "End Consultation" when finished to complete your appointment
#         """)

#         # Add appointment ID input with Python-based population
#         with gr.Row():
#             # Get appointment ID from URL parameters if available
#             import urllib.parse
#             try:
#                 # This will be set by JavaScript, but we can also try to get it server-side
#                 url_params = {}
#                 if hasattr(gr, 'get_current_url'):
#                     current_url = gr.get_current_url()
#                     if current_url:
#                         parsed = urllib.parse.urlparse(current_url)
#                         url_params = urllib.parse.parse_qs(parsed.query)
                
#                 default_appointment_id = url_params.get('appointment_id', [''])[0]
#             except:
#                 default_appointment_id = ""
            
#             appointment_id_input = gr.Textbox(
#                 label="Appointment ID",
#                 placeholder="Enter your appointment ID here...",
#                 info="This will be automatically populated if you came from the doctors page",
#                 value=default_appointment_id
#             )

#         with gr.Tab("Multimodal Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     multi_img_input = gr.Image(label="Upload X-ray Image", type="pil")
#                     multi_img_enhance = gr.Button("Enhance Image")

#                     multi_text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report if sample_image_path is None else None,
#                     )

#                     multi_analyze_btn = gr.Button(
#                         "Analyze Image & Text", variant="primary"
#                     )

#                 with gr.Column():
#                     multi_results = gr.HTML(label="Analysis Results")
#                     multi_plot = gr.HTML(label="Visualization")

#             # Set up examples if sample image exists
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path, example_report]],
#                     inputs=[multi_img_input, multi_text_input],
#                     label="Example X-ray and Report",
#                 )

#         with gr.Tab("Image Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     img_input = gr.Image(label="Upload X-ray Image", type="pil")
#                     img_enhance = gr.Button("Enhance Image")
#                     img_analyze_btn = gr.Button("Analyze Image", variant="primary")

#                 with gr.Column():
#                     img_output = gr.Image(label="Processed Image")
#                     img_results = gr.HTML(label="Analysis Results")
#                     img_plot = gr.HTML(label="Visualization")

#             # Set up example if sample image exists
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path]],
#                     inputs=[img_input],
#                     label="Example X-ray Image",
#                 )

#         with gr.Tab("Text Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report,
#                     )
#                     text_analyze_btn = gr.Button("Analyze Text", variant="primary")

#                 with gr.Column():
#                     text_output = gr.Textbox(label="Processed Text")
#                     text_results = gr.HTML(label="Analysis Results")
#                     text_plot = gr.HTML(label="Entity Visualization")

#             # Set up example
#             gr.Examples(
#                 examples=[[example_report]],
#                 inputs=[text_input],
#                 label="Example Medical Report",
#             )

#         # End Consultation Section
#         with gr.Row():
#             with gr.Column():
#                 end_consultation_btn = gr.Button(
#                     "End Consultation", 
#                     variant="stop", 
#                     size="lg",
#                     elem_classes=["end-consultation-btn"]
#                 )
#                 end_consultation_status = gr.HTML(label="Status")

#         with gr.Tab("About"):
#             gr.Markdown("""
#             ## About MediSync
            
#             MediSync is an AI-powered healthcare solution that uses multi-modal analysis to provide comprehensive insights from medical images and reports.
            
#             ### Key Features
            
#             - **X-ray Image Analysis**: Detects abnormalities in chest X-rays using pre-trained vision models
#             - **Medical Report Processing**: Extracts key information from patient reports using NLP models
#             - **Multi-modal Integration**: Combines insights from both image and text data for more accurate analysis
            
#             ### Models Used
            
#             - **X-ray Analysis**: facebook/deit-base-patch16-224-medical-cxr
#             - **Medical Text Analysis**: medicalai/ClinicalBERT
            
#             ### Important Disclaimer
            
#             This tool is for educational and research purposes only. It is not intended to provide medical advice or replace professional healthcare. Always consult with qualified healthcare providers for medical decisions.
#             """)

#         # Set up event handlers
#         multi_img_enhance.click(
#             app.enhance_image, inputs=multi_img_input, outputs=multi_img_input
#         )
#         multi_analyze_btn.click(
#             app.analyze_multimodal,
#             inputs=[multi_img_input, multi_text_input],
#             outputs=[multi_results, multi_plot],
#         )

#         img_enhance.click(app.enhance_image, inputs=img_input, outputs=img_output)
#         img_analyze_btn.click(
#             app.analyze_image,
#             inputs=img_input,
#             outputs=[img_output, img_results, img_plot],
#         )

#         text_analyze_btn.click(
#             app.analyze_text,
#             inputs=text_input,
#             outputs=[text_output, text_results, text_plot],
#         )

#         # End consultation handler
#         def handle_end_consultation(appointment_id):
#             if not appointment_id or appointment_id.strip() == "":
#                 return "<div style='color: red; padding: 10px; background-color: #ffe6e6; border-radius: 5px;'>Please enter your appointment ID first.</div>"
            
#             # Try to complete the appointment
#             result = complete_appointment(appointment_id.strip())
            
#             if result["status"] == "success":
#                 # Get doctors page URLs from configuration
#                 doctors_urls = get_doctors_page_urls()
                
#                 # Create success message with redirect button
#                 html_response = f"""
#                 <div style='color: green; padding: 15px; background-color: #e6ffe6; border-radius: 5px; margin: 10px 0;'>
#                     <h3>✅ Consultation Completed Successfully!</h3>
#                     <p>{result['message']}</p>
#                     <p>Your appointment has been marked as completed.</p>
#                     <button onclick="window.open('{doctors_urls['local']}', '_blank')" 
#                             style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;">
#                         Return to Doctors Page (Local)
#                     </button>
#                     <button onclick="window.open('{doctors_urls['production']}', '_blank')" 
#                             style="background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; margin-left: 10px;">
#                         Return to Doctors Page (Production)
#                     </button>
#                 </div>
#                 """
#             else:
#                 # Handle connection failure gracefully
#                 if "Cannot connect to Flask app" in result['message']:
#                     # Show a helpful message with manual completion instructions
#                     html_response = f"""
#                     <div style='color: orange; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;'>
#                         <h3>⚠️ Consultation Ready to Complete</h3>
#                         <p>Your consultation analysis is complete! However, we cannot automatically mark your appointment as completed because the Flask app is not accessible from this environment.</p>
#                         <p><strong>Appointment ID:</strong> {appointment_id.strip()}</p>
#                         <p><strong>Next Steps:</strong></p>
#                         <ol>
#                             <li>Copy your appointment ID: <code>{appointment_id.strip()}</code></li>
#                             <li>Return to your Flask app (doctors page)</li>
#                             <li>Manually complete the appointment using the appointment ID</li>
#                         </ol>
#                         <div style="margin-top: 15px;">
#                             <button onclick="window.open('http://127.0.0.1:600/complete_appointment_manual?appointment_id={appointment_id.strip()}', '_blank')" 
#                                     style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Complete Appointment
#                             </button>
#                             <button onclick="window.open('http://127.0.0.1:600/doctors', '_blank')" 
#                                     style="background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Return to Doctors Page
#                             </button>
#                             <button onclick="navigator.clipboard.writeText('{appointment_id.strip()}')" 
#                                     style="background-color: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
#                                 Copy Appointment ID
#                             </button>
#                         </div>
#                     </div>
#                     """
#                 else:
#                     html_response = f"""
#                     <div style='color: red; padding: 15px; background-color: #ffe6e6; border-radius: 5px; margin: 10px 0;'>
#                         <h3>❌ Error Completing Consultation</h3>
#                         <p>{result['message']}</p>
#                         <p>Please try again or contact support if the problem persists.</p>
#                     </div>
#                     """
            
#             return html_response

#         end_consultation_btn.click(
#             handle_end_consultation,
#             inputs=[appointment_id_input],
#             outputs=[end_consultation_status]
#         )

#         # Add custom CSS and JavaScript for better styling and functionality
#         gr.HTML("""
#         <style>
#         .end-consultation-btn {
#             background-color: #dc3545 !important;
#             border-color: #dc3545 !important;
#             color: white !important;
#             font-weight: bold !important;
#         }
#         .end-consultation-btn:hover {
#             background-color: #c82333 !important;
#             border-color: #bd2130 !important;
#         }
#         </style>
        
#         <script>
#         // Function to get URL parameters
#         function getUrlParameter(name) {
#             name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
#             var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
#             var results = regex.exec(location.search);
#             return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
#         }
        
#         // Function to populate appointment ID from URL
#         function populateAppointmentId() {
#             var appointmentId = getUrlParameter('appointment_id');
#             console.log('Found appointment ID:', appointmentId);
            
#             if (appointmentId) {
#                 // Try multiple methods to find and populate the appointment ID input
#                 var success = false;
                
#                 // Method 1: Try by specific element ID
#                 var elementById = document.getElementById('appointment_id_input');
#                 if (elementById) {
#                     elementById.value = appointmentId;
#                     var event = new Event('input', { bubbles: true });
#                     elementById.dispatchEvent(event);
#                     console.log('Set appointment ID by ID to:', appointmentId);
#                     success = true;
#                 }
                
#                 // Method 2: Try by placeholder text
#                 if (!success) {
#                     var selectors = [
#                         'input[placeholder*="appointment ID"]',
#                         'input[placeholder*="appointment_id"]',
#                         'input[placeholder*="Appointment ID"]',
#                         'textarea[placeholder*="appointment ID"]',
#                         'textarea[placeholder*="appointment_id"]',
#                         'textarea[placeholder*="Appointment ID"]'
#                     ];
                    
#                     for (var selector of selectors) {
#                         var elements = document.querySelectorAll(selector);
#                         for (var element of elements) {
#                             console.log('Found element by placeholder:', element);
#                             element.value = appointmentId;
#                             var event = new Event('input', { bubbles: true });
#                             element.dispatchEvent(event);
#                             console.log('Set appointment ID by placeholder to:', appointmentId);
#                             success = true;
#                             break;
#                         }
#                         if (success) break;
#                     }
#                 }
                
#                 // Method 3: Try by label text
#                 if (!success) {
#                     var labels = document.querySelectorAll('label');
#                     for (var label of labels) {
#                         if (label.textContent && label.textContent.toLowerCase().includes('appointment id')) {
#                             var input = label.nextElementSibling;
#                             if (input && (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA')) {
#                                 input.value = appointmentId;
#                                 var event = new Event('input', { bubbles: true });
#                                 input.dispatchEvent(event);
#                                 console.log('Set appointment ID by label to:', appointmentId);
#                                 success = true;
#                                 break;
#                             }
#                         }
#                     }
#                 }
                
#                 // Method 4: Try by Gradio component attributes
#                 if (!success) {
#                     var gradioInputs = document.querySelectorAll('[data-testid="textbox"]');
#                     for (var input of gradioInputs) {
#                         var label = input.closest('.form').querySelector('label');
#                         if (label && label.textContent.toLowerCase().includes('appointment id')) {
#                             input.value = appointmentId;
#                             var event = new Event('input', { bubbles: true });
#                             input.dispatchEvent(event);
#                             console.log('Set appointment ID by Gradio component to:', appointmentId);
#                             success = true;
#                             break;
#                         }
#                     }
#                 }
                
#                 if (!success) {
#                     console.log('Could not find appointment ID input field');
#                     // Log all input elements for debugging
#                     var allInputs = document.querySelectorAll('input, textarea');
#                     console.log('All input elements found:', allInputs.length);
#                     for (var i = 0; i < allInputs.length; i++) {
#                         console.log('Input', i, ':', allInputs[i].placeholder, allInputs[i].id, allInputs[i].className);
#                     }
#                 }
#             } else {
#                 console.log('No appointment ID found in URL');
#             }
#             return success;
#         }
        
#         // Function to wait for Gradio to be ready
#         function waitForGradio() {
#             if (typeof gradio !== 'undefined' && gradio) {
#                 console.log('Gradio detected, waiting for load...');
#                 setTimeout(function() {
#                     populateAppointmentId();
#                     // Also try again after a longer delay
#                     setTimeout(populateAppointmentId, 2000);
#                 }, 1000);
#             } else {
#                 console.log('Gradio not detected, trying direct population...');
#                 populateAppointmentId();
#                 // Try again after a delay
#                 setTimeout(populateAppointmentId, 1000);
#             }
#         }
        
#         // Run when page loads
#         document.addEventListener('DOMContentLoaded', function() {
#             console.log('DOM loaded, attempting to populate appointment ID...');
#             waitForGradio();
#         });
        
#         // Also run when window loads
#         window.addEventListener('load', function() {
#             console.log('Window loaded, attempting to populate appointment ID...');
#             setTimeout(waitForGradio, 500);
#         });
        
#         // Monitor for dynamic content changes
#         var observer = new MutationObserver(function(mutations) {
#             mutations.forEach(function(mutation) {
#                 if (mutation.type === 'childList') {
#                     setTimeout(populateAppointmentId, 100);
#                 }
#             });
#         });
        
#         // Start observing
#         observer.observe(document.body, {
#             childList: true,
#             subtree: true
#         });
#         </script>
#         """)

#     # Run the interface
#     interface.launch()


# if __name__ == "__main__":
#     create_interface() 


# ❌❌❌✖️✖️✖️ test purpose only dont uncomment the code ❌❌❌✖️✖️✖️


import logging
import os
import sys
import tempfile
from pathlib import Path

import gradio as gr
import matplotlib.pyplot as plt
from PIL import Image

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Import our modules
from models.multimodal_fusion import MultimodalFusion
from utils.preprocessing import enhance_xray_image, normalize_report_text
from utils.visualization import (
    plot_image_prediction,
    plot_multimodal_results,
    plot_report_entities,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
)
logger = logging.getLogger(__name__)

# Create temporary directory for sample data if it doesn't exist
os.makedirs(os.path.join(parent_dir, "data", "sample"), exist_ok=True)


# class MediSyncApp:
#     """
#     Main application class for the MediSync multi-modal medical analysis system.
#     """

#     def __init__(self):
#         """Initialize the application and load models."""
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("Initializing MediSync application")

#         # Initialize models with None for lazy loading
#         self.fusion_model = None
#         self.image_model = None
#         self.text_model = None

#     def load_models(self):
#         """
#         Load models if not already loaded.

#         Returns:
#             bool: True if models loaded successfully, False otherwise
#         """
#         try:
#             if self.fusion_model is None:
#                 self.logger.info("Loading models...")
#                 self.fusion_model = MultimodalFusion()
#                 self.image_model = self.fusion_model.image_analyzer
#                 self.text_model = self.fusion_model.text_analyzer
#                 self.logger.info("Models loaded successfully")
#             return True

#         except Exception as e:
#             self.logger.error(f"Error loading models: {e}")
#             return False

#     def analyze_image(self, image):
#         """
#         Analyze a medical image.

#         Args:
#             image: Image file uploaded through Gradio

#         Returns:
#             tuple: (image, image_results_html, plot_as_html)
#         """
#         try:
#             # Ensure models are loaded
#             if not self.load_models() or self.image_model is None:
#                 return image, "Error: Models not loaded properly.", None

#             # Save uploaded image to a temporary file
#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")

#             if isinstance(image, str):
#                 # Copy the file if it's a path
#                 from shutil import copyfile

#                 copyfile(image, temp_path)
#             else:
#                 # Save if it's a Gradio UploadButton image
#                 image.save(temp_path)

#             # Run image analysis
#             self.logger.info(f"Analyzing image: {temp_path}")
#             results = self.image_model.analyze(temp_path)

#             # Create visualization
#             fig = plot_image_prediction(
#                 image,
#                 results.get("predictions", []),
#                 f"Primary Finding: {results.get('primary_finding', 'Unknown')}",
#             )

#             # Convert to HTML for display
#             plot_html = self.fig_to_html(fig)

#             # Format results as HTML
#             html_result = f"""
#             <h2>X-ray Analysis Results</h2>
#             <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#             <p><strong>Confidence:</strong> {results.get("confidence", 0):.1%}</p>
#             <p><strong>Abnormality Detected:</strong> {"Yes" if results.get("has_abnormality", False) else "No"}</p>
            
#             <h3>Top Predictions:</h3>
#             <ul>
#             """

#             # Add top 5 predictions
#             for label, prob in results.get("predictions", [])[:5]:
#                 html_result += f"<li>{label}: {prob:.1%}</li>"

#             html_result += "</ul>"

#             # Add explanation
#             explanation = self.image_model.get_explanation(results)
#             html_result += f"<h3>Analysis Explanation:</h3><p>{explanation}</p>"

#             return image, html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in image analysis: {e}")
#             return image, f"Error analyzing image: {str(e)}", None

#     def analyze_text(self, text):
#         """
#         Analyze a medical report text.

#         Args:
#             text: Report text input through Gradio

#         Returns:
#             tuple: (text, text_results_html, entities_plot_html)
#         """
#         try:
#             # Ensure models are loaded
#             if not self.load_models() or self.text_model is None:
#                 return text, "Error: Models not loaded properly.", None

#             # Check for empty text
#             if not text or len(text.strip()) < 10:
#                 return (
#                     text,
#                     "Error: Please enter a valid medical report text (at least 10 characters).",
#                     None,
#                 )

#             # Normalize text
#             normalized_text = normalize_report_text(text)

#             # Run text analysis
#             self.logger.info("Analyzing medical report text")
#             results = self.text_model.analyze(normalized_text)

#             # Get entities and create visualization
#             entities = results.get("entities", {})
#             fig = plot_report_entities(normalized_text, entities)

#             # Convert to HTML for display
#             entities_plot_html = self.fig_to_html(fig)

#             # Format results as HTML
#             html_result = f"""
#             <h2>Medical Report Analysis Results</h2>
#             <p><strong>Severity Level:</strong> {results.get("severity", {}).get("level", "Unknown")}</p>
#             <p><strong>Severity Score:</strong> {results.get("severity", {}).get("score", 0)}/4</p>
#             <p><strong>Confidence:</strong> {results.get("severity", {}).get("confidence", 0):.1%}</p>
            
#             <h3>Key Findings:</h3>
#             <ul>
#             """

#             # Add findings
#             findings = results.get("findings", [])
#             if findings:
#                 for finding in findings:
#                     html_result += f"<li>{finding}</li>"
#             else:
#                 html_result += "<li>No specific findings detailed.</li>"

#             html_result += "</ul>"

#             # Add entities
#             html_result += "<h3>Extracted Medical Entities:</h3>"

#             for category, items in entities.items():
#                 if items:
#                     html_result += f"<p><strong>{category.capitalize()}:</strong> {', '.join(items)}</p>"

#             # Add follow-up recommendations
#             html_result += "<h3>Follow-up Recommendations:</h3><ul>"
#             followups = results.get("followup_recommendations", [])

#             if followups:
#                 for rec in followups:
#                     html_result += f"<li>{rec}</li>"
#             else:
#                 html_result += "<li>No specific follow-up recommendations.</li>"

#             html_result += "</ul>"

#             return text, html_result, entities_plot_html

#         except Exception as e:
#             self.logger.error(f"Error in text analysis: {e}")
#             return text, f"Error analyzing text: {str(e)}", None

#     def analyze_multimodal(self, image, text):
#         """
#         Perform multimodal analysis of image and text.

#         Args:
#             image: Image file uploaded through Gradio
#             text: Report text input through Gradio

#         Returns:
#             tuple: (results_html, multimodal_plot_html)
#         """
#         try:
#             # Ensure models are loaded
#             if not self.load_models() or self.fusion_model is None:
#                 return "Error: Models not loaded properly.", None

#             # Check for empty inputs
#             if image is None:
#                 return "Error: Please upload an X-ray image for analysis.", None

#             if not text or len(text.strip()) < 10:
#                 return (
#                     "Error: Please enter a valid medical report text (at least 10 characters).",
#                     None,
#                 )

#             # Save uploaded image to a temporary file
#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")

#             if isinstance(image, str):
#                 # Copy the file if it's a path
#                 from shutil import copyfile

#                 copyfile(image, temp_path)
#             else:
#                 # Save if it's a Gradio UploadButton image
#                 image.save(temp_path)

#             # Normalize text
#             normalized_text = normalize_report_text(text)

#             # Run multimodal analysis
#             self.logger.info("Performing multimodal analysis")
#             results = self.fusion_model.analyze(temp_path, normalized_text)

#             # Create visualization
#             fig = plot_multimodal_results(results, image, text)

#             # Convert to HTML for display
#             plot_html = self.fig_to_html(fig)

#             # Generate explanation
#             explanation = self.fusion_model.get_explanation(results)

#             # Format results as HTML
#             html_result = f"""
#             <h2>Multimodal Medical Analysis Results</h2>
            
#             <h3>Overview</h3>
#             <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#             <p><strong>Severity Level:</strong> {results.get("severity", {}).get("level", "Unknown")}</p>
#             <p><strong>Severity Score:</strong> {results.get("severity", {}).get("score", 0)}/4</p>
#             <p><strong>Agreement Score:</strong> {results.get("agreement_score", 0):.0%}</p>
            
#             <h3>Detailed Findings</h3>
#             <ul>
#             """

#             # Add findings
#             findings = results.get("findings", [])
#             if findings:
#                 for finding in findings:
#                     html_result += f"<li>{finding}</li>"
#             else:
#                 html_result += "<li>No specific findings detailed.</li>"

#             html_result += "</ul>"

#             # Add follow-up recommendations
#             html_result += "<h3>Recommended Follow-up</h3><ul>"
#             followups = results.get("followup_recommendations", [])

#             if followups:
#                 for rec in followups:
#                     html_result += f"<li>{rec}</li>"
#             else:
#                 html_result += (
#                     "<li>No specific follow-up recommendations provided.</li>"
#                 )

#             html_result += "</ul>"

#             # Add confidence note
#             confidence = results.get("severity", {}).get("confidence", 0)
#             html_result += f"""
#             <p><em>Note: This analysis has a confidence level of {confidence:.0%}. 
#             Please consult with healthcare professionals for official diagnosis.</em></p>
#             """

#             return html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in multimodal analysis: {e}")
#             return f"Error in multimodal analysis: {str(e)}", None

#     def enhance_image(self, image):
#         """
#         Enhance X-ray image contrast.

#         Args:
#             image: Image file uploaded through Gradio

#         Returns:
#             PIL.Image: Enhanced image
#         """
#         try:
#             if image is None:
#                 return None

#             # Save uploaded image to a temporary file
#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")

#             if isinstance(image, str):
#                 # Copy the file if it's a path
#                 from shutil import copyfile

#                 copyfile(image, temp_path)
#             else:
#                 # Save if it's a Gradio UploadButton image
#                 image.save(temp_path)

#             # Enhance image
#             self.logger.info(f"Enhancing image: {temp_path}")
#             output_path = os.path.join(temp_dir, "enhanced.png")
#             enhance_xray_image(temp_path, output_path)

#             # Load enhanced image
#             enhanced = Image.open(output_path)
#             return enhanced

#         except Exception as e:
#             self.logger.error(f"Error enhancing image: {e}")
#             return image  # Return original image on error

#     def fig_to_html(self, fig):
#         """Convert matplotlib figure to HTML for display in Gradio."""
#         try:
#             import base64
#             import io

#             buf = io.BytesIO()
#             fig.savefig(buf, format="png", bbox_inches="tight")
#             buf.seek(0)
#             img_str = base64.b64encode(buf.read()).decode("utf-8")
#             plt.close(fig)

#             return f'<img src="data:image/png;base64,{img_str}" alt="Analysis Plot">'

#         except Exception as e:
#             self.logger.error(f"Error converting figure to HTML: {e}")
#             return "<p>Error displaying visualization.</p>"

# OLD UI code 
# import logging
# import os
# import sys
# import tempfile
# from pathlib import Path
# import requests
# import gradio as gr
# import matplotlib.pyplot as plt
# from PIL import Image
# import json

# # Import configuration
# try:
#     from .config import get_flask_urls, get_doctors_page_urls, TIMEOUT_SETTINGS
# except ImportError:
#     # Fallback configuration if config file is not available
#     def get_flask_urls():
#         return [
#             "http://127.0.0.1:600/complete_appointment",
#             "http://localhost:600/complete_appointment",
#             "https://your-flask-app-domain.com/complete_appointment",
#             "http://your-flask-app-ip:600/complete_appointment"
#         ]
    
#     def get_doctors_page_urls():
#         return {
#             "local": "http://127.0.0.1:600/doctors",
#             "production": "https://your-flask-app-domain.com/doctors"
#         }
    
#     TIMEOUT_SETTINGS = {"connection_timeout": 5, "request_timeout": 10}

# # Add parent directory to path
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(parent_dir)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
# )
# logger = logging.getLogger(__name__)

# class MediSyncApp:
#     """
#     Main application class for the MediSync multi-modal medical analysis system.
#     """

#     def __init__(self):
#         """Initialize the application and load models."""
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("Initializing MediSync application")
#         self._temp_files = []  # Track temporary files for cleanup
#         self.fusion_model = None
#         self.image_model = None
#         self.text_model = None

#     def __del__(self):
#         """Cleanup temporary files on object destruction."""
#         self.cleanup_temp_files()

#     def cleanup_temp_files(self):
#         """Clean up temporary files."""
#         for temp_file in self._temp_files:
#             try:
#                 if os.path.exists(temp_file):
#                     os.remove(temp_file)
#                     self.logger.debug(f"Cleaned up temporary file: {temp_file}")
#             except Exception as e:
#                 self.logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
#         self._temp_files = []

#     def load_models(self):
#         """
#         Load models if not already loaded.

#         Returns:
#             bool: True if models loaded successfully, False otherwise
#         """
#         if self.fusion_model is not None:
#             return True

#         try:
#             self.logger.info("Loading models...")
#             # For now, we'll create a simple mock implementation
#             # You can replace this with your actual model loading code
#             self.logger.info("Models loaded successfully (mock implementation)")
#             return True
#         except Exception as e:
#             self.logger.error(f"Error loading models: {e}")
#             return False

#     def enhance_image(self, image):
#         """Enhance the uploaded image."""
#         if image is None:
#             return None
        
#         try:
#             # Simple image enhancement (you can replace with actual enhancement logic)
#             enhanced_image = image
#             self.logger.info("Image enhanced successfully")
#             return enhanced_image
#         except Exception as e:
#             self.logger.error(f"Error enhancing image: {e}")
#             return image

#     def analyze_image(self, image):
#         """
#         Analyze a medical image.

#         Args:
#             image: Image file uploaded through Gradio

#         Returns:
#             tuple: (image, image_results_html, plot_as_html)
#         """
#         if image is None:
#             return None, "Please upload an image first.", None

#         if not self.load_models():
#             return image, "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Analyzing image")
            
#             # Mock analysis results (replace with actual model inference)
#             results = {
#                 "primary_finding": "Normal chest X-ray",
#                 "confidence": 0.85,
#                 "has_abnormality": False,
#                 "predictions": [
#                     ("Normal", 0.85),
#                     ("Pneumonia", 0.10),
#                     ("Cardiomegaly", 0.05)
#                 ]
#             }

#             # Create visualization
#             fig = self.plot_image_prediction(
#                 image,
#                 results.get("predictions", []),
#                 f"Primary Finding: {results.get('primary_finding', 'Unknown')}"
#             )

#             # Convert to HTML for display
#             plot_html = self.fig_to_html(fig)
#             plt.close(fig)  # Clean up matplotlib figure

#             # Format results as HTML
#             html_result = self.format_image_results(results)
            
#             return image, html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in image analysis: {e}")
#             return image, f"Error analyzing image: {str(e)}", None

#     def analyze_text(self, text):
#         """
#         Analyze medical report text.

#         Args:
#             text: Medical report text

#         Returns:
#             tuple: (processed_text, text_results_html, plot_as_html)
#         """
#         if not text or text.strip() == "":
#             return "", "Please enter medical report text.", None

#         if not self.load_models():
#             return text, "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Analyzing text")
            
#             # Mock text analysis results (replace with actual model inference)
#             results = {
#                 "entities": [
#                     {"text": "chest X-ray", "type": "PROCEDURE", "confidence": 0.95},
#                     {"text": "55-year-old male", "type": "PATIENT", "confidence": 0.90},
#                     {"text": "cough and fever", "type": "SYMPTOM", "confidence": 0.88}
#                 ],
#                 "sentiment": "neutral",
#                 "key_findings": ["Normal heart size", "Clear lungs", "8mm nodular opacity"]
#             }

#             # Format results as HTML
#             html_result = self.format_text_results(results)
            
#             # Create entity visualization
#             plot_html = self.create_entity_visualization(results["entities"])
            
#             return text, html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in text analysis: {e}")
#             return text, f"Error analyzing text: {str(e)}", None

#     def analyze_multimodal(self, image, text):
#         """
#         Analyze both image and text together.

#         Args:
#             image: Medical image
#             text: Medical report text

#         Returns:
#             tuple: (results_html, plot_as_html)
#         """
#         if image is None and (not text or text.strip() == ""):
#             return "Please provide either an image or text for analysis.", None

#         if not self.load_models():
#             return "Error: Models not loaded properly.", None

#         try:
#             self.logger.info("Performing multimodal analysis")
            
#             # Mock multimodal analysis results (replace with actual model inference)
#             results = {
#                 "combined_finding": "Normal chest X-ray with minor findings",
#                 "confidence": 0.92,
#                 "image_contribution": "Normal cardiac silhouette and clear lung fields",
#                 "text_contribution": "Clinical history supports normal findings",
#                 "recommendations": [
#                     "Follow-up CT for the 8mm nodular opacity",
#                     "Monitor for any changes in symptoms"
#                 ]
#             }

#             # Format results as HTML
#             html_result = self.format_multimodal_results(results)
            
#             # Create combined visualization
#             plot_html = self.create_multimodal_visualization(results)
            
#             return html_result, plot_html

#         except Exception as e:
#             self.logger.error(f"Error in multimodal analysis: {e}")
#             return f"Error in multimodal analysis: {str(e)}", None

#     def format_image_results(self, results):
#         """Format image analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #007bff;">X-ray Analysis Results</h2>
#             <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#             <p><strong>Confidence:</strong> {results.get("confidence", 0):.1%}</p>
#             <p><strong>Abnormality Detected:</strong> {"Yes" if results.get("has_abnormality", False) else "No"}</p>
            
#             <h3>Top Predictions:</h3>
#             <ul>
#         """

#         for label, prob in results.get("predictions", [])[:5]:
#             html_result += f"<li>{label}: {prob:.1%}</li>"

#         html_result += "</ul></div>"
#         return html_result

#     def format_text_results(self, results):
#         """Format text analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #28a745;">Text Analysis Results</h2>
#             <p><strong>Sentiment:</strong> {results.get("sentiment", "Unknown").title()}</p>
            
#             <h3>Key Findings:</h3>
#             <ul>
#         """
        
#         for finding in results.get("key_findings", []):
#             html_result += f"<li>{finding}</li>"
        
#         html_result += "</ul>"
        
#         html_result += "<h3>Extracted Entities:</h3><ul>"
#         for entity in results.get("entities", [])[:5]:
#             html_result += f"<li><strong>{entity['text']}</strong> ({entity['type']}) - {entity['confidence']:.1%}</li>"
        
#         html_result += "</ul></div>"
#         return html_result

#     def format_multimodal_results(self, results):
#         """Format multimodal analysis results as HTML."""
#         html_result = f"""
#         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h2 style="color: #6f42c1;">Multimodal Analysis Results</h2>
#             <p><strong>Combined Finding:</strong> {results.get("combined_finding", "Unknown")}</p>
#             <p><strong>Overall Confidence:</strong> {results.get("confidence", 0):.1%}</p>
            
#             <h3>Image Contribution:</h3>
#             <p>{results.get("image_contribution", "No image analysis available")}</p>
            
#             <h3>Text Contribution:</h3>
#             <p>{results.get("text_contribution", "No text analysis available")}</p>
            
#             <h3>Recommendations:</h3>
#             <ul>
#         """
        
#         for rec in results.get("recommendations", []):
#             html_result += f"<li>{rec}</li>"
        
#         html_result += "</ul></div>"
#         return html_result

#     def plot_image_prediction(self, image, predictions, title):
#         """Create visualization for image predictions."""
#         fig, ax = plt.subplots(figsize=(10, 6))
#         ax.imshow(image)
#         ax.set_title(title, fontsize=14, fontweight='bold')
#         ax.axis('off')
#         return fig

#     def create_entity_visualization(self, entities):
#         """Create visualization for text entities."""
#         if not entities:
#             return "<p>No entities found in text.</p>"
        
#         fig, ax = plt.subplots(figsize=(10, 6))
        
#         entity_types = {}
#         for entity in entities:
#             entity_type = entity['type']
#             if entity_type not in entity_types:
#                 entity_types[entity_type] = 0
#             entity_types[entity_type] += 1
        
#         if entity_types:
#             ax.bar(entity_types.keys(), entity_types.values(), color='skyblue')
#             ax.set_title('Entity Types Found in Text', fontsize=14, fontweight='bold')
#             ax.set_ylabel('Count')
#             plt.xticks(rotation=45)
        
#         return self.fig_to_html(fig)

#     def create_multimodal_visualization(self, results):
#         """Create visualization for multimodal results."""
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
#         # Confidence visualization
#         confidence = results.get("confidence", 0)
#         ax1.pie([confidence, 1-confidence], labels=['Confidence', 'Uncertainty'], 
#                 colors=['lightgreen', 'lightcoral'], autopct='%1.1f%%')
#         ax1.set_title('Analysis Confidence', fontweight='bold')
        
#         # Recommendations count
#         recommendations = results.get("recommendations", [])
#         ax2.bar(['Recommendations'], [len(recommendations)], color='lightblue')
#         ax2.set_title('Number of Recommendations', fontweight='bold')
#         ax2.set_ylabel('Count')
        
#         plt.tight_layout()
#         return self.fig_to_html(fig)

#     def fig_to_html(self, fig):
#         """Convert matplotlib figure to HTML."""
#         import io
#         import base64
        
#         buf = io.BytesIO()
#         fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
#         buf.seek(0)
#         img_str = base64.b64encode(buf.read()).decode()
#         buf.close()
        
#         return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;"/>'

# def complete_appointment(appointment_id):
#     """
#     Complete an appointment by calling the Flask API.
    
#     Args:
#         appointment_id: The appointment ID to complete
        
#     Returns:
#         dict: Response from the API
#     """
#     try:
#         # Get Flask URLs from configuration
#         flask_urls = get_flask_urls()
        
#         payload = {"appointment_id": appointment_id}
        
#         for flask_api_url in flask_urls:
#             try:
#                 logger.info(f"Trying to connect to: {flask_api_url}")
#                 response = requests.post(flask_api_url, json=payload, timeout=TIMEOUT_SETTINGS["connection_timeout"])
                
#                 if response.status_code == 200:
#                     return {"status": "success", "message": "Appointment completed successfully"}
#                 elif response.status_code == 404:
#                     return {"status": "error", "message": "Appointment not found"}
#                 else:
#                     logger.warning(f"Unexpected response from {flask_api_url}: {response.status_code}")
#                     continue
                    
#             except requests.exceptions.ConnectionError:
#                 logger.warning(f"Connection failed to {flask_api_url}")
#                 continue
#             except requests.exceptions.Timeout:
#                 logger.warning(f"Timeout connecting to {flask_api_url}")
#                 continue
#             except Exception as e:
#                 logger.warning(f"Error with {flask_api_url}: {e}")
#                 continue
        
#         # If all URLs fail, return a helpful error message
#         return {
#             "status": "error", 
#             "message": "Cannot connect to Flask app. Please ensure the Flask app is running and accessible."
#         }
            
#     except Exception as e:
#         logger.error(f"Error completing appointment: {e}")
#         return {"status": "error", "message": f"Error: {str(e)}"}

# def create_interface():
#     """Create and launch the Gradio interface."""

#     app = MediSyncApp()

#     # Example medical report for demo
#     example_report = """
#     CHEST X-RAY EXAMINATION
    
#     CLINICAL HISTORY: 55-year-old male with cough and fever.
    
#     FINDINGS: The heart size is at the upper limits of normal. The lungs are clear without focal consolidation, 
#     effusion, or pneumothorax. There is mild prominence of the pulmonary vasculature. No pleural effusion is seen. 
#     There is a small nodular opacity noted in the right lower lobe measuring approximately 8mm, which is suspicious 
#     and warrants further investigation. The mediastinum is unremarkable. The visualized bony structures show no acute abnormalities.
    
#     IMPRESSION:
#     1. Mild cardiomegaly.
#     2. 8mm nodular opacity in the right lower lobe, recommend follow-up CT for further evaluation.
#     3. No acute pulmonary parenchymal abnormality.
    
#     RECOMMENDATIONS: Follow-up chest CT to further characterize the nodular opacity in the right lower lobe.
#     """

#     # Get sample image path if available
#     sample_images_dir = Path(parent_dir) / "data" / "sample"
#     sample_images = list(sample_images_dir.glob("*.png")) + list(
#         sample_images_dir.glob("*.jpg")
#     )

#     sample_image_path = None
#     if sample_images:
#         sample_image_path = str(sample_images[0])

#     # Define interface
#     with gr.Blocks(
#         title="MediSync: Multi-Modal Medical Analysis System", theme=gr.themes.Soft()
#     ) as interface:
#         gr.Markdown("""
#         # MediSync: Multi-Modal Medical Analysis System
        
#         This AI-powered healthcare solution combines X-ray image analysis with patient report text processing 
#         to provide comprehensive medical insights.
        
#         ## How to Use
#         1. Upload a chest X-ray image
#         2. Enter the corresponding medical report text
#         3. Choose the analysis type: image-only, text-only, or multimodal (combined)
#         4. Click "End Consultation" when finished to complete your appointment
#         """)

#         # Add appointment ID input with Python-based population
#         with gr.Row():
#             # Get appointment ID from URL parameters if available
#             import urllib.parse
#             try:
#                 # This will be set by JavaScript, but we can also try to get it server-side
#                 url_params = {}
#                 if hasattr(gr, 'get_current_url'):
#                     current_url = gr.get_current_url()
#                     if current_url:
#                         parsed = urllib.parse.urlparse(current_url)
#                         url_params = urllib.parse.parse_qs(parsed.query)
                
#                 default_appointment_id = url_params.get('appointment_id', [''])[0]
#             except:
#                 default_appointment_id = ""
            
#             appointment_id_input = gr.Textbox(
#                 label="Appointment ID",
#                 placeholder="Enter your appointment ID here...",
#                 info="This will be automatically populated if you came from the doctors page",
#                 value=default_appointment_id
#             )

#         with gr.Tab("Multimodal Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     multi_img_input = gr.Image(label="Upload X-ray Image", type="pil")
#                     multi_img_enhance = gr.Button("Enhance Image")

#                     multi_text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report if sample_image_path is None else None,
#                     )

#                     multi_analyze_btn = gr.Button(
#                         "Analyze Image & Text", variant="primary"
#                     )

#                 with gr.Column():
#                     multi_results = gr.HTML(label="Analysis Results")
#                     multi_plot = gr.HTML(label="Visualization")

#             # Set up examples if sample image exists
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path, example_report]],
#                     inputs=[multi_img_input, multi_text_input],
#                     label="Example X-ray and Report",
#                 )

#         with gr.Tab("Image Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     img_input = gr.Image(label="Upload X-ray Image", type="pil")
#                     img_enhance = gr.Button("Enhance Image")
#                     img_analyze_btn = gr.Button("Analyze Image", variant="primary")

#                 with gr.Column():
#                     img_output = gr.Image(label="Processed Image")
#                     img_results = gr.HTML(label="Analysis Results")
#                     img_plot = gr.HTML(label="Visualization")

#             # Set up example if sample image exists
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path]],
#                     inputs=[img_input],
#                     label="Example X-ray Image",
#                 )

#         with gr.Tab("Text Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report,
#                     )
#                     text_analyze_btn = gr.Button("Analyze Text", variant="primary")

#                 with gr.Column():
#                     text_output = gr.Textbox(label="Processed Text")
#                     text_results = gr.HTML(label="Analysis Results")
#                     text_plot = gr.HTML(label="Entity Visualization")

#             # Set up example
#             gr.Examples(
#                 examples=[[example_report]],
#                 inputs=[text_input],
#                 label="Example Medical Report",
#             )

#         # End Consultation Section
#         with gr.Row():
#             with gr.Column():
#                 end_consultation_btn = gr.Button(
#                     "End Consultation", 
#                     variant="stop", 
#                     size="lg",
#                     elem_classes=["end-consultation-btn"]
#                 )
#                 end_consultation_status = gr.HTML(label="Status")

#         with gr.Tab("About"):
#             gr.Markdown("""
#             ## About MediSync
            
#             MediSync is an AI-powered healthcare solution that uses multi-modal analysis to provide comprehensive insights from medical images and reports.
            
#             ### Key Features
            
#             - **X-ray Image Analysis**: Detects abnormalities in chest X-rays using pre-trained vision models
#             - **Medical Report Processing**: Extracts key information from patient reports using NLP models
#             - **Multi-modal Integration**: Combines insights from both image and text data for more accurate analysis
            
#             ### Models Used
            
#             - **X-ray Analysis**: facebook/deit-base-patch16-224-medical-cxr
#             - **Medical Text Analysis**: medicalai/ClinicalBERT
            
#             ### Important Disclaimer
            
#             This tool is for educational and research purposes only. It is not intended to provide medical advice or replace professional healthcare. Always consult with qualified healthcare providers for medical decisions.
#             """)

#         # Set up event handlers
#         multi_img_enhance.click(
#             app.enhance_image, inputs=multi_img_input, outputs=multi_img_input
#         )
#         multi_analyze_btn.click(
#             app.analyze_multimodal,
#             inputs=[multi_img_input, multi_text_input],
#             outputs=[multi_results, multi_plot],
#         )

#         img_enhance.click(app.enhance_image, inputs=img_input, outputs=img_output)
#         img_analyze_btn.click(
#             app.analyze_image,
#             inputs=img_input,
#             outputs=[img_output, img_results, img_plot],
#         )

#         text_analyze_btn.click(
#             app.analyze_text,
#             inputs=text_input,
#             outputs=[text_output, text_results, text_plot],
#         )

#         # End consultation handler
#         def handle_end_consultation(appointment_id):
#             if not appointment_id or appointment_id.strip() == "":
#                 return "<div style='color: red; padding: 10px; background-color: #ffe6e6; border-radius: 5px;'>Please enter your appointment ID first.</div>"
            
#             # Try to complete the appointment
#             result = complete_appointment(appointment_id.strip())
            
#             if result["status"] == "success":
#                 # Get doctors page URLs from configuration
#                 doctors_urls = get_doctors_page_urls()
                
#                 # Create success message with redirect button
#                 html_response = f"""
#                 <div style='color: green; padding: 15px; background-color: #e6ffe6; border-radius: 5px; margin: 10px 0;'>
#                     <h3>✅ Consultation Completed Successfully!</h3>
#                     <p>{result['message']}</p>
#                     <p>Your appointment has been marked as completed.</p>
#                     <button onclick="window.open('{doctors_urls['local']}', '_blank')" 
#                             style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;">
#                         Return to Doctors Page (Local)
#                     </button>
#                     <button onclick="window.open('{doctors_urls['production']}', '_blank')" 
#                             style="background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; margin-left: 10px;">
#                         Return to Doctors Page (Production)
#                     </button>
#                 </div>
#                 """
#             else:
#                 # Handle connection failure gracefully
#                 if "Cannot connect to Flask app" in result['message']:
#                     # Show a helpful message with manual completion instructions
#                     html_response = f"""
#                     <div style='color: orange; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;'>
#                         <h3>⚠️ Consultation Ready to Complete</h3>
#                         <p>Your consultation analysis is complete! However, we cannot automatically mark your appointment as completed because the Flask app is not accessible from this environment.</p>
#                         <p><strong>Appointment ID:</strong> {appointment_id.strip()}</p>
#                         <p><strong>Next Steps:</strong></p>
#                         <ol>
#                             <li>Copy your appointment ID: <code>{appointment_id.strip()}</code></li>
#                             <li>Return to your Flask app (doctors page)</li>
#                             <li>Manually complete the appointment using the appointment ID</li>
#                         </ol>
#                         <div style="margin-top: 15px;">
#                             <button onclick="window.open('http://127.0.0.1:600/complete_appointment_manual?appointment_id={appointment_id.strip()}', '_blank')" 
#                                     style="background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Complete Appointment
#                             </button>
#                             <button onclick="window.open('http://127.0.0.1:600/doctors', '_blank')" 
#                                     style="background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Return to Doctors Page
#                             </button>
#                             <button onclick="navigator.clipboard.writeText('{appointment_id.strip()}')" 
#                                     style="background-color: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
#                                 Copy Appointment ID
#                             </button>
#                         </div>
#                     </div>
#                     """
#                 else:
#                     html_response = f"""
#                     <div style='color: red; padding: 15px; background-color: #ffe6e6; border-radius: 5px; margin: 10px 0;'>
#                         <h3>❌ Error Completing Consultation</h3>
#                         <p>{result['message']}</p>
#                         <p>Please try again or contact support if the problem persists.</p>
#                     </div>
#                     """
            
#             return html_response

#         end_consultation_btn.click(
#             handle_end_consultation,
#             inputs=[appointment_id_input],
#             outputs=[end_consultation_status]
#         )

#         # Add custom CSS and JavaScript for better styling and functionality
#         gr.HTML("""
#         <style>
#         .end-consultation-btn {
#             background-color: #dc3545 !important;
#             border-color: #dc3545 !important;
#             color: white !important;
#             font-weight: bold !important;
#         }
#         .end-consultation-btn:hover {
#             background-color: #c82333 !important;
#             border-color: #bd2130 !important;
#         }
#         </style>
        
#         <script>
#         // Function to get URL parameters
#         function getUrlParameter(name) {
#             name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
#             var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
#             var results = regex.exec(location.search);
#             return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
#         }
        
#         // Function to populate appointment ID from URL
#         function populateAppointmentId() {
#             var appointmentId = getUrlParameter('appointment_id');
#             console.log('Found appointment ID:', appointmentId);
            
#             if (appointmentId) {
#                 // Try multiple methods to find and populate the appointment ID input
#                 var success = false;
                
#                 // Method 1: Try by specific element ID
#                 var elementById = document.getElementById('appointment_id_input');
#                 if (elementById) {
#                     elementById.value = appointmentId;
#                     var event = new Event('input', { bubbles: true });
#                     elementById.dispatchEvent(event);
#                     console.log('Set appointment ID by ID to:', appointmentId);
#                     success = true;
#                 }
                
#                 // Method 2: Try by placeholder text
#                 if (!success) {
#                     var selectors = [
#                         'input[placeholder*="appointment ID"]',
#                         'input[placeholder*="appointment_id"]',
#                         'input[placeholder*="Appointment ID"]',
#                         'textarea[placeholder*="appointment ID"]',
#                         'textarea[placeholder*="appointment_id"]',
#                         'textarea[placeholder*="Appointment ID"]'
#                     ];
                    
#                     for (var selector of selectors) {
#                         var elements = document.querySelectorAll(selector);
#                         for (var element of elements) {
#                             console.log('Found element by placeholder:', element);
#                             element.value = appointmentId;
#                             var event = new Event('input', { bubbles: true });
#                             element.dispatchEvent(event);
#                             console.log('Set appointment ID by placeholder to:', appointmentId);
#                             success = true;
#                             break;
#                         }
#                         if (success) break;
#                     }
#                 }
                
#                 // Method 3: Try by label text
#                 if (!success) {
#                     var labels = document.querySelectorAll('label');
#                     for (var label of labels) {
#                         if (label.textContent && label.textContent.toLowerCase().includes('appointment id')) {
#                             var input = label.nextElementSibling;
#                             if (input && (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA')) {
#                                 input.value = appointmentId;
#                                 var event = new Event('input', { bubbles: true });
#                                 input.dispatchEvent(event);
#                                 console.log('Set appointment ID by label to:', appointmentId);
#                                 success = true;
#                                 break;
#                             }
#                         }
#                     }
#                 }
                
#                 // Method 4: Try by Gradio component attributes
#                 if (!success) {
#                     var gradioInputs = document.querySelectorAll('[data-testid="textbox"]');
#                     for (var input of gradioInputs) {
#                         var label = input.closest('.form').querySelector('label');
#                         if (label && label.textContent.toLowerCase().includes('appointment id')) {
#                             input.value = appointmentId;
#                             var event = new Event('input', { bubbles: true });
#                             input.dispatchEvent(event);
#                             console.log('Set appointment ID by Gradio component to:', appointmentId);
#                             success = true;
#                             break;
#                         }
#                     }
#                 }
                
#                 if (!success) {
#                     console.log('Could not find appointment ID input field');
#                     // Log all input elements for debugging
#                     var allInputs = document.querySelectorAll('input, textarea');
#                     console.log('All input elements found:', allInputs.length);
#                     for (var i = 0; i < allInputs.length; i++) {
#                         console.log('Input', i, ':', allInputs[i].placeholder, allInputs[i].id, allInputs[i].className);
#                     }
#                 }
#             } else {
#                 console.log('No appointment ID found in URL');
#             }
#             return success;
#         }
        
#         // Function to wait for Gradio to be ready
#         function waitForGradio() {
#             if (typeof gradio !== 'undefined' && gradio) {
#                 console.log('Gradio detected, waiting for load...');
#                 setTimeout(function() {
#                     populateAppointmentId();
#                     // Also try again after a longer delay
#                     setTimeout(populateAppointmentId, 2000);
#                 }, 1000);
#             } else {
#                 console.log('Gradio not detected, trying direct population...');
#                 populateAppointmentId();
#                 // Try again after a delay
#                 setTimeout(populateAppointmentId, 1000);
#             }
#         }
        
#         // Run when page loads
#         document.addEventListener('DOMContentLoaded', function() {
#             console.log('DOM loaded, attempting to populate appointment ID...');
#             waitForGradio();
#         });
        
#         // Also run when window loads
#         window.addEventListener('load', function() {
#             console.log('Window loaded, attempting to populate appointment ID...');
#             setTimeout(waitForGradio, 500);
#         });
        
#         // Monitor for dynamic content changes
#         var observer = new MutationObserver(function(mutations) {
#             mutations.forEach(function(mutation) {
#                 if (mutation.type === 'childList') {
#                     setTimeout(populateAppointmentId, 100);
#                 }
#             });
#         });
        
#         // Start observing
#         observer.observe(document.body, {
#             childList: true,
#             subtree: true
#         });
#         </script>
#         """)

#     # Run the interface
#     interface.launch()


# if __name__ == "__main__":
#     create_interface() 