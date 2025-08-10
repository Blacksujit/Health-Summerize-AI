# import logging
# import os
# import sys
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

# parent_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(parent_dir)

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
# )
# logger = logging.getLogger(__name__)

# class MediSyncApp:
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("Initializing MediSync application")
#         self._temp_files = []
#         self.fusion_model = None
#         self.image_model = None
#         self.text_model = None

#     def __del__(self):
#         self.cleanup_temp_files()

#     def cleanup_temp_files(self):
#         for temp_file in self._temp_files:
#             try:
#                 if os.path.exists(temp_file):
#                     os.remove(temp_file)
#                     self.logger.debug(f"Cleaned up temporary file: {temp_file}")
#             except Exception as e:
#                 self.logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
#         self._temp_files = []

#     def load_models(self):
#         if self.fusion_model is not None:
#             return True
#         try:
#             self.logger.info("Loading models...")
#             self.logger.info("Models loaded successfully (mock implementation)")
#             return True
#         except Exception as e:
#             self.logger.error(f"Error loading models: {e}")
#             return False

#     def enhance_image(self, image):
#         if image is None:
#             return None
#         try:
#             enhanced_image = image
#             self.logger.info("Image enhanced successfully")
#             return enhanced_image
#         except Exception as e:
#             self.logger.error(f"Error enhancing image: {e}")
#             return image

#     def analyze_image(self, image):
#         if image is None:
#             return None, "Please upload an image first.", None
#         if not self.load_models():
#             return image, "Error: Models not loaded properly.", None
#         try:
#             self.logger.info("Analyzing image")
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
#             fig = self.plot_image_prediction(
#                 image,
#                 results.get("predictions", []),
#                 f"Primary Finding: {results.get('primary_finding', 'Unknown')}"
#             )
#             plot_html = self.fig_to_html(fig)
#             plt.close(fig)
#             html_result = self.format_image_results(results)
#             return image, html_result, plot_html
#         except Exception as e:
#             self.logger.error(f"Error in image analysis: {e}")
#             return image, f"Error analyzing image: {str(e)}", None

#     def analyze_text(self, text):
#         if not text or text.strip() == "":
#             return "", "Please enter medical report text.", None
#         if not self.load_models():
#             return text, "Error: Models not loaded properly.", None
#         try:
#             self.logger.info("Analyzing text")
#             results = {
#                 "entities": [
#                     {"text": "chest X-ray", "type": "PROCEDURE", "confidence": 0.95},
#                     {"text": "55-year-old male", "type": "PATIENT", "confidence": 0.90},
#                     {"text": "cough and fever", "type": "SYMPTOM", "confidence": 0.88}
#                 ],
#                 "sentiment": "neutral",
#                 "key_findings": ["Normal heart size", "Clear lungs", "8mm nodular opacity"]
#             }
#             html_result = self.format_text_results(results)
#             plot_html = self.create_entity_visualization(results["entities"])
#             return text, html_result, plot_html
#         except Exception as e:
#             self.logger.error(f"Error in text analysis: {e}")
#             return text, f"Error analyzing text: {str(e)}", None

#     def analyze_multimodal(self, image, text):
#         if image is None and (not text or text.strip() == ""):
#             return "Please provide either an image or text for analysis.", None
#         if not self.load_models():
#             return "Error: Models not loaded properly.", None
#         try:
#             self.logger.info("Performing multimodal analysis")
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
#             html_result = self.format_multimodal_results(results)
#             plot_html = self.create_multimodal_visualization(results)
#             return html_result, plot_html
#         except Exception as e:
#             self.logger.error(f"Error in multimodal analysis: {e}")
#             return f"Error in multimodal analysis: {str(e)}", None

#     def format_image_results(self, results):
#         html_result = f"""
#         <div class="medisync-card medisync-card-bg">
#             <h2 class="medisync-title medisync-blue">X-ray Analysis Results</h2>
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
#         html_result = f"""
#         <div class="medisync-card medisync-card-bg">
#             <h2 class="medisync-title medisync-green">Text Analysis Results</h2>
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
#         html_result = f"""
#         <div class="medisync-card medisync-card-bg">
#             <h2 class="medisync-title medisync-purple">Multimodal Analysis Results</h2>
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
#         fig, ax = plt.subplots(figsize=(10, 6))
#         ax.imshow(image)
#         ax.set_title(title, fontsize=14, fontweight='bold', color='#007bff')
#         ax.axis('off')
#         return fig

