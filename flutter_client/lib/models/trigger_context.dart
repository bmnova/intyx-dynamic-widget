/// Client-side trigger context for sending to the backend.
library;

class TriggerContext {
  final String currentDate;
  final Map<String, dynamic>? weather;
  final List<Map<String, dynamic>> userActions;
  final Map<String, dynamic> userPreferences;
  final Set<String> dismissedWidgets;
  final Map<String, dynamic> developerParams;

  const TriggerContext({
    required this.currentDate,
    this.weather,
    this.userActions = const [],
    this.userPreferences = const {},
    this.dismissedWidgets = const {},
    this.developerParams = const {},
  });

  Map<String, dynamic> toJson() => {
    'current_date': currentDate,
    if (weather != null) 'weather': weather,
    'user_actions': userActions,
    'user_preferences': userPreferences,
    'dismissed_widgets': dismissedWidgets.toList(),
    'developer_params': developerParams,
  };
}
