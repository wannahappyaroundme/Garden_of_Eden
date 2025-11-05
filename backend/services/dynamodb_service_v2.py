"""
DynamoDB Service for Project Eden V2
Handles all database operations for user profiles, conversations, and learning events
"""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from models.user_profile import UserProfile, PersonalityTrait, OneThing, CoreElement, CorePitfall
from models.conversation import Conversation, LearningEvent
from models.goal_progress import GoalProgressTracker, ProgressSnapshot, Milestone
from utils.logger import get_logger
from utils.constants import get_profile_maturity

logger = get_logger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal to float"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def python_to_dynamodb(obj: Any) -> Any:
    """Convert Python floats to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: python_to_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [python_to_dynamodb(item) for item in obj]
    return obj


def dynamodb_to_python(obj: Any) -> Any:
    """Convert DynamoDB Decimal to Python float"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: dynamodb_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dynamodb_to_python(item) for item in obj]
    return obj


class DynamoDBService:
    """Service for interacting with DynamoDB tables"""

    def __init__(
        self,
        region_name: str = "us-east-1",
        profiles_table_name: str = "eden_user_profiles_v2",
        conversations_table_name: str = "eden_conversations_raw",
        learning_events_table_name: str = "eden_learning_events",
        goal_progress_table_name: str = "eden_goal_progress"
    ):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)

        self.profiles_table = self.dynamodb.Table(profiles_table_name)
        self.conversations_table = self.dynamodb.Table(conversations_table_name)
        self.learning_events_table = self.dynamodb.Table(learning_events_table_name)
        self.goal_progress_table = self.dynamodb.Table(goal_progress_table_name)

        logger.info(f"DynamoDB service initialized for region: {region_name}")

    # ==================== User Profile Operations ====================

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        try:
            response = self.profiles_table.get_item(Key={'user_id': user_id})

            if 'Item' not in response:
                logger.info(f"Profile not found for user: {user_id}")
                return None

            # Convert DynamoDB item to UserProfile
            item = dynamodb_to_python(response['Item'])
            profile = UserProfile(**item)

            logger.info(f"Retrieved profile for user {user_id}, version {profile.profile_version}")
            return profile

        except ClientError as e:
            logger.error(f"Error retrieving profile for {user_id}: {e}")
            return None

    async def create_user_profile(self, user_id: str, one_thing: Optional[str] = None) -> UserProfile:
        """Create a new user profile"""
        try:
            profile = UserProfile(
                user_id=user_id,
                profile_version=1,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )

            # Set initial One Thing if provided
            if one_thing:
                profile.one_thing = OneThing(
                    value=one_thing,
                    confidence=0.7,
                    sub_goals=[]
                )

            # Save to DynamoDB
            await self.save_user_profile(profile)

            logger.info(f"Created new profile for user: {user_id}")
            return profile

        except ClientError as e:
            logger.error(f"Error creating profile for {user_id}: {e}")
            raise

    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Save or update user profile"""
        try:
            # Convert to dict and handle datetime/Decimal conversion
            profile_dict = json.loads(profile.json())
            profile_dict = python_to_dynamodb(profile_dict)

            # Update timestamp
            profile_dict['last_updated'] = datetime.now().isoformat()

            self.profiles_table.put_item(Item=profile_dict)

            logger.info(f"Saved profile for user {profile.user_id}, version {profile.profile_version}")
            return True

        except ClientError as e:
            logger.error(f"Error saving profile for {profile.user_id}: {e}")
            return False

    async def get_or_create_profile(self, user_id: str, one_thing: Optional[str] = None) -> UserProfile:
        """Get existing profile or create new one"""
        profile = await self.get_user_profile(user_id)

        if profile is None:
            profile = await self.create_user_profile(user_id, one_thing)

        return profile

    # ==================== Conversation Operations ====================

    async def save_conversation(self, conversation: Conversation) -> bool:
        """Save conversation to DynamoDB"""
        try:
            conv_dict = json.loads(conversation.json())
            conv_dict = python_to_dynamodb(conv_dict)

            self.conversations_table.put_item(Item=conv_dict)

            logger.info(f"Saved conversation {conversation.conversation_id}")
            return True

        except ClientError as e:
            logger.error(f"Error saving conversation {conversation.conversation_id}: {e}")
            return False

    async def get_recent_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Conversation]:
        """Get recent conversations for a user"""
        try:
            response = self.conversations_table.query(
                IndexName='UserIdIndex',  # Requires GSI
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )

            conversations = []
            for item in response.get('Items', []):
                item = dynamodb_to_python(item)
                conv = Conversation(**item)
                conversations.append(conv)

            logger.info(f"Retrieved {len(conversations)} recent conversations for {user_id}")
            return conversations

        except ClientError as e:
            logger.error(f"Error retrieving conversations for {user_id}: {e}")
            return []

    # ==================== Learning Events Operations ====================

    async def log_learning_event(
        self,
        user_id: str,
        event_type: str,
        description: str,
        profile_version: int,
        conversation_id: Optional[str] = None,
        changes: Dict = None
    ) -> bool:
        """Log a learning event"""
        try:
            event = LearningEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                timestamp=datetime.now(),
                event_type=event_type,
                description=description,
                profile_version=profile_version,
                conversation_id=conversation_id,
                changes=changes or {}
            )

            event_dict = json.loads(event.json())
            event_dict = python_to_dynamodb(event_dict)

            self.learning_events_table.put_item(Item=event_dict)

            logger.debug(f"Logged learning event: {event_type} for user {user_id}")
            return True

        except ClientError as e:
            logger.error(f"Error logging learning event for {user_id}: {e}")
            return False

    async def get_learning_events(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[LearningEvent]:
        """Get learning events for a user"""
        try:
            response = self.learning_events_table.query(
                IndexName='UserIdIndex',  # Requires GSI
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )

            events = []
            for item in response.get('Items', []):
                item = dynamodb_to_python(item)
                event = LearningEvent(**item)
                events.append(event)

            logger.info(f"Retrieved {len(events)} learning events for {user_id}")
            return events

        except ClientError as e:
            logger.error(f"Error retrieving learning events for {user_id}: {e}")
            return []

    # ==================== Goal Progress Operations ====================

    async def save_goal_progress(self, tracker: GoalProgressTracker) -> bool:
        """Save or update goal progress tracker"""
        try:
            item = python_to_dynamodb(tracker.to_dict())
            self.goal_progress_table.put_item(Item=item)
            logger.info(f"Saved goal progress for user {tracker.user_id}, goal {tracker.goal_id}")
            return True

        except ClientError as e:
            logger.error(f"Error saving goal progress for {tracker.user_id}: {e}")
            return False

    async def get_goal_progress(self, user_id: str) -> Optional[GoalProgressTracker]:
        """Get goal progress tracker by user_id"""
        try:
            response = self.goal_progress_table.get_item(Key={'user_id': user_id})

            if 'Item' not in response:
                logger.info(f"Goal progress not found for user: {user_id}")
                return None

            # Convert DynamoDB item to GoalProgressTracker
            item = dynamodb_to_python(response['Item'])
            tracker = GoalProgressTracker.from_dict(item)

            logger.info(f"Retrieved goal progress for user {user_id}")
            return tracker

        except ClientError as e:
            logger.error(f"Error retrieving goal progress for {user_id}: {e}")
            return None

    async def add_progress_snapshot(
        self,
        user_id: str,
        snapshot: ProgressSnapshot
    ) -> bool:
        """Add a progress snapshot to user's goal tracker"""
        try:
            # Get existing tracker
            tracker = await self.get_goal_progress(user_id)
            if not tracker:
                logger.warning(f"Cannot add snapshot - no goal tracker found for {user_id}")
                return False

            # Add snapshot
            tracker.add_snapshot(snapshot)

            # Save updated tracker
            return await self.save_goal_progress(tracker)

        except Exception as e:
            logger.error(f"Error adding progress snapshot for {user_id}: {e}")
            return False

    async def update_milestone(
        self,
        user_id: str,
        milestone_id: str,
        is_completed: bool
    ) -> bool:
        """Update milestone completion status"""
        try:
            # Get existing tracker
            tracker = await self.get_goal_progress(user_id)
            if not tracker:
                logger.warning(f"Cannot update milestone - no goal tracker found for {user_id}")
                return False

            # Update milestone
            if is_completed:
                success = tracker.complete_milestone(milestone_id)
            else:
                # Uncomplete milestone
                milestone = tracker.get_milestone(milestone_id)
                if milestone:
                    milestone.is_completed = False
                    milestone.completed_date = None
                    success = True
                else:
                    success = False

            if not success:
                logger.warning(f"Milestone {milestone_id} not found for user {user_id}")
                return False

            # Save updated tracker
            return await self.save_goal_progress(tracker)

        except Exception as e:
            logger.error(f"Error updating milestone for {user_id}: {e}")
            return False

    async def get_progress_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[ProgressSnapshot]:
        """Get progress snapshots from last N days"""
        try:
            tracker = await self.get_goal_progress(user_id)
            if not tracker:
                return []

            return tracker.get_recent_snapshots(days)

        except Exception as e:
            logger.error(f"Error retrieving progress history for {user_id}: {e}")
            return []

    # ==================== Helper Methods ====================

    def format_profile_summary(self, profile: UserProfile) -> dict:
        """Format profile for API response"""
        top_traits = profile.get_top_traits(5)

        recent_emotion = None
        if profile.emotional_patterns.recent_states:
            latest = profile.emotional_patterns.recent_states[-1]
            recent_emotion = f"{latest.state} ({latest.intensity:.1f})"

        return {
            "user_id": profile.user_id,
            "profile_version": profile.profile_version,
            "one_thing": profile.one_thing.value if profile.one_thing else None,
            "core_pitfall": profile.core_pitfall.value if profile.core_pitfall else None,
            "personality_summary": {
                "top_traits": [
                    {"name": trait.name, "weight": trait.weight}
                    for trait in top_traits
                ]
            },
            "recent_emotional_state": recent_emotion,
            "total_conversations": profile.meta_learning.total_conversations,
            "profile_maturity": get_profile_maturity(profile.meta_learning.total_conversations).value,
            "last_updated": profile.last_updated.isoformat()
        }


