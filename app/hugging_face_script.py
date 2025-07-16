import logging
import os
import sys
import tempfile
from pathlib import Path
import requests
import gradio as gr
import matplotlib.pyplot as plt
from PIL import Image

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mediSync.log")],
)
logger = logging.getLogger(__name__)

class MediSyncApp:
    """
    Main application class for the MediSync multi-modal medical analysis system.
    """

    def __init__(self):
        """Initialize the application and load models."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing MediSync application")
        self._temp_files = []  # Track temporary files for cleanup
        self.fusion_model = None
        self.image_model = None
        self.text_model = None

    def __del__(self):
        """Cleanup temporary files on object destruction."""
        self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    self.logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
        self._temp_files = []

    def load_models(self):
        """
        Load models if not already loaded.

        Returns:
            bool: True if models loaded successfully, False otherwise
        """
        if self.fusion_model is not None:
            return True

        try:
            self.logger.info("Loading models...")
            from models.multimodal_fusion import MultimodalFusion
            self.fusion_model = MultimodalFusion()
            self.image_model = self.fusion_model.image_analyzer
            self.text_model = self.fusion_model.text_analyzer
            self.logger.info("Models loaded successfully")
            return True
        except ImportError as e:
            self.logger.error(f"Failed to import required modules: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            return False

    def analyze_image(self, image):
        """
        Analyze a medical image.

        Args:
            image: Image file uploaded through Gradio

        Returns:
            tuple: (image, image_results_html, plot_as_html)
        """
        if not self.load_models() or self.image_model is None:
            return image, "Error: Models not loaded properly.", None

        temp_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                temp_path = temp.name
                self._temp_files.append(temp_path)

                if isinstance(image, str):
                    from shutil import copyfile
                    copyfile(image, temp_path)
                else:
                    image.save(temp_path)

            self.logger.info(f"Analyzing image: {temp_path}")
            results = self.image_model.analyze(temp_path)

            # Create visualization
            fig = self.plot_image_prediction(
                image,
                results.get("predictions", []),
                f"Primary Finding: {results.get('primary_finding', 'Unknown')}"
            )

            # Convert to HTML for display
            plot_html = self.fig_to_html(fig)
            plt.close(fig)  # Clean up matplotlib figure

            # Format results as HTML
            html_result = self.format_image_results(results)
            
            return image, html_result, plot_html

        except Exception as e:
            self.logger.error(f"Error in image analysis: {e}")
            return image, f"Error analyzing image: {str(e)}", None

        finally:
            # Clean up temporary file
            if temp_path and temp_path in self._temp_files:
                try:
                    os.remove(temp_path)
                    self._temp_files.remove(temp_path)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")

    def format_image_results(self, results):
        """Format image analysis results as HTML."""
        html_result = f"""
        <h2>X-ray Analysis Results</h2>
        <p><strong>Primary Finding:</strong> {results.get("primary_finding", "Unknown")}</p>
        <p><strong>Confidence:</strong> {results.get("confidence", 0):.1%}</p>
        <p><strong>Abnormality Detected:</strong> {"Yes" if results.get("has_abnormality", False) else "No"}</p>
        
        <h3>Top Predictions:</h3>
        <ul>
        """

        for label, prob in results.get("predictions", [])[:5]:
            html_result += f"<li>{label}: {prob:.1%}</li>"

        html_result += "</ul>"

        explanation = self.image_model.get_explanation(results)
        html_result += f"<h3>Analysis Explanation:</h3><p>{explanation}</p>"

        return html_result

    def plot_image_prediction(self, image, predictions, title):
        """Create visualization for image predictions."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(image)
        ax.set_title(title)
        ax.axis('off')
        return fig

    def fig_to_html(self, fig):
        """Convert matplotlib figure to HTML."""
        import io
        import base64
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        buf.close()
        
        return f'<img src="data:image/png;base64,{img_str}"/>'


