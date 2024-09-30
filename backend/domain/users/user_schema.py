def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "fullname": user["fullname"],
            "email": user["email"],
            "disabled": user["disabled"],
            "premium": user["premium"],
            "password": user["password"]
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users]