#     def create_entity_visualization(self, entities):
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
#             ax.bar(entity_types.keys(), entity_types.values(), color='#00bfae')
#             ax.set_title('Entity Types Found in Text', fontsize=14, fontweight='bold', color='#00bfae')
#             ax.set_ylabel('Count', color='#00bfae')
#             plt.xticks(rotation=45, color='#222')
#             plt.yticks(color='#222')
#         return self.fig_to_html(fig)

#     def create_multimodal_visualization(self, results):
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
#         confidence = results.get("confidence", 0)
#         ax1.pie([confidence, 1-confidence], labels=['Confidence', 'Uncertainty'],
#                 colors=['#00bfae', '#ff7675'], autopct='%1.1f%%', textprops={'color': '#222'})
#         ax1.set_title('Analysis Confidence', fontweight='bold', color='#00bfae')
#         recommendations = results.get("recommendations", [])
#         ax2.bar(['Recommendations'], [len(recommendations)], color='#6c63ff')
#         ax2.set_title('Number of Recommendations', fontweight='bold', color='#6c63ff')
#         ax2.set_ylabel('Count', color='#6c63ff')
#         plt.tight_layout()
#         return self.fig_to_html(fig)

#     def fig_to_html(self, fig):
#         import io
#         import base64
#         buf = io.BytesIO()
#         fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=fig.get_facecolor())
#         buf.seek(0)
#         img_str = base64.b64encode(buf.read()).decode()
#         buf.close()
#         return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto; background: transparent;"/>'

# def complete_appointment(appointment_id):
#     try:
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
#         return {
#             "status": "error",
#             "message": "Cannot connect to Flask app. Please ensure the Flask app is running and accessible."
#         }
#     except Exception as e:
#         logger.error(f"Error completing appointment: {e}")
#         return {"status": "error", "message": f"Error: {str(e)}"}

# def create_interface():
#     app = MediSyncApp()
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

#     sample_images_dir = Path(parent_dir) / "data" / "sample"
#     sample_images = list(sample_images_dir.glob("*.png")) + list(sample_images_dir.glob("*.jpg"))
#     sample_image_path = str(sample_images[0]) if sample_images else None

#     with gr.Blocks(
#         title="MediSync: Multi-Modal Medical Analysis System",
#         theme=gr.themes.Default(),  # Use Default for HuggingFace dark/light support
#         css="""
#         /* Modern neumorphic card style for all result containers */
#         .medisync-card {
#             border-radius: 18px;
#             box-shadow: 0 4px 24px 0 rgba(0,0,0,0.10), 0 1.5px 4px 0 rgba(0,191,174,0.08);
#             margin: 18px 0;
#             padding: 24px 24px 18px 24px;
#             font-size: 1.08rem;
#             transition: background 0.2s, color 0.2s;
#         }
#         .medisync-card-bg {
#             background: var(--background-fill-primary, #f8f9fa);
#             color: var(--body-text-color, #222);
#         }
#         .medisync-title {
#             font-weight: 700;
#             margin-bottom: 0.7em;
#         }
#         .medisync-blue { color: #00bfae; }
#         .medisync-green { color: #28a745; }
#         .medisync-purple { color: #6c63ff; }
#         .medisync-card ul, .medisync-card ol {
#             margin-left: 1.2em;
#         }
#         .medisync-card li {
#             margin-bottom: 0.2em;
#         }
#         /* Button and input styling for modern look */
#         .gr-button, .end-consultation-btn {
#             border-radius: 8px !important;
#             font-weight: 600 !important;
#             font-size: 1.08rem !important;
#             transition: background 0.2s, color 0.2s;
#         }
#         .end-consultation-btn {
#             background: linear-gradient(90deg, #dc3545 60%, #ff7675 100%) !important;
#             border: none !important;
#             color: #fff !important;
#             box-shadow: 0 2px 8px 0 rgba(220,53,69,0.10);
#         }
#         .end-consultation-btn:hover {
#             background: linear-gradient(90deg, #c82333 60%, #ff7675 100%) !important;
#         }
#         /* Responsive tweaks */
#         @media (max-width: 900px) {
#             .medisync-card { padding: 16px 8px 12px 8px; }
#         }
#         /* Ensure text is visible in dark mode */
#         html[data-theme="dark"] .medisync-card-bg {
#             background: #23272f !important;
#             color: #f8fafc !important;
#         }
#         html[data-theme="dark"] .medisync-title {
#             color: #00bfae !important;
#         }
#         html[data-theme="dark"] .medisync-blue { color: #00bfae !important; }
#         html[data-theme="dark"] .medisync-green { color: #00e676 !important; }
#         html[data-theme="dark"] .medisync-purple { color: #a385ff !important; }
#         /* Make sure all gradio labels and text are visible */
#         label, .gr-label, .gr-text, .gr-html, .gr-markdown {
#             color: var(--body-text-color, #222) !important;
#         }
#         html[data-theme="dark"] label, html[data-theme="dark"] .gr-label, html[data-theme="dark"] .gr-text, html[data-theme="dark"] .gr-html, html[data-theme="dark"] .gr-markdown {
#             color: #f8fafc !important;
#         }
#         """
#     ) as interface:
#         gr.Markdown(
#             """
#             <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 0.5em;">
#                 <img src="https://cdn.jsdelivr.net/gh/saqib-ali-buriro/medivance-assets/medivance_logo.png" alt="Medivance Logo" style="height: 38px; border-radius: 8px; background: #fff; box-shadow: 0 2px 8px 0 rgba(26,115,232,0.10);">
#                 <span style="font-size: 2.1rem; font-weight: 700; color: #00bfae;">MediSync</span>
#             </div>
#             <div style="font-size: 1.18rem; margin-bottom: 1.2em;">
#                 <span style="color: var(--body-text-color, #222);">AI-powered Multi-Modal Medical Analysis System</span>
#             </div>
#             <div style="font-size: 1.05rem; margin-bottom: 1.2em;">
#                 <span style="color: var(--body-text-color, #222);">Seamlessly analyze X-ray images and medical reports for comprehensive healthcare insights.</span>
#             </div>
#             <div style="margin-bottom: 1.2em;">
#                 <ul style="font-size: 1.01rem; color: var(--body-text-color, #222);">
#                     <li>Upload a chest X-ray image</li>
#                     <li>Enter the corresponding medical report text</li>
#                     <li>Choose the analysis type: <b>Image</b>, <b>Text</b>, or <b>Multimodal</b></li>
#                     <li>Click <b>End Consultation</b> to complete your appointment</li>
#                 </ul>
#             </div>
#             """,
#             elem_id="medisync-header"
#         )

