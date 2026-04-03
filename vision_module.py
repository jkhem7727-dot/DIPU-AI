import base64
import pyautogui
from groq import Groq

# Tapaiko Groq API Key yahan halnu
client = Groq(api_key="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") 

def get_screen_analysis():
    try:
        # 1. Screenshot line
        screenshot_path = "screen_view.png"
        pyautogui.screenshot(screenshot_path)
        
        # 2. Image lai Base64 ma convert garne
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 3. Groq Vision Model call garne (FREE Tier)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe exactly what is on this screen in 2 short, friendly sentences. Mention open apps or code if visible."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry baby, I can't see the screen clearly. Error: {e}"
    
    
    
    
    