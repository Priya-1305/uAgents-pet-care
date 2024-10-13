import requests
import firebase_admin
from firebase_admin import credentials, firestore
from uagents import Agent, Context, Model
from datetime import datetime, timedelta

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Your Firebase service account key
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define models for the admin agent
class AdminConfirmation(Model):
    pet_id: str
    user_id: str
    delivery_option: str

# Simulated eCommerce API call to get delivery details
def get_delivery_details(delivery_option):
    # Simulating a call to an eCommerce API
    delivery_time = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')  # Example: 3 days delivery
    return delivery_time

# Update pet status in Firestore to prevent further bookings
def update_pet_status(pet_id):
    pet_ref = db.collection('pets').document(pet_id)
    pet_ref.update({'available': False})

# Update the 'my orders' section in Firestore
def update_order_section(pet_id, user_id, delivery_time):
    db.collection('orders').add({
        'pet_id': pet_id,
        'user_id': user_id,
        'delivery_time': delivery_time,
        'status': 'Confirmed',
        'timestamp': datetime.now()
    })

# Handle purchase confirmation from the app agent
@AppAgent.on_query(model=AdminConfirmation)
async def confirmation_handler(ctx: Context, sender: str, msg: AdminConfirmation):
    try:
        ctx.logger.info(f"Received confirmation for pet ID: {msg.pet_id} from User ID: {msg.user_id}")

        # Get delivery details
        delivery_time = get_delivery_details(msg.delivery_option)

        # Update the 'my orders' section in Firestore
        update_order_section(msg.pet_id, msg.user_id, delivery_time)
        ctx.logger.info(f"Order updated in Firestore for pet ID: {msg.pet_id}")

        # Update pet status to prevent further bookings
        update_pet_status(msg.pet_id)
        ctx.logger.info(f"Updated pet status to unavailable for pet ID: {msg.pet_id}")

        # Notify the app UI via Firestore or another method if needed
        # For example, you could use Firestore triggers or cloud functions to notify the app.

    except Exception as e:
        ctx.logger.error(f"Error processing admin confirmation: {str(e)}")

# Run the agent
if __name__ == "_main_":
    AdminAgent = Agent(
        name="AdminAgent",
        port=8005,
        seed="Admin Agent secret phrase",
        endpoint=["http://127.0.0.1:8005/submit"],
    )
    AdminAgent.run()