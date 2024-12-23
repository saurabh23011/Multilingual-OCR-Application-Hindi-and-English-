# import streamlit as st
# from PIL import Image
# import easyocr
# import numpy as np
# import re

# # Set page configuration
# st.set_page_config(page_title="Multilingual OCR Application", layout="wide")

# # Title of the application
# st.title("Multilingual OCR Application (Hindi and English)")

# # Instructions
# st.markdown("""
# Upload an image containing text in Hindi and/or English. The application will extract the text and allow you to search for keywords within the extracted content.
# """)

# # Sidebar for image upload
# st.sidebar.header("Upload Image")
# uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# # Function to highlight keywords
# def highlight_text(text, keyword):
#     highlighted_text = re.sub(f'({keyword})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
#     return highlighted_text

# if uploaded_file is not None:
#     # Display uploaded image
#     image = Image.open(uploaded_file)
#     st.image(image, caption='Uploaded Image', use_column_width=True)

#     # Convert image to array
#     image_np = np.array(image)

#     # Initialize OCR reader
#     reader = easyocr.Reader(['en', 'hi'], gpu=False)

#     # Perform OCR
#     with st.spinner('Extracting text...'):
#         result = reader.readtext(image_np)

#     # Combine text from result
#     extracted_text = ' '.join([item[1] for item in result])

#     # Display extracted text
#     st.subheader("Extracted Text")
#     st.write(extracted_text)

#     # Search functionality
#     st.subheader("Search within Extracted Text")
#     keyword = st.text_input("Enter keyword to search")

#     if keyword:
#         if re.search(keyword, extracted_text, re.IGNORECASE):
#             st.markdown("**Search Results:**")
#             highlighted = highlight_text(extracted_text, keyword)
#             st.markdown(highlighted, unsafe_allow_html=True)
#         else:
#             st.write("No matches found.")
# app.py
from flask import Flask, render_template, request, jsonify
import easyocr
import numpy as np
from PIL import Image
import io
import re
import base64

app = Flask(__name__)

# Initialize OCR reader globally to avoid reinitializing for each request
reader = easyocr.Reader(['en', 'hi'], gpu=False)

def highlight_text(text, keyword):
    if not keyword:
        return text
    return re.sub(f'({re.escape(keyword)})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Read and process the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Perform OCR
        result = reader.readtext(image_np)
        extracted_text = ' '.join([item[1] for item in result])
        
        # Convert image to base64 for display
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'image': f'data:image/jpeg;base64,{img_str}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search_text():
    data = request.get_json()
    text = data.get('text', '')
    keyword = data.get('keyword', '')
    
    highlighted_text = highlight_text(text, keyword)
    has_matches = bool(re.search(keyword, text, re.IGNORECASE))
    
    return jsonify({
        'highlighted_text': highlighted_text,
        'has_matches': has_matches
    })

if __name__ == '__main__':
    app.run(debug=True)