#         with gr.Row():
#             import urllib.parse
#             try:
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
#                 value=default_appointment_id,
#                 elem_id="appointment_id_input"
#             )

#         with gr.Tab("🧬 Multimodal Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     multi_img_input = gr.Image(label="Upload X-ray Image", type="pil", elem_id="multi_img_input")
#                     multi_img_enhance = gr.Button("Enhance Image", icon="✨")
#                     multi_text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report if sample_image_path is None else None,
#                         elem_id="multi_text_input"
#                     )
#                     multi_analyze_btn = gr.Button("Analyze Image & Text", variant="primary", icon="🔎")
#                 with gr.Column():
#                     multi_results = gr.HTML(label="Analysis Results", elem_id="multi_results")
#                     multi_plot = gr.HTML(label="Visualization", elem_id="multi_plot")
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path, example_report]],
#                     inputs=[multi_img_input, multi_text_input],
#                     label="Example X-ray and Report",
#                 )

#         with gr.Tab("🖼️ Image Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     img_input = gr.Image(label="Upload X-ray Image", type="pil", elem_id="img_input")
#                     img_enhance = gr.Button("Enhance Image", icon="✨")
#                     img_analyze_btn = gr.Button("Analyze Image", variant="primary", icon="🔎")
#                 with gr.Column():
#                     img_output = gr.Image(label="Processed Image", elem_id="img_output")
#                     img_results = gr.HTML(label="Analysis Results", elem_id="img_results")
#                     img_plot = gr.HTML(label="Visualization", elem_id="img_plot")
#             if sample_image_path:
#                 gr.Examples(
#                     examples=[[sample_image_path]],
#                     inputs=[img_input],
#                     label="Example X-ray Image",
#                 )

#         with gr.Tab("📝 Text Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report,
#                         elem_id="text_input"
#                     )
#                     text_analyze_btn = gr.Button("Analyze Text", variant="primary", icon="🔎")
#                 with gr.Column():
#                     text_output = gr.Textbox(label="Processed Text", elem_id="text_output")
#                     text_results = gr.HTML(label="Analysis Results", elem_id="text_results")
#                     text_plot = gr.HTML(label="Entity Visualization", elem_id="text_plot")
#             gr.Examples(
#                 examples=[[example_report]],
#                 inputs=[text_input],
#                 label="Example Medical Report",
#             )

#         with gr.Row():
#             with gr.Column():
#                 end_consultation_btn = gr.Button(
#                     "End Consultation",
#                     variant="stop",
#                     size="lg",
#                     elem_classes=["end-consultation-btn"],
#                     icon="🛑"
#                 )
#                 end_consultation_status = gr.HTML(label="Status", elem_id="end_consultation_status")

