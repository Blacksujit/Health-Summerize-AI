# ✅✅✅✅Up and Working Fine dont uncomment the script ✅✅✅✅

# import logging
# import os
# import sys
# import tempfile
# from pathlib import Path
# import requests
# import gradio as gr
# import matplotlib.pyplot as plt
# from PIL import Image

# # Import configuration for end consultation logic
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

# # Add parent directory to path
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(parent_dir)

# # Import our modules for model and utility logic
# from models.multimodal_fusion import MultimodalFusion
# from utils.preprocessing import enhance_xray_image, normalize_report_text
# from utils.visualization import (
#     plot_image_prediction,
#     plot_multimodal_results,
#     plot_report_entities,
# )

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
# )
# logger = logging.getLogger(__name__)

# # Ensure sample data directory exists
# os.makedirs(os.path.join(parent_dir, "data", "sample"), exist_ok=True)

# class MediSyncApp:
#     """
#     Main application class for the MediSync multi-modal medical analysis system.
#     """

#     def __init__(self):
#         """Initialize the application and load models."""
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("Initializing MediSync application")
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
#             if image is None:
#                 return None, "Please upload an image first.", None
#             if not self.load_models() or self.image_model is None:
#                 return image, "Error: Models not loaded properly.", None

#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")
#             if isinstance(image, str):
#                 from shutil import copyfile
#                 copyfile(image, temp_path)
#             else:
#                 image.save(temp_path)

#             self.logger.info(f"Analyzing image: {temp_path}")
#             results = self.image_model.analyze(temp_path)

#             fig = plot_image_prediction(
#                 image,
#                 results.get("predictions", []),
#                 f"Primary Finding: {results.get('primary_finding', 'Unknown')}",
#             )
#             plot_html = self.fig_to_html(fig)

