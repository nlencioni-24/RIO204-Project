from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserReward(db.Model):
    __tablename__ = 'user_rewards'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "username": self.username,
            "points": self.points
        }

class RoomStatus(db.Model):
    __tablename__ = 'room_status'

    room_id = db.Column(db.Integer, primary_key=True)
    occupancy = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "occupancy": self.occupancy
        }
