import os
import requests
import json
import logging
import traceback
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the user request model for pet-related queries
class PetQuery(Model):
    user_message: str

class PetDetails(Model):
    type: str
    breed: str
    color: str
    gender: str

# Define the bot response model
class BotResponse(Model):
    bot_response: str

# Define the error response model
class ErrorResponse(Model):
    error: str

# Define the details response model
class PetAvailableResponse(Model):
    pet_details: dict

# Function to get chatbot response from OpenAI API
def get_openai_chatbot_response(user_message):
    url = "https://api.openai.com/v1/chat/completions"
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is not set in environment variables.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7,
        "max_tokens": 150,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.6
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "response": response.text if response else "No response"}

# Function to check for available pets in the app agent
def check_available_pets(pet_details):
    return {
        "type": pet_details.type,
        "breed": pet_details.breed,
        "color": pet_details.color,
        "gender": pet_details.gender,
        "price": 1500,
        "details": "Healthy and playful.",
        "availability": True
    }

# Define the PetChatbotAgent using uAgents
PetChatbotAgent = Agent(
    name="PetChatbotAgent",
    port=5001,
    seed="agent1qtcerwsk2zf4h824kkwvyp5pwzltx6dc98esdss6ek3ct3af5awyucameq5",
    endpoint=["http://127.0.0.1:5001/api/chat/"],
)

fund_agent_if_low(PetChatbotAgent.wallet.address())

@PetChatbotAgent.on_event('startup')
async def agent_details(ctx: Context):
    agent_address = PetChatbotAgent.address
    ctx.logger.info(f'Agent Address: {agent_address}')

@PetChatbotAgent.on_query(model=PetQuery, replies={BotResponse, ErrorResponse})
async def query_handler(ctx: Context, sender: str, msg: PetQuery):
    # Your query handling code

    try:
        if "buy pet" in msg.user_message.lower():
            await ctx.send(sender, BotResponse(bot_response="What type of pet are you looking for (e.g., dog, cat, bird)?"))
            user_response = await ctx.wait_for_response(sender)
            pet_type = user_response.bot_response

            await ctx.send(sender, BotResponse(bot_response="What breed are you interested in? (e.g., Husky)"))
            user_response = await ctx.wait_for_response(sender)
            pet_breed = user_response.bot_response

            await ctx.send(sender, BotResponse(bot_response="What color do you prefer? (e.g., black, brown)"))
            user_response = await ctx.wait_for_response(sender)
            pet_color = user_response.bot_response

            await ctx.send(sender, BotResponse(bot_response="What gender do you prefer? (male, female)"))
            user_response = await ctx.wait_for_response(sender)
            pet_gender = user_response.bot_response

            pet_details = PetDetails(
                type=pet_type,
                breed=pet_breed,
                color=pet_color,
                gender=pet_gender
            )

            available_pet = check_available_pets(pet_details)

            if "error" in available_pet:
                await ctx.send(sender, BotResponse(bot_response=available_pet["error"]))
            elif available_pet["availability"]:
                pet_info = f"We have a {available_pet['color']} {available_pet['breed']} ({available_pet['gender']}) available for ${available_pet['price']}.\nDetails: {available_pet['details']}"
                await ctx.send(sender, BotResponse(bot_response=pet_info))
            else:
                await ctx.send(sender, BotResponse(bot_response="Sorry, we don't have that pet available right now."))

        else:
            response = get_openai_chatbot_response(msg.user_message)
            if "error" in response:
                error_message = response["error"]
                logging.error(f"Error from OpenAI API: {error_message}")
                await ctx.send(sender, ErrorResponse(error=error_message))
                return

            bot_response = response.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, I couldn't understand your question about pets.")
            logging.info(f"Bot response: {bot_response}")
            await ctx.send(sender, BotResponse(bot_response=bot_response))

    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)
        await ctx.send(sender, ErrorResponse(error=error_message))

if __name__ == "__main__":
    PetChatbotAgent.run()
