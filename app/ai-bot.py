# # AI bot implementation for a simple chat application
# # Tends to implement 

# import gradio as gr
# from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
# from qwen_vl_utils import process_vision_info

# # Load the pretrained model and processor
# model = Qwen2VLForConditionalGeneration.from_pretrained(
#     "prithivMLmods/Radiology-Infer-Mini", torch_dtype="auto", device_map="auto"
# )
# processor = AutoProcessor.from_pretrained("prithivMLmods/Radiology-Infer-Mini")

# def generate_response(image, text, specialization):
#     """
#     Generate a response based on the uploaded image and/or user query.
#     """
#     # Prepare the message
#     messages = []
#     if image:
#         messages.append({"type": "image", "image": image})
#     if text:
#         messages.append({"type": "text", "text": f"Specialization: {specialization}\n{text}"})
    
#     if not messages:
#         return "Please provide an image or a query to get a response."

#     # Process the input
#     chat_message = [{"role": "user", "content": messages}]
#     text_input = processor.apply_chat_template(chat_message, tokenize=False, add_generation_prompt=True)
#     image_inputs, video_inputs = process_vision_info(chat_message)
#     inputs = processor(
#         text=[text_input],
#         images=image_inputs,
#         videos=video_inputs,
#         padding=True,
#         return_tensors="pt",
#     )
#     inputs = inputs.to("cpu")  # Use CPU for processing (adjust if GPU is available)

#     # Generate the response
#     generated_ids = model.generate(**inputs, max_new_tokens=128)
#     generated_ids_trimmed = [
#         out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
#     ]
#     output_text = processor.batch_decode(
#         generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
#     )
    
#     return output_text[0]

# # Gradio Interface
# with gr.Blocks() as app:
#     gr.Markdown("# 🩺 AI Doctor Assistant")
#     gr.Markdown(
#         "Upload a medical image (e.g., X-ray, MRI) and/or ask a health-related question. "
#         "Select a specialization for more accurate responses."
#     )

#     with gr.Row():
#         image_input = gr.Image(type="pil", label="Upload Medical Image (Optional)")
#         specialization = gr.Dropdown(
#             choices=["general", "radiology", "cardiology", "neurology", "pediatrics"],
#             value="general",
#             label="Specialization"
#         )

#     text_input = gr.Textbox(
#         label="Enter Your Query",
#         placeholder="Type your health-related question here..."
#     )

#     response_output = gr.Textbox(
#         label="AI Doctor's Response",
#         interactive=False
#     )

#     submit_button = gr.Button("Get Response")

#     submit_button.click(
#         fn=generate_response,
#         inputs=[image_input, text_input, specialization],
#         outputs=[response_output]
#     )

# # Launch the app
# app.launch()