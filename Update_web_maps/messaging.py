class messaging(object):
    queue = [ # dictionary of messages to send to each owner when we're all done
        { "recipient": "bwilson", "messages": ["How are things going?"]}
    ]

    def __init__(self):
        return

    def add(self, recipient:str, message:str) -> None:
        """ Add a "message" for "recipient" to the queue. """

        if recipient in self.queue:
            return

        return

    def send(self) -> bool:
        """ Send all the accumulated messages. """
        for item in self.queue:
            print(item['recipient'], item['messages']) 
        return True

# ======================================================================================================

if __name__ == "__main__":

    mq = messaging()
    mq.add('bwilson', "We're having a lovely day.")
    mq.send()

