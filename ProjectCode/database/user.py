class User():
    def __init__(self, id, username, password, designation):
        self.id = id
        self.username = username
        self.password = password
        self.designation = designation

    def __repr__(self):
        return "User name: " + self.username

users = []
users.append(User(id=100000001, username='Loknath', password='Loknath@123', designation='admission desk executive'))
users.append(User(id=100000002, username='Anjali', password='Anjali@123', designation='pharmacist'))
users.append(User(id=100000003, username='Ramesh', password='Ramesh@123', designation='diagnostics executive'))

