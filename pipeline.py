#!/usr/bin/env python
# coding: utf-8

# In[1]:


key_cv="3O8mtlO5GjV0CsYZcOG94ipWYC55LjG043Fc6xcM0dYX6DIMXiREJQQJ99BKACI8hq2XJ3w3AAAFACOGNhwV"
endpoint_cv="https://cv-ai-vision-ws.cognitiveservices.azure.com"

key_tr = "52i26gSYZlRF0WdzqYpMNUwlEah3uh8C5DlNGvSo7Cn2DcMShUUyJQQJ99BKACI8hq2XJ3w3AAAbACOGsclM"
endpoint_tr="https://api.cognitive.microsofttranslator.com"
location="switzerlandnorth"

gemini_api="AIzaSyDv8EkndE83hBkeBQaYh1PcLWD-SWT5Z9w"


# In[2]:


import requests
import uuid
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
# TASK 1: Analyzing images

def analyze_image(image_url):
    """Analyze image and extract caption + tags"""    
    analyze_url = f"{endpoint_cv}/vision/v3.2/analyze"
    headers = {"Ocp-Apim-Subscription-Key": key_cv}
    params = {"visualFeatures": "Description,Tags"}
    data = {"url": image_url}
    
    response = requests.post(analyze_url, headers=headers, params=params, json=data)
    result = response.json()
    
    # Extract caption
    caption = ""
    if 'description' in result:
        captions = result['description'].get("captions", [])
        if captions:
            caption = captions[0]['text']
    
    # Extract tags
    tags = []
    if 'tags' in result:
        tags = [tag['name'] for tag in result['tags']]
    
    # Create vision context summary
    vision_context = f"Image description: {caption}\nImage tags: {', '.join(tags)}"
    
    return vision_context, caption, tags, result


# In[3]:


image_url = "https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/media/quickstarts/presentation.png"
vision_context, caption, tags, result = analyze_image(image_url)
print(vision_context)


# In[4]:


get_ipython().system('pip install --upgrade google-generativeai')


# In[5]:


import sys

get_ipython().system('{sys.executable} -m pip install --upgrade google-generativeai')

 


# In[6]:


import google.generativeai as genai
genai.configure(api_key=gemini_api)


# In[7]:


model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Say 'Hello World'")
print(response.text)


# In[8]:


# TASK 2: Creative Text Generation
def generate_creative_content(vision_context):
    prompt = f"""
        Based on this image analysis: {vision_context}
        
        Write a short, imaginative and creative paragraph (3-4 sentences) describing or expanding on this image scene.
        Be descriptive, engaging, and tell a mini-story about what's happening.
        """
    return model.generate_content(prompt).text    



# In[9]:


text=generate_creative_content(vision_context)
print(text)


# In[10]:


# TASK 3: Style Transformation

def transform_style(original_text, target_style="arabic poetic"):
    """Rewrite text in a specific style"""
    print(f"🎨 Transforming to {target_style} style...")
    
    style_prompts = {
        "arabic poetic": f"Rewrite this paragraph in an elegant Arabic poetic style, using metaphorical language, rhythmic flow, and beautiful imagery:\n\n{original_text}",
        "marketing": f"Rewrite this as exciting marketing copy that would appear in a professional advertisement. Make it persuasive and engaging:\n\n{original_text}",
        "child story": f"Rewrite this as a friendly children's story with simple, magical language that a child would love:\n\n{original_text}",
        "news report": f"Rewrite this as a formal news report with professional, factual language:\n\n{original_text}"
    }
    
    prompt = style_prompts[target_style]
    
    return  model.generate_content(prompt).text




# In[11]:


transformed_text = transform_style(text,"marketing")
print(transformed_text)


# In[12]:


# Task 4 : translation
def translate_text(text, target_language='ar'):
    path = '/translate'
    constructed_url = endpoint_tr + path

    params = {
        'api-version': '3.0',
        'to': target_language
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key_tr,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': text}]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    
    translated_text = response[0]['translations'][0]['text']
    return translated_text

text_to_translate = "Hello world, this is a test translation!"
translated = translate_text(text_to_translate, 'ar')
print(translated)


# In[13]:


import sys

get_ipython().system('{sys.executable} -m pip install --upgrade gradio')

 


# In[14]:


import gradio as gr

def run_complete_pipeline(image_url, style_choice, target_language):
    """Complete pipeline from image to translated story"""
    try:
        # Task 1: Image Analysis
        vision_context, caption, tags, result = analyze_image(image_url)
        
        # Task 2: Creative Generation
        creative_text = generate_creative_content(vision_context)
        
        # Task 3: Style Transformation
        styled_text = transform_style(creative_text, style_choice)
        
        # Task 4: Translation
        translated_text = translate_text(styled_text, target_language)
        
        # Display image
        response_image = requests.get(image_url)
        img = Image.open(BytesIO(response_image.content))
        
        return (
            vision_context,
            creative_text,
            styled_text,
            translated_text,
            img
        )
        
    except Exception as e:
        return f"Error: {str(e)}", "", "", "", None

# Create Gradio interface
with gr.Blocks(title="AI Image to Multilingual Story") as demo:
    gr.Markdown("# 🎨 AI Image to Multilingual Story Pipeline")
    gr.Markdown("Transform any image into a creative story, style it, and translate it!")
    
    with gr.Row():
        with gr.Column():
            image_url = gr.Textbox(
                label="🌐 Image URL", 
                placeholder="Paste image URL here...",
                info="Use a publicly accessible image URL"
            )
            
            style_choice = gr.Dropdown(
                choices=["arabic poetic", "marketing", "child story", "news report"],
                label="🎭 Select Style",
                value="arabic poetic",
                info="Choose the writing style"
            )
            
            target_language = gr.Dropdown(
                choices=["ar", "fr", "es", "de", "it", "ja", "ko", "zh-Hans"],
                label="🌍 Target Language",
                value="ar",
                info="Select translation language"
            )
            
            generate_btn = gr.Button("🚀 Generate Story", variant="primary")
        
        with gr.Column():
            output_image = gr.Image(
                label="🖼️ Input Image", 
                height=300,
                interactive=False
            )
    
    with gr.Row():
        with gr.Column():
            vision_output = gr.Textbox(
                label="🔍 Vision Analysis", 
                lines=3,
                max_lines=5
            )
            creative_output = gr.Textbox(
                label="✍️ Creative Paragraph", 
                lines=4,
                max_lines=6
            )
        
        with gr.Column():
            styled_output = gr.Textbox(
                label="🎨 Styled Text", 
                lines=4,
                max_lines=6
            )
            translated_output = gr.Textbox(
                label="🌍 Translated Text", 
                lines=4,
                max_lines=6
            )
    
    # Connect the button to the function
    generate_btn.click(
        fn=run_complete_pipeline,
        inputs=[image_url, style_choice, target_language],
        outputs=[vision_output, creative_output, styled_output, translated_output, output_image]
    )
    
    # Examples
    gr.Examples(
        examples=[
            ["https://picsum.photos/800/600", "arabic poetic", "ar"],
            ["https://images.unsplash.com/photo-1575936123452-b67c3203c357", "marketing", "fr"],
            ["https://picsum.photos/800/600?nature", "child story", "es"]
        ],
        inputs=[image_url, style_choice, target_language],
        outputs=[vision_output, creative_output, styled_output, translated_output, output_image],
        fn=run_complete_pipeline,
        cache_examples=False
    )

# Launch the interface
demo.launch(share=True)


# In[ ]:




