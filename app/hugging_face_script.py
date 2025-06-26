# import logging
# import os
# import sys
# import tempfile
# from pathlib import Path

# import gradio as gr
# import matplotlib.pyplot as plt
# from PIL import Image

# # Add parent directory to path
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(parent_dir)

# # Import our modules
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

# # Create temporary directory for sample data if it doesn't exist
# os.makedirs(os.path.join(parent_dir, "data", "sample"), exist_ok=True)


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
#         """)

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

#     # Run the interface
#     interface.launch()


# if __name__ == "__main__":
#     create_interface()


# Example Script 