/// Legacy widget definition models (for direct Firestore usage).
library;

enum WidgetActionType { navigate, openUrl, triggerFlow, dismiss }

enum WidgetCategory { contextual, promotional, functional, informational }

class WidgetAction {
  final WidgetActionType type;
  final String label;
  final String target;
  final Map<String, dynamic> metadata;

  const WidgetAction({
    required this.type,
    required this.label,
    required this.target,
    this.metadata = const {},
  });

  factory WidgetAction.fromJson(Map<String, dynamic> json) {
    return WidgetAction(
      type: WidgetActionType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => WidgetActionType.dismiss,
      ),
      label: json['label'] as String? ?? '',
      target: json['target'] as String? ?? '',
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toJson() => {
    'type': type.name,
    'label': label,
    'target': target,
    'metadata': metadata,
  };
}

class WidgetContent {
  final String title;
  final String description;
  final String imageUrl;
  final List<WidgetAction> actions;

  const WidgetContent({
    required this.title,
    this.description = '',
    this.imageUrl = '',
    this.actions = const [],
  });

  factory WidgetContent.fromJson(Map<String, dynamic> json) {
    return WidgetContent(
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      imageUrl: json['image_url'] as String? ?? '',
      actions: (json['actions'] as List<dynamic>?)
              ?.map((e) => WidgetAction.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'image_url': imageUrl,
    'actions': actions.map((a) => a.toJson()).toList(),
  };
}

class WidgetDefinition {
  final String id;
  final String name;
  final WidgetCategory category;
  final WidgetContent content;
  final int priority;
  final int? ttlMs;
  final double? createdAt;

  const WidgetDefinition({
    required this.id,
    required this.name,
    required this.category,
    required this.content,
    this.priority = 0,
    this.ttlMs,
    this.createdAt,
  });

  factory WidgetDefinition.fromJson(Map<String, dynamic> json) {
    return WidgetDefinition(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      category: WidgetCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => WidgetCategory.informational,
      ),
      content: WidgetContent.fromJson(
        json['content'] as Map<String, dynamic>? ?? {},
      ),
      priority: json['priority'] as int? ?? 0,
      ttlMs: json['ttl_ms'] as int?,
      createdAt: (json['created_at'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'category': category.name,
    'content': content.toJson(),
    'priority': priority,
    'ttl_ms': ttlMs,
    'created_at': createdAt,
  };
}