#             html_result = f"""
#             <div class="medisync-card medisync-card-bg medisync-force-text">
#                 <h2 class="medisync-title medisync-blue">
#                     <b>X-ray Analysis Results</b>
#                 </h2>
#                 <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#                 <p><strong>Confidence:</strong> {results.get("confidence", 0):.1%}</p>
#                 <p><strong>Abnormality Detected:</strong> {"Yes" if results.get("has_abnormality", False) else "No"}</p>
#                 <h3>Top Predictions:</h3>
#                 <ul>
#             """
#             for label, prob in results.get("predictions", [])[:5]:
#                 html_result += f"<li>{label}: {prob:.1%}</li>"
#             html_result += "</ul>"
#             explanation = self.image_model.get_explanation(results)
#             html_result += f"<h3>Analysis Explanation:</h3><p>{explanation}</p>"
#             html_result += "</div>"
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
#             if not text or text.strip() == "":
#                 return "", "Please enter medical report text.", None
#             if not self.load_models() or self.text_model is None:
#                 return text, "Error: Models not loaded properly.", None
#             if not text or len(text.strip()) < 10:
#                 return (
#                     text,
#                     "Error: Please enter a valid medical report text (at least 10 characters).",
#                     None,
#                 )
#             normalized_text = normalize_report_text(text)
#             self.logger.info("Analyzing medical report text")
#             results = self.text_model.analyze(normalized_text)
#             entities = results.get("entities", {})
#             fig = plot_report_entities(normalized_text, entities)
#             entities_plot_html = self.fig_to_html(fig)
#             html_result = f"""
#             <div class="medisync-card medisync-card-bg medisync-force-text">
#                 <h2 class="medisync-title medisync-green">
#                     <b>Text Analysis Results</b>
#                 </h2>
#                 <p><strong>Severity Level:</strong> {results.get("severity", {}).get("level", "Unknown")}</p>
#                 <p><strong>Severity Score:</strong> {results.get("severity", {}).get("score", 0)}/4</p>
#                 <p><strong>Confidence:</strong> {results.get("severity", {}).get("confidence", 0):.1%}</p>
#                 <h3>Key Findings:</h3>
#                 <ul>
#             """
#             findings = results.get("findings", [])
#             if findings:
#                 for finding in findings:
#                     html_result += f"<li>{finding}</li>"
#             else:
#                 html_result += "<li>No specific findings detailed.</li>"
#             html_result += "</ul>"
#             html_result += "<h3>Extracted Medical Entities:</h3>"
#             for category, items in entities.items():
#                 if items:
#                     html_result += f"<p><strong>{category.capitalize()}:</strong> {', '.join(items)}</p>"
#             html_result += "<h3>Follow-up Recommendations:</h3><ul>"
#             followups = results.get("followup_recommendations", [])
#             if followups:
#                 for rec in followups:
#                     html_result += f"<li>{rec}</li>"
#             else:
#                 html_result += "<li>No specific follow-up recommendations.</li>"
#             html_result += "</ul></div>"
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
#             if not self.load_models() or self.fusion_model is None:
#                 return "Error: Models not loaded properly.", None
#             if image is None:
#                 return "Error: Please upload an X-ray image for analysis.", None
#             if not text or len(text.strip()) < 10:
#                 return (
#                     "Error: Please enter a valid medical report text (at least 10 characters).",
#                     None,
#                 )
#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")
#             if isinstance(image, str):
#                 from shutil import copyfile
#                 copyfile(image, temp_path)
#             else:
#                 image.save(temp_path)
#             normalized_text = normalize_report_text(text)
#             self.logger.info("Performing multimodal analysis")
#             results = self.fusion_model.analyze(temp_path, normalized_text)
#             fig = plot_multimodal_results(results, image, text)
#             plot_html = self.fig_to_html(fig)
#             explanation = self.fusion_model.get_explanation(results)
#             html_result = f"""
#             <div class="medisync-card medisync-card-bg medisync-force-text">
#                 <h2 class="medisync-title medisync-purple">
#                     <b>Multimodal Analysis Results</b>
#                 </h2>
#                 <h3>Overview</h3>
#                 <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
#                 <p><strong>Severity Level:</strong> {results.get("severity", {}).get("level", "Unknown")}</p>
#                 <p><strong>Severity Score:</strong> {results.get("severity", {}).get("score", 0)}/4</p>
#                 <p><strong>Agreement Score:</strong> {results.get("agreement_score", 0):.0%}</p>
#                 <h3>Detailed Findings</h3>
#                 <ul>
#             """
#             findings = results.get("findings", [])
#             if findings:
#                 for finding in findings:
#                     html_result += f"<li>{finding}</li>"
#             else:
#                 html_result += "<li>No specific findings detailed.</li>"
#             html_result += "</ul>"
#             html_result += "<h3>Recommended Follow-up</h3><ul>"
#             followups = results.get("followup_recommendations", [])
#             if followups:
#                 for rec in followups:
#                     html_result += f"<li>{rec}</li>"
#             else:
#                 html_result += "<li>No specific follow-up recommendations provided.</li>"
#             html_result += "</ul>"
#             confidence = results.get("severity", {}).get("confidence", 0)
#             html_result += f"""
#                 <p><em>Note: This analysis has a confidence level of {confidence:.0%}. 
#                 Please consult with healthcare professionals for official diagnosis.</em></p>
#                 <h3>Analysis Explanation:</h3>
#                 <p>{explanation}</p>
#             </div>
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
#             temp_dir = tempfile.mkdtemp()
#             temp_path = os.path.join(temp_dir, "upload.png")
#             if isinstance(image, str):
#                 from shutil import copyfile
#                 copyfile(image, temp_path)
#             else:
#                 image.save(temp_path)
#             self.logger.info(f"Enhancing image: {temp_path}")
#             output_path = os.path.join(temp_dir, "enhanced.png")
#             enhance_xray_image(temp_path, output_path)
#             enhanced = Image.open(output_path)
#             return enhanced
#         except Exception as e:
#             self.logger.error(f"Error enhancing image: {e}")
#             return image

