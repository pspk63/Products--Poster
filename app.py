from flask import Flask, request, render_template_string
import os
import requests
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

BOT_TOKEN = '7116731852:AAGjUszBxmi5lK-RbOhKA9uyixxqs8YSOF4'
CHANNEL_IDS = ['@ShoppingZonefashion', '@StylespotZone', '@ElectronicGadgets_Ap', '@groceryzone']

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Post Form</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 400px;
        }
        h2 {
            margin-bottom: 20px;
            font-size: 24px;
        }
        input[type="text"], input[type="number"], textarea, input[type="file"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .channels {
            margin: 15px 0;
        }
        .channels label {
            display: block;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Create Telegram Post</h2>
        <form action="/post" method="post" enctype="multipart/form-data">
        
            <input type="file" name="image" accept="image/*" required>
            <input type="text" name="title" placeholder="Title" required>
            <textarea name="description" placeholder="Description" required></textarea>
            <div class="channels">
                <h3>Select Channels:</h3>
                <label><input type="checkbox" name="channels" value="@ShoppingZonefashion"> Shopping Zone Fashion</label>
                <label><input type="checkbox" name="channels" value="@StylespotZone"> Style Spot Zone</label>
                <label><input type="checkbox" name="channels" value="@ElectronicGadgets_Ap"> Electronic Gadgets</label>
                <label><input type="checkbox" name="channels" value="@groceryzone"> Grocery Zone</label>
            </div>
            <input type="number" name="mrp" placeholder="MRP" required>
            <input type="number" name="discount" placeholder="Discount" required>
            <input type="text" name="link" placeholder="Link" required>
            <button type="submit">Submit</button>
        </form>
    </div>
</body>
</html>
'''

def send_telegram_message(photo_path, title, description, mrp, discount, link, selected_channels):
    try:
        message = (
            f"🎉 <b>{title}</b> 🎉\n\n"
            f"📜 {description}\n\n"
            f"💰 <b>MRP:</b>\n"
            f"┌────────────────┐\n"
            f"│🇮🇳 <b>{mrp}</b> │<b> 💸Low Budget</b>\n"
            f"└────────────────┘\n"
            f"🔖 <b>Discount:</b>\n"
            f"┌────────────────┐\n"
            f"│🛍 <b>{discount}%OFF</b> │<b> Buy Now</b>\n"
            f"└────────────────┘\n\n"
        )

        for channel_id in selected_channels:
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': channel_id,
                    'caption': message,
                    'parse_mode': 'HTML',
                    'reply_markup': '{"inline_keyboard":[[{"text":"Order Now","url":"' + link + '"}]]}'
                }
                url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
                response = requests.post(url, files=files, data=data)

                # Log response from Telegram API for debugging
                if response.status_code != 200:
                    print(f"Error sending message to {channel_id}: {response.status_code}, {response.text}")
                else:
                    print(f"Message sent successfully to {channel_id}: {response.text}")

    except Exception as e:
        print(f"Exception in send_telegram_message: {str(e)}")

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/post', methods=['POST'])
def post():
    if 'image' not in request.files:
        return 'No image file', 400

    image = request.files['image']
    if image.filename == '':
        return 'No selected file', 400

    if image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)

        title = request.form['title']
        description = request.form['description']
        mrp = request.form['mrp']
        discount = request.form['discount']
        link = request.form['link']

        # Get selected channels from the form (list of channels)
        selected_channels = request.form.getlist('channels')

        # Start a new thread to send the Telegram message to the selected channels
        threading.Thread(target=send_telegram_message, args=(image_path, title, description, mrp, discount, link, selected_channels)).start()
        return 'Post created successfully', 200

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run()