#         with gr.Tab("ℹ️ About"):
#             gr.Markdown(
#                 """
#                 <div class="medisync-card medisync-card-bg">
#                 <h2 class="medisync-title medisync-blue">About MediSync</h2>
#                 <p>
#                 <b>MediSync</b> is an AI-powered healthcare solution that uses multi-modal analysis to provide comprehensive insights from medical images and reports.
#                 </p>
#                 <h3>Key Features</h3>
#                 <ul>
#                     <li><b>X-ray Image Analysis</b>: Detects abnormalities in chest X-rays using pre-trained vision models</li>
#                     <li><b>Medical Report Processing</b>: Extracts key information from patient reports using NLP models</li>
#                     <li><b>Multi-modal Integration</b>: Combines insights from both image and text data for more accurate analysis</li>
#                 </ul>
#                 <h3>Models Used</h3>
#                 <ul>
#                     <li><b>X-ray Analysis</b>: facebook/deit-base-patch16-224-medical-cxr</li>
#                     <li><b>Medical Text Analysis</b>: medicalai/ClinicalBERT</li>
#                 </ul>
#                 <h3 style="color:#dc3545;">Important Disclaimer</h3>
#                 <p>
#                 This tool is for educational and research purposes only. It is not intended to provide medical advice or replace professional healthcare. Always consult with qualified healthcare providers for medical decisions.
#                 </p>
#                 </div>
#                 """
#             )

#         # Event handlers
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

#         def handle_end_consultation(appointment_id):
#             if not appointment_id or appointment_id.strip() == "":
#                 return "<div style='color: #dc3545; padding: 10px; background-color: #ffe6e6; border-radius: 5px;'>Please enter your appointment ID first.</div>"
#             result = complete_appointment(appointment_id.strip())
#             if result["status"] == "success":
#                 doctors_urls = get_doctors_page_urls()
#                 html_response = f"""
#                 <div style='color: #28a745; padding: 15px; background-color: #e6ffe6; border-radius: 5px; margin: 10px 0;'>
#                     <h3>✅ Consultation Completed Successfully!</h3>
#                     <p>{result['message']}</p>
#                     <p>Your appointment has been marked as completed.</p>
#                     <button onclick="window.open('{doctors_urls['local']}', '_blank')" 
#                             style="background-color: #00bfae; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;">
#                         Return to Doctors Page (Local)
#                     </button>
#                     <button onclick="window.open('{doctors_urls['production']}', '_blank')" 
#                             style="background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; margin-left: 10px;">
#                         Return to Doctors Page (Production)
#                     </button>
#                 </div>
#                 """
#             else:
#                 if "Cannot connect to Flask app" in result['message']:
#                     html_response = f"""
#                     <div style='color: #ff9800; padding: 15px; background-color: #fff3cd; border-radius: 5px; margin: 10px 0;'>
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
#                                     style="background-color: #00bfae; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Complete Appointment
#                             </button>
#                             <button onclick="window.open('http://127.0.0.1:600/doctors', '_blank')" 
#                                     style="background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
#                                 Return to Doctors Page
#                             </button>
#                             <button onclick="navigator.clipboard.writeText('{appointment_id.strip()}')" 
#                                     style="background-color: #23272f; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
#                                 Copy Appointment ID
#                             </button>
#                         </div>
#                     </div>
#                     """
#                 else:
#                     html_response = f"""
#                     <div style='color: #dc3545; padding: 15px; background-color: #ffe6e6; border-radius: 5px; margin: 10px 0;'>
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

#         # JavaScript for appointment ID auto-population
#         gr.HTML("""
#         <script>
#         function getUrlParameter(name) {
#             name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
#             var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
#             var results = regex.exec(location.search);
#             return results === null ? '' : decodeURIComponent(results[1].replace(/\\+/g, ' '));
#         }
#         function populateAppointmentId() {
#             var appointmentId = getUrlParameter('appointment_id');
#             if (appointmentId) {
#                 var input = document.getElementById('appointment_id_input');
#                 if (input) {
#                     input.value = appointmentId;
#                     var event = new Event('input', { bubbles: true });
#                     input.dispatchEvent(event);
#                 }
#             }
#         }
#         document.addEventListener('DOMContentLoaded', function() {
#             setTimeout(populateAppointmentId, 800);
#         });
#         window.addEventListener('load', function() {
#             setTimeout(populateAppointmentId, 1200);
#         });
#         </script>
#         """)

#     interface.launch()

# if __name__ == "__main__":
#     create_interface()

# Some tests on this code 