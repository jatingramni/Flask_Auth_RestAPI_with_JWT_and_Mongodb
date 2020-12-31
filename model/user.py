class User(object):
    def __init__(self, id, email, username, password):
        self.id = id
        self.email = email
        self.username = username
        self.password = password
    
    def __str__(self):
      return f"User id: {self.id}"
    