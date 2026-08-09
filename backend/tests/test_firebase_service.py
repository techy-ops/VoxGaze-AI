import asyncio
from app.services.firebase_service import FirebaseService


def test_firebase_service_crud_lifecycle():
    """
    Test FirebaseService create, profile persistence, lookup, last login update,
    and user deletion methods.
    """
    async def _async_test():
        svc = FirebaseService()
        email = "service_test@voxgaze.ai"
        password = "TestPassword123!"

        # 1. Create User
        user = await svc.create_user(email=email, password=password, display_name="Service Test User")
        assert user["email"] == email
        assert "uid" in user
        uid = user["uid"]

        # 2. Create User Profile in Firestore
        profile = await svc.create_user_profile(uid=uid, profile_data={"email": email, "display_name": "Service Test User"})
        assert profile["user_id"] == uid
        assert profile["role"] == "user"
        assert profile["profile_completed"] is True

        # 3. Fetch User Profile
        fetched_profile = await svc.get_user_profile(uid)
        assert fetched_profile["user_id"] == uid
        assert fetched_profile["email"] == email

        # 4. Update Last Login
        await svc.update_last_login(uid)
        updated_profile = await svc.get_user_profile(uid)
        assert "last_login" in updated_profile

        # 5. Delete User
        deleted = await svc.delete_user(uid)
        assert deleted is True

    asyncio.run(_async_test())
