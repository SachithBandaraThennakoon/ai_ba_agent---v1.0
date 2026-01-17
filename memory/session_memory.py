class SessionMemory:
    def __init__(self):
        self.messages = []
        self.confirmed = False

    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })

    def get(self):
        return self.messages

    def confirm(self):
        self.confirmed = True

    def is_confirmed(self):
        return self.confirmed
