import streamlit as st
from PIL import Image
import io
import logging
import hashlib
#import os
#import requests
#import json
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions


temperature = 0.9

generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 99998,
}
fixed_logo = """
<div class="fixed top-0 left-0 w-full bg-white py-4 px-6 z-50">
    <p class="text-lg font-bold text-gray-800">Docify</p>
</div>
"""
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.title("Docify 🩺")
# st.title("Docify 🩺")
# st.write("---")
# Create a sidebar menu
st.sidebar.title("Menu")
page = st.sidebar.selectbox("Select a page", ["Home", "History", "About"])


# Create a home page
if page == "Home":
    genai.configure(api_key='Enter your own API key')
    select_model = st.radio("Select Type", ["Consultancy", "Image Consultancy"])

    if select_model == "Image Consultancy":
        uploaded_image = st.file_uploader(
            "upload image",
            label_visibility="collapsed",
            accept_multiple_files=False,
            type=["png", "jpg"],
        )
            # st.caption(
            #     "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
            # )
        if uploaded_image:
            image_bytes = uploaded_image.read()
        picture = st.camera_input("Take a picture")

            # if picture:
            #     st.image(picture)

        if picture is not None:
            image_bytes = picture.getvalue()

    def get_response(message, model="gemini-pro"):
        model = genai.GenerativeModel(model)
        res = model.generate_content(message,
                                    generation_config=generation_config)
        return res


    if "message" not in st.session_state:
        st.session_state["message"] = []
    message = st.session_state["message"]

        # The vision model gemini-pro-vision is not optimized for multi-turn chat.
        # st.header("Docify")
        # st.write("How can I help you?")

        # Initialize session state for chat history if it doesn't exist
    if message and select_model != "Image Consultancy":
        for item in message:
            role, parts = item.values()
            if role == "user":
                st.chat_message("user").markdown(parts[0])
            elif role == "model":
                st.chat_message("assistant").markdown(parts[0])
    
    # chat = st.radio("Select one of the following options", ["Common Cold", "Influenza (Flu)", "Pneumonia", "Tuberculosis (TB)", "Hypertension", "Other","none of these"])
    # if chat == "Other":
    #     chat2 = st.text_input("Enter the disease name")
    # if chat == "Other":
    #     chat = chat2

    st.write("How can I help you?")
    chat_message = st.chat_input("Ask me about health related query...")
    
    # if chat == "none of these":
    #     instruction = " "
    # else:
    #     instruction = "i am having " + chat
    
    
    res = None
    if chat_message:
        st.chat_message("user").markdown(chat_message)
        res_area = st.chat_message("assistant").markdown("...")
        

        if select_model == "Image Consultancy":
            if "image_bytes" in globals():
                vision_message = [chat_message,
                                    Image.open(io.BytesIO(image_bytes))]
                try:
                    res = get_response(vision_message, model="gemini-pro-vision")
                except google_exceptions.InvalidArgument as e:
                    if "API key not valid" in str(e):
                        st.error("API key not valid. Please pass a valid API key.")
                    else:
                        st.error("An error occurred. Please try again.")
                except Exception as e:
                    logging.error(e)
                    st.error("Error occurred. Please refresh your page and try again.")
            else:
                vision_message = [{"role": "user", "parts": [chat_message]}]
                st.warning(
                    "Since there is no uploaded image, the result is generated by the default gemini-pro model.")
                try:
                    res = get_response(vision_message)
                except google_exceptions.InvalidArgument as e:
                    if "API key not valid" in str(e):
                        st.error("API key not valid. Please pass a valid API key.")
                    else:
                        st.error("An error occurred. Please try again.")
                except Exception as e:
                    logging.error(e)
                    st.error("Error occurred. Please refresh your page and try again.")
        else:
            message.append(
                {"role": "user", "parts": [chat_message]},
            )
            try:
                res = get_response(message)
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please refresh your page and try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occurred. Please refresh your page and try again.")

        if res is not None:
            res_text = ""
            for chunk in res:
                if chunk.candidates:
                    res_text += chunk.text
                if res_text == "":
                    res_text = "unappropriate words"
                    st.error("Your words violate the rules that have been set. Please try again!")
            res_area.markdown(res_text)

            if select_model != "Image Consultancy":
                message.append({"role": "model", "parts": [res_text]})
 
    # st.title("Food Detection Chatbot")
    # st.write("Welcome to our food detection chatbot!")

    # # Add an image scanner
    # uploaded_image = st.file_uploader("Upload an image of your food", type=["png", "jpg"])
    # if uploaded_image:
    #     image_bytes = uploaded_image.read()
    #     st.image(image_bytes, caption="Uploaded Image")
    #     # image_data = image_bytes.decode("utf-8")
    #     try:
    #         image_data = image_bytes.decode("utf-8")
    #     except UnicodeDecodeError:
    #         image_data = image_bytes.decode("latin-1")
    #     # Add a chatbot
    #     st.header("Chat with our food detection bot")
    #     user_input = st.text_input("Ask our bot about your food")
    #     if user_input:
    #         api_url = "https://api.gemini.com/v1/food/detect"
    #         api_key = "AIzaSyCDdVJJrGLSKFN56TaPXEu_y6Vauvs7IKg"
    #         headers = {"Authorization": f"Bearer {api_key}"}
    #         data = json.dumps({"image": image_data, "text": user_input})
    #         response = requests.post(api_url, headers=headers, json=data)
    #         if response.status_code == 200:
    #             response_json = response.json()
    #             st.write("Bot:", response_json["message"])
    #         else:
    #             st.write("Error:", response.text)

    #         # Call your food detection API or model here
    #         response = "Sorry, our bot is still learning!"
    #         st.write("Bot:", response)

# Create an account page
elif page == "History":   
    st.title("History")
    # for item in message:
    #     role, parts = item.values()
    #     if role == "user":
    #         st.write(parts[0])
    #     elif role == "model":
    #         st.write(parts[0])
    
# Main function to run Streamlit app

# Create an about page
elif page == "About":
    st.title("About")
    st.write("This is our about page")

# Run the app
# if _name_ == "_main_":
#     st.write("Running the app...")
