/// Local LLM Service - On-device AI for simple queries
library;

import 'intent_classifier_service.dart';

/// Local response for simple queries
class LocalResponse {
  final String text;
  final bool needsTTS;

  const LocalResponse({
    required this.text,
    this.needsTTS = true,
  });
}

/// Local LLM Service (rule-based for now, can be replaced with TFLite model)
class LocalLLMService {
  final IntentClassifierService _classifier = IntentClassifierService();

  /// Generate local response for simple queries
  Future<LocalResponse?> generateResponse(String query) async {
    final intent = _classifier.classifyIntent(query);

    // Only handle simple intents locally
    if (!intent.isSimple) {
      return null; // Defer to cloud
    }

    switch (intent.category) {
      case IntentCategory.greeting:
        return _generateGreeting(query);

      case IntentCategory.time:
        return _generateTimeResponse();

      case IntentCategory.weather:
        return null; // Weather requires API, defer to cloud

      case IntentCategory.simpleQuestion:
        return _generateSimpleAnswer(query);

      default:
        return null; // Defer to cloud
    }
  }

  /// Generate greeting response
  LocalResponse _generateGreeting(String query) {
    final now = DateTime.now();
    final hour = now.hour;

    String greeting;
    if (hour < 12) {
      greeting = '좋은 아침이에요!';
    } else if (hour < 18) {
      greeting = '안녕하세요!';
    } else {
      greeting = '좋은 저녁이에요!';
    }

    final responses = [
      '$greeting 무엇을 도와드릴까요?',
      '$greeting 오늘 하루는 어떠세요?',
      '$greeting Adam이에요. 어떻게 도와드릴까요?',
    ];

    return LocalResponse(
      text: responses[now.second % responses.length],
      needsTTS: true,
    );
  }

  /// Generate time response
  LocalResponse _generateTimeResponse() {
    final now = DateTime.now();
    final hour = now.hour;
    final minute = now.minute;

    String period = hour < 12 ? '오전' : '오후';
    int displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);

    return LocalResponse(
      text: '지금은 $period $displayHour시 $minute분이에요.',
      needsTTS: true,
    );
  }

  /// Generate simple answer
  LocalResponse? _generateSimpleAnswer(String query) {
    final lowerQuery = query.toLowerCase();

    // Handle "who are you" type questions
    if (lowerQuery.contains('누구') || lowerQuery.contains('who')) {
      return const LocalResponse(
        text: '저는 Adam이에요. 당신의 AI 파트너입니다.',
        needsTTS: true,
      );
    }

    // Handle "what is this" type questions
    if (lowerQuery.contains('이게 뭐') || lowerQuery.contains('what')) {
      return const LocalResponse(
        text: '좀 더 자세히 설명해 주시겠어요? 구체적으로 무엇에 대해 궁금하신가요?',
        needsTTS: true,
      );
    }

    // Defer to cloud for other questions
    return null;
  }

  /// Check if query can be handled locally
  bool canHandleLocally(String query) {
    final intent = _classifier.classifyIntent(query);
    return intent.isSimple && intent.confidence > 0.7;
  }

  /// Dispose resources (for TFLite model cleanup in future)
  void dispose() {
    // Will be used when TFLite model is added
  }
}
