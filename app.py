import json
import logging
from quart import Quart, request, jsonify
from quart_cors import cors
from firebase_admin import firestore, credentials, initialize_app
from uagents.query import query
from uagents import Model


chat_agent_address = 'agent1qtcerwsk2zf4h824kkwvyp5pwzltx6dc98esdss6ek3ct3af5awyucameq5'  # This seems to be the agent ID

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Quart application
app = Quart(__name__)
app = cors(app, allow_origin="http://127.0.0.1:5000/api/chat/")

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Agent address for pet-related queries


# Define models for pet-related queries
class ChatbotRequest(Model):
    user_message: str

class PetQueryResponse(Model):
    bot_response: str

@app.route('/')
async def home() -> str:
    return "Welcome to the E-commerce Agent!"

@app.route('/api/test-chat/', methods=['GET'])
async def test_chat_with_bot():
    try:
        # Prepare a simple test message
        test_message = "Hello, agent! This is a test message."
        logger.info("Sending test query to chat agent with message: %s", test_message)

        # Send the test query to the agent
        response = await query(destination=chat_agent_address, message=ChatbotRequest(user_message=test_message), timeout=240.0)

        if response is None:
            raise ValueError("Received no response from the agent")

        # Decode and log the agent's response
        response_data = json.loads(response.decode_payload())
        logger.info("Received test response from chat agent: %s", response_data)

        # Return the agent's response to the frontend
        return jsonify({'response': response_data.get('bot_response', 'No valid response received')})

    except Exception as e:
        logger.error("Error occurred during test query: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
async def submit() -> jsonify:
    try:
        data = await request.json
        # You can process the incoming data as needed
        response = {"message": "Response from agent", "data_received": data}
        return jsonify(response)

    except Exception as e:
        logger.error("Error occurred during submission: %s", e)
        return jsonify({'error': str(e)}), 500

# Route for pet-related chatbot queries
@app.route('/api/chat/', methods=['POST'])
async def chat_with_bot() -> jsonify:
    try:
        data = await request.json
        user_message = data.get('user_message', '')

        if not user_message:
            return jsonify({'error': 'User message is required'}), 400

        logger.info("Sending query to chat agent with user message: %s", user_message)

        # Update agent address to the correct endpoint
        chat_agent_address = 'agent1qf8tzekvqptgzaj470zw5zy4ts3ezurx9cypqg2kur3y5g2740wakjgsnt0'  # Ensure this is correct
        logger.info("Constructed agent address: %s", chat_agent_address)

        # Send the query to the agent
        response = await query(destination=chat_agent_address, message=ChatbotRequest(user_message=user_message), timeout=240.0)

        if response is None:
            raise ValueError("Received no response from the agent")

        response_data = json.loads(response.decode_payload())
        logger.info("Received response from chat agent: %s", response_data)

        if isinstance(response_data, dict) and 'error' in response_data:
            raise ValueError(response_data['error'])

        return jsonify({'response': response_data.get('bot_response', 'No valid response received')})

    except Exception as e:
        logger.error("Error occurred while handling chat request: %s", e)
        return jsonify({'error': str(e)}), 500



        # Add email to Firebase
        db.collection('subscribers').add({'email': email})

        logger.info("Subscribed email: %s", email)
        return jsonify({'message': 'Subscription successful!'}), 200

    except Exception as e:
        logger.error("Error occurred during subscription: %s", e)
        return jsonify({'error': str(e)}), 500

# Run the Quart app
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
