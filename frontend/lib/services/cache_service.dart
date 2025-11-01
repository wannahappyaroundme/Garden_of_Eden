/// Cache service for storing and retrieving data locally
library;

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/chat_models.dart';
import '../utils/logger.dart';

/// Cache service
class CacheService {
  static final CacheService _instance = CacheService._internal();
  factory CacheService() => _instance;
  CacheService._internal();

  final Logger _logger = Logger();
  SharedPreferences? _prefs;

  /// Initialize cache
  Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    _logger.info('Cache service initialized');
  }

  /// Cache keys
  static const String _keyUserProfile = 'user_profile_';
  static const String _keyLastResponse = 'last_response';
  static const String _keyAppSettings = 'app_settings';

  // ==================== User Profile ====================

  /// Save user profile to cache
  Future<void> saveProfile(UserProfile profile) async {
    try {
      final key = '$_keyUserProfile${profile.userId}';
      final json = jsonEncode({
        'user_id': profile.userId,
        'profile_version': profile.profileVersion,
        'one_thing': profile.oneThing,
        'core_pitfall': profile.corePitfall,
        'personality_summary': {
          'top_traits': profile.topTraits
              .map((t) => {'name': t.name, 'weight': t.weight})
              .toList(),
        },
        'recent_emotional_state': profile.recentEmotionalState,
        'total_conversations': profile.totalConversations,
        'profile_maturity': profile.profileMaturity,
        'last_updated': profile.lastUpdated.toIso8601String(),
      });

      await _prefs?.setString(key, json);
      _logger.debug('Saved profile to cache', data: {'userId': profile.userId});
    } catch (e) {
      _logger.error('Failed to save profile to cache', error: e);
    }
  }

  /// Load user profile from cache
  Future<UserProfile?> loadProfile(String userId) async {
    try {
      final key = '$_keyUserProfile$userId';
      final json = _prefs?.getString(key);

      if (json == null) {
        _logger.debug('No cached profile found', data: {'userId': userId});
        return null;
      }

      final data = jsonDecode(json) as Map<String, dynamic>;
      final profile = UserProfile.fromJson(data);

      _logger.debug('Loaded profile from cache', data: {'userId': userId});
      return profile;
    } catch (e) {
      _logger.error('Failed to load profile from cache', error: e);
      return null;
    }
  }

  /// Clear user profile cache
  Future<void> clearProfile(String userId) async {
    final key = '$_keyUserProfile$userId';
    await _prefs?.remove(key);
    _logger.debug('Cleared profile cache', data: {'userId': userId});
  }

  // ==================== Conversation History ====================

  /// Save last response
  Future<void> saveLastResponse(ChatResponse response) async {
    try {
      final json = jsonEncode({
        'conversation_id': response.conversationId,
        'response_text': response.responseText,
        'pitfall_warning_triggered': response.pitfallWarningTriggered,
        'emotional_support_mode': response.emotionalSupportMode,
        'profile_updated': response.profileUpdated,
        'profile_version': response.profileVersion,
        'processing_time_ms': response.processingTimeMs,
        'cached_at': DateTime.now().toIso8601String(),
      });

      await _prefs?.setString(_keyLastResponse, json);
      _logger.debug('Saved last response to cache');
    } catch (e) {
      _logger.error('Failed to save last response', error: e);
    }
  }

  /// Load last response
  Future<ChatResponse?> loadLastResponse() async {
    try {
      final json = _prefs?.getString(_keyLastResponse);

      if (json == null) {
        return null;
      }

      final data = jsonDecode(json) as Map<String, dynamic>;

      // Check if cached response is recent (within 1 hour)
      final cachedAt = DateTime.parse(data['cached_at'] as String);
      if (DateTime.now().difference(cachedAt).inHours > 1) {
        _logger.debug('Cached response expired');
        return null;
      }

      final response = ChatResponse.fromJson(data);
      _logger.debug('Loaded last response from cache');
      return response;
    } catch (e) {
      _logger.error('Failed to load last response', error: e);
      return null;
    }
  }

  // ==================== App Settings ====================

  /// Save app settings
  Future<void> saveSettings({
    double? ttsVolume,
    bool? cameraEnabled,
    String? defaultPersona,
  }) async {
    try {
      final current = await loadSettings();

      final settings = {
        'tts_volume': ttsVolume ?? current['tts_volume'] ?? 1.0,
        'camera_enabled': cameraEnabled ?? current['camera_enabled'] ?? true,
        'default_persona': defaultPersona ?? current['default_persona'] ?? 'adam',
      };

      await _prefs?.setString(_keyAppSettings, jsonEncode(settings));
      _logger.debug('Saved app settings', data: settings);
    } catch (e) {
      _logger.error('Failed to save settings', error: e);
    }
  }

  /// Load app settings
  Future<Map<String, dynamic>> loadSettings() async {
    try {
      final json = _prefs?.getString(_keyAppSettings);

      if (json == null) {
        return _getDefaultSettings();
      }

      final settings = jsonDecode(json) as Map<String, dynamic>;
      _logger.debug('Loaded app settings');
      return settings;
    } catch (e) {
      _logger.error('Failed to load settings', error: e);
      return _getDefaultSettings();
    }
  }

  /// Get default settings
  Map<String, dynamic> _getDefaultSettings() {
    return {
      'tts_volume': 1.0,
      'camera_enabled': true,
      'default_persona': 'adam',
    };
  }

  // ==================== Clear All ====================

  /// Clear all cache
  Future<void> clearAll() async {
    await _prefs?.clear();
    _logger.info('Cleared all cache');
  }

  /// Get cache size (approximate)
  Future<int> getCacheSize() async {
    try {
      final keys = _prefs?.getKeys() ?? {};
      int totalSize = 0;

      for (final key in keys) {
        final value = _prefs?.get(key);
        if (value is String) {
          totalSize += value.length;
        } else if (value is double) {
          totalSize += 8; // Approximate size of double
        } else if (value is int) {
          totalSize += 8; // Approximate size of int
        } else if (value is bool) {
          totalSize += 1; // Approximate size of bool
        }
      }

      _logger.debug('Cache size calculated', data: {'bytes': totalSize});
      return totalSize;
    } catch (e) {
      _logger.error('Failed to calculate cache size', error: e);
      return 0;
    }
  }
}
