import os
import json
from firebase_admin import firestore, credentials, initialize_app
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Define the model for the request to search for pet data
class PetSearchRequest(Model):
    pet_type: str
    breed: str

# Define the model for the response with pet details
class PetDetailsResponse(Model):
    pet_type: str
    breed: str
    price: int
    description: str
    image_url: str
    availability: bool

# Define the error response model
class ErrorResponse(Model):
    error: str

# Create the AppAgent using uAgents
AppAgent = Agent(
    name="AppAgent",
    port=5003,  # Different port from UserAgent
    seed="agent1qf8tzekvqptgzaj470zw5zy4ts3ezurx9cypqg2kur3y5g2740wakjgsnt0",
    endpoint=["http://127.0.0.1:5003/api/app/"],  # Make sure this matches your backend
)

# Ensure the agent has enough funds for operations (if needed)
fund_agent_if_low(AppAgent.wallet.address())

@AppAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'AppAgent Address is {AppAgent.address}')

# Handle incoming queries for pet data
# ... (previous imports remain the same)

@AppAgent.on_query(model=PetSearchRequest, replies={PetDetailsResponse, ErrorResponse})
async def query_handler(ctx: Context, sender: str, msg: PetSearchRequest):
    try:
        ctx.logger.info(f"Searching for pet: Type={msg.pet_type}, Breed={msg.breed}")
        
        # Fetch data from Firebase Firestore
        pet_ref = db.collection('pets').document(msg.pet_type).collection(msg.breed).get()
        
        if not pet_ref:
            ctx.logger.error(f"Pet not found in database for Type={msg.pet_type}, Breed={msg.breed}")
            await ctx.send(sender, ErrorResponse(error="Pet not found in database."))
            return
        
        pet_data = pet_ref[0].to_dict()  # No need to check again if pet_ref is not empty

        ctx.logger.info(f"Pet found: {pet_data}")
        # Send the details of the pet back to the UserAgent
        await ctx.send(sender, PetDetailsResponse(
            pet_type=msg.pet_type,
            breed=msg.breed,
            price=pet_data.get('price', 0),
            description=pet_data.get('description', 'No description available.'),
            image_url=pet_data.get('image_url', ''),
            availability=pet_data.get('availability', False)
        ))

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorResponse(error=error_message))

# Run the AppAgent
if __name__ == "__main__":
    AppAgent.run()
