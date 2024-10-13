# Function to get chatbot response from OpenAI API (pet-related queries)
def get_openai_chatbot_response(user_message):
    url = "https://api.openai.com/v1/chat/completions"