def create_interface():
    """Create and launch the Gradio interface."""

    app = MediSyncApp()

    # Example medical report for demo
    example_report = """
    CHEST X-RAY EXAMINATION
    
    CLINICAL HISTORY: 55-year-old male with cough and fever.
    
    FINDINGS: The heart size is at the upper limits of normal. The lungs are clear without focal consolidation, 
    effusion, or pneumothorax. There is mild prominence of the pulmonary vasculature. No pleural effusion is seen. 
    There is a small nodular opacity noted in the right lower lobe measuring approximately 8mm, which is suspicious 
    and warrants further investigation. The mediastinum is unremarkable. The visualized bony structures show no acute abnormalities.
    
    IMPRESSION:
    1. Mild cardiomegaly.
    2. 8mm nodular opacity in the right lower lobe, recommend follow-up CT for further evaluation.
    3. No acute pulmonary parenchymal abnormality.
    
    RECOMMENDATIONS: Follow-up chest CT to further characterize the nodular opacity in the right lower lobe.
    """

    # Get sample image path if available
    sample_images_dir = Path(parent_dir) / "data" / "sample"
    sample_images = list(sample_images_dir.glob("*.png")) + list(
        sample_images_dir.glob("*.jpg")
    )

    sample_image_path = None
    if sample_images:
        sample_image_path = str(sample_images[0])

    # Define interface
    with gr.Blocks(
        title="MediSync: Multi-Modal Medical Analysis System", theme=gr.themes.Soft()
    ) as interface:
        gr.Markdown("""
        # MediSync: Multi-Modal Medical Analysis System
        
        This AI-powered healthcare solution combines X-ray image analysis with patient report text processing 
        to provide comprehensive medical insights.
        
        ## How to Use
        1. Upload a chest X-ray image
        2. Enter the corresponding medical report text
        3. Choose the analysis type: image-only, text-only, or multimodal (combined)
        """)

        with gr.Tab("Multimodal Analysis"):
            with gr.Row():
                with gr.Column():
                    multi_img_input = gr.Image(label="Upload X-ray Image", type="pil")
                    multi_img_enhance = gr.Button("Enhance Image")

                    multi_text_input = gr.Textbox(
                        label="Enter Medical Report Text",
                        placeholder="Enter the radiologist's report text here...",
                        lines=10,
                        value=example_report if sample_image_path is None else None,
                    )

                    multi_analyze_btn = gr.Button(
                        "Analyze Image & Text", variant="primary"
                    )

                with gr.Column():
                    multi_results = gr.HTML(label="Analysis Results")
                    multi_plot = gr.HTML(label="Visualization")

            # Set up examples if sample image exists
            if sample_image_path:
                gr.Examples(
                    examples=[[sample_image_path, example_report]],
                    inputs=[multi_img_input, multi_text_input],
                    label="Example X-ray and Report",
                )

        with gr.Tab("Image Analysis"):
            with gr.Row():
                with gr.Column():
                    img_input = gr.Image(label="Upload X-ray Image", type="pil")
                    img_enhance = gr.Button("Enhance Image")
                    img_analyze_btn = gr.Button("Analyze Image", variant="primary")

                with gr.Column():
                    img_output = gr.Image(label="Processed Image")
                    img_results = gr.HTML(label="Analysis Results")
                    img_plot = gr.HTML(label="Visualization")

            # Set up example if sample image exists
            if sample_image_path:
                gr.Examples(
                    examples=[[sample_image_path]],
                    inputs=[img_input],
                    label="Example X-ray Image",
                )

        with gr.Tab("Text Analysis"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        label="Enter Medical Report Text",
                        placeholder="Enter the radiologist's report text here...",
                        lines=10,
                        value=example_report,
                    )
                    text_analyze_btn = gr.Button("Analyze Text", variant="primary")

                with gr.Column():
                    text_output = gr.Textbox(label="Processed Text")
                    text_results = gr.HTML(label="Analysis Results")
                    text_plot = gr.HTML(label="Entity Visualization")

            # Set up example
            gr.Examples(
                examples=[[example_report]],
                inputs=[text_input],
                label="Example Medical Report",
            )

        with gr.Tab("About"):
            gr.Markdown("""
            ## About MediSync
            
            MediSync is an AI-powered healthcare solution that uses multi-modal analysis to provide comprehensive insights from medical images and reports.
            
            ### Key Features
            
            - **X-ray Image Analysis**: Detects abnormalities in chest X-rays using pre-trained vision models
            - **Medical Report Processing**: Extracts key information from patient reports using NLP models
            - **Multi-modal Integration**: Combines insights from both image and text data for more accurate analysis
            
            ### Models Used
            
            - **X-ray Analysis**: facebook/deit-base-patch16-224-medical-cxr
            - **Medical Text Analysis**: medicalai/ClinicalBERT
            
            ### Important Disclaimer
            
            This tool is for educational and research purposes only. It is not intended to provide medical advice or replace professional healthcare. Always consult with qualified healthcare providers for medical decisions.
            """)

        # Set up event handlers
        multi_img_enhance.click(
            app.enhance_image, inputs=multi_img_input, outputs=multi_img_input
        )
        multi_analyze_btn.click(
            app.analyze_multimodal,
            inputs=[multi_img_input, multi_text_input],
            outputs=[multi_results, multi_plot],
        )

        img_enhance.click(app.enhance_image, inputs=img_input, outputs=img_output)
        img_analyze_btn.click(
            app.analyze_image,
            inputs=img_input,
            outputs=[img_output, img_results, img_plot],
        )

        text_analyze_btn.click(
            app.analyze_text,
            inputs=text_input,
            outputs=[text_output, text_results, text_plot],
        )

    # Run the interface
    interface.launch()


if __name__ == "__main__":
    create_interface()


# Example Script 