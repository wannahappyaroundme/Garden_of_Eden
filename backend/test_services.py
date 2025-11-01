"""
Quick test script to verify all services are working
Run this after setup to ensure everything is configured correctly
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_services():
    """Test all core services"""
    print("🧪 Testing Project Eden V2 Services")
    print("=" * 50)
    print()

    # Test 1: Environment Variables
    print("1️⃣ Testing Environment Variables...")
    required_vars = ["GEMINI_API_KEY", "GROQ_API_KEY", "AWS_REGION"]
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"   ❌ {var} not set")
        else:
            print(f"   ✅ {var} is set")

    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("Please add them to your .env file\n")
        return
    else:
        print("   ✅ All required environment variables present\n")

    # Test 2: Gemini LLM Service
    print("2️⃣ Testing Gemini LLM Service...")
    try:
        from services.llm_gemini_v2 import GeminiService

        llm = GeminiService()
        print("   ✅ Gemini service initialized")

        # Simple test
        topic = await llm.extract_topic_from_text("I want to learn React Native")
        print(f"   ✅ Topic extraction works: '{topic}'\n")

    except Exception as e:
        print(f"   ❌ Gemini service failed: {e}\n")
        return

    # Test 3: TTS Service
    print("3️⃣ Testing Edge TTS Service...")
    try:
        from services.tts_service import TTSService
        from utils.constants import PersonaType

        tts = TTSService()
        print("   ✅ TTS service initialized")

        # Generate sample audio
        audio_path = await tts.generate_speech(
            text="테스트입니다",
            persona=PersonaType.ADAM
        )

        if audio_path and os.path.exists(audio_path):
            print(f"   ✅ TTS generation works: {audio_path}")
            # Clean up
            try:
                os.remove(audio_path)
            except:
                pass
        else:
            print("   ❌ TTS generation failed")

        print()

    except Exception as e:
        print(f"   ❌ TTS service failed: {e}\n")

    # Test 4: DynamoDB Service (connection only)
    print("4️⃣ Testing DynamoDB Service...")
    try:
        from services.dynamodb_service_v2 import DynamoDBService

        db = DynamoDBService()
        print("   ✅ DynamoDB service initialized")

        # Try to get a profile (will return None if doesn't exist)
        profile = await db.get_user_profile("test_user_12345")

        if profile is None:
            print("   ✅ DynamoDB connection works (profile not found is expected)")
        else:
            print(f"   ✅ DynamoDB connection works (found profile version {profile.profile_version})")

        print()

    except Exception as e:
        print(f"   ⚠️  DynamoDB service warning: {e}")
        print("   Note: Make sure tables are created: python -m services.dynamodb_service_v2\n")

    # Test 5: User Profile Models
    print("5️⃣ Testing User Profile Models...")
    try:
        from models.user_profile import UserProfile, OneThing, PersonalityTrait

        profile = UserProfile(
            user_id="test_user",
            profile_version=1
        )

        profile.one_thing = OneThing(
            value="Test goal",
            confidence=0.8,
            sub_goals=[]
        )

        profile.add_trait("test_trait", initial_weight=0.7, evidence="Test evidence")

        context = profile.to_context_string()
        print("   ✅ User profile models work")
        print(f"   ✅ Profile context generation works ({len(context)} chars)\n")

    except Exception as e:
        print(f"   ❌ User profile models failed: {e}\n")

    # Test 6: Master Directive Prompts
    print("6️⃣ Testing Master Directive Prompts...")
    try:
        from prompts.master_directive import build_master_directive

        prompt = build_master_directive(
            user_message="Test message",
            user_profile_context="Test profile",
            persona_name="Adam",
            recent_memory="No memory",
            visual_context="No visual",
            one_thing="Test goal",
            core_pitfall="Test pitfall",
            pitfall_triggers="None",
            detected_topic="Test",
            mode_specific_instructions=""
        )

        print("   ✅ Master Directive prompt generation works")
        print(f"   ✅ Prompt length: {len(prompt)} chars\n")

    except Exception as e:
        print(f"   ❌ Master Directive prompts failed: {e}\n")

    # Summary
    print("=" * 50)
    print("✅ Core services test complete!")
    print()
    print("Next steps:")
    print("1. Create DynamoDB tables (if not done): python -m services.dynamodb_service_v2")
    print("2. Run the server: python main.py")
    print("3. Test API: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    asyncio.run(test_services())
