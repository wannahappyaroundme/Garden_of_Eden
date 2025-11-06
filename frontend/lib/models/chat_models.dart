/// Data models for chat and API communication
library;

import 'dart:typed_data';

/// Chat Response from backend
class ChatResponse {
  final String conversationId;
  final String responseText;
  final String? responseAudioUrl;
  final String? responseAudioBase64;
  final bool pitfallWarningTriggered;
  final bool emotionalSupportMode;
  final bool profileUpdated;
  final int profileVersion;
  final int processingTimeMs;
  final Map<String, int>? tokensUsed;

  ChatResponse({
    required this.conversationId,
    required this.responseText,
    this.responseAudioUrl,
    this.responseAudioBase64,
    required this.pitfallWarningTriggered,
    required this.emotionalSupportMode,
    required this.profileUpdated,
    required this.profileVersion,
    required this.processingTimeMs,
    this.tokensUsed,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    // Parse tokens_used if present
    Map<String, int>? tokensUsed;
    if (json['tokens_used'] != null) {
      tokensUsed = Map<String, int>.from(json['tokens_used'] as Map);
    }

    return ChatResponse(
      conversationId: json['conversation_id'] as String,
      responseText: json['response_text'] as String,
      responseAudioUrl: json['response_audio_url'] as String?,
      responseAudioBase64: json['response_audio_base64'] as String?,
      pitfallWarningTriggered: json['pitfall_warning_triggered'] as bool? ?? false,
      emotionalSupportMode: json['emotional_support_mode'] as bool? ?? false,
      profileUpdated: json['profile_updated'] as bool? ?? false,
      profileVersion: json['profile_version'] as int? ?? 0,
      processingTimeMs: json['processing_time_ms'] as int? ?? 0,
      tokensUsed: tokensUsed,
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
    final personalitySummary = json['personality_summary'] as Map<String, dynamic>?;
    final topTraitsList = personalitySummary?['top_traits'] as List? ?? [];

    return UserProfile(
      userId: json['user_id'] as String,
      profileVersion: json['profile_version'] as int? ?? 0,
      oneThing: json['one_thing'] as String?,
      corePitfall: json['core_pitfall'] as String?,
      topTraits: topTraitsList
          .map((t) => PersonalityTrait.fromJson(t as Map<String, dynamic>))
          .toList(),
      recentEmotionalState: json['recent_emotional_state'] as String?,
      totalConversations: json['total_conversations'] as int? ?? 0,
      profileMaturity: json['profile_maturity'] as String? ?? 'new',
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : DateTime.now(),
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

/// Onboarding Response from backend
/// Used for Socratic dialogue onboarding flow
class OnboardingResponse {
  final String? sessionId;
  final String? question;
  final String? questionType;  // personal_info, multiple_choice, open_ended
  final List<Map<String, dynamic>>? options;  // For multiple choice questions
  final int? step;
  final int? totalSteps;
  final bool completed;
  final String? message;
  final OnboardingResult? result;

  OnboardingResponse({
    this.sessionId,
    this.question,
    this.questionType,
    this.options,
    this.step,
    this.totalSteps,
    required this.completed,
    this.message,
    this.result,
  });

  factory OnboardingResponse.fromJson(Map<String, dynamic> json) {
    // Handle both 'next_question' and 'question' fields
    String? questionText = json['question'] as String?;
    if (questionText == null || questionText.isEmpty) {
      questionText = json['next_question'] as String?;
    }

    // Make sure empty strings become null
    if (questionText != null && questionText.isEmpty) {
      questionText = null;
    }

    // Parse options for multiple choice questions
    List<Map<String, dynamic>>? options;
    if (json['options'] != null) {
      final optionsList = json['options'] as List;
      options = optionsList.map((opt) => Map<String, dynamic>.from(opt as Map)).toList();
    }

    return OnboardingResponse(
      sessionId: json['session_id'] as String?,
      question: questionText,
      questionType: json['question_type'] as String?,
      options: options,
      step: json['step'] as int?,
      totalSteps: json['total_steps'] as int?,
      completed: json['completed'] as bool? ?? false,
      message: json['message'] as String?,
      result: json['result'] != null
          ? OnboardingResult.fromJson(json['result'] as Map<String, dynamic>)
          : null,
    );
  }
}

/// Onboarding Result after completion
class OnboardingResult {
  final String userId;
  final String oneThing;
  final String? coreIdentity;
  final String? coreMotivation;
  final List<String> personalityHints;
  final String conversationSummary;

  OnboardingResult({
    required this.userId,
    required this.oneThing,
    this.coreIdentity,
    this.coreMotivation,
    required this.personalityHints,
    required this.conversationSummary,
  });

  factory OnboardingResult.fromJson(Map<String, dynamic> json) {
    final hints = json['personality_hints'] as List? ?? [];
    return OnboardingResult(
      userId: json['user_id'] as String,
      oneThing: json['one_thing'] as String,
      coreIdentity: json['core_identity'] as String?,
      coreMotivation: json['core_motivation'] as String?,
      personalityHints: hints.map((h) => h as String).toList(),
      conversationSummary: json['conversation_summary'] as String? ?? '',
    );
  }
}

/// Session Information
/// Used for tracking continuous conversation sessions
class SessionInfo {
  final String sessionId;
  final String userId;
  final String persona;
  final int turnCount;
  final DateTime createdAt;
  final DateTime lastActivity;
  final bool isActive;
  final bool isExpired;

  SessionInfo({
    required this.sessionId,
    required this.userId,
    required this.persona,
    required this.turnCount,
    required this.createdAt,
    required this.lastActivity,
    required this.isActive,
    required this.isExpired,
  });

  factory SessionInfo.fromJson(Map<String, dynamic> json) {
    return SessionInfo(
      sessionId: json['session_id'] as String,
      userId: json['user_id'] as String,
      persona: json['persona'] as String,
      turnCount: json['turn_count'] as int? ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      lastActivity: DateTime.parse(json['last_activity'] as String),
      isActive: json['is_active'] as bool? ?? false,
      isExpired: json['is_expired'] as bool? ?? false,
    );
  }

  /// Check if session needs refresh (close to expiration)
  bool needsRefresh() {
    final now = DateTime.now();
    final timeSinceActivity = now.difference(lastActivity);
    // Refresh if inactive for more than 8 minutes (TTL is 10 minutes)
    return timeSinceActivity.inMinutes > 8;
  }
}
