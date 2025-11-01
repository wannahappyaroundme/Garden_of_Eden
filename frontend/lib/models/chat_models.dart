/// Data models for chat and API communication
library;

import 'dart:typed_data';

/// Chat Response from backend
class ChatResponse {
  final String conversationId;
  final String responseText;
  final String? responseAudioBase64;
  final bool pitfallWarningTriggered;
  final bool emotionalSupportMode;
  final bool profileUpdated;
  final int profileVersion;
  final int processingTimeMs;

  ChatResponse({
    required this.conversationId,
    required this.responseText,
    this.responseAudioBase64,
    required this.pitfallWarningTriggered,
    required this.emotionalSupportMode,
    required this.profileUpdated,
    required this.profileVersion,
    required this.processingTimeMs,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      conversationId: json['conversation_id'] as String,
      responseText: json['response_text'] as String,
      responseAudioBase64: json['response_audio_base64'] as String?,
      pitfallWarningTriggered: json['pitfall_warning_triggered'] as bool,
      emotionalSupportMode: json['emotional_support_mode'] as bool,
      profileUpdated: json['profile_updated'] as bool,
      profileVersion: json['profile_version'] as int,
      processingTimeMs: json['processing_time_ms'] as int,
    );
  }
}

/// User Profile Response
class UserProfile {
  final String userId;
  final int profileVersion;
  final String? oneThing;
  final String? corePitfall;
  final List<PersonalityTrait> topTraits;
  final String? recentEmotionalState;
  final int totalConversations;
  final String profileMaturity;
  final DateTime lastUpdated;

  UserProfile({
    required this.userId,
    required this.profileVersion,
    this.oneThing,
    this.corePitfall,
    required this.topTraits,
    this.recentEmotionalState,
    required this.totalConversations,
    required this.profileMaturity,
    required this.lastUpdated,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    final personalitySummary = json['personality_summary'] as Map<String, dynamic>;
    final topTraitsList = personalitySummary['top_traits'] as List;

    return UserProfile(
      userId: json['user_id'] as String,
      profileVersion: json['profile_version'] as int,
      oneThing: json['one_thing'] as String?,
      corePitfall: json['core_pitfall'] as String?,
      topTraits: topTraitsList
          .map((t) => PersonalityTrait.fromJson(t as Map<String, dynamic>))
          .toList(),
      recentEmotionalState: json['recent_emotional_state'] as String?,
      totalConversations: json['total_conversations'] as int,
      profileMaturity: json['profile_maturity'] as String,
      lastUpdated: DateTime.parse(json['last_updated'] as String),
    );
  }
}

/// Personality Trait
class PersonalityTrait {
  final String name;
  final double weight;

  PersonalityTrait({
    required this.name,
    required this.weight,
  });

  factory PersonalityTrait.fromJson(Map<String, dynamic> json) {
    return PersonalityTrait(
      name: json['name'] as String,
      weight: (json['weight'] as num).toDouble(),
    );
  }
}

/// Camera Frame (for upload)
class CameraFrame {
  final Uint8List imageBytes;
  final DateTime timestamp;

  CameraFrame({
    required this.imageBytes,
    required this.timestamp,
  });
}
