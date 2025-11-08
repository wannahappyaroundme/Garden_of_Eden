/// Intent Classifier Service - Determines query complexity
library;

/// Query complexity levels
enum QueryComplexity {
  simple, // Can be handled by on-device AI or cache
  complex, // Requires cloud AI
}

/// Intent categories
enum IntentCategory {
  greeting,
  time,
  weather,
  simpleQuestion,
  conversation,
  advice,
  complex,
}

/// Intent classification result
class IntentResult {
  final QueryComplexity complexity;
  final IntentCategory category;
  final double confidence;

  const IntentResult({
    required this.complexity,
    required this.category,
    required this.confidence,
  });

  bool get isSimple => complexity == QueryComplexity.simple;
  bool get isComplex => complexity == QueryComplexity.complex;
}

/// Intent Classifier Service
class IntentClassifierService {
  // Simple patterns for local processing
  static const _greetingPatterns = [
    '안녕',
    '하이',
    'hi',
    'hello',
    '헬로',
    '굿모닝',
    'good morning',
  ];

  static const _timePatterns = [
    '시간',
    '몇 시',
    'time',
    '지금',
    'now',
  ];

  static const _weatherPatterns = [
    '날씨',
    'weather',
    '비',
    '눈',
    '맑',
    '흐림',
  ];

  static const _simpleQuestionPatterns = [
    '뭐야',
    '뭐',
    '누구',
    'what',
    'who',
    '언제',
    'when',
  ];

  // Complex patterns requiring cloud AI
  static const _conversationPatterns = [
    '나',
    '내',
    '오늘',
    '어제',
    '힘들',
    '기분',
    '생각',
  ];

  static const _advicePatterns = [
    '어떻게',
    'how',
    '방법',
    '해야',
    '하면',
    '추천',
    'recommend',
  ];

  /// Classify user query intent
  IntentResult classifyIntent(String query) {
    final lowerQuery = query.toLowerCase().trim();

    // Empty query
    if (lowerQuery.isEmpty) {
      return const IntentResult(
        complexity: QueryComplexity.complex,
        category: IntentCategory.complex,
        confidence: 1.0,
      );
    }

    // Check for simple patterns first
    if (_containsAny(lowerQuery, _greetingPatterns)) {
      return const IntentResult(
        complexity: QueryComplexity.simple,
        category: IntentCategory.greeting,
        confidence: 0.9,
      );
    }

    if (_containsAny(lowerQuery, _timePatterns)) {
      return const IntentResult(
        complexity: QueryComplexity.simple,
        category: IntentCategory.time,
        confidence: 0.85,
      );
    }

    if (_containsAny(lowerQuery, _weatherPatterns)) {
      return const IntentResult(
        complexity: QueryComplexity.simple,
        category: IntentCategory.weather,
        confidence: 0.8,
      );
    }

    // Check for complex patterns
    if (_containsAny(lowerQuery, _conversationPatterns) ||
        _containsAny(lowerQuery, _advicePatterns)) {
      return const IntentResult(
        complexity: QueryComplexity.complex,
        category: IntentCategory.conversation,
        confidence: 0.75,
      );
    }

    // Short queries are likely simple
    if (query.length < 15 && _containsAny(lowerQuery, _simpleQuestionPatterns)) {
      return const IntentResult(
        complexity: QueryComplexity.simple,
        category: IntentCategory.simpleQuestion,
        confidence: 0.7,
      );
    }

    // Default to complex for safety
    return const IntentResult(
      complexity: QueryComplexity.complex,
      category: IntentCategory.complex,
      confidence: 0.6,
    );
  }

  /// Check if query contains any of the patterns
  bool _containsAny(String query, List<String> patterns) {
    return patterns.any((pattern) => query.contains(pattern.toLowerCase()));
  }

  /// Calculate complexity score (0.0 = simple, 1.0 = complex)
  double calculateComplexityScore(String query) {
    final result = classifyIntent(query);
    return result.isSimple ? 0.0 : 1.0;
  }
}
