# %%
import requests
import os 

def send_slack_message(text: str):
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print("✅ Slack message sent")
    else:
        print(f"❌ Failed to send message: {response.text}")


if __name__ == "__main__":
    payload = {
        "text": (
            "🏡 *New Rental Listing!*\n\n"
            "📍 *Address*: Prinsengracht 123, Amsterdam\n"
            "💰 *Price*: €1,950 / month\n"
            "📏 *Size*: 75 m²\n"
            "🔗 <https://example.com/listing/12345|View Listing>"
        )
    }

    send_slack_message(payload["text"])