# ==================== Table Creation Scripts ====================

def create_tables():
    """
    Create DynamoDB tables (run once for setup)
    Note: This should be run separately, not in production code
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Create Profiles Table
    try:
        profiles_table = dynamodb.create_table(
            TableName='eden_user_profiles_v2',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating profiles table...")
        profiles_table.wait_until_exists()
        print("Profiles table created!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Profiles table already exists")
        else:
            raise

    # Create Conversations Table
    try:
        conversations_table = dynamodb.create_table(
            TableName='eden_conversations_raw',
            KeySchema=[
                {'AttributeName': 'conversation_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'conversation_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating conversations table...")
        conversations_table.wait_until_exists()
        print("Conversations table created!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Conversations table already exists")
        else:
            raise

    # Create Learning Events Table
    try:
        learning_events_table = dynamodb.create_table(
            TableName='eden_learning_events',
            KeySchema=[
                {'AttributeName': 'event_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'event_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating learning events table...")
        learning_events_table.wait_until_exists()
        print("Learning events table created!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Learning events table already exists")
        else:
            raise

    # Create Goal Progress Table
    try:
        goal_progress_table = dynamodb.create_table(
            TableName='eden_goal_progress',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating goal progress table...")
        goal_progress_table.wait_until_exists()
        print("Goal progress table created!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Goal progress table already exists")
        else:
            raise


if __name__ == "__main__":
    # Run this script directly to create tables
    create_tables()
