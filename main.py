from chatbot import DualChatbot

def main():
    role_dict = {
        'role1': {'name': 'Customer', 'action': 'ordering food'},
        'role2': {'name': 'Waitstaff', 'action': 'taking the order'}
    }

    chatbot = DualChatbot(
        engine="OpenAI",
        role_dict=role_dict,
        language="English",
        scenario="at a restaurant",
        proficiency_level="Beginner",
        learning_mode="Conversation",
        session_length="Short"
    )

    print("Starting the conversation...")

    for _ in range(8):  # Short conversation
        output1, output2, translate1, translate2 = chatbot.step()
        print(f"Customer: {output1}")
        print(f"Translation: {translate1}")
        print(f"Waitstaff: {output2}")
        print(f"Translation: {translate2}")

if __name__ == "__main__":
    main()
