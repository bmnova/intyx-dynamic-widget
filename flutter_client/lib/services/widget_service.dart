/// Service for communicating with the backend API.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/trigger_context.dart';
import '../models/widget_response.dart';

class WidgetService {
  final String baseUrl;
  final http.Client _client;

  WidgetService({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  /// Fetch all widgets, optionally filtered by user.
  Future<List<WidgetEntry>> getWidgets({String? userId}) async {
    final uri = Uri.parse('$baseUrl/api/widgets').replace(
      queryParameters: userId != null ? {'user_id': userId} : null,
    );
    final response = await _client.get(uri);
    _checkResponse(response);

    final data = json.decode(response.body) as Map<String, dynamic>;
    return WidgetResponse.fromJson(data).widgets;
  }

  /// Evaluate triggers and get matching widgets.
  Future<List<WidgetEntry>> evaluateTriggers(TriggerContext context) async {
    final uri = Uri.parse('$baseUrl/api/widgets/evaluate');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode(context.toJson()),
    );
    _checkResponse(response);

    final data = json.decode(response.body) as Map<String, dynamic>;
    return WidgetResponse.fromJson(data).widgets;
  }

  /// Ask AI to suggest widgets for a context.
  Future<WidgetResponse> suggestWidgets(Map<String, dynamic> context) async {
    final uri = Uri.parse('$baseUrl/api/ai/suggest-widget');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode(context),
    );
    _checkResponse(response);

    final data = json.decode(response.body) as Map<String, dynamic>;
    return WidgetResponse.fromJson(data);
  }

  /// Dismiss a widget for a user.
  Future<void> dismissWidget(String widgetId, String userId) async {
    final uri = Uri.parse('$baseUrl/api/widgets/$widgetId/dismiss');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'user_id': userId}),
    );
    _checkResponse(response);
  }

  /// Record a widget interaction.
  Future<void> recordInteraction(
    String widgetId,
    String userId, {
    String action = 'tap',
  }) async {
    final uri = Uri.parse('$baseUrl/api/widgets/$widgetId/interact');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'user_id': userId, 'action': action}),
    );
    _checkResponse(response);
  }

  /// Record a user action for trigger evaluation.
  Future<void> recordUserAction(
    String userId,
    String action, {
    Map<String, dynamic>? metadata,
  }) async {
    final uri = Uri.parse('$baseUrl/api/widgets/user/action');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'user_id': userId,
        'action': action,
        if (metadata != null) 'metadata': metadata,
      }),
    );
    _checkResponse(response);
  }

  void dispose() => _client.close();

  void _checkResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw WidgetServiceException(
        'API error: ${response.statusCode}',
        statusCode: response.statusCode,
        body: response.body,
      );
    }
  }
}

class WidgetServiceException implements Exception {
  final String message;
  final int statusCode;
  final String body;

  WidgetServiceException(this.message, {required this.statusCode, required this.body});

  @override
  String toString() => 'WidgetServiceException($statusCode): $message';
}