#     def fig_to_html(self, fig):
#         """Convert matplotlib figure to HTML for display in Gradio."""
#         try:
#             import base64
#             import io
#             buf = io.BytesIO()
#             fig.savefig(buf, format="png", bbox_inches="tight", dpi=100, facecolor=fig.get_facecolor())
#             buf.seek(0)
#             img_str = base64.b64encode(buf.read()).decode("utf-8")
#             plt.close(fig)
#             return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto; background: transparent;"/>'
#         except Exception as e:
#             self.logger.error(f"Error converting figure to HTML: {e}")
#             return "<p>Error displaying visualization.</p>"

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
#     import urllib.parse
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
#         theme=gr.themes.Default(),
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
#             font-weight: 900;
#             font-size: 1.45em;
#             margin-bottom: 0.7em;
#             letter-spacing: 1px;
#             text-shadow: 0 2px 8px #00bfae33, 0 1px 0 #fff;
#             /* Remove display:flex and gap for simple bold text */
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
#             font-size: 1rem !important;
#             padding: 8px 18px !important;
#             min-width: 120px !important;
#             min-height: 38px !important;
#             transition: background 0.2s, color 0.2s;
#         }
#         .end-consultation-btn {
#             background: linear-gradient(90deg, #dc3545 60%, #ff7675 100%) !important;
#             border: none !important;
#             color: #fff !important;
#             box-shadow: 0 2px 8px 0 rgba(220,53,69,0.10);
#             font-size: 1.05rem !important;
#             padding: 10px 24px !important;
#             min-width: 160px !important;
#             min-height: 40px !important;
#         }
#         .end-consultation-btn:hover {
#             background: linear-gradient(90deg, #c82333 60%, #ff7675 100%) !important;
#         }
#         /* Responsive tweaks */
#         @media (max-width: 900px) {
#             .medisync-card { padding: 16px 8px 12px 8px; }
#             .medisync-title { font-size: 1.1em; }
#         }
#         /* Ensure text is visible in dark mode */
#         html[data-theme="dark"] .medisync-card-bg,
#         html[data-theme="dark"] .medisync-card-bg.medisync-force-text {
#             background: #23272f !important;
#             color: #f8fafc !important;
#         }
#         html[data-theme="dark"] .medisync-title {
#             color: #00bfae !important;
#             text-shadow: 0 2px 8px #00bfae33, 0 1px 0 #23272f;
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
#         /* Force all text in medisync-card and status outputs to be visible in all themes */
#         .medisync-force-text, .medisync-force-text * {
#             color: var(--body-text-color, #222) !important;
#         }
#         html[data-theme="dark"] .medisync-force-text, html[data-theme="dark"] .medisync-force-text * {
#             color: #f8fafc !important;
#         }
#         /* End consultation status output: remove color and theme, keep text black and simple */
#         #end_consultation_status, #end_consultation_status * {
#             color: #000 !important;
#             background: #fff !important;
#             font-size: 1.12rem !important;
#             font-weight: 600 !important;
#         }
#         /* Style the buttons inside the end consultation status popup */
#         #end_consultation_status button {
#             font-size: 1rem !important;
#             font-weight: 600 !important;
#             border-radius: 6px !important;
#             padding: 8px 18px !important;
#             margin-top: 8px !important;
#             margin-bottom: 4px !important;
#             min-width: 120px !important;
#             min-height: 36px !important;
#             box-shadow: 0 1.5px 4px 0 rgba(0,191,174,0.08);
#         }
#         #end_consultation_status button:active, #end_consultation_status button:focus {
#             outline: 2px solid #00bfae !important;
#         }
#         #end_consultation_status .btn-green {
#             background-color: #00bfae !important;
#             color: #fff !important;
#         }
#         #end_consultation_status .btn-purple {
#             background-color: #6c63ff !important;
#             color: #fff !important;
#         }
#         #end_consultation_status .btn-dark {
#             background-color: #23272f !important;
#             color: #fff !important;
#         }
#         #end_consultation_status .btn-orange {
#             background-color: #ff9800 !important;
#             color: #fff !important;
#         }
#         #end_consultation_status .btn-red {
#             background-color: #dc3545 !important;
#             color: #fff !important;
#         }
#         """
#     ) as interface:
#         gr.Markdown(
#             """
#             <div style="margin-bottom: 0.5em;">
#                 <span style="font-size: 2.4rem; font-weight: bold; letter-spacing: 1.5px;">
#                     <b>MediSync</b>
#                 </span>
#             </div>
#             <div style="font-size: 1.22rem; margin-bottom: 1.2em; font-weight: 600;">
#                 <span>AI-powered Multi-Modal Medical Analysis System</span>
#             </div>
#             <div style="font-size: 1.09rem; margin-bottom: 1.2em;">
#                 <span>Seamlessly analyze X-ray images and medical reports for comprehensive healthcare insights.</span>
#             </div>
#             <div style="margin-bottom: 1.2em;">
#                 <ul style="font-size: 1.04rem;">
#                     <li>Upload a chest X-ray image</li>
#                     <li>Enter the corresponding medical report text</li>
#                     <li>Choose the analysis type: <b>Image</b>, <b>Text</b>, or <b>Multimodal</b></li>
#                     <li>Click <b>End Consultation</b> to complete your appointment</li>
#                 </ul>
#             </div>
#             """,
#             elem_id="medisync-header"
#         )
        
