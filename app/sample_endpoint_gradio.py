def create_interface():
    """Create and launch the Gradio interface with all fixes implemented."""

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

    # Get sample image path with robust error handling
    sample_image_path = None
    try:
        sample_images_dir = Path(__file__).parent.parent / "data" / "sample"
        os.makedirs(sample_images_dir, exist_ok=True)
        
        # Check for existing images first
        sample_images = list(sample_images_dir.glob("*.png")) + list(sample_images_dir.glob("*.jpg"))
        
        if not sample_images:
            # Download fallback sample image if none exist
            fallback_url = "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/1-s2.0-S0929664620300449-gr2_lrg-a.jpg"
            sample_path = sample_images_dir / "sample_xray.jpg"
            
            try:
                response = requests.get(fallback_url, timeout=10)
                if response.status_code == 200:
                    with open(sample_path, 'wb') as f:
                        f.write(response.content)
                    sample_image_path = str(sample_path)
                    logging.info("Successfully downloaded fallback sample image")
                else:
                    logging.warning(f"Failed to download sample image. Status code: {response.status_code}")
            except Exception as download_error:
                logging.warning(f"Could not download sample image: {str(download_error)}")
        else:
            sample_image_path = str(sample_images[0])
    except Exception as e:
        logging.error(f"Error setting up sample images: {str(e)}")

    # Define interface with robust parameter handling
    with gr.Blocks(
        title="MediSync: Multi-Modal Medical Analysis System", 
        theme=gr.themes.Soft()
    ) as interface:
        # Get appointment ID from URL parameters
        try:
            from gradio.context import Context
            appointment_id_value = Context.request.query_params.get("appointment_id", "") if hasattr(Context, 'request') else ""
        except Exception as e:
            logging.warning(f"Could not get URL parameters: {str(e)}")
            appointment_id_value = ""

        appointment_id = gr.Textbox(
            visible=False,
            value=appointment_id_value
        )

        gr.Markdown("""
        # MediSync: Multi-Modal Medical Analysis System
        
        This AI-powered healthcare solution combines X-ray image analysis with patient report text processing 
        to provide comprehensive medical insights.
        
        ## How to Use
        1. Upload a chest X-ray image
        2. Enter the corresponding medical report text
        3. Choose the analysis type: image-only, text-only, or multimodal (combined)
        4. Click "End Consultation" when finished to complete your appointment
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
                        value=example_report if not sample_image_path else None,
                    )

                    multi_analyze_btn = gr.Button(
                        "Analyze Image & Text", variant="primary"
                    )

                with gr.Column():
                    multi_results = gr.HTML(label="Analysis Results")
                    multi_plot = gr.HTML(label="Visualization")

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

        # Consultation completion section
        with gr.Row():
            with gr.Column():
                end_consultation_btn = gr.Button(
                    "End Consultation", 
                    variant="stop",
                    size="lg"
                )
                completion_status = gr.HTML()

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

        def complete_consultation(appointment_id):
            """Handle consultation completion."""
            if not appointment_id:
                return "<div class='alert alert-error'>No appointment ID found. Please contact support.</div>"
            
            try:
                # Replace with your actual Flask app URL
                flask_app_url = "http://127.0.0.1:600/complete_consultation"
                
                response = requests.post(
                    flask_app_url,
                    json={"appointment_id": appointment_id},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return """
                    <div class='alert alert-success'>
                        Consultation completed successfully. Redirecting...
                        <script>
                            setTimeout(function() {
                                window.location.href = "http://127.0.0.1:600/doctors";
                            }, 2000);
                        </script>
                    </div>
                    """
                else:
                    return f"""
                    <div class='alert alert-error'>
                        Error completing appointment (Status: {response.status_code}). 
                        Please contact support.
                    </div>
                    """
                    
            except Exception as e:
                return f"""
                <div class='alert alert-error'>
                    Error: {str(e)}
                </div>
                """

        end_consultation_btn.click(
            fn=complete_consultation,
            inputs=[appointment_id],
            outputs=completion_status
        )

    try:
        interface.launch()
    except Exception as e:
        logging.error(f"Failed to launch interface: {str(e)}")
        raise RuntimeError("Failed to launch MediSync interface") from e


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    create_interface()
