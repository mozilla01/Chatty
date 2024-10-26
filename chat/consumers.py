from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Room, Message, Tags, Domain
import json
from together import Together

client = Together()

def get_tags(query):
    all_tags = Tags.objects.all()
    all_domains = Domain.objects.all()
    tags_string = ''
    domain_string = ''
    for tag in all_tags:
        tags_string += tag.name + ',' if tag != all_tags.last() else tag.name
    for domain in all_domains:
        domain_string += domain.name + ',' if domain != all_domains.last() else domain.name
    prompt = f"""
        You will be given a question. Provide comma separated tags and one domain for the question. Don't write anything else. Just write the tags and the domain in this format: Tags separated by commas followed by a semicolon and then the domain. For example: <tag1>,<tag2>,<tag3>,...;<domain>. The domain must be a general term that encompasses all the tags.
        You can use the following tags or create your own: {tags_string}
        You can use the following domains or create your own: {domain_string}
    """
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        messages=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': query}],
        max_tokens=100,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content.split(";")

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"].lower()
        if not Room.objects.filter(name=self.room_name).exists():
            room = Room.objects.create(name=self.room_name, host=self.scope["user"])
            room.save()
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        message_split = message.split(" ")
        query = False
        if message_split[0] == "/query" and Room.objects.get(name=self.room_name).host == self.scope["user"]:
            query = True
            message = " ".join(message_split[1:])
        author = text_data_json["author"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message, "author": author}
        )
        information = None
        if query:
            print('Getting tags...')
            information = get_tags(message)
        print('Tags:', information)

        # Save message to database
        room = Room.objects.get(name=self.room_name)
        if query:
            for tag in information[0].split(","):
                tag = "-".join(tag.strip().lower().split(" "))
                tag_obj = None
                if Tags.objects.filter(name=tag).exists():
                    tag_obj = Tags.objects.get(name=tag)
                else:
                    domain = None
                    if not Domain.objects.filter(name=information[1].strip()).exists():
                        domain = Domain.objects.create(name=information[1].strip())
                        domain.save()
                    else:
                        domain = Domain.objects.get(name=information[1].strip())
                    tag_obj = Tags.objects.create(name=tag, domain=domain)
                tag_obj.rooms.add(room)
                tag_obj.users.add(self.scope["user"])
                tag_obj.save()
        
        Message.objects.create(
            room=room, author=self.scope["user"], content=message, query=query
        ).save()

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        author = event["author"] 

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "author": author}))