#         # --- BRUTAL FIX: Always set appointment id from URL using JS, forcibly, and keep it in sync ---
#         with gr.Row():
#             appointment_id_input = gr.Textbox(
#                 label="Appointment ID",
#                 placeholder="Enter your appointment ID here...",
#                 info="This will be automatically populated if you came from the doctors page",
#                 value="",
#                 elem_id="appointment_id_input"
#             )

#         # Populate appointment id from URL on initial load using server-side request (robust, no JS dependency)
#         def _populate_appointment_id_on_load(request: gr.Request):
#             try:
#                 params = getattr(request, "query_params", {}) or {}
#                 appointment_id = params.get("appointment_id", "")
#                 if appointment_id:
#                     return gr.update(value=appointment_id)
#                 return gr.update()
#             except Exception as e:
#                 logger.warning(f"Could not populate appointment_id from URL: {e}")
#                 return gr.update()

#         with gr.Tab("🧬 Multimodal Analysis"):
#             with gr.Row():
#                 with gr.Column():
#                     multi_img_input = gr.Image(label="Upload X-ray Image", type="pil", elem_id="multi_img_input")
#                     multi_img_enhance = gr.Button("Enhance Image")
#                     multi_text_input = gr.Textbox(
#                         label="Enter Medical Report Text",
#                         placeholder="Enter the radiologist's report text here...",
#                         lines=10,
#                         value=example_report if sample_image_path is None else None,
#                         elem_id="multi_text_input"
#                     )
#                     multi_analyze_btn = gr.Button("Analyze Image & Text", variant="primary")
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
#                     img_enhance = gr.Button("Enhance Image")
#                     img_analyze_btn = gr.Button("Analyze Image", variant="primary")
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
#                     text_analyze_btn = gr.Button("Analyze Text", variant="primary")
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
#                     elem_classes=["end-consultation-btn"]
#                 )
#                 end_consultation_status = gr.HTML(label="Status", elem_id="end_consultation_status")

#         with gr.Tab("ℹ️ About"):
#             gr.Markdown(
#                 """
#                 <div class="medisync-card medisync-card-bg medisync-force-text">
#                 <h2 class="medisync-title medisync-blue">
#                     <b>About MediSync</b>
#                 </h2>
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
#             # Output status: styled with color for buttons and clear status box, as per template
#             if not appointment_id or appointment_id.strip() == "":
#                 return "<div style='color: #000; background: #fff; padding: 10px; border-radius: 5px;'>Please enter your appointment ID first.</div>"
#             result = complete_appointment(appointment_id.strip())
#             if result["status"] == "success":
#                 doctors_urls = get_doctors_page_urls()
#                 html_response = f"""
#                 <div style='color: #000; background: #fff; padding: 15px; border-radius: 5px; margin: 10px 0;'>
#                     <h3 style="color: #28a745;">✅ Consultation Completed Successfully!</h3>
#                     <p style="color: #28a745;">✔️ {result['message']}</p>
#                     <p>Your appointment has been marked as completed.</p>
#                     <button class="btn-green" onclick="window.open('{doctors_urls['local']}', '_blank')"
#                             style="margin-top: 10px;">
#                         Return to Doctors Page (Local)
#                     </button>
#                     <button class="btn-purple" onclick="window.open('{doctors_urls['production']}', '_blank')"
#                             style="margin-top: 10px; margin-left: 10px;">
#                         Return to Doctors Page (Production)
#                     </button>
#                 </div>
#                 """
#             else:
#                 if "Cannot connect to Flask app" in result['message']:
#                     html_response = f"""
#                     <div style='color: #000; background: #fff; padding: 15px; border-radius: 5px; margin: 10px 0;'>
#                         <h3 style="color: #ff9800;">⚠️ Consultation Ready to Complete</h3>
#                         <p>Your consultation analysis is complete! However, we cannot automatically mark your appointment as completed because the Flask app is not accessible from this environment.</p>
#                         <p><strong>Appointment ID:</strong> {appointment_id.strip()}</p>
#                         <p><strong>Next Steps:</strong></p>
#                         <ol>
#                             <li>Copy your appointment ID: <code>{appointment_id.strip()}</code></li>
#                             <li>Return to your Flask app (doctors page)</li>
#                             <li>Manually complete the appointment using the appointment ID</li>
#                         </ol>
#                         <div style="margin-top: 15px;">
#                             <button class="btn-green" onclick="window.open('http://127.0.0.1:600/complete_appointment_manual?appointment_id={appointment_id.strip()}', '_blank')" style="margin-right: 10px;">
#                                 Complete Appointment
#                             </button>
#                             <button class="btn-purple" onclick="window.open('http://127.0.0.1:600/doctors', '_blank')" style="margin-right: 10px;">
#                                 Return to Doctors Page
#                             </button>
#                             <button class="btn-dark" onclick="navigator.clipboard.writeText('{appointment_id.strip()}')">
#                                 Copy Appointment ID
#                             </button>
#                         </div>
#                     </div>
#                     """
#                 else:
#                     html_response = f"""
#                     <div style='color: #000; background: #fff; padding: 15px; border-radius: 5px; margin: 10px 0;'>
#                         <h3 style="color: #dc3545;">❌ Error Completing Consultation</h3>
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

#         # --- Client-side fallback: update the underlying input/textarea inside the Gradio container ---
#         gr.HTML("""
#         <script>
#         function getUrlParameter(name) {
#             name = name.replace(/[[]/, '\\[').replace(/[\]]/, '\\]');
#             var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
#             var results = regex.exec(window.location.search);
#             return results === null ? '' : decodeURIComponent(results[1].replace(/\\+/g, ' '));
#         }
#         function setAppointmentIdFallback() {
#             var appointmentId = getUrlParameter('appointment_id');
#             var container = document.getElementById('appointment_id_input');
#             if (!container || !appointmentId) return;
#             var input = container.querySelector('input, textarea');
#             if (!input && container.shadowRoot) {
#                 input = container.shadowRoot.querySelector('input, textarea');
#             }
#             if (input && input.value !== appointmentId) {
#                 input.value = appointmentId;
#                 input.dispatchEvent(new Event('input', { bubbles: true }));
#                 input.dispatchEvent(new Event('change', { bubbles: true }));
#             }
#         }
#         // Try to apply once on load and occasionally afterward in case Gradio re-renders
#         const fallbackInterval = setInterval(setAppointmentIdFallback, 1000);
#         window.addEventListener('DOMContentLoaded', setAppointmentIdFallback);
#         window.addEventListener('load', setAppointmentIdFallback);
#         // Stop after some time to avoid running forever (10s)
#         setTimeout(() => clearInterval(fallbackInterval), 10000);
#         </script>
#         """)

#         # Server-side load event to populate appointment id reliably
#         interface.load(
#             _populate_appointment_id_on_load,
#             inputs=None,
#             outputs=appointment_id_input
#         )

#     interface.launch()

# if __name__ == "__main__":
#     create_interface()

# ✅✅✅✅Up and Working Fine dont uncomment the script ✅✅✅✅